import streamlit as st
import pandas as pd
import plotly.express as px

# -------------------------
# LEITURA DOS DADOS
# -------------------------
df_fisica = pd.read_excel("DADOS DE FÍSICA - MOSTRA DE ARTES 2026.xlsx", sheet_name="DADOS DE FÍSICA - MOSTRA DE ART")
df_quimica = pd.read_excel("DADOS DE FÍSICA - MOSTRA DE ARTES 2026.xlsx", sheet_name="DADOS DE QUÍMICA")

# -------------------------
# TRATAMENTO DOS DADOS
# -------------------------
df_fisica['LOCAL'] = df_fisica['LOCAL'].str.strip().str.lower()
df_quimica['LOCAL'] = df_quimica['LOCAL'].str.strip().str.lower()

# Física: separar DB
df_fisica['DB MAX - MIN'] = df_fisica['DB MAX - MIN'].astype(str).str.replace('–', '-', regex=False)
df_fisica[['DB', 'DB_MIN']] = df_fisica['DB MAX - MIN'].str.split('-', expand=True)
df_fisica['DB'] = pd.to_numeric(df_fisica['DB'], errors='coerce')
df_fisica['DB_MIN'] = pd.to_numeric(df_fisica['DB_MIN'], errors='coerce')

# Química: converter temperatura
df_quimica['TEMPERATURA (°C)'] = pd.to_numeric(df_quimica['TEMPERATURA (°C)'], errors='coerce')

# REMOÇÃO DE VALORES NULOS E ZEROS
df_fisica = df_fisica[df_fisica['DB'].notna() & (df_fisica['DB'] != 0)]
df_quimica = df_quimica[df_quimica['TEMPERATURA (°C)'].notna() & (df_quimica['TEMPERATURA (°C)'] != 0)]

# Tratamento centralizado de Data e Hora
df_fisica['HORÁRIO'] = df_fisica['HORÁRIO'].astype(str).str.replace('00:00:00', '').str.strip()
df_quimica['HORÁRIO'] = df_quimica['HORÁRIO'].astype(str).str.replace('00:00:00', '').str.strip()

df_fisica['DATA_HORA_DT'] = pd.to_datetime(
    df_fisica['DATA'].astype(str) + ' ' + df_fisica['HORÁRIO'].astype(str),
    dayfirst=True, errors='coerce'
)
df_quimica['DATA_HORA_DT'] = pd.to_datetime(
    df_quimica['DATA'].astype(str) + ' ' + df_quimica['HORÁRIO'].astype(str),
    dayfirst=True, errors='coerce'
)

# Formatação amigável das datas
df_fisica['DATA'] = df_fisica['DATA_HORA_DT'].dt.strftime('%d/%m/%Y')
df_quimica['DATA'] = df_quimica['DATA_HORA_DT'].dt.strftime('%d/%m/%Y')

# -------------------------
# AGRUPAMENTO EM 5 ÁREAS
# -------------------------
def agrupar_local(local_nome):
    if local_nome in ["teletubbies", "teletubies"]:
        return "Teletubies"
    elif local_nome in ["acadêmico 1", "ala a", "ala b", "ala c", "ala d", "ala e", "ala f",
                        "nasa", "estacionamento", "p1", "sala de aula", "p2", "atrás da p2", "dentro da p2"]:
        return "Acadêmico 1"
    elif local_nome in ["acadêmico 2", "ala g", "ala h", "ala i", "ala j", "ala k", "ala l",
                        "avião", "vão entre os acadêmicos", "saída acedmiccc", "área do avião, acadêmico 2",
                        "tratamento de água"]:
        return "Acadêmico 2"
    elif local_nome in ["biblioteca", "biblioteca (2º andar)", "entrada principal", "ponto de ônibus",
                        "praça da biblioteca", "perto do ponto de ônibus"]:
        return "Biblioteca"
    else:
        return "Quadras"

df_fisica['ÁREA'] = df_fisica['LOCAL'].apply(agrupar_local)
df_quimica['ÁREA'] = df_quimica['LOCAL'].apply(agrupar_local)

# -------------------------
# DASHBOARD STREAMLIT
# -------------------------
st.set_page_config(page_title="Dados Senac Ciências 2CDD02", page_icon="📊", layout="wide")

st.title("📊 Dados Senac Ciências 2CDD02")

st.markdown("""
Este site mostra os dados coletados de **Física** (nível de ruído em decibéis) e **Química** (temperatura em graus Celsius) 
divididos em 5 áreas principais: **Teletubies, Acadêmico 1, Acadêmico 2, Biblioteca e Quadras**.

feito com python, Streamlit, Pandas e Plotly.

por Arthur Sartori Cavalcanti

👉 **Como usar:**
- Selecione um local específico abaixo para analisar a evolução no tempo ou escolha **"todos"** para comparar as áreas.
- Passe o mouse ou o dedo por cima dos pontos nos gráficos para ver os detalhes da medição.
""")

# -------------------------
# SELEÇÃO DE ÁREA
# -------------------------
st.subheader("🎯 Seleção do Local para Análise")
local = st.selectbox(
    "Escolha o local:",
    ["todos", "Teletubies", "Acadêmico 1", "Acadêmico 2", "Biblioteca", "Quadras"]
)

# =========================================================
# BLOCO DO IF: QUANDO UM LOCAL ESPECÍFICO É SELECIONADO
# =========================================================
if local != "todos":
    # -------------------------
    # FÍSICA (ÁREA ESPECÍFICA)
    # -------------------------
    df_local_fisica = df_fisica[df_fisica['ÁREA'] == local]
    st.subheader(f"🎧 Física - Ruído (dB) — {local}")
    
    media_fisica = df_local_fisica['DB'].mean()
    max_fisica = df_local_fisica['DB'].max()
    min_fisica = df_local_fisica['DB'].min()
    
    col1, col2, col3 = st.columns(3)
    col1.metric("Média (dB)", f"{media_fisica:.1f}" if pd.notna(media_fisica) else "N/A")
    col2.metric("Máximo (dB)", f"{max_fisica:.1f}" if pd.notna(max_fisica) else "N/A")
    col3.metric("Mínimo (dB)", f"{min_fisica:.1f}" if pd.notna(min_fisica) else "N/A")

    df_area = df_local_fisica[df_local_fisica['DATA_HORA_DT'].notna()].sort_values('DATA_HORA_DT')
    df_area['DATA_HORA_ROTULO'] = df_area['DATA_HORA_DT'].dt.strftime('%d/%m %H:%M')
    df_area_agrupado = df_area.groupby('DATA_HORA_ROTULO', sort=False, as_index=False)['DB'].mean()

    fig_linha = px.line(
        df_area_agrupado,
        x="DATA_HORA_ROTULO",
        y="DB",
        markers=True,
        title=f"Ruído (dB) ao Longo do Tempo — {local}",
        labels={"DATA_HORA_ROTULO": "Dia e Horário", "DB": "Média de Ruído (dB)"}
    )
    fig_linha.update_xaxes(type='category')
    st.plotly_chart(fig_linha, use_container_width=True)

    # -------------------------
    # QUÍMICA (ÁREA ESPECÍFICA)
    # -------------------------
    st.subheader(f"🌡️ Química - Temperatura (°C) — {local}")
    df_local_quimica = df_quimica[df_quimica['ÁREA'] == local]
    
    media_quimica = df_local_quimica['TEMPERATURA (°C)'].mean()
    max_quimica = df_local_quimica['TEMPERATURA (°C)'].max()
    min_quimica = df_local_quimica['TEMPERATURA (°C)'].min()
    
    col1, col2, col3 = st.columns(3)
    col1.metric("Média (°C)", f"{media_quimica:.1f}" if pd.notna(media_quimica) else "N/A")
    col2.metric("Máximo (°C)", f"{max_quimica:.1f}" if pd.notna(max_quimica) else "N/A")
    col3.metric("Mínimo (°C)", f"{min_quimica:.1f}" if pd.notna(min_quimica) else "N/A")

    df_area_temp = df_local_quimica[df_local_quimica['DATA_HORA_DT'].notna()].sort_values('DATA_HORA_DT')
    df_area_temp['DATA_HORA_ROTULO'] = df_area_temp['DATA_HORA_DT'].dt.strftime('%d/%m %H:%M')
    df_temp_agrupado = df_area_temp.groupby('DATA_HORA_ROTULO', sort=False, as_index=False)['TEMPERATURA (°C)'].mean()

    fig_linha_temp = px.line(
        df_temp_agrupado,
        x="DATA_HORA_ROTULO",
        y="TEMPERATURA (°C)",
        markers=True,
        title=f"Variação de Temperatura (°C) ao Longo do Tempo — {local}",
        labels={"DATA_HORA_ROTULO": "Dia e Horário", "TEMPERATURA (°C)": "Média de Temperatura (°C)"}
    )
    fig_linha_temp.update_xaxes(type='category')
    st.plotly_chart(fig_linha_temp, use_container_width=True)

    # ---------------------------------------------------------
    # ANÁLISE CONDICIONAL COM IF, ELIF E ELSE DENTRO DO IF LOCAL
    # ---------------------------------------------------------
    st.subheader(f"📝 Análise Diagnóstica do Local — {local}")

    # 1. Avaliação do Ruído (dB)
    if pd.notna(max_fisica) and pd.notna(min_fisica):
        dif_db = max_fisica - min_fisica
        
        if dif_db > 15:
            texto_db = f"🔊 **Ruído (Alta Variação - {dif_db:.1f} dB):** A diferença entre o pico de som e o momento mais calmo é **muito grande**. Este local passa por momentos de silêncio alternados com picos barulhentos."
        elif dif_db >= 8:
            texto_db = f"🔉 **Ruído (Variação Moderada - {dif_db:.1f} dB):** A variação de som é **mais ou menos equilibrada**, apresentando oscilações normais sem grandes sobressaltos constantes."
        else:
            texto_db = f"🔇 **Ruído (Baixa Variação - {dif_db:.1f} dB):** A diferença é **muito pequena**. O nível sonoro deste local é estável e praticamente constante o tempo todo."
    else:
        texto_db = "🔊 **Ruído:** Não há dados suficientes para calcular a diferença."

    # 2. Avaliação da Temperatura (°C)
    if pd.notna(max_quimica) and pd.notna(min_quimica):
        dif_temp = max_quimica - min_quimica
        
        if dif_temp > 8:
            texto_temp = f"🔥 **Temperatura (Alta Variação - {dif_temp:.1f} °C):** A diferença entre a maior e a menor temperatura é **muito alta**. O ambiente sofre forte oscilação térmica ao longo do dia."
            
        elif dif_temp >= 3:
            texto_temp = f"🌤️ **Temperatura (Variação Moderada - {dif_temp:.1f} °C):** A variação de temperatura é **mais ou menos aceitável**, acompanhando o clima natural sem mudanças abruptas."
        else:
            texto_temp = f"❄️ **Temperatura (Baixa Variação - {dif_temp:.1f} °C):** A variação é **muito pouca**. O clima no ambiente se mantém quase inalterado."
    else:
        texto_temp = "🌡️ **Temperatura:** Não há dados suficientes para calcular a diferença."

    # Exibição dos diagnósticos
    st.markdown(texto_db)
    st.markdown(texto_temp)

# =========================================================
# BLOCO DO ELSE: VISÃO GERAL DE TODOS OS LOCAIS
# =========================================================
else:
    # -------------------------
    # FÍSICA (TODAS AS ÁREAS)
    # -------------------------
    st.subheader("🎧 Física - Ruído (dB) — Visão Geral")

    media_fisica = df_fisica['DB'].mean()
    max_fisica = df_fisica['DB'].max()
    min_fisica = df_fisica['DB'].min()

    col1, col2, col3 = st.columns(3)
    col1.metric("Média Geral (dB)", f"{media_fisica:.1f}")
    col2.metric("Máximo Geral (dB)", f"{max_fisica:.1f}")
    col3.metric("Mínimo Geral (dB)", f"{min_fisica:.1f}")

    fig_fisica = px.box(
        df_fisica,
        x="ÁREA",
        y="DB",
        color="ÁREA",
        title="Níveis de Ruído por Área",
        points="all",
        hover_data={
            "ÁREA": False,
            "DB": ":.1f",
            "DATA": True,
            "HORÁRIO": True,
            "LOCAL": True
        }
    )
    fig_fisica.update_traces(boxmean="sd")
    st.plotly_chart(fig_fisica, use_container_width=True)

    # -------------------------
    # QUÍMICA (TODAS AS ÁREAS)
    # -------------------------
    st.subheader("🌡️ Química - Temperatura (°C) — Visão Geral")

    media_quimica = df_quimica['TEMPERATURA (°C)'].mean()
    max_quimica = df_quimica['TEMPERATURA (°C)'].max()
    min_quimica = df_quimica['TEMPERATURA (°C)'].min()

    col4, col5, col6 = st.columns(3)
    col4.metric("Média Geral (°C)", f"{media_quimica:.1f}")
    col5.metric("Máximo Geral (°C)", f"{max_quimica:.1f}")
    col6.metric("Mínimo Geral (°C)", f"{min_quimica:.1f}")

    fig_quimica = px.box(
        df_quimica,
        x="ÁREA",
        y="TEMPERATURA (°C)",
        color="ÁREA",
        title="Distribuição da Temperatura por Área",
        points="all",
        hover_data={
            "ÁREA": False,
            "TEMPERATURA (°C)": ":.1f",
            "DATA": True,
            "HORÁRIO": True,
            "LOCAL": True
        }
    )
    fig_quimica.update_traces(boxmean="sd")
    st.plotly_chart(fig_quimica, use_container_width=True)

    # -------------------------
    # ANÁLISE GERAL (NO ELSE)
    # -------------------------
    st.subheader("📈 Análises")
    st.markdown(f"""
    - **Física:** A média geral de ruído foi de **{media_fisica:.1f} dB**, com máximo de **{max_fisica:.1f} dB** e mínimo de **{min_fisica:.1f} dB**.  
      Isso mostra quais áreas são mais barulhentas e quais são mais silenciosas.

    - **Química:** A média geral de temperatura foi de **{media_quimica:.1f} °C**, com máximo de **{max_quimica:.1f} °C** e mínimo de **{min_quimica:.1f} °C**.  
      Assim é possível identificar os locais mais quentes e os mais frescos ao longo do dia.
    """)
