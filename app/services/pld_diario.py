import pandas as pd
import requests as req


def get_pld_diario() -> pd.DataFrame:
    DATASTORE_SEARCH_URL = "https://dadosabertos.ccee.org.br/api/3/action/datastore_search"
    resource_id = {
        '2025': "2a180a6b-f092-43eb-9f82-a48798b803dc"
    }

    all_records = []
    offset = 0
    limit = 32000

    while True:
        params = {
            "resource_id": resource_id['2025'],  # ← único ajuste necessário
            "limit": limit,
            "offset": offset
        }

        try:
            response = req.get(DATASTORE_SEARCH_URL, params=params, timeout=30)
            response.raise_for_status()

            data = response.json()

            if not data["success"]:
                break

            records = data["result"]["records"]
            total = data["result"]["total"]

            if not records:
                break

            all_records.extend(records)
            offset += len(records)

            if offset >= total:
                break

        except Exception:
            break

    return pd.DataFrame(all_records)


def pld_diario(df: pd.DataFrame) -> pd.DataFrame:
    return df[df["SUBMERCADO"] == "SUDESTE"].drop(
    columns=["_id", "PERIODO_COMERCIALIZACAO"],
    errors="ignore"
    )

def media_pld_diario(df: pd.DataFrame) -> float:
    return df["PLD_HORA"].mean()

def periodo_pld(df: pd.DataFrame) -> list:
    meses = df["MES_REFERENCIA"].dropna().unique().tolist()
    return sorted(meses)