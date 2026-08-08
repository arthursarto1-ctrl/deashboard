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
df_fisica['LOCAL'] = df_fisica['LOCAL'].astype(str).str.strip().str.lower()
df_quimica['LOCAL'] = df_quimica['LOCAL'].astype(str).str.strip().str.lower()

# Física: separar DB
df_fisica['DB MAX - MIN'] = df_fisica['DB MAX - MIN'].astype(str).str.replace('–', '-', regex=False)
df_fisica[['DB', 'DB_MIN']] = df_fisica['DB MAX - MIN'].str.split('-', expand=True)
df_fisica['DB'] = pd.to_numeric(df_fisica['DB'], errors='coerce')
df_fisica['DB_MIN'] = pd.to_numeric(df_fisica['DB_MIN'], errors='coerce')

# Química: converter temperatura
df_quimica['TEMPERATURA (°C)'] = pd.to_numeric(df_quimica['TEMPERATURA (°C)'], errors='coerce')

# REMOÇÃO DE VALORES NULOS E ZEROS NAS MEDIÇÕES
df_fisica = df_fisica[df_fisica['DB'].notna() & (df_fisica['DB'] != 0)].copy()
df_quimica = df_quimica[df_quimica['TEMPERATURA (°C)'].notna() & (df_quimica['TEMPERATURA (°C)'] != 0)].copy()

# Tratamento centralizado de Data e Hora
df_fisica['HORÁRIO'] = df_fisica['HORÁRIO'].astype(str).str.replace('00:00:00', '').str.strip()
df_quimica['HORÁRIO'] = df_quimica['HORÁRIO'].astype(str).str.replace('00:00:00', '').str.strip()

# Converter para datetime combinando Data e Horário
df_fisica['DATA_HORA_DT'] = pd.to_datetime(
    df_fisica['DATA'].astype(str).str.strip() + ' ' + df_fisica['HORÁRIO'],
    dayfirst=True, errors='coerce'
)
df_quimica['DATA_HORA_DT'] = pd.to_datetime(
    df_quimica['DATA'].astype(str).str.strip() + ' ' + df_quimica['HORÁRIO'],
    dayfirst=True, errors='coerce'
)

# REMOVER LINHAS COM DATAS INVÁLIDAS / NULAS
df_fisica = df_fisica.dropna(subset=['DATA_HORA_DT']).copy()
df_quimica = df_quimica.dropna(subset=['DATA_HORA_DT']).copy()

# Recriar as colunas formatadas
df_fisica['DATA'] = df_fisica['DATA_HORA_DT'].dt.strftime('%d/%m/%Y')
df_fisica['HORÁRIO'] = df_fisica['DATA_HORA_DT'].dt.strftime('%H:%M')

df_quimica['DATA'] = df_quimica['DATA_HORA_DT'].dt.strftime('%d/%m/%Y')
df_quimica['HORÁRIO'] = df_quimica['DATA_HORA_DT'].dt.strftime('%H:%M')

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
# CONFIGURAÇÃO DA PÁGINA
# -------------------------
st.set_page_config(page_title="Dados Senac Ciências 2CDD02", page_icon="📊", layout="wide")

# -------------------------
# FILTROS NA BARRA LATERAL (SIDEBAR)
# -------------------------
st.sidebar.header("⚙️ Filtros Secundários")

# 1. Filtro de Intervalo de Datas
min_data = min(df_fisica['DATA_HORA_DT'].min(), df_quimica['DATA_HORA_DT'].min()).date()
max_data = max(df_fisica['DATA_HORA_DT'].max(), df_quimica['DATA_HORA_DT'].max()).date()

periodo = st.sidebar.date_input(
    "🗓️ Período das Medições:",
    value=(min_data, max_data),
    min_value=min_data,
    max_value=max_data,
    format="DD/MM/YYYY"
)

if isinstance(periodo, (list, tuple)) and len(periodo) == 2:
    data_inicio, data_fim = periodo
else:
    data_inicio, data_fim = min_data, max_data

# 2. Filtro de Faixa de Valores para Física (dB)
min_db_val = float(df_fisica['DB'].min())
max_db_val = float(df_fisica['DB'].max())
faixa_db = st.sidebar.slider(
    "🎧 Faixa de Ruído (dB):",
    min_value=min_db_val,
    max_value=max_db_val,
    value=(min_db_val, max_db_val),
    step=1.0
)

# 3. Filtro de Faixa de Valores para Química (°C)
min_temp_val = float(df_quimica['TEMPERATURA (°C)'].min())
max_temp_val = float(df_quimica['TEMPERATURA (°C)'].max())
faixa_temp = st.sidebar.slider(
    "🌡️ Faixa de Temperatura (°C):",
    min_value=min_temp_val,
    max_value=max_temp_val,
    value=(min_temp_val, max_temp_val),
    step=0.5
)

# Aplicando os Filtros Secundários aos DataFrames
df_fisica = df_fisica[
    (df_fisica['DATA_HORA_DT'].dt.date >= data_inicio) & 
    (df_fisica['DATA_HORA_DT'].dt.date <= data_fim) &
    (df_fisica['DB'] >= faixa_db[0]) & 
    (df_fisica['DB'] <= faixa_db[1])
]

df_quimica = df_quimica[
    (df_quimica['DATA_HORA_DT'].dt.date >= data_inicio) & 
    (df_quimica['DATA_HORA_DT'].dt.date <= data_fim) &
    (df_quimica['TEMPERATURA (°C)'] >= faixa_temp[0]) & 
    (df_quimica['TEMPERATURA (°C)'] <= faixa_temp[1])
]

# -------------------------
# CONTEÚDO DA PÁGINA PRINCIPAL
# -------------------------
st.title("📊 Dados Senac Ciências 2CDD02")

st.markdown("""
Este site mostra os dados coletados de **Física** (nível de ruído em decibéis) e **Química** (temperatura em graus Celsius) 
divididos em 5 áreas principais: **Teletubies, Acadêmico 1, Acadêmico 2, Biblioteca e Quadras**.

Feito com Python, Streamlit, Pandas e Plotly.  
Por Arthur Sartori Cavalcanti
""")

# =========================================================
# GUIA DE USO (CELULAR E COMPUTADOR)
# =========================================================
with st.expander("❓ Como usar este site? (Toque/Clique para abrir)"):
    st.markdown("""
    ### 📱 No Celular:
    1. **📍 Selecionar Local:** Use a caixa **"SELEÇÃO DE LOCAL"** para escolher entre a visão geral (`todos`) ou uma área específica.
    2. **⚙️ Filtros:** Toque na seta **`>`** no canto superior esquerdo para filtrar por datas e intervalos de valores.
    3. **🎧 Navegação por Matéria:** Escolha entre as abas principais **Física (Ruído)** e **Química (Temperatura)**.
    4. **📊 Troca de Visão:** Em cada matéria, use as abas **"📊 Gráficos e Métricas"** ou **"📋 Tabela de Dados Brutos"**.
    5. **🔎 Interatividade:** Toque nos pontos dos gráficos para ver os valores exatos e horários.

    ---

    ### 💻 No Computador:
    1. **📍 Seleção de Local:** O menu central permite filtrar rapidamente qualquer uma das 5 áreas ou visualizar a análise consolidada (`todos`).
    2. **⚙️ Barra Lateral Fixa:** Utilize o painel da esquerda para aplicar filtros detalhados de período e limites de valores (dB e °C).
    3. **📋 Visualização Dupla:** Alternar entre os gráficos analíticos e as tabelas completas de dados brutos de Física e Química no topo de cada matéria.
    4. **🖱️ Recursos do Gráfico:** Passe o mouse sobre as barras/pontos para ver detalhes. Use a barra de ferramentas do canto superior direito do gráfico para fazer zoom ou baixar a imagem.
    """)

st.write("---")

# =========================================================
# FILTRO DE SELEÇÃO DE LOCAL EM DESTAQUE NA PARTE PRINCIPAL
# =========================================================
st.markdown("### 📍 SELEÇÃO DE LOCAL")
local = st.selectbox(
    "Escolha o local para visualizar as métricas e gráficos:",
    ["todos", "Teletubies", "Acadêmico 1", "Acadêmico 2", "Biblioteca", "Quadras"],
    index=0
)

st.write("---")

# -------------------------
# CRIAÇÃO DAS ABAS PRINCIPAIS
# -------------------------
tab_fisica, tab_quimica = st.tabs(["🎧 Física (Ruído)", "🌡️ Química (Temperatura)"])

# =========================================================
# ABA 1: FÍSICA
# =========================================================
with tab_fisica:
    subtab_graficos_fisica, subtab_dados_fisica = st.tabs(["📊 Gráficos e Métricas", "📋 Tabela de Dados Brutos"])

    with subtab_graficos_fisica:
        if df_fisica.empty:
            st.warning("Nenhum dado de Física disponível para os filtros aplicados.")
        elif local != "todos":
            df_local_fisica = df_fisica[df_fisica['ÁREA'] == local]
            st.subheader(f"🎧 Física - Ruído (dB) — {local}")
            
            if not df_local_fisica.empty:
                media_fisica = df_local_fisica['DB'].mean()
                mediana_fisica = df_local_fisica['DB'].median()
                max_fisica = df_local_fisica['DB'].max()
                min_fisica = df_local_fisica['DB'].min()
                
                q1 = df_local_fisica['DB'].quantile(0.25)
                q3 = df_local_fisica['DB'].quantile(0.75)
                iqr = q3 - q1
                limite_inferior = q1 - 1.5 * iqr
                limite_superior = q3 + 1.5 * iqr
                
                c1, c2, c3, c4, c5, c6 = st.columns(6)
                c1.metric("Média (dB)", f"{media_fisica:.1f}")
                c2.metric("Mediana (dB)", f"{mediana_fisica:.1f}")
                c3.metric("Mínimo (dB)", f"{min_fisica:.1f}")
                c4.metric("Máximo (dB)", f"{max_fisica:.1f}")
                c5.metric("Limite Inferior", f"{limite_inferior:.1f}")
                c6.metric("Limite Superior", f"{limite_superior:.1f}")

                df_area = df_local_fisica.sort_values('DATA_HORA_DT')
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

                st.subheader(f"📝 Diagnóstico do Ruído — {local}")
                dif_db = max_fisica - min_fisica
                if dif_db > 15:
                    texto_db = f"🔊 **Ruído (Alta Variação - {dif_db:.1f} dB):** A diferença entre o pico de som e o momento mais calmo é **muito grande**. Este local passa por momentos de silêncio alternados com picos barulhentos."
                elif dif_db >= 8:
                    texto_db = f"🔉 **Ruído (Variação Moderada - {dif_db:.1f} dB):** A variação de som é **mais ou menos equilibrada**, apresentando oscilações normais sem grandes sobressaltos constantes."
                else:
                    texto_db = f"🔇 **Ruído (Baixa Variação - {dif_db:.1f} dB):** A diferença é **muito pequena**. O nível sonoro deste local é estável e praticamente constante o tempo todo."
                st.markdown(texto_db)
            else:
                st.warning(f"Nenhum dado encontrado para a área '{local}' com os filtros atuais.")

        else:
            st.subheader("🎧 Física - Ruído (dB) — Visão Geral")

            media_fisica = df_fisica['DB'].mean()
            mediana_fisica = df_fisica['DB'].median()
            max_fisica = df_fisica['DB'].max()
            min_fisica = df_fisica['DB'].min()

            q1 = df_fisica['DB'].quantile(0.25)
            q3 = df_fisica['DB'].quantile(0.75)
            iqr = q3 - q1
            limite_inferior = q1 - 1.5 * iqr
            limite_superior = q3 + 1.5 * iqr

            c1, c2, c3, c4, c5, c6 = st.columns(6)
            c1.metric("Média Geral (dB)", f"{media_fisica:.1f}")
            c2.metric("Mediana Geral (dB)", f"{mediana_fisica:.1f}")
            c3.metric("Mínimo Geral (dB)", f"{min_fisica:.1f}")
            c4.metric("Máximo Geral (dB)", f"{max_fisica:.1f}")
            c5.metric("Limite Inferior", f"{limite_inferior:.1f}")
            c6.metric("Limite Superior", f"{limite_superior:.1f}")

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
                    "LOCAL": False
                }
            )
            fig_fisica.update_traces(boxmean="sd")
            st.plotly_chart(fig_fisica, use_container_width=True)

            st.subheader("📈 Análise Geral de Ruído")
            st.markdown(f"""
            A média geral de ruído calculada para todos os pontos foi de **{media_fisica:.1f} dB**, com mediana de **{mediana_fisica:.1f} dB**.  
            O gráfico acima permite comparar o nível de dispersão sonora entre cada uma das 5 áreas coletadas.
            """)

    with subtab_dados_fisica:
        st.subheader("📋 Tabela de Dados Brutos - Física")
        df_filtrado_fisica = df_fisica if local == "todos" else df_fisica[df_fisica['ÁREA'] == local]
        if not df_filtrado_fisica.empty:
            df_exibir_fisica = df_filtrado_fisica[['ÁREA', 'LOCAL', 'DATA', 'HORÁRIO', 'DB']].rename(columns={
                'ÁREA': 'Área Agrupada',
                'LOCAL': 'Local Específico',
                'DATA': 'Data',
                'HORÁRIO': 'Horário',
                'DB': 'Ruído (dB)'
            })
            st.dataframe(df_exibir_fisica, use_container_width=True)
        else:
            st.warning("Nenhum dado bruto encontrado para a área selecionada.")

# =========================================================
# ABA 2: QUÍMICA
# =========================================================
with tab_quimica:
    subtab_graficos_quimica, subtab_dados_quimica = st.tabs(["📊 Gráficos e Métricas", "📋 Tabela de Dados Brutos"])

    with subtab_graficos_quimica:
        if df_quimica.empty:
            st.warning("Nenhum dado de Química disponível para os filtros aplicados.")
        elif local != "todos":
            st.subheader(f"🌡️ Química - Temperatura (°C) — {local}")
            df_local_quimica = df_quimica[df_quimica['ÁREA'] == local]
            
            if not df_local_quimica.empty:
                media_quimica = df_local_quimica['TEMPERATURA (°C)'].mean()
                mediana_quimica = df_local_quimica['TEMPERATURA (°C)'].median()
                max_quimica = df_local_quimica['TEMPERATURA (°C)'].max()
                min_quimica = df_local_quimica['TEMPERATURA (°C)'].min()
                
                q1_temp = df_local_quimica['TEMPERATURA (°C)'].quantile(0.25)
                q3_temp = df_local_quimica['TEMPERATURA (°C)'].quantile(0.75)
                iqr_temp = q3_temp - q1_temp
                limite_inferior_temp = q1_temp - 1.5 * iqr_temp
                limite_superior_temp = q3_temp + 1.5 * iqr_temp
                
                c1, c2, c3, c4, c5, c6 = st.columns(6)
                c1.metric("Média (°C)", f"{media_quimica:.1f}")
                c2.metric("Mediana (°C)", f"{mediana_quimica:.1f}")
                c3.metric("Mínimo (°C)", f"{min_quimica:.1f}")
                c4.metric("Máximo (°C)", f"{max_quimica:.1f}")
                c5.metric("Limite Inferior", f"{limite_inferior_temp:.1f}")
                c6.metric("Limite Superior", f"{limite_superior_temp:.1f}")

                df_area_temp = df_local_quimica.sort_values('DATA_HORA_DT')
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

                st.subheader(f"📝 Diagnóstico Térmico — {local}")
                dif_temp = max_quimica - min_quimica
                if dif_temp > 8:
                    texto_temp = f"🔥 **Temperatura (Alta Variação - {dif_temp:.1f} °C):** A diferença entre a maior e a menor temperatura é **muito alta**. O ambiente sofre forte oscilação térmica ao longo do dia."
                elif dif_temp >= 3:
                    texto_temp = f"🌤️ **Temperatura (Variação Moderada - {dif_temp:.1f} °C):** A variação de temperatura é **mais ou menos aceitável**, acompanhando o clima natural sem mudanças abruptas."
                else:
                    texto_temp = f"❄️ **Temperatura (Baixa Variação - {dif_temp:.1f} °C):** A variação é **muito pouca**. O clima no ambiente se mantém quase inalterado."

                st.markdown(texto_temp)
            else:
                st.warning(f"Nenhum dado encontrado para a área '{local}' com os filtros atuais.")

        else:
            st.subheader("🌡️ Química - Temperatura (°C) — Visão Geral")

            media_quimica = df_quimica['TEMPERATURA (°C)'].mean()
            mediana_quimica = df_quimica['TEMPERATURA (°C)'].median()
            max_quimica = df_quimica['TEMPERATURA (°C)'].max()
            min_quimica = df_quimica['TEMPERATURA (°C)'].min()

            q1_temp = df_quimica['TEMPERATURA (°C)'].quantile(0.25)
            q3_temp = df_quimica['TEMPERATURA (°C)'].quantile(0.75)
            iqr_temp = q3_temp - q1_temp
            limite_inferior_temp = q1_temp - 1.5 * iqr_temp
            limite_superior_temp = q3_temp + 1.5 * iqr_temp

            c1, c2, c3, c4, c5, c6 = st.columns(6)
            c1.metric("Média Geral (°C)", f"{media_quimica:.1f}")
            c2.metric("Mediana Geral (°C)", f"{mediana_quimica:.1f}")
            c3.metric("Mínimo Geral (°C)", f"{min_quimica:.1f}")
            c4.metric("Máximo Geral (°C)", f"{max_quimica:.1f}")
            c5.metric("Limite Inferior", f"{limite_inferior_temp:.1f}")
            c6.metric("Limite Superior", f"{limite_superior_temp:.1f}")

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
                    "LOCAL": False
                }
            )
            fig_quimica.update_traces(boxmean="sd")
            st.plotly_chart(fig_quimica, use_container_width=True)

            st.subheader("📈 Análise Geral de Temperatura")
            st.markdown(f"""
            A média geral de temperatura registrada foi de **{media_quimica:.1f} °C**, atingindo pico máximo de **{max_quimica:.1f} °C** e mínimo de **{min_quimica:.1f} °C**.  
            A visualização gráfica permite analisar a dispersão térmica e identificar os locais mais quentes e mais frios.
            """)

    with subtab_dados_quimica:
        st.subheader("📋 Tabela de Dados Brutos - Química")
        df_filtrado_quimica = df_quimica if local == "todos" else df_quimica[df_quimica['ÁREA'] == local]
        if not df_filtrado_quimica.empty:
            df_exibir_quimica = df_filtrado_quimica[['ÁREA', 'LOCAL', 'DATA', 'HORÁRIO', 'TEMPERATURA (°C)']].rename(columns={
                'ÁREA': 'Área Agrupada',
                'LOCAL': 'Local Específico',
                'DATA': 'Data',
                'HORÁRIO': 'Horário',
                'TEMPERATURA (°C)': 'Temperatura (°C)'
            })
            st.dataframe(df_exibir_quimica, use_container_width=True)
        else:
            st.warning("Nenhum dado bruto encontrado para a área selecionada.")
