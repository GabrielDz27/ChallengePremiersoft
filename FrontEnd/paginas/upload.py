import streamlit as st
import requests
import os
import pandas as pd

BACKEND_URL = os.getenv("BACKEND_URL", "http://127.0.0.1:8000/api/v1")

st.title("Upload de Arquivos para o Backend")

# Escolha do tipo de dado para upload
tipo = st.selectbox("Selecione o tipo de dado", [
    "Pacientes", 
    "Hospitais", 
    "Médicos", 
    "Especialidades"
])

arquivo = st.file_uploader(f"Escolha um CSV para enviar ({tipo})", type="csv")

if arquivo:
    df = pd.read_csv(arquivo)
    st.write("📄 Preview do arquivo:")
    st.dataframe(df)

    if st.button("Enviar para o backend"):
        try:
            # Converter DataFrame em lista de dicionários
            dados = df.to_dict(orient="records")
            response = requests.post(f"{BACKEND_URL}/{tipo.lower()}", json=dados)
            response.raise_for_status()
            st.success(f"Arquivo enviado com sucesso! Status: {response.status_code}")
        except requests.exceptions.RequestException as e:
            st.error(f"Erro ao enviar para o backend: {e}")