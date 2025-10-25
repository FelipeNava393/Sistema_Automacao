from re import sub
import requests
import pandas as pd

def get_pld_mensal() -> pd.DataFrame:
    resource_id = "9b9a4ae6-3db4-48f8-8130-ffa229835f7a"
    url_pld = "https://dadosabertos.ccee.org.br/api/3/action/datastore_search"
    
    all_records = []
    offset = 0
    limit = 100
    
    while True:
        params = {
            "resource_id": resource_id,
            "limit": limit,
            "offset": offset
        }
        
        try:
            response = requests.get(url_pld, params=params, timeout=30)
            response.raise_for_status()
            data = response.json()
        except (requests.exceptions.RequestException, requests.exceptions.JSONDecodeError) as e:
            return pd.DataFrame()
        
        # Validação da resposta
        if not data.get("success") or "result" not in data or "records" not in data["result"]:
            return pd.DataFrame()
        
        records = data["result"]["records"]
        
        # Se não há mais registros, sair do loop
        if not records:
            break
        
        all_records.extend(records)
        offset += len(records)
        
        # Verificar se chegamos ao total de registros
        if offset >= data["result"].get("total", 0):
            break

    return pd.DataFrame(all_records)

def tratamento_pld(df: pd.DataFrame) -> pd.DataFrame:
    df = df.drop(["_id"], axis=1, errors="ignore")
    if "MES_REFERENCIA" in df.columns:
        df["MES_REFERENCIA"] = pd.to_datetime(df["MES_REFERENCIA"],format='%Y%m', errors='coerce')
        df["MES_REFERENCIA"] = df["MES_REFERENCIA"].dt.strftime('%Y-%m')
    
    return df

def submercado_disponivel(df: pd.DataFrame) -> list:
    if "SUBMERCADO" in df.columns:
        submercados = sorted(df["SUBMERCADO"].unique().tolist())
        return submercados

    return []

def periodo_disponivel(df: pd.DataFrame) -> list:
    if "MES_REFERENCIA" in df.columns:
        periodos = (
            pd.to_datetime(df["MES_REFERENCIA"], errors="coerce").dropna().dt.strftime("%Y-%m").unique().tolist()
        )
        return sorted(periodos)

    return []

def pld_filtrado(df: pd.DataFrame, submercado: list, periodo: list) -> pd.DataFrame:
    if "MES_REFERENCIA" in df.columns and "SUBMERCADO" in df.columns:
        df_filtrado = df[df["SUBMERCADO"].isin(submercado) & df["MES_REFERENCIA"].isin(periodo)]
        return df_filtrado

    return pd.DataFrame()
