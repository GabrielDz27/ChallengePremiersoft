import streamlit as st
from paginas import tabelas, upload

st.title("APS - Agência Premiersoft de Saúde")

abas = st.tabs([ "📁 Upload de Arquivos", "📄 Tabelas", "📊 Dashboard"])

with abas[0]:
    upload.show()

with abas[1]:
    tabelas.show()