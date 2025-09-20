import streamlit as st
from paginas import main_page, upload_page


st.title("APS - Agência Premiersoft de Saúde")

# Menu de navegação
pagina = st.sidebar.selectbox("Escolha a página", ["Página Principal", "Upload de Arquivos"])

# Renderiza a página escolhida
if pagina == "Página Principal":
    main_page.show()  # função que contém seu código de abas
elif pagina == "Upload de Arquivos":
    upload_page.show()  # função que contém o código de upload