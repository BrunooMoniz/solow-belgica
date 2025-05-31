import pandas as pd
import numpy as np
import statsmodels.api as sm
import matplotlib.pyplot as plt
import os
import sys
from pathlib import Path

# Adicionando o diretório de dados ao path
sys.path.append(str(Path(__file__).parent.parent))
from data.belgium_data import *

def run_solow_model(data, output_dir):
    """
    Executa o modelo de Solow com capital humano para os dados fornecidos.
    
    O modelo de Solow com capital humano é baseado na equação:
    ln(Y/L) = ln(A) + α*ln(K/L) + β*ln(H)
    
    Onde:
    - Y/L é o PIB per capita
    - A é a produtividade total dos fatores
    - K/L é o estoque de capital per capita
    - H é o capital humano (anos de escolaridade)
    - α é a elasticidade do produto em relação ao capital físico
    - β é a elasticidade do produto em relação ao capital humano
    """
    
    # Preparando os dados para a regressão
    # Usamos os dados a partir de 1960 para garantir consistência
    model_data = data[['Year', 'ln_gdp_per_capita', 'ln_capital_per_capita', 'ln_education']].copy()
    model_data = model_data.dropna()
    
    # Adicionando constante para o intercepto
    X = model_data[['ln_capital_per_capita', 'ln_education']]
    X = sm.add_constant(X)
    y = model_data['ln_gdp_per_capita']
    
    # Estimando o modelo
    model = sm.OLS(y, X)
    results = model.fit()
    
    # Salvando os resultados
    with open(f"{output_dir}/solow_model_results.txt", "w") as f:
        f.write(results.summary().as_text())
    
    # Criando tabela de resultados em formato mais amigável
    coefs = results.params
    std_errs = results.bse
    t_values = results.tvalues
    p_values = results.pvalues
    conf_int = results.conf_int()
    
    results_table = pd.DataFrame({
        'Coeficiente': coefs,
        'Erro Padrão': std_errs,
        'Estatística t': t_values,
        'Valor p': p_values,
        'IC 95% (Inferior)': conf_int[0],
        'IC 95% (Superior)': conf_int[1]
    })
    
    # Adicionando métricas de ajuste do modelo
    metrics = pd.DataFrame({
        'Métrica': ['R²', 'R² Ajustado', 'F-statistic', 'Prob (F-statistic)', 'AIC', 'BIC', 'Observações'],
        'Valor': [results.rsquared, results.rsquared_adj, results.fvalue, results.f_pvalue, 
                 results.aic, results.bic, results.nobs]
    })
    
    # Salvando as tabelas
    results_table.to_csv(f"{output_dir}/solow_model_coefficients.csv")
    metrics.to_csv(f"{output_dir}/solow_model_metrics.csv", index=False)
    
    # Calculando valores previstos e resíduos
    model_data['predicted'] = results.predict(X)
    model_data['residuals'] = results.resid
    
    # Criando gráficos
    plt.figure(figsize=(12, 8))
    
    # Gráfico 1: PIB per capita observado vs previsto
    plt.subplot(2, 2, 1)
    plt.plot(model_data['Year'], np.exp(model_data['ln_gdp_per_capita']), 'b-', label='Observado')
    plt.plot(model_data['Year'], np.exp(model_data['predicted']), 'r--', label='Previsto')
    plt.title('PIB per capita: Observado vs Previsto')
    plt.xlabel('Ano')
    plt.ylabel('PIB per capita (USD constantes)')
    plt.legend()
    plt.grid(True)
    
    # Gráfico 2: Resíduos ao longo do tempo
    plt.subplot(2, 2, 2)
    plt.plot(model_data['Year'], model_data['residuals'], 'g-')
    plt.axhline(y=0, color='r', linestyle='-')
    plt.title('Resíduos ao longo do tempo')
    plt.xlabel('Ano')
    plt.ylabel('Resíduos')
    plt.grid(True)
    
    # Gráfico 3: Relação entre capital físico e PIB
    plt.subplot(2, 2, 3)
    plt.scatter(model_data['ln_capital_per_capita'], model_data['ln_gdp_per_capita'])
    plt.title('Relação entre Capital Físico e PIB')
    plt.xlabel('ln(Capital per capita)')
    plt.ylabel('ln(PIB per capita)')
    plt.grid(True)
    
    # Gráfico 4: Relação entre capital humano e PIB
    plt.subplot(2, 2, 4)
    plt.scatter(model_data['ln_education'], model_data['ln_gdp_per_capita'])
    plt.title('Relação entre Capital Humano e PIB')
    plt.xlabel('ln(Anos de Escolaridade)')
    plt.ylabel('ln(PIB per capita)')
    plt.grid(True)
    
    plt.tight_layout()
    plt.savefig(f"{output_dir}/solow_model_plots.png")
    
    # Criando tabela completa com dados originais e resultados do modelo
    full_results = data.merge(model_data[['Year', 'predicted', 'residuals']], on='Year', how='left')
    full_results['predicted_gdp_per_capita'] = np.exp(full_results['predicted'])
    full_results['gdp_growth_rate'] = full_results['GDP per capita constant dollars'].pct_change() * 100
    full_results['predicted_growth_rate'] = full_results['predicted_gdp_per_capita'].pct_change() * 100
    
    # Calculando contribuições para o crescimento
    # Baseado nos coeficientes estimados
    alpha = coefs['ln_capital_per_capita']  # Elasticidade do capital físico
    beta = coefs['ln_education']  # Elasticidade do capital humano
    
    # Contribuição do capital físico = α * Δln(K/L)
    full_results['capital_contribution'] = alpha * full_results['ln_capital_per_capita'].diff()
    
    # Contribuição do capital humano = β * Δln(H)
    full_results['human_capital_contribution'] = beta * full_results['ln_education'].diff()
    
    # Contribuição da PTF (Produtividade Total dos Fatores) = Δln(Y/L) - α*Δln(K/L) - β*Δln(H)
    full_results['ptf_contribution'] = (full_results['ln_gdp_per_capita'].diff() - 
                                       full_results['capital_contribution'] - 
                                       full_results['human_capital_contribution'])
    
    # Convertendo para percentual
    for col in ['capital_contribution', 'human_capital_contribution', 'ptf_contribution']:
        full_results[col] = full_results[col] * 100
    
    # Salvando a tabela completa
    full_results.to_csv(f"{output_dir}/solow_model_full_results.csv", index=False)
    
    return results, full_results

if __name__ == "__main__":
    # Definindo diretórios
    current_dir = os.path.dirname(os.path.abspath(__file__))
    parent_dir = os.path.dirname(current_dir)
    data_dir = os.path.join(parent_dir, "data")
    results_dir = os.path.join(parent_dir, "results")
    
    # Executando o script de preparação de dados se necessário
    if not os.path.exists(os.path.join(data_dir, "belgium_processed.csv")):
        print("Processando dados da Bélgica...")
        # Executando o script de preparação de dados
        exec(open(os.path.join(data_dir, "belgium_data.py")).read())
    
    # Carregando os dados processados
    belgium_data = pd.read_csv(os.path.join(data_dir, "belgium_processed.csv"))
    
    # Executando o modelo de Solow
    print("Executando o modelo de Solow com capital humano para a Bélgica...")
    results, full_results = run_solow_model(belgium_data, results_dir)
    
    print("Modelo executado com sucesso! Resultados salvos em:", results_dir)
    print("\nResumo do modelo:")
    print(results.summary())
