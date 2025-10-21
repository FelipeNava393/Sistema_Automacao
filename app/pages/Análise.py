import streamlit as st
import pandas as pd
import plotly_express as px
from services.ena import *
from services.ear import *
from services.fator_alavancagem import *

tab1, tab2 = st.tabs(["Relatório Mensal", "Fator de Alavancagem"])

class RelatorioMensal:
    def __init__(self):
        st.header("Relatório Mensal")
        # Selectbox para escolher a automação
        self.automacao = st.selectbox(
            "Selecione a automação desejada:",
            ("Automação ENA", "Automação EAR"),
            key="automacao_selecionada"
        )
        st.write("---")

    def automacao_ena(self):
        st.subheader("Automação ENA")
        ano_desejado = st.text_input("Digite o ano desejado (ex: 2025):").strip()
        mes_desejado = st.text_input("Digite o mês desejado (ex: 09 para Setembro):").strip()
        subsistema = st.text_input("Digite o ID do subsistema desejado (ex: SE):").strip()

        if st.button("Processar ENA"):
            try:
                ano = int(ano_desejado)
                mes = int(mes_desejado)
            except ValueError:
                st.error("Ano ou mês inválido. Use números inteiros.")
                return

            inicio_periodo_str, fim_periodo_str = get_periodo_mes(ano, mes)
            st.write(f"Período a ser filtrado: {inicio_periodo_str} até {fim_periodo_str}")

            try:
                df = get_ena_subsistema_diario(ano_desejado)
                df_ena = tratamento_subsistema_ena(df, subsistema, inicio_periodo_str, fim_periodo_str)
                ena_bruta_media = ena_media(df_ena)
                st.dataframe(df_ena)
                st.success(f"Ena bruta média para o subsistema {subsistema} no período: {ena_bruta_media} MWmed")
            except Exception as e:
                st.error(f"Erro ao processar dados: {e}")

    def automacao_ear(self):
        st.subheader("Automação EAR")
        ano_desejado = st.text_input("Digite o ano desejado (ex: 2025):").strip()
        mes_desejado = st.text_input("Digite o mês desejado (ex: 09 para Setembro):").strip()
        subsistema = st.text_input("Digite o ID do subsistema desejado (ex: SE):").strip()

        if st.button("Processar EAR"):
            try:
                ano = int(ano_desejado)
                mes = int(mes_desejado)
            except ValueError:
                st.error("Ano ou mês inválido. Use números inteiros.")
                return

            inicio_periodo_str, fim_periodo_str = get_periodo_mes(ano, mes)
            st.write(f"Período a ser filtrado: {inicio_periodo_str} até {fim_periodo_str}")

            try:
                df = get_ear_subsistema_diario(ano_desejado)
                df_ear = tratamento_subsistema_ear(df, subsistema, inicio_periodo_str, fim_periodo_str)
                ear_percentual = ear_percentual_final(df_ear)
                st.dataframe(df_ear)
                st.success(f"EAR percentual final para o subsistema {subsistema} no período: {ear_percentual}%")
            except Exception as e:
                st.error(f"Erro ao processar dados: {e}")

class FatorAlavancagem:
    def __init__(self):
        st.header("Fator de Alavancagem")
        self.opcao = st.selectbox(
            "Selecione a opção desejada:",
            ("Tabela", "Gráficos"),
            key="fator_alavancagem_opcao"
        )

    @st.cache_data(show_spinner=True, ttl=3600)
    def carregar_dados(_self):
        """Carrega e trata os dados com cache."""
        df_fator = get_fator_alavancagem()
        df_tratado = tratamento_fa(df_fator)
        if "DATA_ENVIO_FATOR_ALAVANCAGEM" in df_tratado.columns:
        # Converte para datetime
            df_tratado["DATA_ENVIO_FATOR_ALAVANCAGEM"] = pd.to_datetime(
                df_tratado["DATA_ENVIO_FATOR_ALAVANCAGEM"], 
                dayfirst=True,
                errors="coerce"
            )
            df_tratado = df_tratado.sort_values(
                by="DATA_ENVIO_FATOR_ALAVANCAGEM", 
                ascending=False
            )

        return df_tratado

    def tabela_fator_alavancagem(self):
        st.subheader("Tabela do Fator de Alavancagem")
        st.text("Use os filtros abaixo para exibir os dados desejados:")

        with st.spinner("Carregando dados do Fator de Alavancagem..."):
            df_tratado = self.carregar_dados()

        if "contrapartes_select" not in st.session_state:
            st.session_state["contrapartes_select"] = []
        if "df_filtrado_fa" not in st.session_state:
            st.session_state["df_filtrado_fa"] = pd.DataFrame()

        contrapartes = contraparte_disponiveis(df_tratado)
        contrapartes_select = st.multiselect(
            'Selecione as Contrapartes:',
            options=contrapartes,
            default=st.session_state["contrapartes_select"],
            placeholder="Escolha uma ou mais contrapartes..."
        )
        st.session_state["contrapartes_select"] = contrapartes_select

        # --- aplica filtros normalmente ---
        df_filtrado = df_tratado.copy()

        if not contrapartes_select:
            st.info("Selecione ao menos uma contraparte para exibir os dados.")
            st.session_state["df_filtrado_fa"] = pd.DataFrame()
            return
        
        if contrapartes_select:
            df_filtrado = filtro_contrapartes(df_filtrado, contrapartes_select)

        df_filtrado = df_filtrado.sort_values(by=['SIGLA_AGENTE', 'DATA_ENVIO_FATOR_ALAVANCAGEM'], ascending=[True, False])
        st.session_state["df_filtrado_fa"] = df_filtrado
        if df_filtrado.empty:
            st.warning("Nenhum registro encontrado para os filtros aplicados.")
        else:
            st.success(f"{len(df_filtrado)} registros encontrados.")
            st.dataframe(df_filtrado)


    def graficos_fator_alavancagem(self):
        st.subheader("Gráficos do Fator de Alavancagem")

        if "df_filtrado_fa" not in st.session_state or st.session_state["df_filtrado_fa"].empty:
            st.warning("Nenhum filtro aplicado ainda. Vá para a aba 'Tabela' e aplique um filtro primeiro.")
            return

        df = st.session_state["df_filtrado_fa"]
        st.write(f"Exibindo {len(df)} registros filtrados.")
        # Localiza a linha com o maior FATOR_ALAVANCAGEM (%)
        col1, col2 = st.columns(2)

        # KPI 1: Máximo FA e Contraparte
        linha_max = df['FATOR_ALAVANCAGEM (%)'].idxmax()
        max_fa = df.loc[linha_max, 'FATOR_ALAVANCAGEM (%)']
        agente_max = df.loc[linha_max, 'SIGLA_AGENTE']

        with col1:
            st.metric("Fator de Alavancagem Máximo (%)", f"{max_fa:.2f}")
            st.write(f"Contraparte com maior FA: **{agente_max}**")

        # KPI 2: Desvio Padrão por contraparte
        desvio_padrao_por_contraparte = df.groupby('SIGLA_AGENTE')['FATOR_ALAVANCAGEM (%)'].std().reset_index()

        with col2:
            st.metric("Média do Desvio Padrão (%)", f"{desvio_padrao_por_contraparte['FATOR_ALAVANCAGEM (%)'].mean():.2f}")

        # --- Gráfico de Desvio Padrão ---
        st.subheader("Desvio Padrão do Fator de Alavancagem por Contraparte")
        fig_std = px.bar(
            desvio_padrao_por_contraparte,
            x='SIGLA_AGENTE',
            y='FATOR_ALAVANCAGEM (%)',
            title='Desvio Padrão do Fator de Alavancagem por Contraparte',
            labels={'SIGLA_AGENTE': 'Contraparte', 'FATOR_ALAVANCAGEM (%)': 'Desvio Padrão (%)'},
            color='SIGLA_AGENTE'
        )
        st.plotly_chart(fig_std, use_container_width=True)

        # --- Gráfico do Fator de Alavancagem ao longo do tempo ---
        st.subheader("Fator de Alavancagem ao Longo do Tempo por Contraparte")
        fig_fa = px.scatter(
            df,
            x="DATA_ENVIO_FATOR_ALAVANCAGEM",
            y="FATOR_ALAVANCAGEM (%)",
            color="SIGLA_AGENTE",
            title="Fator de Alavancagem ao Longo do Tempo",
            labels={"DATA_ENVIO_FATOR_ALAVANCAGEM": "Data de Envio", "FATOR_ALAVANCAGEM (%)": "Fator de Alavancagem (%)"},
            hover_data=["CNPJ"]  # opcional para exibir CNPJs ao passar o mouse
        )
        st.plotly_chart(fig_fa, use_container_width=True)
        
# --- Execução principal ---
if __name__ == "__main__":
    with tab1:
        relatorio = RelatorioMensal()
        match relatorio.automacao:
            case "Automação ENA":
                relatorio.automacao_ena()
            case "Automação EAR":
                relatorio.automacao_ear()

    with tab2:
        indicador_alavancagem = FatorAlavancagem()
        match indicador_alavancagem.opcao:
            case "Tabela":
                indicador_alavancagem.tabela_fator_alavancagem()
            case "Gráficos":
                indicador_alavancagem.graficos_fator_alavancagem()
        