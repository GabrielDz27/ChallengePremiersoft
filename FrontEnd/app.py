import streamlit as st
from paginas import tabelas, upload

st.title("APS - Agência Premiersoft de Saúde")

abas = st.tabs(["📊 Tabelas", "📁 Upload de Arquivos"])

with abas[0]:
    tabelas.show()

with abas[1]:
    upload.show()