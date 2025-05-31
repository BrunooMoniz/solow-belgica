import pandas as pd
import numpy as np
import os

# Definindo o diretório de dados
data_dir = os.path.dirname(os.path.abspath(__file__))
upload_dir = "/home/ubuntu/upload"

# Carregando os dados econômicos
econ_data = pd.read_csv(f"{upload_dir}/31-05-2507_44_50_theglobaleconomy.csv")
edu_data = pd.read_csv(f"{upload_dir}/expected-years-of-schooling.csv")

# Filtrando apenas os dados da Bélgica
belgium_econ = econ_data[econ_data['Country'] == 'Belgium'].copy()
belgium_edu = edu_data[edu_data['Entity'] == 'Belgium'].copy()

# Renomeando colunas para facilitar o merge
belgium_edu = belgium_edu.rename(columns={'Expected years of schooling': 'education'})

# Mesclando os dados por ano
belgium_data = pd.merge(belgium_econ, belgium_edu[['Year', 'education']], 
                        on='Year', how='left')

# Tratando valores ausentes para anos de escolaridade antes de 1990
# Usando interpolação linear para estimar valores faltantes
# Primeiro, vamos criar uma série temporal completa
years = np.arange(belgium_data['Year'].min(), belgium_data['Year'].max() + 1)
complete_df = pd.DataFrame({'Year': years})

# Mesclando com os dados existentes
belgium_data = pd.merge(complete_df, belgium_data, on='Year', how='left')

# Preenchendo valores ausentes para o país e código
belgium_data['Country'] = 'Belgium'
belgium_data['Code'] = 'BEL'
belgium_data['ContinentCode'] = 'EU'

# Interpolação para anos de escolaridade
# Para anos anteriores a 1990, vamos usar uma abordagem conservadora
# baseada na tendência observada entre 1990 e 2000
first_valid_edu = belgium_data.loc[belgium_data['education'].notna(), 'education'].iloc[0]
edu_growth_rate = (belgium_data.loc[belgium_data['Year'] == 2000, 'education'].values[0] - 
                   belgium_data.loc[belgium_data['Year'] == 1990, 'education'].values[0]) / 10

# Aplicando uma taxa de crescimento reversa para estimar anos anteriores a 1990
for year in range(1989, belgium_data['Year'].min() - 1, -1):
    idx = belgium_data[belgium_data['Year'] == year].index[0]
    next_year_edu = belgium_data.loc[belgium_data['Year'] == (year + 1), 'education'].values[0]
    if pd.isna(next_year_edu):
        continue
    belgium_data.loc[idx, 'education'] = next_year_edu - edu_growth_rate

# Interpolação linear para quaisquer outros valores ausentes
belgium_data['education'] = belgium_data['education'].interpolate(method='linear')

# Tratando valores ausentes para investimento em capital e força de trabalho
# Para investimento em capital, vamos usar uma proporção do PIB para anos anteriores a 1970
gdp_inv_ratio = belgium_data.loc[(belgium_data['Year'] >= 1970) & 
                                (belgium_data['Year'] <= 1980), 
                                'Capital investment billion USD'].sum() / \
                belgium_data.loc[(belgium_data['Year'] >= 1970) & 
                                (belgium_data['Year'] <= 1980), 
                                'GDP per capita constant dollars'].sum()

for year in range(1969, belgium_data['Year'].min() - 1, -1):
    idx = belgium_data[belgium_data['Year'] == year].index[0]
    gdp = belgium_data.loc[idx, 'GDP per capita constant dollars']
    belgium_data.loc[idx, 'Capital investment billion USD'] = gdp * gdp_inv_ratio

# Para força de trabalho, vamos usar uma taxa de crescimento baseada nos anos disponíveis
# Primeiro, vamos identificar o primeiro ano com dados de força de trabalho
first_labor_year = belgium_data.loc[belgium_data['Labor force million people'].notna(), 'Year'].min()
first_labor_value = belgium_data.loc[belgium_data['Year'] == first_labor_year, 'Labor force million people'].values[0]

# Calculando a taxa média de crescimento anual para os primeiros 5 anos disponíveis
labor_years = belgium_data.loc[belgium_data['Labor force million people'].notna(), 'Year'].sort_values()[:5]
labor_growth = (belgium_data.loc[belgium_data['Year'] == labor_years.iloc[-1], 'Labor force million people'].values[0] / 
                first_labor_value) ** (1 / (labor_years.iloc[-1] - first_labor_year)) - 1

# Aplicando uma taxa de crescimento reversa para estimar anos anteriores
for year in range(int(first_labor_year) - 1, belgium_data['Year'].min() - 1, -1):
    idx = belgium_data[belgium_data['Year'] == year].index[0]
    next_year_labor = belgium_data.loc[belgium_data['Year'] == (year + 1), 'Labor force million people'].values[0]
    belgium_data.loc[idx, 'Labor force million people'] = next_year_labor / (1 + labor_growth)

# Interpolação linear para quaisquer outros valores ausentes
belgium_data['Labor force million people'] = belgium_data['Labor force million people'].interpolate(method='linear')
belgium_data['Capital investment billion USD'] = belgium_data['Capital investment billion USD'].interpolate(method='linear')

# Calculando variáveis adicionais necessárias para o modelo de Solow
# PIB total (em bilhões de dólares)
belgium_data['GDP billion USD'] = belgium_data['GDP per capita constant dollars'] * belgium_data['Labor force million people']

# Estoque de capital (usando o método do inventário perpétuo)
# K(t) = I(t) + (1-δ)K(t-1), onde δ é a taxa de depreciação
delta = 0.06  # Taxa de depreciação padrão de 6%

# Inicializando o estoque de capital
# K(0) = I(0) / (g + δ), onde g é a taxa de crescimento do investimento
g = belgium_data['Capital investment billion USD'].pct_change().mean()
belgium_data['Capital stock billion USD'] = 0.0

# Primeiro ano
first_year = belgium_data['Year'].min()
first_inv = belgium_data.loc[belgium_data['Year'] == first_year, 'Capital investment billion USD'].values[0]
belgium_data.loc[belgium_data['Year'] == first_year, 'Capital stock billion USD'] = first_inv / (g + delta)

# Anos subsequentes
for year in range(int(first_year) + 1, int(belgium_data['Year'].max()) + 1):
    prev_idx = belgium_data[belgium_data['Year'] == (year - 1)].index[0]
    curr_idx = belgium_data[belgium_data['Year'] == year].index[0]
    
    prev_k = belgium_data.loc[prev_idx, 'Capital stock billion USD']
    curr_i = belgium_data.loc[curr_idx, 'Capital investment billion USD']
    
    belgium_data.loc[curr_idx, 'Capital stock billion USD'] = curr_i + (1 - delta) * prev_k

# Calculando variáveis em termos per capita
belgium_data['Capital stock per capita'] = belgium_data['Capital stock billion USD'] * 1e9 / (belgium_data['Labor force million people'] * 1e6)

# Calculando variáveis em logaritmo natural para o modelo de Solow
belgium_data['ln_gdp_per_capita'] = np.log(belgium_data['GDP per capita constant dollars'])
belgium_data['ln_capital_per_capita'] = np.log(belgium_data['Capital stock per capita'])
belgium_data['ln_education'] = np.log(belgium_data['education'])

# Salvando os dados tratados
belgium_data.to_csv(f"{data_dir}/belgium_processed.csv", index=False)

print("Dados da Bélgica processados e salvos com sucesso!")
