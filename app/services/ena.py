import requests
from io import StringIO
import pandas as pd
import time
import calendar
from datetime import datetime

# Função para buscar o CSV (mantida a mesma)
def get_ena_subsistema_diario(ano_busca: str) -> pd.DataFrame:
    api_url = f"https://ons-aws-prod-opendata.s3.amazonaws.com/dataset/ena_subsistema_di/ENA_DIARIO_SUBSISTEMA_{ano_busca}.csv"
    response = requests.get(api_url)
    response.raise_for_status() 
    csv_data = StringIO(response.text)

    df = pd.read_csv(csv_data, sep=';') 
    return df

# Função para obter o período do mês
def get_periodo_mes(ano: int, mes: int):
    ultimo_dia = calendar.monthrange(ano, mes)[1]
    inicio = f"01/{mes:02d}/{ano}" 
    fim = f"{ultimo_dia:02d}/{mes:02d}/{ano}"
    return inicio, fim

# Função para tratar os dados
def tratamento_subsistema_ena(df: pd.DataFrame, id_subsistema: str, inicio_periodo: str, fim_periodo: str) -> pd.DataFrame:
    df_filtrado = df[df['id_subsistema'] == id_subsistema].copy()
    
    df_filtrado['ena_data_dt'] = pd.to_datetime(
        df_filtrado['ena_data'], 
        format='%Y-%m-%d'
    )
    
    data_inicio_dt = datetime.strptime(inicio_periodo, '%d/%m/%Y')
    data_fim_dt = datetime.strptime(fim_periodo, '%d/%m/%Y')

    df_filtrado['ena_data_apenas_data'] = df_filtrado['ena_data_dt'].dt.date
    data_inicio_apenas_data = data_inicio_dt.date()
    data_fim_apenas_data = data_fim_dt.date()

    df_final = df_filtrado.loc[
        (df_filtrado['ena_data_apenas_data'] >= data_inicio_apenas_data) &
        (df_filtrado['ena_data_apenas_data'] <= data_fim_apenas_data)
    ].copy()

    df_final = df_final.drop(columns=['ena_data_dt', 'ena_data_apenas_data'])
    
    return df_final

# Função para realizar cálculos
def ena_media(df: pd.DataFrame) -> float:
    ena_bruta_media = df['ena_bruta_regiao_mwmed'].mean().round()
    return ena_bruta_media    
