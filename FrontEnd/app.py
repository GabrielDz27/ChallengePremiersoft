import streamlit as st
import pandas as pd

# Título da aplicação
st.title("Meu Dashboard CID")

# Exemplo: carregar uma tabela CSV
df = pd.read_csv("cid.csv")  # ou outro arquivo de dados

# Mostrar tabela
st.dataframe(df)

# Filtro simples
cid_filter = st.text_input("Filtrar por CID:")
if cid_filter:
    filtered_df = df[df['cid'].str.contains(cid_filter, case=False)]
    st.dataframe(filtered_df)