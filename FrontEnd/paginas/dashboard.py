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
    
    if "aba_selecionada" not in st.session_state:
        st.session_state.aba_selecionada = "Métricas Gerais"

    abas = [
        "Métricas Gerais",
        "Médicos por local",
        "Pacientes por Doença",
        "Pacientes por Hospital",
        "Médicos por Especialidade",
        "Pacientes por Estado/Município",
        "Hospitais por Município/Estado",
        "Ocupação Hospitalar"
    ]

    aba_selecionada = st.sidebar.selectbox(
        "Selecione a aba:",
        abas,
        index=abas.index(st.session_state.aba_selecionada)
    )
    st.subheader("Dashboard")

    st.session_state.aba_selecionada = aba_selecionada

    # ---------------------------
    # Métricas Gerais
    # ---------------------------
    if aba_selecionada == "Métricas Gerais":
        st.header("Métricas Gerais")

        def extrair_total(valor, chave="total_medicos"):
            if isinstance(valor, dict):
                return valor.get(chave, 0)
            elif isinstance(valor, int) or isinstance(valor, float):
                return valor
            else:
                return 0

        col1, col2, col3 = st.columns(3)
        col4, col5, col6 = st.columns(3)

        pacientes = requests.get(f"{BACKEND_URL}/{endpoints['Pacientes']}/contagem").json()
        hospitais = requests.get(f"{BACKEND_URL}/{endpoints['Hospitais']}/contagem").json()
        medicos = requests.get(f"{BACKEND_URL}/{endpoints['Médicos']}/contagem").json()
        especialidades = requests.get(f"{BACKEND_URL}/{endpoints['Especialidades']}/contagem").json()
        municipios = requests.get(f"{BACKEND_URL}/{endpoints['Municípios']}/contagem").json()

        col1.metric("Total de Pacientes", extrair_total(pacientes, "total_pacientes"))
        col2.metric("Total de Hospitais", extrair_total(hospitais, "total_hospitais"))
        col3.metric("Total de Médicos", extrair_total(medicos, "total_medicos"))

        col4.metric("Total de Especialidades", extrair_total(especialidades, "total_especialidades"))
        col5.metric("Total de Municípios", extrair_total(municipios, "total_municipios"))
        col6.empty()
    
    # ---------------------------
    # Medicos por local 
    # ---------------------------
    elif aba_selecionada == "Médicos por local":
        st.header("Médicos por local")

        resposta = requests.get(f"{BACKEND_URL}/medicos/local").json()

        if isinstance(resposta, list) and resposta:

            estados_unicos = sorted(list({row["estado_uf"] for row in resposta}))
            estado_selecionado = st.selectbox("Filtrar por Estado:", estados_unicos)

            dados_filtrados = [row for row in resposta if row["estado_uf"] == estado_selecionado]

            if dados_filtrados:
                todos_municipios = [row["municipio_nome"] for row in dados_filtrados]

                municipios_selecionados = st.multiselect(
                    "Selecionar Municípios (máx. 10, opcional):",
                    options=todos_municipios
                )

                if municipios_selecionados:
                    if len(municipios_selecionados) > 10:
                        st.warning("Você pode selecionar no máximo 10 municípios. Os primeiros 10 serão usados.")
                        municipios_selecionados = municipios_selecionados[:10]

                    dados_filtrados = [row for row in dados_filtrados if row["municipio_nome"] in municipios_selecionados]

                municipios = [row["municipio_nome"] for row in dados_filtrados]
                totais = [row["total_medicos"] for row in dados_filtrados]

                if dados_filtrados:
                    option = {
                        "title": {"text": f"Médicos por Município - {estado_selecionado}"},
                        "tooltip": {},
                        "xAxis": {
                            "type": "category",
                            "data": municipios,
                            "axisLabel": {
                                "rotate": 30,
                                "interval": 0,
                                "formatter": "{value}",
                                "fontSize": 12,
                                "margin": 25
                            }
                        },
                        "yAxis": {"type": "value"},
                        "series": [{"data": totais, "type": "bar", "itemStyle": {"color": "#4C66AF"}}],
                        "grid": {"bottom": 120, "left": 60, "right": 40},
                        "dataZoom": [
                            {"type": "slider", "xAxisIndex": 0, "start": 0, "end": 20},
                            {"type": "inside", "xAxisIndex": 0}
                        ]
                    }

                    st_echarts(options=option, height="500px", width="100%")
                else:
                    st.warning("Nenhum médico encontrado para os municípios selecionados.")
            else:
                st.warning("Nenhum município encontrado para este estado.")
        else:
            st.warning("Nenhum dado de médicos por município encontrado.")

    # ---------------------------
    # Pacientes por Hospital
    # ---------------------------
    elif aba_selecionada == "Pacientes por Doença":
        st.header("Pacientes por Doença")

        resposta = requests.get(f"{BACKEND_URL}/pacientes/doencas").json()

        if isinstance(resposta, list) and resposta:

            todas_doencas = [row["descricao_doenca"] for row in resposta]

            doencas_selecionadas = st.multiselect(
                "Selecionar Doenças (máx. 10, opcional):",
                options=todas_doencas
            )

            if doencas_selecionadas:
                if len(doencas_selecionadas) > 10:
                    st.warning("Você pode selecionar no máximo 10 doenças. As primeiras 10 serão usadas.")
                    doencas_selecionadas = doencas_selecionadas[:10]

                dados_filtrados = [row for row in resposta if row["descricao_doenca"] in doencas_selecionadas]
            else:
                dados_filtrados = resposta

            if dados_filtrados:
                doencas = [row["descricao_doenca"] for row in dados_filtrados]
                totais = [row["total_pacientes"] for row in dados_filtrados]

                option = {
                    "title": {"text": "Pacientes por Doença"},
                    "tooltip": {},
                    "xAxis": {
                        "type": "category",
                        "data": doencas,
                        "axisLabel": {
                            "rotate": 0, 
                            "interval": 0,
                            "formatter": "{value}",
                            "fontSize": 12,
                            "margin": 25
                        }
                    },
                    "yAxis": {"type": "value"},
                    "series": [{"data": totais, "type": "bar", "itemStyle": {"color": "#4C66AF"}}],
                    "grid": {"bottom": 120, "left": 60, "right": 40},
                    "dataZoom": [
                        {"type": "slider", "xAxisIndex": 0, "start": 0, "end": 20},
                        {"type": "inside", "xAxisIndex": 0}
                    ]
                }

                st_echarts(options=option, height="500px", width="100%")
            else:
                st.warning("Nenhum paciente encontrado para as doenças selecionadas.")
        else:
            st.warning("Nenhum dado de pacientes por doença encontrado.")    
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