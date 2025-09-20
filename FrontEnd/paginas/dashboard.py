import streamlit as st
import os
import requests
import pandas as pd
import plotly.express as px

# URL do backend configurável via variável de ambiente
BACKEND_URL = os.getenv("BACKEND_URL", "http://127.0.0.1:8000/api/v1")

def show():
    st.title("📊 Dashboard APS - Agência Premiersoft de Saúde")

    # -------------------
    # Parte 1: Buscar dados do backend
    # -------------------
    endpoints = {
        "Pacientes": "pacientes",
        "Hospitais": "hospitais",
        "Médicos": "medicos",
        "Especialidades": "especialidades",
        "Hospitais-Especialidades": "hospitais_especialidades",
        "Médicos-Hospitais": "medicos_hospitais",
    }

    dfs = {}
    for nome, endpoint in endpoints.items():
        try:
            response = requests.get(f"{BACKEND_URL}/{endpoint}")
            response.raise_for_status()
            data = response.json()
            if isinstance(data, list) and len(data) > 0:
                dfs[nome] = pd.DataFrame(data)
            else:
                dfs[nome] = pd.DataFrame()  # dataframe vazio
        except requests.exceptions.RequestException as e:
            st.error(f"Erro ao conectar no backend ({nome}): {e}")
            dfs[nome] = pd.DataFrame()

    # -------------------
    # Parte 2: Métricas gerais
    # -------------------
    st.subheader("📌 Métricas Gerais")
    col1, col2, col3 = st.columns(3)
    col1.metric("Pacientes", len(dfs.get("Pacientes", [])))
    col2.metric("Hospitais", len(dfs.get("Hospitais", [])))
    col3.metric("Médicos", len(dfs.get("Médicos", [])))

    # -------------------
    # Parte 3: Gráficos interativos
    # -------------------
    st.subheader("📈 Distribuição de Pacientes por Hospital")
    if not dfs.get("Pacientes", pd.DataFrame()).empty and \
       not dfs.get("Pacientes-Hospitais", pd.DataFrame()).empty and \
       not dfs.get("Hospitais", pd.DataFrame()).empty:

        # Unir dados de pacientes com hospitais
        pacientes_hosp = pd.merge(
            dfs["Pacientes-Hospitais"], 
            dfs["Hospitais"], 
            left_on="hospital_id", 
            right_on="id", 
            how="left"
        )

        grafico = pacientes_hosp.groupby("nome")["paciente_id"].count().reset_index()
        grafico = grafico.rename(columns={"paciente_id": "Quantidade de Pacientes"})
        fig = px.bar(grafico, x="nome", y="Quantidade de Pacientes", title="Pacientes por Hospital")
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Dados de pacientes ou hospitais não disponíveis para o gráfico.")

    st.subheader("📈 Médicos por Especialidade")
    if not dfs.get("Médicos", pd.DataFrame()).empty and \
       not dfs.get("Especialidades", pd.DataFrame()).empty:

        # Juntar médicos com suas especialidades
        med_esp = pd.merge(
            dfs["Médicos"], 
            dfs["Especialidades"], 
            left_on="especialidade_id", 
            right_on="id", 
            how="left"
        )

        grafico2 = med_esp.groupby("nome_y")["id_x"].count().reset_index()
        grafico2 = grafico2.rename(columns={"id_x": "Quantidade de Médicos", "nome_y": "Especialidade"})
        fig2 = px.pie(grafico2, names="Especialidad", values="Quantidade de Médicos", title="Médicos por Especialidade")
        st.plotly_chart(fig2, use_container_width=True)
    else:
        st.info("Dados de médicos ou especialidades não disponíveis para o gráfico.")
