import re
from io import BytesIO
import os
import numpy as np
import pandas as pd
import requests

from .get_data import get_data

# COLUNAS MAPEADAS

COMMON_COLUMNS = [
    "STAND",
    "AREA",
    "NOME FANTASIA",
    "RECEITA REALIZADA",
    "RECEITA PREVISTA",
    "PERCENTUAL COMISSÃO",
    "STATUS",
    "CIDADE",
    "RECORRENTE",
    "CONTRATO ASSINADO",
    "CONTRATO LINK",
    "CATEGORIA",
]

DEFAULT_COLUMN_VALUES = {
    "STAND": "",
    "AREA": "",
    "NOME FANTASIA": "",
    "RECEITA REALIZADA": "0",
    "RECEITA PREVISTA": "0",
    "PERCENTUAL COMISSÃO": "0",
    "STATUS": "",
    "CIDADE": "",
    "RECORRENTE": "",
    "CONTRATO ASSINADO": "",
    "CONTRATO LINK": "",
    "CATEGORIA": "",
}

# VARIÁVEIS PARA TRATAMENTO DE DADOS

BOOL_TRUE = {"SIM", "S", "TRUE", "1", "RECORRENTE"}
BOOL_FALSE = {"NAO", "NÃO", "N", "FALSE", "0", "NOVO"}

# Limites superiores exclusivos para uso com iloc[start:end]
STAND_ES_END_ROW = 164
FOOD_ES_END_ROW = 42
STAND_RJ_END_ROW = 89

# FUNÇÕES AUXILIARES

def limpar_valor(valor):
    if valor == "" or pd.isna(valor):
        return "0"

    if isinstance(valor, (int, float)):
        return str(valor)

    if isinstance(valor, str):
        valor = re.sub(r"[^\d,\.\-]", "", valor)
        if "," in valor:
            valor = valor.replace(".", "")
            valor = valor.replace(",", ".")

    return valor


def sim_nao_para_bool(valor):
    if pd.isna(valor) or str(valor).strip() == "":
        return None

    valor = str(valor).strip().upper()
    if valor in BOOL_TRUE:
        return True
    if valor in BOOL_FALSE:
        return False
    return None

def preparar_planilha(
    df,
    selected_columns,
    row_range=None,
    tipo=None,
    pipeline=None,
    evento=None,
    defaults=None,
    rename_map=None,
):
    df = df.copy()
    if row_range is not None:
        start, end = row_range
        df = df.iloc[start:end]

    df.columns = df.columns.str.strip()
    if rename_map:
        df = df.rename(columns=rename_map)

    defaults = defaults or DEFAULT_COLUMN_VALUES
    for column_name, default_value in defaults.items():
        if column_name not in df.columns:
            df[column_name] = default_value

    df = df.fillna("")
    df = df[[col for col in selected_columns]]

    for amount_col in ["RECEITA REALIZADA", "RECEITA PREVISTA", "PERCENTUAL COMISSÃO"]:
        if amount_col in df.columns:
            df[amount_col] = (
                pd.to_numeric(df[amount_col].apply(limpar_valor), errors="coerce")
                .fillna(0)
                .astype(float)
            )

    df["NOME FANTASIA"] = df["NOME FANTASIA"].astype(str).str.strip().str.upper()
    df["STATUS"] = df["STATUS"].astype(str).str.strip()
    df["TO DENTRO"] = df["STATUS"].apply(sim_nao_para_bool)
    df["RECORRENTE"] = df["RECORRENTE"].apply(sim_nao_para_bool)
    df["CONTRATO ASSINADO"] = df["CONTRATO ASSINADO"].apply(sim_nao_para_bool)
    df["CONTRATO ENVIADO"] = np.where(
        df["CONTRATO LINK"].astype(str).str.strip() == "", "NÃO", "SIM"
    )
    df["CONTRATO ENVIADO"] = df["CONTRATO ENVIADO"].apply(sim_nao_para_bool)
    df["CIDADE"] = df["CIDADE"].astype(str).str.strip().str.upper()
    df["CATEGORIA"] = df["CATEGORIA"].astype(str).str.strip().str.upper()

    df["TIPO"] = tipo or ""
    df["PIPELINE"] = pipeline or ""
    df["EVENTO"] = evento or ""
    df["SNAPSHOT"] = pd.Timestamp.today()
    return df

# FUNÇÕES PARA CARREGAR DADOS DE CADA PLANILHA

def carregar_expositores_es_stand(url: str) -> pd.DataFrame:
    df = get_data(url, SHEET_NAME="BD COMERCIAL")
    return preparar_planilha(
        df,
        selected_columns=COMMON_COLUMNS,
        row_range=(0, STAND_ES_END_ROW),
        tipo="STAND",
        pipeline="ES_MAIO_26",
        evento="ESPÍRITO SANTO",
    )

def carregar_expositores_es_food(url: str) -> pd.DataFrame:
    df = get_data(url, SHEET_NAME="BD FOOD MAIO 2026")
    return preparar_planilha(
        df,
        selected_columns=[
            "STAND",
            "AREA",
            "NOME FANTASIA",
            "RECEITA REALIZADA",
            "RECEITA PREVISTA",
            "PERCENTUAL COMISSÃO",
            "STATUS",
            "CIDADE",
            "RECORRENTE",
            "CONTRATO ASSINADO",
            "CONTRATO LINK",
            "CATEGORIA",
        ],
        row_range=(1, FOOD_ES_END_ROW),
        tipo="FOOD",
        pipeline="ES_MAIO_26",
        evento="ESPÍRITO SANTO",
        defaults={**DEFAULT_COLUMN_VALUES, "CIDADE": "", "RECORRENTE": ""},
    )

def carregar_expositores_rj(url: str) -> pd.DataFrame:
    df = get_data(url, SHEET_NAME="BD COMERCIAL", header=1)
    return preparar_planilha(
        df,
        selected_columns=COMMON_COLUMNS,
        row_range=(0, STAND_RJ_END_ROW),
        tipo="STAND",
        pipeline="RJ_26",
        evento="RIO DE JANEIRO",
        rename_map={
            "CONTRATO ENVIADO WHAT": "CONTRATO ENVIADO",
            "CONTRATO ASSINADO?": "CONTRATO ASSINADO",
        },
    )

def carregar_expositores_sp(url: str) -> pd.DataFrame:
    df = get_data(url, SHEET_NAME="BD COMERCIAL")
    return preparar_planilha(
        df,
        selected_columns=COMMON_COLUMNS,
        tipo="STAND",
        pipeline="SP_26",
        evento="SÃO PAULO",
    )

# JUNTAR PLANILHAS

def combinar_planilhas(dataframes: list[pd.DataFrame]) -> pd.DataFrame:
    df = pd.concat(dataframes, ignore_index=True)
    
    df["ID_EXPOSITOR"] = (
        df["EVENTO"].astype(str) + "|" + 
        df["NOME FANTASIA"].astype(str) + "_" + 
        df["STAND"].astype(str)
    ).str.upper()

    df.columns = [
        col.strip().lower().replace(" ", "_") 
        for col in df.columns
    ]
    
    df = df.drop_duplicates(subset=["id_expositor"])
    
    return df


