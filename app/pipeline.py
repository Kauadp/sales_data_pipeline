from config import URL_DB, URL_ES_FOOD, URL_ES_STAND, URL_RJ_STAND, URL_SP_STAND
from data.get_data import get_data
from data.transform import carregar_expositores_es_food, carregar_expositores_es_stand, carregar_expositores_rj, carregar_expositores_sp, combinar_planilhas
from db.database import get_engine
from db.operations import carregar_banco
import pandas as pd

def run_pipeline():
    df1 = carregar_expositores_es_stand(URL_ES_STAND)
    df2 = carregar_expositores_es_food(URL_ES_FOOD)
    df3 = carregar_expositores_rj(URL_RJ_STAND)
    df4 = carregar_expositores_sp(URL_SP_STAND)
    df = combinar_planilhas([df1, df2, df3, df4])
    engine = get_engine(URL_DB)
    carregar_banco(df, engine)

if __name__ == "__main__":
    run_pipeline()

