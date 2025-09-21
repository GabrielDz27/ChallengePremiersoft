import os
import streamlit as st
import requests
from streamlit_echarts import st_echarts

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
        "Municípios": "municipios"
    }
    
    # Aba inicial
    if "aba_selecionada" not in st.session_state:
        st.session_state.aba_selecionada = "Métricas Gerais"

    # Lista de abas
    abas = [
        "Métricas Gerais",
        "Pacientes por Hospital",
        "Médicos por Especialidade",
        "Pacientes por Estado/Município",
        "Hospitais por Município/Estado",
        "Ocupação Hospitalar"
    ]

    # Menu em formato de select (dropdown)

    aba_selecionada = st.sidebar.selectbox(
        "Selecione a aba:",
        abas,
        index=abas.index(st.session_state.aba_selecionada)
    )

    # Atualiza no session_state
    st.session_state.aba_selecionada = aba_selecionada


    # ---------------------------
    # Métricas Gerais
    # ---------------------------
    if aba_selecionada == "Métricas Gerais":
        st.header("📊 Métricas Gerais")

        def extrair_count(valor):
            if isinstance(valor, dict):
                return valor.get("count", 0)
            elif isinstance(valor, int) or isinstance(valor, float):
                return valor
            else:
                return 0

        # Criar duas linhas de três colunas
        col1, col2, col3 = st.columns(3)
        col4, col5, col6 = st.columns(3)

        # Buscar dados da API
        pacientes = requests.get(f"{BACKEND_URL}/{endpoints['Pacientes']}?count_only=true").json()
        hospitais = requests.get(f"{BACKEND_URL}/{endpoints['Hospitais']}?count_only=true").json()
        medicos = requests.get(f"{BACKEND_URL}/{endpoints['Médicos']}?count_only=true").json()
        especialidades = requests.get(f"{BACKEND_URL}/{endpoints['Especialidades']}?count_only=true").json()
        municipios = requests.get(f"{BACKEND_URL}/{endpoints['Municípios']}?count_only=true").json()

        # Linha 1
        col1.metric("Total de Pacientes", extrair_count(pacientes))
        col2.metric("Total de Hospitais", extrair_count(hospitais))
        col3.metric("Total de Médicos", extrair_count(medicos))

        # Linha 2
        col4.metric("Total de Especialidades", extrair_count(especialidades))
        col5.metric("Total de Municípios", extrair_count(municipios))
        col6.empty()  # deixa a última coluna vazia para alinhar


    # # ---------------------------
    # # Pacientes por Hospital
    # # ---------------------------
    # elif aba_selecionada == "Pacientes por Hospital":
    #     st.title("Pacientes por Hospital")
    #     ph = requests.get(f"{BACKEND_URL}/{endpoints['Pacientes-Hospitais']}").json()
    #     hosp = requests.get(f"{BACKEND_URL}/{endpoints['Hospitais']}").json()
        
    #     # Contagem de pacientes por hospital
    #     hospital_names = [h['nome'] for h in hosp]
    #     contagem = {h['codigo']: 0 for h in hosp}
    #     for registro in ph:
    #         contagem[registro['hospital_codigo']] += 1
    #     values = [contagem[h['codigo']] for h in hosp]
        
    #     option = {
    #         "xAxis": {"type": "category", "data": hospital_names},
    #         "yAxis": {"type": "value"},
    #         "series": [{"data": values, "type": "bar"}]
    #     }
    #     st_echarts(options=option, height="500px")

    # ---------------------------
    # Médicos por Especialidade
    # ---------------------------
    # elif aba_selecionada == "Médicos por Especialidade": #fazer grficco por especialidade
       
    #     st_echarts(options=option, height="500px")

    # # ---------------------------
    # # Pacientes por Estado/Município
    # # ---------------------------
    # elif aba_selecionada == "Pacientes por Estado/Município":
    #     st.title("Pacientes por Estado/Município")
    #     pacientes = requests.get(f"{BACKEND_URL}/{endpoints['Pacientes']}").json()
    #     municipios = requests.get(f"{BACKEND_URL}/{endpoints['Municípios']}").json()
    #     estados = requests.get(f"{BACKEND_URL}/{endpoints['Estados']}").json()
        
    #     # Exemplo simples: contagem de pacientes por estado
    #     estado_map = {e['codigo_uf']: e['uf'] for e in estados}
    #     municipio_map = {m['codigo_ibge']: m['codigo_uf'] for m in municipios}
        
    #     contagem_estados = {}
    #     for p in pacientes:
    #         uf = estado_map.get(municipio_map.get(p['municipio_id']))
    #         if uf:
    #             contagem_estados[uf] = contagem_estados.get(uf, 0) + 1
        
    #     option = {
    #         "xAxis": {"type": "category", "data": list(contagem_estados.keys())},
    #         "yAxis": {"type": "value"},
    #         "series": [{"data": list(contagem_estados.values()), "type": "bar"}]
    #     }
    #     st_echarts(options=option, height="500px")

    # # ---------------------------
    # # Hospitais por Município/Estado
    # # ---------------------------
    # elif aba_selecionada == "Hospitais por Município/Estado":
    #     st.title("Hospitais por Município/Estado")
    #     hosp = requests.get(f"{BACKEND_URL}/{endpoints['Hospitais']}").json()
    #     municipios = requests.get(f"{BACKEND_URL}/{endpoints['Municípios']}").json()
    #     estados = requests.get(f"{BACKEND_URL}/{endpoints['Estados']}").json()
        
    #     municipio_map = {m['codigo_ibge']: m['codigo_uf'] for m in municipios}
    #     estado_map = {e['codigo_uf']: e['uf'] for e in estados}
        
    #     contagem_estados = {}
    #     for h in hosp:
    #         uf = estado_map.get(municipio_map.get(h['municipio_id']))
    #         if uf:
    #             contagem_estados[uf] = contagem_estados.get(uf, 0) + 1
        
    #     option = {
    #         "xAxis": {"type": "category", "data": list(contagem_estados.keys())},
    #         "yAxis": {"type": "value"},
    #         "series": [{"data": list(contagem_estados.values()), "type": "bar"}]
    #     }
    #     st_echarts(options=option, height="500px")

    # # ---------------------------
    # # Ocupação Hospitalar
    # # ---------------------------
    # elif aba_selecionada == "Ocupação Hospitalar":
    #     st.title("Ocupação Hospitalar")
    #     hosp = requests.get(f"{BACKEND_URL}/{endpoints['Hospitais']}").json()
    #     ph = requests.get(f"{BACKEND_URL}/{endpoints['Pacientes-Hospitais']}").json()
        
    #     ocupacao = {}
    #     for h in hosp:
    #         count = sum(1 for p in ph if p['hospital_codigo'] == h['codigo'])
    #         taxa = (count / h['leitos_totais']) * 100 if h['leitos_totais'] > 0 else 0
    #         ocupacao[h['nome']] = round(taxa, 2)
        
    #     option = {
    #         "xAxis": {"type": "category", "data": list(ocupacao.keys())},
    #         "yAxis": {"type": "value"},
    #         "series": [{"data": list(ocupacao.values()), "type": "bar"}]
    #     }
    #     st_echarts(options=option, height="500px")