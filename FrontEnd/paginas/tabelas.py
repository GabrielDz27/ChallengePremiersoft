
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
            st.write(f" Dados de **{nome}**")
        
            try:
                response = requests.get(f"{BASE_URL}/{endpoints[nome]}")
                response.raise_for_status()
                data = response.json()
                if isinstance(data, list) and len(data) > 0:
                    df = pd.DataFrame(data)
                    st.dataframe(df, use_container_width=True)
                else:
                    st.info("Nenhum dado encontrado.")

<<<<<<< HEAD
abas = st.tabs(list(endpoints.keys()))

for nome, aba in zip(endpoints.keys(), abas):
    with aba:
        st.write(f" Dados de **{nome}**")
    
        try:
            response = requests.get(f"{BACKEND_URL}/{endpoints[nome]}")
            response.raise_for_status()
            data = response.json()
            if isinstance(data, list) and len(data) > 0:
                df = pd.DataFrame(data)
                st.dataframe(df, use_container_width=True)
            else:
                st.info("Nenhum dado encontrado.")

        except requests.exceptions.RequestException as e:
            st.error(f"Erro ao conectar no backend: {e}")
=======
            except requests.exceptions.RequestException as e:
                st.error(f"Erro ao conectar no backend: {e}")
>>>>>>> 3cea8a3d4de81a64db71b4ff0b0c2d47cec90543
