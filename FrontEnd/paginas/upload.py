import streamlit as st
import requests
import os
import pandas as pd
import xml.etree.ElementTree as ET
import io

BACKEND_URL = os.getenv("BACKEND_URL", "http://127.0.0.1:8000/api/v1")

TIPOS_DADOS = {
    "Pacientes": "pacientes",
    "Hospitais": "hospitais",
    "Médicos": "medicos",
    "Especialidades": "especialidades"
}

# --- Parser para XML ---
def parse_xml(file):
    content = file.read()   # lê o conteúdo em memória
    file.seek(0)            # reseta o ponteiro (pra não quebrar se usar depois)
    tree = ET.parse(io.BytesIO(content))
    root = tree.getroot()
    data = []
    for elem in root.findall("registro"):  # <-- ajuste conforme a estrutura real do XML
        item = {child.tag: child.text for child in elem}
        data.append(item)
    return pd.DataFrame(data)


def show():
    st.subheader("Upload de Arquivos para o Backend")

    # Tipo de dado → mapeado para endpoint fixo
    tipo_label = st.selectbox("Selecione o tipo de dado", list(TIPOS_DADOS.keys()))
    tipo_endpoint = TIPOS_DADOS[tipo_label]

    # Formato do arquivo
    formato = st.selectbox("Formato do arquivo", [
        "CSV", "Excel", "JSON", "XML", "HL7", "FHIR"
    ])

    arquivo = st.file_uploader(
        f"Escolha um arquivo ({formato})",
        type=["csv", "xlsx", "json", "xml", "txt"]
    )

    if arquivo:
        try:
            # --- Identifica formato ---
            if formato == "CSV":
                df = pd.read_csv(arquivo)
            elif formato == "Excel":
                df = pd.read_excel(arquivo)
            elif formato == "JSON":
                df = pd.read_json(arquivo)
            elif formato == "XML":
                df = parse_xml(arquivo)
            elif formato == "HL7":
                st.warning("⚠️ Parser HL7 ainda não implementado")
                return
            elif formato == "FHIR":
                st.warning("⚠️ Parser FHIR ainda não implementado")
                return

            # Preview do arquivo
            st.write("📄 Preview do arquivo:")
            st.dataframe(df)

            # Envio para backend
            if st.button("Enviar para o backend"):
                dados = df.to_dict(orient="records")
                response = requests.post(f"{BACKEND_URL}/{tipo_endpoint}", json=dados)
                response.raise_for_status()
                st.success(f"✅ Arquivo enviado com sucesso! Status: {response.status_code}")

        except Exception as e:
            st.error(f"Erro ao processar o arquivo: {e}")
