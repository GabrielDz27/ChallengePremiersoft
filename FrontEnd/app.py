import streamlit as st
from paginas import dashboard, tabelas, upload

st.set_page_config(
    page_title="APS - Agência Premiersoft de Saúde",
    layout="wide"
)

st.title("APS - Agência Premiersoft de Saúde")

# Guarda a página atual
if "pagina" not in st.session_state:
    st.session_state.pagina = "Dashboard"

st.markdown("""
   <style>
    /* Cor do botão selecionado */
    div[role="radiogroup"] > label[data-baseweb="radio"][aria-checked="true"] > div:first-child {
        background-color: #E0F2FF !important; /* azul claro */
        border-color: #A0C4FF !important;
    }

    /* Cor do texto do botão selecionado */
    div[role="radiogroup"] > label[data-baseweb="radio"][aria-checked="true"] span {
        color: #1D4ED8 !important; /* azul escuro */
        font-weight: bold;
    }

    /* Hover: muda fundo e texto */
    div[role="radiogroup"] > label[data-baseweb="radio"]:hover > div:first-child {
        background-color: #F0F9FF !important; /* fundo hover */
    }

    div[role="radiogroup"] > label[data-baseweb="radio"]:hover span {
        color: black !important; /* texto hover */
    }
    </style>
""", unsafe_allow_html=True)

st.sidebar.markdown("## Navegação")
pagina = st.sidebar.radio("Ir para:", ["Dashboard", "Tabelas", "Upload"], index=["Dashboard", "Tabelas", "Upload"].index(st.session_state.pagina))
st.session_state.pagina = pagina

st.markdown("---")

# Mostra o conteúdo da aba selecionada
if st.session_state.pagina == "Dashboard":
    dashboard.show()
elif st.session_state.pagina == "Tabelas":
    tabelas.show()
elif st.session_state.pagina == "Upload":
    upload.show()
