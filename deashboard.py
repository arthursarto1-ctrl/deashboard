import streamlit as st
import pandas as pd
import plotly.express as px

# -------------------------
# CONFIGURAÇÃO DA PÁGINA
# -------------------------
st.set_page_config(page_title="Dados Senac Ciências 2CDD02", page_icon="📊", layout="wide")

# -------------------------
# LEITURA E TRATAMENTO
# -------------------------
@st.cache_data
def carregar_dados():
    df_f = pd.read_excel("DADOS DE FÍSICA - MOSTRA DE ARTES 2026.xlsx", sheet_name="DADOS DE FÍSICA - MOSTRA DE ART")
    df_q = pd.read_excel("DADOS DE FÍSICA - MOSTRA DE ARTES 2026.xlsx", sheet_name="DADOS DE QUÍMICA")

    df_f['LOCAL'] = df_f['LOCAL'].astype(str).str.strip().str.lower()
    df_q['LOCAL'] = df_q['LOCAL'].astype(str).str.strip().str.lower()

    # Física: separar DB
    df_f['DB MAX - MIN'] = df_f['DB MAX - MIN'].astype(str).str.replace('–','-', regex=False)
    df_f[['DB','DB_MIN']] = df_f['DB MAX - MIN'].str.split('-', expand=True)
    df_f['DB'] = pd.to_numeric(df_f['DB'], errors='coerce')
    df_f['DB_MIN'] = pd.to_numeric(df_f['DB_MIN'], errors='coerce')

    # Química: converter temperatura
    df_q['TEMPERATURA (°C)'] = pd.to_numeric(df_q['TEMPERATURA (°C)'], errors='coerce')

    # Removendo nulos e zeros
    df_f = df_f[df_f['DB'].notna() & (df_f['DB'] != 0)]
    df_q = df_q[df_q['TEMPERATURA (°C)'].notna() & (df_q['TEMPERATURA (°C)'] != 0)]

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

    df_f['ÁREA'] = df_f['LOCAL'].apply(agrupar_local)
    df_q['ÁREA'] = df_q['LOCAL'].apply(agrupar_local)
    df_q['DATA_HORA'] = df_q['DATA'].astype(str) + " " + df_q['HORÁRIO'].astype(str)

    return df_f, df_q

df_fisica, df_quimica = carregar_dados()

# -------------------------
# FILTROS NA SIDEBAR
# -------------------------
st.sidebar.header("🔍 Filtros")
todas_areas = sorted(list(set(df_fisica['ÁREA'].unique()).union(set(df_quimica['ÁREA'].unique()))))
areas_selecionadas = st.sidebar.multiselect("Selecione as Áreas:", todas_areas, default=todas_areas)

df_f_filtrado = df_fisica[df_fisica['ÁREA'].isin(areas_selecionadas)]
df_q_filtrado = df_quimica[df_quimica['ÁREA'].isin(areas_selecionadas)]

# -------------------------
# CONTEÚDO PRINCIPAL
# -------------------------
st.title("📊 Dados Senac Ciências 2CDD02")

tab_fisica, tab_quimica, tab_dados = st.tabs(["🎧 Física (Ruído)", "🌡️ Química (Temperatura)", "📄 Dados Brutos"])

# -------------------------
# ABA 1: FÍSICA
# -------------------------
with tab_fisica:
    st.subheader("Análise de Níveis de Ruído (dB)")
    
    if not df_f_filtrado.empty:
        col1, col2, col3 = st.columns(3)
        col1.metric("Média", f"{df_f_filtrado['DB'].mean():.1f} dB")
        col2.metric("Máximo", f"{df_f_filtrado['DB'].max():.1f} dB")
        col3.metric("Mínimo", f"{df_f_filtrado['DB'].min():.1f} dB")

        # Exibe gráfico de linha se houver apenas 1 área selecionada
        if df_f_filtrado['ÁREA'].nunique() == 1:
            area_nome = df_f_filtrado['ÁREA'].iloc[0]
            fig_f = px.line(
                df_f_filtrado.reset_index(drop=True),
                y="DB",
                markers=True,
                title=f"Evolução Temporal do Ruído — {area_nome}",
                labels={"index": "Nº da Medição", "DB": "Nível de Ruído (dB)"}
            )
        else:
            fig_f = px.box(
                df_f_filtrado, 
                x="ÁREA", 
                y="DB", 
                color="ÁREA", 
                points="all", 
                title="Distribuição do Ruído por Área"
            )
            fig_f.update_traces(boxmean="sd")

        st.plotly_chart(fig_f, use_container_width=True)
    else:
        st.warning("Nenhum dado de Física disponível para os filtros selecionados.")

# -------------------------
# ABA 2: QUÍMICA
# -------------------------
with tab_quimica:
    st.subheader("Análise de Temperatura (°C)")
    
    if not df_q_filtrado.empty:
        col1, col2, col3 = st.columns(3)
        col1.metric("Média", f"{df_q_filtrado['TEMPERATURA (°C)'].mean():.1f} °C")
        col2.metric("Máximo", f"{df_q_filtrado['TEMPERATURA (°C)'].max():.1f} °C")
        col3.metric("Mínimo", f"{df_q_filtrado['TEMPERATURA (°C)'].min():.1f} °C")

        # Exibe gráfico de linha se houver apenas 1 área selecionada
        if df_q_filtrado['ÁREA'].nunique() == 1:
            area_nome = df_q_filtrado['ÁREA'].iloc[0]
            fig_q = px.line(
                df_q_filtrado, 
                x="DATA_HORA", 
                y="TEMPERATURA (°C)", 
                markers=True,
                title=f"Evolução Temporal da Temperatura — {area_nome}",
                labels={"DATA_HORA": "Data/Hora", "TEMPERATURA (°C)": "Temperatura (°C)"}
            )
        else:
            fig_q = px.scatter(
                df_q_filtrado, 
                x="DATA_HORA", 
                y="TEMPERATURA (°C)", 
                color="ÁREA", 
                title="Variação Térmica por Dia/Horário e Área"
            )

        st.plotly_chart(fig_q, use_container_width=True)
    else:
        st.warning("Nenhum dado de Química disponível para os filtros selecionados.")

# -------------------------
# ABA 3: DADOS BRUTOS
# -------------------------
with tab_dados:
    st.subheader("Tabelas de Dados Filtrados")
    st.write("### Física")
    st.dataframe(df_f_filtrado, use_container_width=True)
    st.write("### Química")
    st.dataframe(df_q_filtrado, use_container_width=True)
            
