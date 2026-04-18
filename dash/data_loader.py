import pandas as pd
from sqlalchemy import create_engine
import streamlit as st

@st.cache_data
def load_data_atual():
    engine = create_engine(st.secrets["postgres"]["url"])
    return pd.read_sql("SELECT * FROM expositores_atual", engine)

@st.cache_data
def load_data_historico():
    engine = create_engine(st.secrets["postgres"]["url"])
    return pd.read_sql("SELECT * FROM expositores_historico", engine)