# 📄 Pipeline de Dados de Vendas e Dashboard

![Python](https://img.shields.io/badge/Python-3.11-blue?logo=python)
![ETL](https://img.shields.io/badge/ETL-Data%20Pipeline-green)
![Dash](https://img.shields.io/badge/Dash-Dashboard-0e76a8)
![Status](https://img.shields.io/badge/Status-Development-yellow)

---

# 📌 Visão Geral

Este repositório implementa uma **pipeline de processamento de dados de vendas/expositores** em Python, com extração, transformação, carregamento e um dashboard interativo em Dash.

O projeto centraliza dados em `expositores_combinados.csv` e inclui módulos para:

- Importação e tratamento de dados (pasta `app/`)
- Persistência em banco via `database.py`
- Pipeline ETL automatizada (`db_pipeline.py`)
- Dashboard e visualização interativa (`dash/`)

O objetivo é substituir processos manuais de consolidação e análise por uma pipeline reprodutível, rastreável e fácil de operar.

---


# 🚀 Funcionalidades

## 📥 Ingestão de Dados

Dados são carregados de `expositores_combinados.csv` (local) ou de fontes configuradas, e lidos com **pandas**.

Campos típicos:

- Identificador do expositor
- Nome/Razão social
- Contato / Email
- Categoria / Tipo de Stand
- Valores e condições de pagamento

---

## 🧹 Tratamento e Validação

O pipeline aplica rotinas de limpeza e validação:

- Normalização de strings
- Tratamento de valores nulos
- Validação básica de emails e CPFs/CNPJs quando aplicável
- Conversões de tipos (datas, numéricos)

Além disso, há logging detalhado para acompanhar cada execução.

---

## 🗄️ Persistência em Banco

O módulo `app/database.py` contém funções para:

- Criar/atualizar tabelas
- Inserir lotes de dados
- Consultas agregadas para relatórios

Atualmente a configuração suporta SQLite por padrão, podendo ser apontada para Postgres/MySQL via `secrets.toml`.

---

## 📊 Dashboard em Dash

O diretório `dash/` contém um painel interativo para exploração dos dados:

- Visualização de vendas por categoria
- Filtros por período, categoria e região
- Exportação de relatórios simples

O painel pode ser executado localmente para monitoramento e validação dos dados gerados pela pipeline.

---

# ⚙️ Pipeline de Processamento

Fluxo principal:

1️⃣ Leitura de `expositores_combinados.csv`

2️⃣ Normalização e limpeza com **pandas**

3️⃣ Validação de campos críticos

4️⃣ Inserção/atualização no banco via `database.py`

5️⃣ Geração de artefatos para dashboard

6️⃣ Atualização do dashboard (quando aplicável)

---

# 📈 Performance e Benefícios

Antes: consolidação manual de planilhas e relatórios.

Depois: pipeline repetível que reduz tempo manual e aumenta confiabilidade dos dados.

- Processos que levavam horas podem ser executados em minutos.
- Agrega controle e auditabilidade via logs e versão dos dados.

---

# 📦 Implantação

Para desenvolvimento local, siga os passos acima. Para produção:

- Configure uma instância de banco (Postgres recomendado).
- Agende `db_pipeline.py` via cron/Agendador de tarefas.
- Hospede o dashboard em um servidor (Gunicorn/Proxy) ou em serviços como Heroku/DigitalOcean.

---

# 🧠 Arquitetura

Componentes principais:

- `app/` — módulos de ingestão, transformação e persistência
- `dash/` — configuração e código do dashboard
- `expositores_combinados.csv` — dataset de exemplo
- `secrets.toml` / `dash/config.toml` — configurações sensíveis e parâmetros

---

# 🔧 Tecnologias Utilizadas

- Python 3.8+
- Pandas
- SQLAlchemy (ou sqlite3)
- Dash / Plotly
- TOML para configuração

---

# 📈 Impacto

Este projeto demonstra como automatizar a ingestão e análise de dados de vendas/expositores, entregando:

- Menos trabalho manual
- Relatórios mais rápidos e consistentes
- Base para decisões operacionais em tempo hábil

---

# 👤 Autor

**Kauã Dias**  
Estudante de Estatística | Data Science | Automação com Python

- 🐙 GitHub: https://github.com/Kauadp  
- 🔗 LinkedIn: https://www.linkedin.com/in/kauad/