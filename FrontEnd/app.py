import streamlit as st
from paginas import dashboard, tabelas, upload

# Configuração da página
st.set_page_config(
    page_title="APS - Agência Premiersoft de Saúde",
    layout="wide"
)

st.title("APS - Agência Premiersoft de Saúde")
if "pagina" not in st.session_state:
    st.session_state.pagina = "Dashboard"

# Menu lateral como "nav"
if st.sidebar.button("📊 Dashboard"):
    st.session_state.pagina = "Dashboard"
elif st.sidebar.button("📄 Tabelas"):
    st.session_state.pagina = "Tabelas"
elif st.sidebar.button("📁 Upload"):
    st.session_state.pagina = "Upload"
    
st.markdown("---")

# Mostra o conteúdo da aba selecionada
if st.session_state.pagina == "Dashboard":
    dashboard.show()
elif st.session_state.pagina == "Tabelas":
    tabelas.show()
elif st.session_state.pagina == "Upload":
    upload.show()