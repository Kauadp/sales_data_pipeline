from config import URL_DB, URL_ES_FOOD, URL_ES_STAND, URL_RJ_STAND, URL_SP_STAND
from data.get_data import get_data
from data.transform import carregar_expositores_es_food, carregar_expositores_es_stand, carregar_expositores_rj, carregar_expositores_sp, combinar_planilhas
from db.database import get_engine
from db.operations import carregar_banco
import pandas as pd
from forecast import rodar_etl_oficial

def _definir_porte(area):
    if area <= 20:
        return "Pequeno"
    if area <= 35:
        return "Medio"
    return "Grande"

def run_pipeline():
    df1 = carregar_expositores_es_stand(URL_ES_STAND)
    df2 = carregar_expositores_es_food(URL_ES_FOOD)
    df3 = carregar_expositores_rj(URL_RJ_STAND)
    df4 = carregar_expositores_sp(URL_SP_STAND)
    df = combinar_planilhas([df1, df2, df3, df4])
    engine = get_engine(URL_DB)
    carregar_banco(df, engine)

    query = f"""
        SELECT DISTINCT 
            e.id_expositor, 
            e.nome_fantasia,
            e.area, 
            e.percentual_comissao, 
            e.receita_realizada
        FROM expositores_atual e
        LEFT JOIN forecast_trends_cache f 
            ON f.id_expositor = e.id_expositor
            AND f.area = e.area 
        WHERE e.percentual_comissao > 0
        AND f.id_expositor IS NULL 
        AND e.pipeline = 'RJ_26'
        """
    
    df_novos = pd.read_sql(query, engine)

    if not df_novos.empty:
        df_novos["porte"] = df_novos["area"].apply(_definir_porte)
        rodar_etl_oficial(engine, df_novos)

if __name__ == "__main__":
    run_pipeline()

