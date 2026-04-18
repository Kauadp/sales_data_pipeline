import pandas as pd
import requests
from io import BytesIO

def get_data(url: str, SHEET_NAME: str, header: int = 0) -> pd.DataFrame:

    headers = {
        "User-Agent": "Mozilla/5.0"
    }

    print(f"Baixando dados da planilha...")

    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
    except requests.RequestException as e:
        print(f"Erro ao baixar do Link {url}: {e}")
        raise

    df = pd.read_excel(BytesIO(response.content), sheet_name = SHEET_NAME, header = header)

    print("Download concluído com sucesso!")

    return df

