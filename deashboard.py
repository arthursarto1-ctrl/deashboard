import streamlit as st
import pandas as pd
import plotly.express as px

# -------------------------
# LEITURA DOS DADOS
# -------------------------
# Basta deixar o arquivo na mesma pasta do projeto
df_fisica = pd.read_excel("DADOS DE FÍSICA - MOSTRA DE ARTES 2026.xlsx", sheet_name="DADOS DE FÍSICA - MOSTRA DE ART")
df_quimica = pd.read_excel("DADOS DE FÍSICA - MOSTRA DE ARTES 2026.xlsx", sheet_name="DADOS DE QUÍMICA")

# -------------------------
# TRATAMENTO DOS DADOS
# -------------------------
df_fisica['LOCAL'] = df_fisica['LOCAL'].str.strip().str.lower()
df_quimica['LOCAL'] = df_quimica['LOCAL'].str.strip().str.lower()

# Física: separar DB
df_fisica['DB MAX - MIN'] = df_fisica['DB MAX - MIN'].astype(str).str.replace('–','-', regex=False)
df_fisica[['DB','DB_MIN']] = df_fisica['DB MAX - MIN'].str.split('-', expand=True)
df_fisica['DB'] = pd.to_numeric(df_fisica['DB'], errors='coerce')
df_fisica['DB_MIN'] = pd.to_numeric(df_fisica['DB_MIN'], errors='coerce')

# Química: converter temperatura
df_quimica['TEMPERATURA (°C)'] = pd.to_numeric(df_quimica['TEMPERATURA (°C)'], errors='coerce')

# -------------------------
# AGRUPAMENTO EM 5 ÁREAS
# -------------------------
def agrupar_local(local):
    if local in ["teletubbies","teletubies"]:
        return "Teletubies"
    elif local in ["acadêmico 1","ala a","ala b","ala c","ala d","ala e","ala f",
                   "nasa","estacionamento","p1","sala de aula","p2","atrás da p2","dentro da p2"]:
        return "Acadêmico 1"
    elif local in ["acadêmico 2","ala g","ala h","ala i","ala j","ala k","ala l",
                   "avião","vão entre os acadêmicos","saída acedmiccc","área do avião, acadêmico 2",
                   "tratamento de água"]:
        return "Acadêmico 2"
    elif local in ["biblioteca","biblioteca (2º andar)","entrada principal","ponto de ônibus",
                   "praça da biblioteca","perto do ponto de ônibus"]:
        return "Biblioteca"
    else:
        return "Quadras"

df_fisica['ÁREA'] = df_fisica['LOCAL'].apply(agrupar_local)
df_quimica['ÁREA'] = df_quimica['LOCAL'].apply(agrupar_local)

df_quimica['DATA_HORA'] = df_quimica['DATA'].astype(str) + " " + df_quimica['HORÁRIO'].astype(str)

# -------------------------
# DASHBOARD STREAMLIT
# -------------------------
st.set_page_config(page_title="Dados Senac Ciências 2CDD02", page_icon="📊", layout="wide")

st.title("📊 Dados Senac Ciências 2CDD02")

st.markdown("""
Este site mostra os dados coletados de **Física** (nível de ruído em decibéis) e **Química** (temperatura em graus Celsius) 
divididos em 5 áreas principais: **Teletubies, Acadêmico 1, Acadêmico 2, Biblioteca e Quadras**.

👉 Como usar:
- Passe o **mouse** (computador) ou o **dedo** (celular/tablet) por cima das bolinhas para ver os detalhes da medição.
- Cada bolinha representa um valor individual coletado.
- As caixas (boxplot) mostram o resumo: mínimo, máximo, mediana e média.
- as bolinhas/quadrados do lado do grafico servem para ocultar ou mostrar os dados de cada área.
""")

# -------------------------
# FÍSICA
# -------------------------
st.subheader("🎧 Física - Ruído (dB)")

media_fisica = df_fisica['DB'].mean()
max_fisica = df_fisica['DB'].max()
min_fisica = df_fisica['DB'].min()

col1, col2, col3 = st.columns(3)
col1.metric("Média (dB)", f"{media_fisica:.1f}")
col2.metric("Máximo (dB)", f"{max_fisica:.1f}")
col3.metric("Mínimo (dB)", f"{min_fisica:.1f}")

fig_fisica = px.box(
    df_fisica,
    x="ÁREA",
    y="DB",
    color="ÁREA",
    title="Níveis de ruído por área",
    points="all"   # mostra todas as bolinhas individuais
)
fig_fisica.update_traces(boxmean="sd")  # adiciona média e desvio padrão
st.plotly_chart(fig_fisica, use_container_width=True)

# -------------------------
# QUÍMICA
# -------------------------
st.subheader("🌡️ Química - Temperatura (°C)")

media_quimica = df_quimica['TEMPERATURA (°C)'].mean()
max_quimica = df_quimica['TEMPERATURA (°C)'].max()
min_quimica = df_quimica['TEMPERATURA (°C)'].min()

col4, col5, col6 = st.columns(3)
col4.metric("Média (°C)", f"{media_quimica:.1f}")
col5.metric("Máximo (°C)", f"{max_quimica:.1f}")
col6.metric("Mínimo (°C)", f"{min_quimica:.1f}")

fig_quimica = px.scatter(
    df_quimica,
    x="DATA_HORA",
    y="TEMPERATURA (°C)",
    color="ÁREA",
    title="Temperatura por dia/horário e área"
)
st.plotly_chart(fig_quimica, use_container_width=True)

# -------------------------
# ANÁLISE SIMPLES
# -------------------------
st.subheader("📈 Análises")
st.markdown(f"""
- **Física:** A média de ruído foi de **{media_fisica:.1f} dB**, com máximo de **{max_fisica:.1f} dB** e mínimo de **{min_fisica:.1f} dB**.  
  Isso mostra quais áreas são mais barulhentas e quais são mais silenciosas.

- **Química:** A média de temperatura foi de **{media_quimica:.1f} °C**, com máximo de **{max_quimica:.1f} °C** e mínimo de **{min_quimica:.1f} °C**.  
  Assim é possível identificar os locais mais quentes e os mais frescos ao longo do dia.
""")
