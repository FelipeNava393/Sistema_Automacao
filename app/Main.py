import streamlit as st

st.set_page_config(
    page_title="Automações e Análises",
    layout="wide",
    initial_sidebar_state="expanded"
)   

st.title("Automação de Informações")
st.subheader("Instruções")

st.markdown("""
### 🔎 O que você pode fazer neste sistema

Este painel foi desenvolvido para facilitar a visualização, análise e automação de informações relacionadas ao setor elétrico. As principais funcionalidades incluem:

---

### ⚡ **ENA e EAR – Energia Natural Afluente e Energia Armazenada**
- Consulte valores atualizados de ENA e EAR.
- Visualize informações por submercado.
- Acompanhe variações semanais e mensais.

---

### 📊 **Fator de Alavancagem (por Contraparte)**
- Analise o desempenho e exposição das contrapartes.
- Aplique filtros personalizados.
- Visualize gráficos e indicadores essenciais.

---

### 💰 **PLD Mensal**
- Consulte o Preço de Liquidação das Diferenças (PLD) por mês.
- Filtre períodos específicos.
- Analise médias e tendências ao longo do ano.

---

### 🕒 **PLD Horário**
- Acompanhe o PLD ao longo das horas do dia.
- Filtre datas específicas.
- Compare horários e identifique padrões de preço.

---

### 📌 **Como utilizar o sistema**
1. Utilize o menu lateral para escolher o módulo desejado.  
2. Aplique filtros sempre que disponíveis, garantindo uma visualização precisa.  
3. Após aplicar o filtro, explore tabelas, gráficos e métricas exibidas.  
4. Alguns módulos exigem que ao menos um filtro seja selecionado para carregar dados.

---

### 💡 **Dicas**
- Prefira períodos menores para análises mais rápidas.  
- Combine filtros para obter análises mais completas.  
- Caso algo não carregue, verifique se selecionou um item no filtro.
""")
