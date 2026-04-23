# Pipeline de Dados de Expositores + Dashboard

![Python](https://img.shields.io/badge/Python-3.11-blue?logo=python)
![Streamlit](https://img.shields.io/badge/Dashboard-Streamlit-ff4b4b?logo=streamlit)
![PostgreSQL](https://img.shields.io/badge/Banco-PostgreSQL-336791?logo=postgresql)
![Status](https://img.shields.io/badge/Status-Development-yellow)

---

## Visão Geral

Pipeline ETL em Python que extrai dados de planilhas Excel (Google Drive), transforma e carrega em PostgreSQL, com um dashboard Streamlit para análise comercial de expositores.

O projeto substitui consolidação manual de planilhas por uma pipeline reprodutível com rastreabilidade histórica dos dados.

---

## Estrutura

```
├── app/
│   ├── config.py             # URLs e secrets
│   ├── pipeline.py           # Orquestração do ETL
│   ├── data/
│   │   ├── get_data.py       # Download das planilhas Excel
│   │   └── transform.py      # Limpeza e transformação dos dados
│   └── db/
│       ├── database.py       # Engine SQLAlchemy (singleton)
│       └── operations.py     # TRUNCATE + INSERT + histórico
├── dash/
│   ├── dashboard.py          # App Streamlit
│   ├── kpis.py               # Cálculo de KPIs e gráficos
│   ├── data_loader.py        # Leitura do banco com cache
│   ├── exagerado_theme.py    # Tema e componentes visuais
│   └── config.toml           # Configurações do Streamlit
├── forecast/
│   ├── __init__.py           # Exports das funções principais
│   ├── model.py              # Modelo NeuralProphet + Croston
│   ├── pipeline.py           # ETL de previsão e otimização
│   ├── simulation.py         # Simulação Monte Carlo
│   └── trends.py             # Busca de trends do Google
├── models/
│   └── model_otimo.np        # Modelo NeuralProphet treinado
├── img/
│   └── favicon.ico
├── notebooks/
│   ├── model_training_forecast.ipynb
│   ├── pricing_analysis_es.ipynb
│   ├── pricing_analysis_rj.ipynb
│   └── simulation_validation.ipynb
├── .streamlit/
│   └── secrets.toml          # Configurações sensíveis
├── README.md
└── requirements.txt
```

---

## Arquitetura do Banco

Tabelas PostgreSQL:

**`expositores_atual`** — estado mais recente de cada expositor (1 linha por expositor). Truncada e recarregada a cada execução do ETL.

**`expositores_historico`** — acumula snapshots ao longo do tempo. Só insere linhas com hash diferente do último estado, rastreando qualquer mudança em qualquer campo.

**`forecast_trends_cache`** — cache de previsões de trends para cada expositor.

**`forecast_trends_otm`** — resultados da otimização de parâmetros por expositor.

---

## ETL

Fluxo executado via botão no dashboard ou diretamente por `pipeline.py`:

1. Download das planilhas Excel via URL (Google Drive)
2. Limpeza, normalização e tipagem dos dados
3. Combinação dos DataFrames por evento (ES, RJ, SP)
4. `TRUNCATE` do `expositores_atual` + insert dos dados novos
5. Insert no `expositores_historico` apenas das linhas com hash diferente

Tudo dentro de uma única transação — se qualquer passo falhar, o banco fica intacto.

---

## Módulo de Previsão (forecast/)

### trends.py
Busca dados de trends do Google Trends para cada expositor:
- Usa a biblioteca `pytrends` para consultar volume de buscas
- Classifica a série temporal (ótima, intermitente, sem sinal)
- Retorna DataFrame com dados históricos de trends

### model.py
Modelo de previsão com duas abordagens:
- **NeuralProphet**: modelo de série temporal neural (model_otimo.np)
- **Croston**: método para séries intermitentes (poucos dados)
- Classifica automaticamente o tipo de série e escolhe o melhor método

### simulation.py
Simulação Monte Carlo para análise de cenários:
- `rodar_monte_carlo()`: executa N simulações com parâmetros variáveis
- `melhores_parametros_otimizados()`: encontra melhores parâmetros para atingir 60% de probabilidade

### pipeline.py
ETL de previsão que orchestra todos os módulos:
- `rodar_etl_oficial()`: processa todos os expositores comissionados
- `rodar_etl_otimizacao()`: processa um expositor específico para simulação

---

## Dashboard

Desenvolvido em Streamlit com as seções:

- **Comercial** — expositores, vacâncias, contratos, recorrência
- **Receita** — receita realizada vs meta, top 3 expositores
- **Descontos** — total concedido, média por expositor
- **Espaço** — área ocupada vs disponível, receita por m²
- **Comissionado** — expositores com comissão ativa e performance
- **Previsão** — projeção de receita e gap para meta
- **Simulação** — simulação Monte Carlo para análise de cenários

Filtros disponíveis: evento (ES / RJ / SP), período (Hoje / Semana / Mês / Total) e tipo (STAND / FOOD).

---

## Configuração

Crie um arquivo `.streamlit/secrets.toml`:

```toml
[urls]
URL_ES_STAND = "..."
URL_ES_FOOD = "..."
URL_RJ_STAND = "..."
URL_SP_STAND = "..."

[postgres]
url = "postgresql://user:password@host:5432/dbname"

[data_alvo]
DATA_ALVO = "2026-08-01"
```

Instale as dependências:

```bash
pip install -r requirements.txt
```

Rode o dashboard:

```bash
streamlit run dash/dashboard.py
```

---

## Tecnologias

- Python 3.11
- Pandas + NumPy
- SQLAlchemy + psycopg2
- PostgreSQL
- Streamlit + Plotly
- NeuralProphet (forecasting)
- PyTrends (Google Trends)
- scikit-learn

---

## Modelos de Previsão

### NeuralProphet
- Modelo neural para séries temporais
- Treinado com dados de Google Trends dos expositores
- Arquivo: `models/model_otimo.np`
- Capaz de capturar sazonalidade e tendências

### Croston
- Método estatístico para séries intermitentes
- Usado quando há muitos zeros na série (baixa frequência)
- Alternativa mais robusta para séries com poucos dados

---

## Simulação Monte Carlo

O módulo de simulação permite:
- Executar N iterações com parâmetros aleatórios
- Calcular probabilidade de atingir meta
- Identificar melhores combinações de área/desconto/comissão
- Gerar tabela de cenários para decisão comercial

---

## Autor

**Kauã Dias**  
Estudante de Estatística | Data Science | Automação com Python

- GitHub: [Kauadp](https://github.com/Kauadp)
- LinkedIn: [kauad](https://www.linkedin.com/in/kauad/)