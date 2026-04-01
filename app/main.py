import re
from io import BytesIO
import os
import numpy as np
import pandas as pd
import requests

from .secrets import get_secret

# Defer reading sheet URLs until runtime so deployed environments
# (e.g. Streamlit cloud using `st.secrets`) resolve them when the
# ETL is triggered instead of at import time.
URL_ES_STAND = None
URL_ES_FOOD = None
URL_RJ_STAND = None

COMMON_COLUMNS = [
    "STAND",
    "AREA",
    "NOME FANTASIA",
    "RECEITA REALIZADA",
    "RECEITA PREVISTA",
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
    "STATUS": "",
    "CIDADE": "",
    "RECORRENTE": "",
    "CONTRATO ASSINADO": "",
    "CONTRATO LINK": "",
    "CATEGORIA": "",
}

BOOL_TRUE = {"SIM", "S", "TRUE", "1", "RECORRENTE"}
BOOL_FALSE = {"NAO", "NÃO", "N", "FALSE", "0", "NOVO"}


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


def baixar_planilha_excel(url, sheet_name, header=0):
    if not url:
        raise ValueError("URL da planilha não foi fornecida.")

    headers = {"User-Agent": "Mozilla/5.0"}
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    return pd.read_excel(BytesIO(response.content), sheet_name=sheet_name, header=header)


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

    for amount_col in ["RECEITA REALIZADA", "RECEITA PREVISTA"]:
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


def carregar_expositores_es_stand(url):
    df = baixar_planilha_excel(url, sheet_name="BD COMERCIAL")
    return preparar_planilha(
        df,
        selected_columns=COMMON_COLUMNS,
        row_range=(1, 173),
        tipo="STAND",
        pipeline="ES_MAIO_26",
        evento="ESPÍRITO SANTO",
    )


def carregar_expositores_es_food(url):
    df = baixar_planilha_excel(url, sheet_name="BD FOOD MAIO 2026")
    return preparar_planilha(
        df,
        selected_columns=[
            "STAND",
            "AREA",
            "NOME FANTASIA",
            "RECEITA REALIZADA",
            "RECEITA PREVISTA",
            "STATUS",
            "CIDADE",
            "RECORRENTE",
            "CONTRATO ASSINADO",
            "CONTRATO LINK",
            "CATEGORIA",
        ],
        row_range=(1, 42),
        tipo="FOOD",
        pipeline="ES_MAIO_26",
        evento="ESPÍRITO SANTO",
        defaults={**DEFAULT_COLUMN_VALUES, "CIDADE": "", "RECORRENTE": ""},
    )


def carregar_expositores_rj(url):
    df = baixar_planilha_excel(url, sheet_name="BD COMERCIAL", header=1)
    return preparar_planilha(
        df,
        selected_columns=COMMON_COLUMNS,
        row_range=(0, 102),
        tipo="STAND",
        pipeline="RJ_26",
        evento="RIO DE JANEIRO",
        rename_map={
            "CONTRATO ENVIADO WHAT": "CONTRATO ENVIADO",
            "CONTRATO ASSINADO?": "CONTRATO ASSINADO",
        },
    )


def combinar_planilhas(dataframes):
    return pd.concat(dataframes, ignore_index=True)


def run_etl(
    save_csv: bool = False,
    csv_path: str = "expositores_combinados.csv",
    url_es_stand: str | None = None,
    url_es_food: str | None = None,
    url_rj_stand: str | None = None,
) -> pd.DataFrame:
    # Resolve URLs at runtime. If not provided, try to load from configured secrets.
    url_es_stand = url_es_stand or get_secret("URL_ES_STAND")
    url_es_food = url_es_food or get_secret("URL_ES_FOOD")
    url_rj_stand = url_rj_stand or get_secret("URL_RJ_STAND")

    missing = [k for k, v in {
        "URL_ES_STAND": url_es_stand,
        "URL_ES_FOOD": url_es_food,
        "URL_RJ_STAND": url_rj_stand,
    }.items() if not v]

    if missing:
        raise ValueError(
            f"URL(s) da planilha não configurada(s): {', '.join(missing)}."
            " Verifique secrets.toml ou Streamlit secrets (st.secrets)."
        )

    df1 = carregar_expositores_es_stand(url_es_stand)
    df2 = carregar_expositores_es_food(url_es_food)
    df3 = carregar_expositores_rj(url_rj_stand)
    df = combinar_planilhas([df1, df2, df3])
    if save_csv:
        df.to_csv(csv_path, index=False)
    return df


if __name__ == "__main__":
    df = run_etl(save_csv=True)
    print(f"ETL concluído: {len(df)} linhas geradas e salvas em expositores_combinados.csv")
