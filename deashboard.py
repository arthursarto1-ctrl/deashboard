import locale
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from PIL import Image

# -------------------------
# CONFIGURAÇÃO DE LOCALE (PORTUGUÊS - BRASIL)
# -------------------------
try:
    locale.setlocale(locale.LC_TIME, "pt_BR.UTF-8")
except:
    try:
        locale.setlocale(locale.LC_TIME, "pt_BR")
    except:
        pass

# -------------------------
# ORDEM DAS ÁREAS E PALETA DE CORES PERSONALIZADA
# -------------------------
ORDEM_AREAS = ["Área 1", "Área 2", "Área 3", "Área 4", "Área 5", "Área 6", "Área 7"]

CORES_AREAS = {
    "Área 1": "#FF69B4",  # Rosa
    "Área 2": "#FF7F00",  # Laranja
    "Área 3": "#E41A1C",  # Vermelho
    "Área 4": "#FFD700",  # Amarelo
    "Área 5": "#4DAF4A",  # Verde
    "Área 6": "#377EB8",  # Azul
    "Área 7": "#999999"   # Cinza (Outros)
}

# -------------------------
# LEITURA DOS DADOS
# -------------------------
@st.cache_data
def carregar_dados():
    df_f = pd.read_excel("DADOS DE FÍSICA - MOSTRA DE ARTES 2026.xlsx", sheet_name="DADOS DE FÍSICA - MOSTRA DE ART")
    df_q = pd.read_excel("DADOS DE FÍSICA - MOSTRA DE ARTES 2026.xlsx", sheet_name="DADOS DE QUÍMICA")
    return df_f, df_q

try:
    df_fisica, df_quimica = carregar_dados()
except Exception as e:
    st.error(f"Erro ao carregar o arquivo Excel: {e}")
    st.stop()

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

# -------------------------
# PROCESSAMENTO DE DATAS EM PADRÃO BRASILEIRO (DIA/MÊS/ANO)
# -------------------------
def processar_data_hora_br(df):
    if pd.api.types.is_datetime64_any_dtype(df['DATA']):
        data_dt = df['DATA']
    else:
        data_dt = pd.to_datetime(df['DATA'], dayfirst=True, errors='coerce')

    horario_str = df['HORÁRIO'].astype(str).str.replace('00:00:00', '').str.strip()
    horario_str = horario_str.apply(lambda x: x if len(x) >= 4 else '00:00')

    data_str = data_dt.dt.strftime('%Y-%m-%d')
    data_hora_final = pd.to_datetime(data_str + ' ' + horario_str, errors='coerce')
    
    return data_hora_final.fillna(data_dt)

df_fisica['DATA_HORA_DT'] = processar_data_hora_br(df_fisica)
df_quimica['DATA_HORA_DT'] = processar_data_hora_br(df_quimica)

# REMOVER APENAS LINHAS ONDE A DATA FOR NULA
df_fisica = df_fisica.dropna(subset=['DATA_HORA_DT']).copy()
df_quimica = df_quimica.dropna(subset=['DATA_HORA_DT']).copy()

# Recriar as colunas formatadas em Padrão Brasileiro (DD/MM/YYYY)
df_fisica['DATA'] = df_fisica['DATA_HORA_DT'].dt.strftime('%d/%m/%Y')
df_fisica['HORÁRIO'] = df_fisica['DATA_HORA_DT'].dt.strftime('%H:%M')

df_quimica['DATA'] = df_quimica['DATA_HORA_DT'].dt.strftime('%d/%m/%Y')
df_quimica['HORÁRIO'] = df_quimica['DATA_HORA_DT'].dt.strftime('%H:%M')

# -------------------------
# AGRUPAMENTO EM ÁREAS
# -------------------------
def agrupar_local(local_nome):
    if local_nome in [
        "p1", "biblioteca", "biblioteca (2º andar)", "biblioteca (segundo andar)", 
        "praça", "praça da biblioteca", "praça no meio"
    ]:
        return "Área 1"
    
    elif local_nome in [
        "acadêmico 1", "ala a", "ala b", "ala c", "ala g", "ala i", "nasa", "sala de aula"
    ]:
        return "Área 2"
    
    elif local_nome in [
        "acadêmico 2", "ala k", "ala k, acadêmico 2", "avião", "prédio de design", "prédio de dising", 
        "vão entre os acadêmicos", "área do avião, acadêmico 2"
    ]:
        return "Área 3"
    
    elif local_nome in [
        "frente da academia", "atrás da p2", "atrás do auditório", "dentro da p2", 
        "dentro da quadra", "dentro do auditório", "centro de convenções", "frente do centro de convenções", 
        "hall quadras", "p2", "parte de trás da quadra", "prédio das quadras internas", 
        "prédio quadras internas", "quadras abertas", "quadras externas", 
        "quadras externas e sala de aula", "quadras internas", "área 6 e 8 (quadras)", "perto da quadra interna"
    ]:
        return "Área 4"
    
    elif local_nome in [
        "p3", "atrás da p3", "teletubbies", "teletubies", "tratamento de água", 
        "teletubbies e região do senac", "estufa (8)", "lado de fora"
    ]:
        return "Área 5"
    
    elif local_nome in [
        "estacionamento", "estacionamento e arredores", "estacionamento externo (área toda)", 
        "estacionamento frontal", "estacionamento lateral", "entrada principal", 
        "frente do auditório", "frente auditorio", "ponto de ônibus", "perto do ponto de ônibus", 
        "perto ponto de onibus", "saída acedmiccc"
    ]:
        return "Área 6"
    
    else:
        return "Área 7"

df_fisica['ÁREA'] = df_fisica['LOCAL'].apply(agrupar_local)
df_quimica['ÁREA'] = df_quimica['LOCAL'].apply(agrupar_local)

# FORÇANDO A ORDENAÇÃO CATEGÓRICA DE ÁREA 1 A ÁREA 7 NO PANDAS
df_fisica['ÁREA'] = pd.Categorical(df_fisica['ÁREA'], categories=ORDEM_AREAS, ordered=True)
df_quimica['ÁREA'] = pd.Categorical(df_quimica['ÁREA'], categories=ORDEM_AREAS, ordered=True)

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
divididos em áreas do campus.

Feito com Python, Streamlit, Pandas e Plotly.  
Por Arthur Sartori Cavalcanti
""")
# =========================================================
# GUIA DE USO (CELULAR E COMPUTADOR)
# =========================================================
with st.expander("❓ Como usar este site? (Toque/Clique para abrir)"):
    st.markdown("""
    ### 📱 No Celular:
    1. **📍 Selecionar Local:** Use a caixa **"SELEÇÃO DE LOCAL"** ou veja o mapa interativo para escolher uma área.
    2. **⚙️ Filtros:** Toque na seta **`>`** no canto superior esquerdo para filtrar por datas e intervalos de valores.
    3. **🎧 Navegação por Matéria:** Escolha entre as abas principais **Física (Ruído)** e **Química (Temperatura)**.
    4. **📊 Troca de Visão:** Em cada matéria, use as abas **"📊 Gráficos e Métricas"** ou **"📋 Tabela de Dados Brutos"**.
    5. **🔎 Interatividade:** Toque nos pontos dos gráficos para ver os valores exatos e horários.

    ---

    ### 💻 No Computador:
    1. **📍 Seleção de Local:** O menu central e o mapa interativo permitem filtrar rapidamente qualquer uma das áreas ou visualizar a análise consolidada (`todos`).
    2. **⚙️ Barra Lateral Fixa:** Utilize o painel da esquerda para aplicar filtros detalhados de período (DD/MM/AAAA) e limites de valores (dB e °C).
    3. **📋 Visualização Dupla:** Alternar entre os gráficos analíticos e as tabelas completas de dados brutos de Física e Química no topo de cada matéria.
    4. **🖱️ Recursos do Gráfico:** Passe o mouse sobre as barras/pontos para ver detalhes.
    """)

st.write("---")

# =========================================================
# MAPA INTERATIVO DO CAMPUS
# =========================================================
st.markdown("### 🗺️ Mapa Interativo do Campus (Visão Aérea)")

try:
    map_img = Image.open("foto senac de cima.png")
    img_width, img_height = map_img.size

    fig_map = go.Figure()

    fig_map.add_layout_image(
        dict(
            source=map_img,
            xref="x",
            yref="y",
            x=0,
            y=img_height,
            sizex=img_width,
            sizey=img_height,
            sizing="contain",
            opacity=1,
            layer="below"
        )
    )

    areas_coords = {
         # Área 1 (Rosa - Canto inferior esquerdo)
         "Área 1": {
             "x": [0, 0.227 * img_width, 0.227 * img_width, 0],
             "y": [0.536 * img_height, 0.536 * img_height, img_height, img_height],
             "color": CORES_AREAS["Área 1"],
             "label": "A1: Biblioteca e P1"
         },
         
         # Área 2 (Laranja - Bloco inferior + brazo vertical à esquerda do a3)
         "Área 2": {
             "x": [
                 0.227 * img_width, 
                 0.308 * img_width, 
                 0.308 * img_width, 
                 0.667 * img_width, 
                 0.667 * img_width, 
                 0.227 * img_width
             ],
             "y": [
                 0.383 * img_height, 
                 0.383 * img_height, 
                 0.611 * img_height, 
                 0.611 * img_height, 
                 0.838 * img_height, 
                 0.838 * img_height
             ],
             "color": CORES_AREAS["Área 2"],
             "label": "A2: Acadêmico 1"
         },
         
         # Área 3 (Vermelho - Bloco central com recuo no canto inferior direito)
         "Área 3": {
             "x": [
                 0.308 * img_width, 
                 0.721 * img_width, 
                 0.721 * img_width, 
                 0.667 * img_width, 
                 0.667 * img_width, 
                 0.308 * img_width
             ],
             "y": [
                 0.383 * img_height, 
                 0.383 * img_height, 
                 0.575 * img_height, 
                 0.575 * img_height, 
                 0.611 * img_height, 
                 0.611 * img_height
             ],
             "color": CORES_AREAS["Área 3"],
             "label": "A3: Acadêmico 2"
         },
         
         # Área 4 (Amarelo - Lado direito: Quadras + encaixe abaixo do a3)
         "Área 4": {
             "x": [
                 0.721 * img_width, 
                 img_width, 
                 img_width, 
                 0.667 * img_width, 
                 0.667 * img_width, 
                 0.721 * img_width
             ],
             "y": [
                 0, 
                 0, 
                 0.838 * img_height, 
                 0.838 * img_height, 
                 0.575 * img_height, 
                 0.575 * img_height
             ],
             "color": CORES_AREAS["Área 4"],
             "label": "A4: Quadras,academias,centro de convenções"
         },
         
         # Área 5 (Verde - Canto superior esquerdo em L)
         "Área 5": {
             "x": [
                 0, 
                 0.721 * img_width, 
                 0.721 * img_width, 
                 0.227 * img_width, 
                 0.227 * img_width, 
                 0
             ],
             "y": [
                 0, 
                 0, 
                 0.383 * img_height, 
                 0.383 * img_height, 
                 0.536 * img_height, 
                 0.536 * img_height
             ],
             "color": CORES_AREAS["Área 5"],
             "label": "A5: Teletubbies e P3"
         },
         
         # Área 6 (Azul Escuro - Faixa inferior de fora a fora à direita)
         "Área 6": {
             "x": [0.227 * img_width, img_width, img_width, 0.227 * img_width],
             "y": [0.838 * img_height, 0.838 * img_height, img_height, img_height],
             "color": CORES_AREAS["Área 6"],
             "label": "A6: Estacionamento e Entrada"
         }
     }

    for area_key, data in areas_coords.items():
        y_plotly = [img_height - y for y in data["y"]]
        
        fig_map.add_trace(go.Scatter(
            x=data["x"],
            y=y_plotly,
            fill="toself",
            fillcolor=data["color"],
            opacity=0.35,
            line=dict(color=data["color"], width=3),
            name=area_key,
            hoverinfo="text",
            text=f"<b>{area_key}</b><br>{data['label']}"
        ))

    fig_map.update_xaxes(visible=False, range=[0, img_width])
    fig_map.update_yaxes(visible=False, range=[0, img_height], scaleanchor="x", scaleratio=1)
    
    fig_map.update_layout(
        title="<b>Passe o mouse ou toque sobre as regiões para identificar cada Área</b>",
        margin=dict(l=0, r=0, t=40, b=0),
        height=550,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="center", x=0.5)
    )

    st.plotly_chart(fig_map, use_container_width=True)

except Exception as e:
    st.info("💡 Coloque a imagem 'foto senac de cima.png' na mesma pasta do código para exibir o mapa interativo sobreposto.")

st.write("---")

# =========================================================
# BLOCO DINÂMICO DE DESTAQUES AUTOMÁTICOS
# =========================================================
st.markdown("### 🏆 Destaques Automáticos da Coleta")

# TABELA 1: MÉDIAS POR ÁREA
st.markdown("##### 📍 Médias por Área Agrupada")
col_m1, col_m2, col_m3, col_m4 = st.columns(4)

if not df_quimica.empty:
    temp_medias = df_quimica.groupby('ÁREA', observed=False)['TEMPERATURA (°C)'].mean()
    area_mais_quente = temp_medias.idxmax()
    val_mais_quente = temp_medias.max()
    
    area_mais_gelada = temp_medias.idxmin()
    val_mais_gelada = temp_medias.min()
    
    col_m1.metric("🔥 Área Mais Quente", f"{area_mais_quente}", f"{val_mais_quente:.1f} °C (Média)")
    col_m2.metric("❄️ Área Mais Gelada", f"{area_mais_gelada}", f"{val_mais_gelada:.1f} °C (Média)")
else:
    col_m1.metric("🔥 Área Mais Quente", "Sem dados", "0.0 °C")
    col_m2.metric("❄️ Área Mais Gelada", "Sem dados", "0.0 °C")

if not df_fisica.empty:
    db_medias = df_fisica.groupby('ÁREA', observed=False)['DB'].mean()
    area_mais_barulhenta = db_medias.idxmax()
    val_mais_barulhenta = db_medias.max()
    
    area_mais_silenciosa = db_medias.idxmin()
    val_mais_silenciosa = db_medias.min()
    
    col_m3.metric("📢 Área Mais Barulhenta", f"{area_mais_barulhenta}", f"{val_mais_barulhenta:.1f} dB (Média)")
    col_m4.metric("🔇 Área Mais Silenciosa", f"{area_mais_silenciosa}", f"{val_mais_silenciosa:.1f} dB (Média)")
else:
    col_m3.metric("📢 Área Mais Barulhenta", "Sem dados", "0.0 dB")
    col_m4.metric("🔇 Área Mais Silenciosa", "Sem dados", "0.0 dB")

# TABELA 2: EXTREMOS ABSOLUTOS
st.markdown("##### ⚡ Medições Extremas Registradas (Picos e Mínimos)")
col_e1, col_e2, col_e3, col_e4 = st.columns(4)

if not df_quimica.empty:
    idx_max_temp = df_quimica['TEMPERATURA (°C)'].idxmax()
    row_max_temp = df_quimica.loc[idx_max_temp]
    val_ext_max_temp = row_max_temp['TEMPERATURA (°C)']
    
    idx_min_temp = df_quimica['TEMPERATURA (°C)'].idxmin()
    row_min_temp = df_quimica.loc[idx_min_temp]
    val_ext_min_temp = row_min_temp['TEMPERATURA (°C)']

    col_e1.metric("🌡️ Maior Temp. Absoluta", f"{row_max_temp['ÁREA']}", f"{val_ext_max_temp:.1f} °C ({row_max_temp['DATA']})")
    col_e2.metric("🧊 Menor Temp. Absoluta", f"{row_min_temp['ÁREA']}", f"{val_ext_min_temp:.1f} °C ({row_min_temp['DATA']})")
else:
    col_e1.metric("🌡️ Maior Temp. Absoluta", "Sem dados", "0.0 °C")
    col_e2.metric("🧊 Menor Temp. Absoluta", "Sem dados", "0.0 °C")

if not df_fisica.empty:
    idx_max_db = df_fisica['DB'].idxmax()
    row_max_db = df_fisica.loc[idx_max_db]
    val_ext_max_db = row_max_db['DB']

    idx_min_db = df_fisica['DB'].idxmin()
    row_min_db = df_fisica.loc[idx_min_db]
    val_ext_min_db = row_min_db['DB']

    col_e3.metric("🔊 Maior Pico de Som", f"{row_max_db['ÁREA']}", f"{val_ext_max_db:.1f} dB ({row_max_db['DATA']})")
    col_e4.metric("🔕 Menor Ruído Absoluto", f"{row_min_db['ÁREA']}", f"{val_ext_min_db:.1f} dB ({row_min_db['DATA']})")
else:
    col_e3.metric("🔊 Maior Pico de Som", "Sem dados", "0.0 dB")
    col_e4.metric("🔕 Menor Ruído Absoluto", "Sem dados", "0.0 dB")

st.write("---")

# =========================================================
# FILTRO DE SELEÇÃO DE LOCAL EM DESTAQUE NA PARTE PRINCIPAL
# =========================================================
st.markdown("### 📍 SELEÇÃO DE LOCAL")
local = st.selectbox(
    "Escolha o local para visualizar as métricas e gráficos:",
    ["todos", "Área 1", "Área 2", "Área 3", "Área 4", "Área 5", "Área 6"],
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

                df_area = df_local_fisica.sort_values('DATA_HORA_DT').copy()
                df_area['DATA_HORA_ROTULO'] = df_area['DATA_HORA_DT'].dt.strftime('%d/%m %H:%M')

                cor_area_sel = CORES_AREAS.get(local, "#3366CC")

                fig_linha = px.line(
                    df_area,
                    x="DATA_HORA_ROTULO",
                    y="DB",
                    markers=True,
                    title=f"Ruído (dB) ao Longo do Tempo — {local}",
                    labels={"DATA_HORA_ROTULO": "Data e Horário", "DB": "Ruído (dB)", "LOCAL": "Local Exato"},
                    hover_data={"LOCAL": True, "DATA_HORA_ROTULO": True, "DB": ":.1f"}
                )
                fig_linha.update_traces(line_color=cor_area_sel, marker=dict(color=cor_area_sel, size=8))
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
                category_orders={"ÁREA": ORDEM_AREAS},
                color_discrete_map=CORES_AREAS,
                title="Níveis de Ruído por Área",
                points="all",
                labels={"DB": "Ruído (dB)", "DATA": "Data (DD/MM/AAAA)", "HORÁRIO": "Horário", "LOCAL": "Local Exato"},
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

            st.subheader("📈 Análise Geral de Ruído")
            st.markdown(f"""
            A média geral de ruído calculada para todos os pontos foi de **{media_fisica:.1f} dB**, com mediana de **{mediana_fisica:.1f} dB**.  
            O gráfico acima permite comparar o nível de dispersão sonora entre cada uma das áreas coletadas.
            """)

    with subtab_dados_fisica:
        st.subheader("📋 Tabela de Dados Brutos - Física")
        df_filtrado_fisica = df_fisica if local == "todos" else df_fisica[df_fisica['ÁREA'] == local]
        if not df_filtrado_fisica.empty:
            df_exibir_fisica = df_filtrado_fisica[['ÁREA', 'LOCAL', 'DATA', 'HORÁRIO', 'DB']].rename(columns={
                'ÁREA': 'Área Agrupada',
                'LOCAL': 'Local Específico',
                'DATA': 'Data (DD/MM/AAAA)',
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

                df_area_temp = df_local_quimica.sort_values('DATA_HORA_DT').copy()
                df_area_temp['DATA_HORA_ROTULO'] = df_area_temp['DATA_HORA_DT'].dt.strftime('%d/%m %H:%M')

                cor_area_sel = CORES_AREAS.get(local, "#3366CC")

                fig_linha_temp = px.line(
                    df_area_temp,
                    x="DATA_HORA_ROTULO",
                    y="TEMPERATURA (°C)",
                    markers=True,
                    title=f"Variação de Temperatura (°C) ao Longo do Tempo — {local}",
                    labels={"DATA_HORA_ROTULO": "Data e Horário", "TEMPERATURA (°C)": "Temperatura (°C)", "LOCAL": "Local Exato"},
                    hover_data={"LOCAL": True, "DATA_HORA_ROTULO": True, "TEMPERATURA (°C)": ":.1f"}
                )
                fig_linha_temp.update_traces(line_color=cor_area_sel, marker=dict(color=cor_area_sel, size=8))
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
                category_orders={"ÁREA": ORDEM_AREAS},
                color_discrete_map=CORES_AREAS,
                title="Distribuição da Temperatura por Área",
                points="all",
                labels={"TEMPERATURA (°C)": "Temperatura (°C)", "DATA": "Data (DD/MM/AAAA)", "HORÁRIO": "Horário", "LOCAL": "Local Exato"},
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
                'DATA': 'Data (DD/MM/AAAA)',
                'HORÁRIO': 'Horário',
                'TEMPERATURA (°C)': 'Temperatura (°C)'
            })
            st.dataframe(df_exibir_quimica, use_container_width=True)
        else:
            st.warning("Nenhum dado bruto encontrado para a área selecionada.")
