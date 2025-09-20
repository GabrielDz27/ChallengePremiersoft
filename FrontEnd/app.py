import streamlit as st
import requests
import pandas as pd
import os

# BASE_URL = "http://localhost:8000"

st.title("APS")

st.subheader("Agência Premiersoft de saúde")

endpoints = {
    "Pacientes": "pacientes",
    "Hospitais": "hospitais",
    "Médicos": "medicos",
    "Especialidades": "especialidades",
    "Hospitais-Especialidades": "hospitais_especialidades",
    "Médicos-Hospitais": "medicos_hospitais",
    "Pacientes-Hospitais": "pacientes_hospitais",
    "CID-10": "cid10",
    "Estados": "estados",
    "Municípios": "municipios",
}

abas = st.tabs(list(endpoints.keys()))

for nome, aba in zip(endpoints.keys(), abas):
    with aba:
        st.write(f"📌 Dados de **{nome}**")
    
    # trocar para o fetch que esta em baixo
        caminho = os.path.join('data', endpoints[nome] + '.csv')

        if os.path.exists(caminho):
            df = pd.read_csv(caminho)
            st.dataframe(df, use_container_width=True)
        else:
            st.warning(f"O arquivo `{endpoints[nome]}`.csv não foi encontrado em data.")

        # try:
        #     # response = requests.get(f"{BASE_URL}/{endpoints[nome]}")
        #     # response.raise_for_status()
        #     # data = response.json()
        #     # if isinstance(data, list) and len(data) > 0:
        #         # df = pd.DataFrame(data)
        #         # st.dataframe(df, use_container_width=True)
        #     # else:
        #     #     st.info("Nenhum dado encontrado.")

        # except requests.exceptions.RequestException as e:
        #     st.error(f"Erro ao conectar no backend: {e}")