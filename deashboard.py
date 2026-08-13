import locale
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from PIL import Image

# -------------------------
# CONFIGURAÇÃO DE LOCALE
# -------------------------
try:
  locale.setlocale(locale.LC_TIME, 'pt_BR.UTF-8')
except:
  try:
    locale.setlocale(locale.LC_TIME, 'pt_BR')
  except:
    pass

# -------------------------
# ORDEM DAS ÁREAS, CORES E NOMES
# -------------------------
ORDEM_AREAS = [
    'Área 1',
    'Área 2',
    'Área 3',
    'Área 4',
    'Área 5',
    'Área 6',
    'Área 7',
]

CORES_AREAS = {
    'Área 1': '#FF69B4',  # Rosa
    'Área 2': '#FF4D4D',  # Vermelho
    'Área 3': '#FF7300',  # Laranja
    'Área 4': '#FFD700',  # Amarelo
    'Área 5': '#2ECC71',  # Verde
    'Área 6': '#3498DB',  # Azul
    'Área 7': '#95A5A6',  # Cinza
}

NOMES_AREAS = {
    'Área 1': 'Biblioteca e P1',
    'Área 2': 'Acadêmico 1',
    'Área 3': 'Acadêmico 2',
    'Área 4': 'Quadras e Convenções',
    'Área 5': 'Teletubbies e P3',
    'Área 6': 'Estacionamento e Entrada',
    'Área 7': 'Outros',
}


# -------------------------
# LEITURA DOS DADOS
# -------------------------
@st.cache_data
def carregar_dados():
  df_f = pd.read_excel(
      'DADOS DE FÍSICA - MOSTRA DE ARTES 2026.xlsx',
      sheet_name='DADOS DE FÍSICA - MOSTRA DE ART',
  )
  df_q = pd.read_excel(
      'DADOS DE FÍSICA - MOSTRA DE ARTES 2026.xlsx', sheet_name='DADOS DE QUÍMICA'
  )
  return df_f, df_q


try:
  df_fisica, df_quimica = carregar_dados()
except Exception as e:
  st.error(f'Erro ao carregar o arquivo Excel: {e}')
  st.stop()

# -------------------------
# TRATAMENTO DOS DADOS
# -------------------------
df_fisica['LOCAL'] = df_fisica['LOCAL'].astype(str).str.strip().str.lower()
df_quimica['LOCAL'] = df_quimica['LOCAL'].astype(str).str.strip().str.lower()

df_fisica['DB MAX - MIN'] = (
    df_fisica['DB MAX - MIN'].astype(str).str.replace('–', '-', regex=False)
)
df_fisica[['DB', 'DB_MIN']] = df_fisica['DB MAX - MIN'].str.split(
    '-', expand=True
)
df_fisica['DB'] = pd.to_numeric(df_fisica['DB'], errors='coerce')

df_quimica['TEMPERATURA (°C)'] = pd.to_numeric(
    df_quimica['TEMPERATURA (°C)'], errors='coerce'
)

df_fisica = df_fisica[
    df_fisica['DB'].notna() & (df_fisica['DB'] != 0)
].copy()
df_quimica = df_quimica[
    df_quimica['TEMPERATURA (°C)'].notna() & (df_quimica['TEMPERATURA (°C)'] != 0)
].copy()


# -------------------------
# PROCESSAMENTO DE DATA E HORA
# -------------------------
def processar_data_hora_br(df):
  if pd.api.types.is_datetime64_any_dtype(df['DATA']):
    data_dt = df['DATA']
  else:
    data_dt = pd.to_datetime(df['DATA'], dayfirst=True, errors='coerce')

  horario_str = (
      df['HORÁRIO'].astype(str).str.replace('00:00:00', '').str.strip()
  )
  horario_str = horario_str.apply(lambda x: x if len(x) >= 4 else '00:00')

  data_str = data_dt.dt.strftime('%Y-%m-%d')
  data_hora_final = pd.to_datetime(
      data_str + ' ' + horario_str, errors='coerce'
  )

  return data_hora_final.fillna(data_dt)


df_fisica['DATA_HORA_DT'] = processar_data_hora_br(df_fisica)
df_quimica['DATA_HORA_DT'] = processar_data_hora_br(df_quimica)

df_fisica = df_fisica.dropna(subset=['DATA_HORA_DT']).copy()
df_quimica = df_quimica.dropna(subset=['DATA_HORA_DT']).copy()


# -------------------------
# AGRUPAMENTO EM ÁREAS
# -------------------------
def agrupar_local(local_nome):
  if local_nome in [
      'p1',
      'biblioteca',
      'biblioteca (2º andar)',
      'biblioteca (segundo andar)',
      'praça',
      'praça da biblioteca',
      'praça no meio',
  ]:
    return 'Área 1'
  elif local_nome in [
      'acadêmico 1',
      'ala a',
      'ala b',
      'ala c',
      'ala g',
      'ala i',
      'nasa',
      'sala de aula',
  ]:
    return 'Área 2'
  elif local_nome in [
      'acadêmico 2',
      'ala k',
      'ala k, acadêmico 2',
      'avião',
      'prédio de design',
      'prédio de dising',
      'vão entre os acadêmicos',
      'área do avião, acadêmico 2',
  ]:
    return 'Área 3'
  elif local_nome in [
      'frente da academia',
      'atrás da p2',
      'atrás do auditório',
      'dentro da p2',
      'dentro da quadra',
      'dentro do auditório',
      'centro de convenções',
      'frente do centro de convenções',
      'hall quadras',
      'p2',
      'parte de trás da quadra',
      'prédio das quadras internas',
      'prédio quadras internas',
      'quadras abertas',
      'quadras externas',
      'quadras externas e sala de aula',
      'quadras internas',
      'área 6 e 8 (quadras)',
      'perto da quadra interna',
  ]:
    return 'Área 4'
  elif local_nome in [
      'p3',
      'atrás da p3',
      'teletubbies',
      'teletubies',
      'tratamento de água',
      'teletubbies e região do senac',
      'estufa (8)',
      'lado de fora',
  ]:
    return 'Área 5'
  elif local_nome in [
      'estacionamento',
      'estacionamento e arredores',
      'estacionamento externo (área toda)',
      'estacionamento frontal',
      'estacionamento lateral',
      'entrada principal',
      'frente do auditório',
      'frente auditorio',
      'ponto de ônibus',
      'perto do ponto de ônibus',
      'perto ponto de onibus',
      'saída acedmiccc',
  ]:
    return 'Área 6'
  else:
    return 'Área 7'


df_fisica['ÁREA'] = df_fisica['LOCAL'].apply(agrupar_local)
df_quimica['ÁREA'] = df_quimica['LOCAL'].apply(agrupar_local)

# -------------------------
# CONFIGURAÇÃO DA PÁGINA
# -------------------------
st.set_page_config(
    page_title='Dashboard Senac Ciências', page_icon='📊', layout='wide'
)

# =========================================================
# BARRA LATERAL (SIDEBAR) - FILTROS MÍN E MÁX
# =========================================================
st.sidebar.header('🎛️ Filtros de Mín e Máx')

min_db_val, max_db_val = float(df_fisica['DB'].min()), float(
    df_fisica['DB'].max()
)
filtro_db = st.sidebar.slider(
    '🔊 Filtro de Ruído (dB):',
    min_value=min_db_val,
    max_value=max_db_val,
    value=(min_db_val, max_db_val),
    step=0.5,
)

min_temp_val, max_temp_val = float(df_quimica['TEMPERATURA (°C)'].min()), float(
    df_quimica['TEMPERATURA (°C)'].max()
)
filtro_temp = st.sidebar.slider(
    '🌡️ Filtro de Temperatura (°C):',
    min_value=min_temp_val,
    max_value=max_temp_val,
    value=(min_temp_val, max_temp_val),
    step=0.5,
)

st.title('📊 Dashboard Senac Ciências')

# =========================================================
# 1. COMO USAR NO CELULAR E NO COMPUTADOR
# =========================================================
with st.expander('📱 💻 **Como usar no Computador e no Celular**', expanded=False):
  col_info1, col_info2 = st.columns(2)

  with col_info1:
    st.markdown("""
        #### 💻 No Computador:
        * **Ver Detalhes:** Passe o cursor do mouse sobre os pontos nos gráficos para ver o horário exato e o valor medido.
        * **Zoom Interativo:** Clique e arraste o mouse para dar zoom. Dê **dois cliques** para resetar.
        * **Ocultar Áreas:** Clique na legenda para desativar temporariamente uma área.
        """)

  with col_info2:
    st.markdown("""
        #### 📱 No Celular:
        * **Acesso Wi-Fi:** Digite no navegador o endereço **Network URL** gerado pelo computador.
        * **Toque para Detalhar:** Toque nos pontos do gráfico para exibir as medições.
        * **Filtros Mín/Máx:** Utilize a barra lateral recolhível para filtrar limites de ruído e temperatura.
        """)

st.write('---')

# =========================================================
# 2. MAPA INTERATIVO DO CAMPUS
# =========================================================
st.markdown('### 🗺️ Mapa Interativo do Campus')

try:
  map_img = Image.open('foto senac de cima.png')
  img_width, img_height = map_img.size

  fig_map = go.Figure()

  fig_map.add_layout_image(
      dict(
          source=map_img,
          xref='x',
          yref='y',
          x=0,
          y=img_height,
          sizex=img_width,
          sizey=img_height,
          sizing='contain',
          opacity=1,
          layer='below',
      )
  )

  areas_coords = {
      'Área 1': {
          'x': [0, 0.227 * img_width, 0.227 * img_width, 0],
          'y': [
              0.536 * img_height,
              0.536 * img_height,
              img_height,
              img_height,
          ],
          'color': CORES_AREAS['Área 1'],
          'label': 'A1: Biblioteca e P1',
      },
      'Área 2': {
          'x': [
              0.227 * img_width,
              0.308 * img_width,
              0.308 * img_width,
              0.667 * img_width,
              0.667 * img_width,
              0.227 * img_width,
          ],
          'y': [
              0.383 * img_height,
              0.383 * img_height,
              0.611 * img_height,
              0.611 * img_height,
              0.838 * img_height,
              0.838 * img_height,
          ],
          'color': CORES_AREAS['Área 2'],
          'label': 'A2: Acadêmico 1',
      },
      'Área 3': {
          'x': [
              0.308 * img_width,
              0.721 * img_width,
              0.721 * img_width,
              0.667 * img_width,
              0.667 * img_width,
              0.308 * img_width,
          ],
          'y': [
              0.383 * img_height,
              0.383 * img_height,
              0.575 * img_height,
              0.575 * img_height,
              0.611 * img_height,
              0.611 * img_height,
          ],
          'color': CORES_AREAS['Área 3'],
          'label': 'A3: Acadêmico 2',
      },
      'Área 4': {
          'x': [
              0.721 * img_width,
              img_width,
              img_width,
              0.667 * img_width,
              0.667 * img_width,
              0.721 * img_width,
          ],
          'y': [
              0,
              0,
              0.838 * img_height,
              0.838 * img_height,
              0.575 * img_height,
              0.575 * img_height,
          ],
          'color': CORES_AREAS['Área 4'],
          'label': 'A4: Quadras e Convenções',
      },
      'Área 5': {
          'x': [
              0,
              0.721 * img_width,
              0.721 * img_width,
              0.227 * img_width,
              0.227 * img_width,
              0,
          ],
          'y': [
              0,
              0,
              0.383 * img_height,
              0.383 * img_height,
              0.536 * img_height,
              0.536 * img_height,
          ],
          'color': CORES_AREAS['Área 5'],
          'label': 'A5: Teletubbies e P3',
      },
      'Área 6': {
          'x': [0.227 * img_width, img_width, img_width, 0.227 * img_width],
          'y': [
              0.838 * img_height,
              0.838 * img_height,
              img_height,
              img_height,
          ],
          'color': CORES_AREAS['Área 6'],
          'label': 'A6: Estacionamento e Entrada',
      },
  }

  for area_key, data in areas_coords.items():
    y_plotly = [img_height - y for y in data['y']]
    fig_map.add_trace(
        go.Scatter(
            x=data['x'],
            y=y_plotly,
            fill='toself',
            fillcolor=data['color'],
            opacity=0.35,
            line=dict(color=data['color'], width=2),
            name=area_key,
            hoverinfo='text',
            text=f"<b>{area_key}</b><br>{data['label']}",
        )
    )

  fig_map.update_xaxes(visible=False, range=[0, img_width])
  fig_map.update_yaxes(
      visible=False, range=[0, img_height], scaleanchor='x', scaleratio=1
  )
  fig_map.update_layout(
      margin=dict(l=0, r=0, t=10, b=0),
      height=380,
      legend=dict(
          orientation='h', yanchor='bottom', y=1.02, xanchor='center', x=0.5
      ),
      template='plotly_dark',
  )

  st.plotly_chart(fig_map, use_container_width=True)

except Exception:
  st.info(
      "💡 Coloque a imagem 'foto senac de cima.png' na mesma pasta para ativar o mapa."
  )

st.write('---')

# =========================================================
# 3. DESTAQUES AUTOMÁTICOS DA COLETA
# =========================================================
st.markdown('### 🏆 Destaques Automáticos da Coleta')

st.markdown('#### 📍 Médias por Área Agrupada')
ch1, ch2, ch3, ch4 = st.columns(4)

mean_q = df_quimica.groupby('ÁREA')['TEMPERATURA (°C)'].mean()
area_quente = mean_q.idxmax() if not mean_q.empty else '-'
val_quente = mean_q.max() if not mean_q.empty else 0.0

area_gelada = mean_q.idxmin() if not mean_q.empty else '-'
val_gelada = mean_q.min() if not mean_q.empty else 0.0

mean_f = df_fisica.groupby('ÁREA')['DB'].mean()
area_barulhenta = mean_f.idxmax() if not mean_f.empty else '-'
val_barulhenta = mean_f.max() if not mean_f.empty else 0.0

area_silenciosa = mean_f.idxmin() if not mean_f.empty else '-'
val_silenciosa = mean_f.min() if not mean_f.empty else 0.0

# Médias
ch1.metric(
    label='🔥 Área Mais Quente',
    value=f"{area_quente} • {NOMES_AREAS.get(area_quente, '')}",
    delta=f"{val_quente:.1f} °C (Média)",
    delta_color='normal',
)

ch2.metric(
    label='❄️ Área Mais Gelada',
    value=f"{area_gelada} • {NOMES_AREAS.get(area_gelada, '')}",
    delta=f"{val_gelada:.1f} °C (Média)",  # Sinal negativo gera 1 seta ↓
    delta_color='inverse',  # Inverse deixa a cor verde
)

ch3.metric(
    label='📢 Área Mais Barulhenta',
    value=f"{area_barulhenta} • {NOMES_AREAS.get(area_barulhenta, '')}",
    delta=f"{val_barulhenta:.1f} dB (Média)",
    delta_color='normal',
)

ch4.metric(
    label='🔕 Área Mais Silenciosa',
    value=f"{area_silenciosa} • {NOMES_AREAS.get(area_silenciosa, '')}",
    delta=f"{val_silenciosa:.1f} dB (Média)",  # Sinal negativo gera 1 seta ↓
    delta_color='inverse',  # Inverse deixa a cor verde
)

st.markdown('#### ⚡ Medições Extremas Registradas (Picos e Mínimos)')
ce1, ce2, ce3, ce4 = st.columns(4)

# Maior e Menor Temperatura
idx_max_t = df_quimica['TEMPERATURA (°C)'].idxmax()
row_max_t = df_quimica.loc[idx_max_t]
dt_max_t = row_max_t['DATA_HORA_DT'].strftime('%d/%m/%Y')

idx_min_t = df_quimica['TEMPERATURA (°C)'].idxmin()
row_min_t = df_quimica.loc[idx_min_t]
dt_min_t = row_min_t['DATA_HORA_DT'].strftime('%d/%m/%Y')

# Maior e Menor Ruído
idx_max_db = df_fisica['DB'].idxmax()
row_max_db = df_fisica.loc[idx_max_db]
dt_max_db = row_max_db['DATA_HORA_DT'].strftime('%d/%m/%Y')

idx_min_db = df_fisica['DB'].idxmin()
row_min_db = df_fisica.loc[idx_min_db]
dt_min_db = row_min_db['DATA_HORA_DT'].strftime('%d/%m/%Y')

ce1.metric(
    label='🌡️ Maior Temp. Absoluta',
    value=f"{row_max_t['ÁREA']} • {row_max_t['LOCAL'].title()}",
    delta=f"{row_max_t['TEMPERATURA (°C)']:.1f} °C ({dt_max_t})",
    delta_color='normal',
)

ce2.metric(
    label='🧊 Menor Temp. Absoluta',
    value=f"{row_min_t['ÁREA']} • {row_min_t['LOCAL'].title()}",
    delta=(
        f"{row_min_t['TEMPERATURA (°C)']:.1f} °C ({dt_min_t})"
    ),  # Sinal negativo gera 1 seta ↓
    delta_color='inverse',  # Deixa verde
)

ce3.metric(
    label='🔊 Maior Pico de Som',
    value=f"{row_max_db['ÁREA']} • {row_max_db['LOCAL'].title()}",
    delta=f"{row_max_db['DB']:.1f} dB ({dt_max_db})",
    delta_color='normal',
)

ce4.metric(
    label='🔕 Menor Ruído Absoluto',
    value=f"{row_min_db['ÁREA']} • {row_min_db['LOCAL'].title()}",
    delta=(
        f"{row_min_db['DB']:.1f} dB ({dt_min_db})"
    ),  # Sinal negativo gera 1 seta ↓
    delta_color='inverse',  # Deixa verde
)

st.write('---')

# =========================================================
# 4. FILTROS E CONFIGURAÇÕES DOS GRÁFICOS
# =========================================================
with st.expander('⚙️ **Filtros e Configurações dos Gráficos**', expanded=True):
  col1, col2 = st.columns([1, 1])

  min_data = min(
      df_fisica['DATA_HORA_DT'].min(), df_quimica['DATA_HORA_DT'].min()
  ).date()
  max_data = max(
      df_fisica['DATA_HORA_DT'].max(), df_quimica['DATA_HORA_DT'].max()
  ).date()

  with col1:
    periodo = st.date_input(
        '🗓️ Período das Medições:',
        value=(min_data, max_data),
        min_value=min_data,
        max_value=max_data,
        format='DD/MM/YYYY',
    )

    areas_selecionadas = st.multiselect(
        '📍 Áreas Exibidas:',
        options=ORDEM_AREAS,
        default=['Área 1', 'Área 2', 'Área 3', 'Área 4', 'Área 5', 'Área 6'],
    )

  with col2:
    col_g1, col_g2 = st.columns(2)
    with col_g1:
      tipo_grafico = st.selectbox(
          '📊 Tipo de Gráfico:',
          options=[
              '📈 Linha (Evolução Temporal)',
              '📍 Dispersão (Pontos/Scatter)',
              '📦 Boxplot (Distribuição por Área)',
              '📊 Barras (Média por Área)',
          ],
          index=0,
      )
    with col_g2:
      modo_visao = st.radio(
          '👁️ Disposição:',
          options=['Sobreposto', 'Separado por Área'],
          index=0,
          horizontal=True,
      )

    agrupar_linha_diario = st.checkbox(
        '🧹 Agrupar Linhas por Média Diária (Linhas limpas e retas)',
        value=True,
        help='Mantenha ativado para simplificar os pontos do mesmo dia.',
    )

# Processar datas selecionadas
if isinstance(periodo, (list, tuple)) and len(periodo) == 2:
  data_inicio, data_fim = periodo
else:
  data_inicio, data_fim = min_data, max_data

# Filtragem dos dataframes aplicando filtros do topo e da barra lateral
df_fisica_filtrado = df_fisica[
    (df_fisica['DATA_HORA_DT'].dt.date >= data_inicio)
    & (df_fisica['DATA_HORA_DT'].dt.date <= data_fim)
    & (df_fisica['ÁREA'].isin(areas_selecionadas))
    & (df_fisica['DB'] >= filtro_db[0])
    & (df_fisica['DB'] <= filtro_db[1])
].copy()

df_quimica_filtrado = df_quimica[
    (df_quimica['DATA_HORA_DT'].dt.date >= data_inicio)
    & (df_quimica['DATA_HORA_DT'].dt.date <= data_fim)
    & (df_quimica['ÁREA'].isin(areas_selecionadas))
    & (df_quimica['TEMPERATURA (°C)'] >= filtro_temp[0])
    & (df_quimica['TEMPERATURA (°C)'] <= filtro_temp[1])
].copy()


# -------------------------
# GERADOR DE GRÁFICOS OTIMIZADO
# -------------------------
def gerar_grafico_otimizado(df, col_valor, titulo, label_valor):
  df_plot = df.copy()

  is_facet = modo_visao == 'Separado por Área'
  facet_col = 'ÁREA' if is_facet else None
  facet_wrap = 3 if is_facet else 0

  # 1. LINHA
  if tipo_grafico == '📈 Linha (Evolução Temporal)':
    if agrupar_linha_diario:
      df_plot['DATA_DIA'] = df_plot['DATA_HORA_DT'].dt.floor('D')
      df_plot = (
          df_plot.groupby(['ÁREA', 'DATA_DIA'], observed=False)[col_valor]
          .mean()
          .reset_index()
      )
      df_plot = df_plot.rename(columns={'DATA_DIA': 'DATA_HORA_DT'})

    df_plot = df_plot.sort_values(['ÁREA', 'DATA_HORA_DT']).reset_index(
        drop=True
    )

    fig = px.line(
        df_plot,
        x='DATA_HORA_DT',
        y=col_valor,
        color='ÁREA',
        facet_col=facet_col,
        facet_col_wrap=facet_wrap,
        markers=True,
        title=titulo,
        labels={'DATA_HORA_DT': 'Data', col_valor: label_valor},
        color_discrete_map=CORES_AREAS,
        template='plotly_dark',
    )
    fig.update_traces(
        line=dict(width=2.5, shape='linear'), marker=dict(size=7)
    )

  # 2. DISPERSÃO
  elif tipo_grafico == '📍 Dispersão (Pontos/Scatter)':
    df_plot = df_plot.sort_values(['ÁREA', 'DATA_HORA_DT']).reset_index(
        drop=True
    )
    fig = px.scatter(
        df_plot,
        x='DATA_HORA_DT',
        y=col_valor,
        color='ÁREA',
        facet_col=facet_col,
        facet_col_wrap=facet_wrap,
        opacity=0.8,
        title=titulo,
        labels={'DATA_HORA_DT': 'Data e Horário', col_valor: label_valor},
        color_discrete_map=CORES_AREAS,
        template='plotly_dark',
    )
    fig.update_traces(marker=dict(size=8))

  # 3. BOXPLOT
  elif tipo_grafico == '📦 Boxplot (Distribuição por Área)':
    fig = px.box(
        df_plot,
        x='ÁREA',
        y=col_valor,
        color='ÁREA',
        points='all',
        title=titulo,
        labels={col_valor: label_valor},
        color_discrete_map=CORES_AREAS,
        template='plotly_dark',
    )
    fig.update_traces(boxmean='sd')

  # 4. BARRAS
  elif tipo_grafico == '📊 Barras (Média por Área)':
    df_bar = (
        df_plot.groupby('ÁREA', observed=False)[col_valor].mean().reset_index()
    )
    fig = px.bar(
        df_bar,
        x='ÁREA',
        y=col_valor,
        color='ÁREA',
        text_auto='.1f',
        title=f'Média de {label_valor} por Área',
        labels={col_valor: f'Média de {label_valor}'},
        color_discrete_map=CORES_AREAS,
        template='plotly_dark',
    )

  # ESTILIZAÇÃO FINAL
  fig.update_layout(
      margin=dict(l=20, r=20, t=50, b=30),
      height=500 if not is_facet else 650,
      hovermode='closest' if is_facet else 'x unified',
      legend=dict(
          orientation='h', yanchor='bottom', y=1.02, xanchor='center', x=0.5
      ),
  )

  if tipo_grafico in [
      '📈 Linha (Evolução Temporal)',
      '📍 Dispersão (Pontos/Scatter)',
  ]:
    fig.update_xaxes(
        tickformat='%d/%m', showgrid=True, gridwidth=0.1, dtick='86400000.0'
    )

  return fig


# =========================================================
# 5. ABAS DA MATÉRIA (FÍSICA OU QUÍMICA)
# =========================================================
tab_fisica, tab_quimica = st.tabs(
    ['🎧 Física (Ruído)', '🌡️ Química (Temperatura)']
)

with tab_fisica:
  if df_fisica_filtrado.empty:
    st.warning(
        'Nenhum dado encontrado para os filtros selecionados (área, data ou'
        ' limites de dB).'
    )
  else:
    c1, c2, c3, c4 = st.columns(4)
    c1.metric('Média', f"{df_fisica_filtrado['DB'].mean():.1f} dB")
    c2.metric('Mediana', f"{df_fisica_filtrado['DB'].median():.1f} dB")
    c3.metric('Menor Ruído', f"{df_fisica_filtrado['DB'].min():.1f} dB")
    c4.metric('Pico de Ruído', f"{df_fisica_filtrado['DB'].max():.1f} dB")

    fig_f = gerar_grafico_otimizado(
        df_fisica_filtrado, 'DB', 'Evolução de Ruído (dB)', 'Ruído (dB)'
    )
    st.plotly_chart(fig_f, use_container_width=True)

    with st.expander('📄 **Ver Tabela de Dados Brutos (Física)**', expanded=False):
      colunas_f = [
          col
          for col in ['DATA', 'HORÁRIO', 'LOCAL', 'ÁREA', 'DB MAX - MIN', 'DB']
          if col in df_fisica_filtrado.columns
      ]
      st.dataframe(
          df_fisica_filtrado[colunas_f],
          use_container_width=True,
          hide_index=True,
      )

with tab_quimica:
  if df_quimica_filtrado.empty:
    st.warning(
        'Nenhum dado encontrado para os filtros selecionados (área, data ou'
        ' limites de °C).'
    )
  else:
    c1, c2, c3, c4 = st.columns(4)
    c1.metric(
        'Média', f"{df_quimica_filtrado['TEMPERATURA (°C)'].mean():.1f} °C"
    )
    c2.metric(
        'Mediana', f"{df_quimica_filtrado['TEMPERATURA (°C)'].median():.1f} °C"
    )
    c3.metric(
        'Menor Temp.', f"{df_quimica_filtrado['TEMPERATURA (°C)'].min():.1f} °C"
    )
    c4.metric(
        'Maior Temp.', f"{df_quimica_filtrado['TEMPERATURA (°C)'].max():.1f} °C"
    )

    fig_q = gerar_grafico_otimizado(
        df_quimica_filtrado,
        'TEMPERATURA (°C)',
        'Evolução Térmica (°C)',
        'Temperatura (°C)',
    )
    st.plotly_chart(fig_q, use_container_width=True)

    with st.expander('📄 **Ver Tabela de Dados Brutos (Química)**', expanded=False):
      colunas_q = [
          col
          for col in ['DATA', 'HORÁRIO', 'LOCAL', 'ÁREA', 'TEMPERATURA (°C)']
          if col in df_quimica_filtrado.columns
      ]
      st.dataframe(
          df_quimica_filtrado[colunas_q],
          use_container_width=True,
          hide_index=True,
      )
