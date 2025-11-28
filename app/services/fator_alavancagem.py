import requests
import pandas as pd

def get_fator_alavancagem() -> pd.DataFrame:
    resource_id = "fd313e62-8bab-4492-92a3-55df91aef670"
    url = "https://dadosabertos.ccee.org.br/api/3/action/datastore_search"
    all_records = []
    offset = 0
    limit = 32000

    while True:
        params = {
            "resource_id": resource_id,
            "limit": limit,
            "offset": offset
        }

        try:
            response = requests.get(url, params=params, timeout=30)
            response.raise_for_status()
            data = response.json()
        except (requests.exceptions.RequestException, requests.exceptions.JSONDecodeError):
            return pd.DataFrame()

        if not data.get("success") or "result" not in data or "records" not in data["result"]:
            return pd.DataFrame()

        records = data["result"]["records"]
        if not records:
            break

        all_records.extend(records)
        offset += len(records)

        if offset >= data["result"].get("total", 0):
            break

    return pd.DataFrame(all_records)

def tratamento_fa(df: pd.DataFrame) -> pd.DataFrame:
    df = df.drop(['_id', 'MES_DO_EVENTO', 'CODIGO_EVENTO', 'TIPO_EVENTO', 'TIPO_CALCULO', 'VERSAO_CALCULO'], axis=1, errors='ignore')
    df = df.fillna(-1)
    df = df.rename(columns={'FATOR_ALAVANCAGEM': 'FATOR_ALAVANCAGEM (%)'})
    df['FATOR_ALAVANCAGEM (%)'] = pd.to_numeric(df['FATOR_ALAVANCAGEM (%)'], errors='coerce') * 100
    return df

def contraparte_disponiveis(df: pd.DataFrame) -> list:
    if 'NOME_RAZAO_SOCIAL' in df.columns:
        contrapartes = sorted(df['NOME_RAZAO_SOCIAL'].dropna().astype(str).unique().tolist())
        return contrapartes
    return []

def filtro_contrapartes(df: pd.DataFrame, contrapartes: list) -> pd.DataFrame:
    if 'NOME_RAZAO_SOCIAL' in df.columns and contrapartes:
        df = df[df['NOME_RAZAO_SOCIAL'].isin(contrapartes)]
    return df
