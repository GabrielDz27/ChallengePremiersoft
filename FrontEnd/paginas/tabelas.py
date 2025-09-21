import streamlit as st
import os
import requests
import pandas as pd

BACKEND_URL = os.getenv("BACKEND_URL", "http://127.0.0.1:8000/api/v1")

def show():
    endpoints = {
        "Pacientes": "pacientes",
        "Hospitais": "hospitais",
        "Médicos": "medicos",
        "Especialidades": "especialidades",
        # "Hospitais-Especialidades": "hospitais_especialidades",
        # "Médicos-Hospitais": "medicos_hospitais",
        # "Pacientes-Hospitais": "pacientes_hospitais",
        # "CID-10": "cid10",
        # "Estados": "estados",
        # "Municípios": "municipios",
    }

    colunas_amigaveis = {
        "codigo": "Código",
        "nome_completo": "Nome Completo",
        "cpf": "CPF",
        "municipio_id": "ID do Município",
        "cid10_id": "ID CID-10",
        "especialidade_id": "ID da Especialidade",
    }

    abas = st.tabs(list(endpoints.keys()))

    for nome, aba in zip(endpoints.keys(), abas):
        with aba:
            st.write(f"Dados de **{nome}**")
            try:
                response = requests.get(f"{BACKEND_URL}/{endpoints[nome]}")
                response.raise_for_status()
                data = response.json()

                if isinstance(data, list) and len(data) > 0:
                    df = pd.DataFrame(data)
                    df.rename(columns={k: v for k, v in colunas_amigaveis.items() if k in df.columns}, inplace=True)
                    st.dataframe(df, use_container_width=True)
                else:
                    st.info("Nenhum dado encontrado.")

            except requests.exceptions.RequestException as e:
                st.error(f"Não foi possível carregar os dados de {nome}. Por favor, verifique a conexão com o servidor ou tente novamente mais tarde.")
                print(f"Erro técnico: {e}")