# Configurações globais do Streamlit
import streamlit as st

# URL para o arquivo Excel, armazenada em secrets.toml
URL_ES_STAND = st.secrets["urls"]["URL_ES_STAND"]
URL_ES_FOOD = st.secrets["urls"]["URL_ES_FOOD"]
URL_RJ_STAND = st.secrets["urls"]["URL_RJ_STAND"]
URL_SP_STAND = st.secrets["urls"]["URL_SP_STAND"]


# URL para o banco de dados PostgreSQL, armazenada em secrets.toml
URL_DB = st.secrets["postgres"]["url"]