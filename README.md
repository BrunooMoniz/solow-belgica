# Modelo de Solow com Capital Humano para a Bélgica

Este projeto implementa o modelo de Solow com capital humano para a Bélgica, utilizando dados de PIB per capita, investimento em capital, força de trabalho e anos esperados de escolaridade.

Vídeo sobre o trabalho: https://youtu.be/EcgMg5JjiYs

Para o trabalho completo, acesse: https://ecwhaxlr.manus.space/#introducao

## Estrutura do Projeto

```
solow_belgium_entrega/
├── code/                   # Código fonte
│   └── solow_model.py      # Script principal para execução do modelo
├── data/                   # Dados utilizados
│   ├── belgium_data.py     # Script de preparação dos dados
│   └── belgium_processed.csv # Dados processados
├── results/                # Resultados da análise
│   ├── solow_model_coefficients.csv  # Coeficientes estimados
│   ├── solow_model_full_results.csv  # Resultados completos
│   ├── solow_model_metrics.csv       # Métricas de ajuste do modelo
│   ├── solow_model_plots.png         # Gráficos do modelo
│   └── solow_model_results.txt       # Resumo dos resultados
├── site/                   # Site para apresentação dos resultados
│   ├── assets/             # Arquivos CSS e JavaScript
│   ├── index.html          # Página principal do site
│   └── solow_model_plots.png # Gráficos para o site
└── requirements.txt        # Dependências do projeto
```

## Requisitos

Para executar o código, você precisará de:

- Python 3.8 ou superior
- Bibliotecas Python listadas em `requirements.txt`

## Instalação

1. Clone ou extraia este repositório para sua máquina local
2. Instale as dependências:

```bash
pip install -r requirements.txt
```

## Execução do Modelo

Para executar o modelo de Solow com capital humano para a Bélgica:

```bash
cd solow_belgium_entrega
python code/solow_model.py
```

Este comando irá:
1. Processar os dados da Bélgica (se necessário)
2. Estimar o modelo de Solow com capital humano
3. Gerar tabelas e gráficos com os resultados
4. Salvar todos os resultados no diretório `results/`

## Visualização do Site

O site de apresentação está disponível no diretório `site/`. Para visualizá-lo:

1. Navegue até o diretório `site/`
2. Abra o arquivo `index.html` em qualquer navegador moderno

Alternativamente, você pode hospedar o site em qualquer servidor web estático.

## Resultados Principais

Os principais resultados da estimação do modelo de Solow com capital humano para a Bélgica são:

- Elasticidade do capital físico: 0,191
- Elasticidade do capital humano: 0,473
- R²: 0,991

Estes resultados indicam que o capital humano tem um impacto substancialmente maior no PIB per capita da Bélgica em comparação com o capital físico, destacando a importância dos investimentos em educação para o crescimento econômico do país.

## Autor

Bruno Moniz - Ciências Econômicas - PUC
