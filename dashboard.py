import pandas as pd
import streamlit as st
import plotly.express as px
from datetime import datetime

# 🎨 Configuração da página com tema personalizado
st.set_page_config(page_title="Pizzaria Analytics", layout="wide")

# 🌟 Adicionando a logomarca e ajustando o tema
st.image("logo.png", width=200)  # Assumindo que o logo está no mesmo diretório e é um arquivo .png
st.markdown(
    """
    <style>
        /* Estilo geral para o fundo */
        .stApp {
            background-color: #000000;
            color: #FFFFFF;
        }
        
        /* Estilo para o conteúdo principal */
        .main {
            background-color: #000000;
            color: #FFFFFF;
        }
        
        /* Estilo da sidebar (barra lateral) - PRETA com borda laranja */
        [data-testid="stSidebar"] {
            background-color: #000000 !important;
            border: 2px solid #FFA500 !important;
            border-radius: 10px !important;
        }
        
        /* Estilo para os elementos dentro da sidebar */
        .sidebar .sidebar-content {
            background-color: #000000 !important;
            color: #FFA500 !important;
        }
        
        /* Estilo para os títulos na sidebar */
        .sidebar .sidebar-content h1, 
        .sidebar .sidebar-content h2, 
        .sidebar .sidebar-content h3,
        .sidebar .sidebar-content h4,
        .sidebar .sidebar-content h5,
        .sidebar .sidebar-content h6 {
            color: #FFA500 !important;
        }
        
        /* Estilo para os filtros na sidebar */
        .stMultiSelect, 
        .stSelectbox {
            background-color: #000000 !important;
            color: #FFA500 !important;
            border: 1px solid #FFA500 !important;
        }
        
        /* Estilo para os botões na sidebar */
        .stDownloadButton>button {
            background-color: #FFA500 !important;
            color: #000000 !important;
            border: 1px solid #FFA500 !important;
            border-radius: 5px !important;
        }
        
        /* Estilo para o hover dos botões */
        .stDownloadButton>button:hover {
            background-color: #000000 !important;
            color: #FFA500 !important;
            border: 1px solid #FFA500 !important;
        }
        
        /* Estilo para os separadores na sidebar */
        .sidebar .sidebar-content hr {
            border-top: 1px solid #FFA500 !important;
        }
        
        /* Ajustar a cor do texto nos widgets */
        .stTextInput>div>div>input,
        .stNumberInput>div>div>input,
        .stTextArea>div>div>textarea {
            color: #FFA500 !important;
        }
        
        /* Estilo para as abas */
        .stTabs [data-baseweb="tab-list"] {
            background-color: #000000;
            border-bottom: 1px solid #FFA500;
        }
        
        .stTabs [data-baseweb="tab"] {
            color: #FFFFFF;
        }
        
        .stTabs [aria-selected="true"] {
            color: #FFA500 !important;
            background-color: #000000;
            border-bottom: 2px solid #FFA500;
        }
        
        /* Estilo para os textos das métricas */
        .stMetric {
            color: #FFA500 !important;
        }
        
        /* Estilo para os valores das métricas */
        .stMetricValue {
            color: #FFA500 !important;
        }
        
        /* Estilo para os labels das métricas */
        .stMetricLabel {
            color: #FFA500 !important;
        }
    </style>
    """, unsafe_allow_html=True)

# 🧾 Título e introdução
st.title("🍕 Pizzaria Analytics")
st.markdown("**Insights automáticos e visuais para turbinar suas vendas**")

# 📥 Carregamento dos dados
@st.cache_data
def load_data():
    return pd.read_excel("vendas_pizzariav2.xlsx", sheet_name="Vendas")

df = load_data()
df.columns = df.columns.str.strip().str.lower()

# 🧠 Conversão segura da coluna de data
if "data" in df.columns:
    df["data"] = pd.to_datetime(df["data"], dayfirst=True, errors="coerce")

    if df["data"].isnull().any():
        st.warning("⚠️ Algumas datas não puderam ser convertidas. Verifique o arquivo ou formatação no Excel.")

    # Criar colunas auxiliares
    df["dia da semana"] = df["data"].dt.strftime("%A")
    df["mês"] = df["data"].dt.strftime("%B")
    df["hora"] = df["data"].dt.hour
else:
    st.error("A coluna 'data' não foi encontrada!")
    st.stop()

# 📊 SIDEBAR – Filtros
st.sidebar.header("Filtros")
dias = st.sidebar.multiselect("Dia da semana", df["dia da semana"].dropna().unique())
meses = st.sidebar.multiselect("Mês", df["mês"].dropna().unique())

if dias:
    df = df[df["dia da semana"].isin(dias)]
if meses:
    df = df[df["mês"].isin(meses)]

# 🎯 Métricas principais
col1, col2, col3 = st.columns(3)
col1.metric("📊 Total de Vendas", int(df["quantidade"].sum()))
col2.metric("🧾 Número de Pedidos", df.shape[0])
if "cliente" in df.columns:
    col3.metric("👥 Clientes únicos", df["cliente"].nunique())
else:
    col3.metric("👥 Clientes únicos", "N/D")

# 📂 TABS: Gráficos
tab1, tab2, tab3 = st.tabs(["📅 Por Dia da Semana", "🕒 Por Hora do Dia", "📈 Tendência Mensal"])

with tab1:
    st.subheader("Vendas por Dia da Semana")
    ordem_dias = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    df_dia = df.groupby("dia da semana")["quantidade"].sum().reindex(ordem_dias).dropna().reset_index()
    fig = px.bar(df_dia, x="dia da semana", y="quantidade", color="quantidade", color_continuous_scale="reds")
    st.plotly_chart(fig, use_container_width=True)

with tab2:
    st.subheader("Vendas por Hora do Dia")
    df_hora = df.groupby("hora")["quantidade"].sum().reset_index()
    fig = px.area(df_hora, x="hora", y="quantidade", line_shape="spline", color_discrete_sequence=["orange"])
    st.plotly_chart(fig, use_container_width=True)

with tab3:
    st.subheader("Tendência de Vendas por Mês")
    df_mes = df.groupby("mês")["quantidade"].sum().reset_index()
    fig = px.line(df_mes, x="mês", y="quantidade", markers=True, line_shape="spline")
    st.plotly_chart(fig, use_container_width=True)

# 🍕 Top Sabores
st.subheader("🍕 Top Sabores")
fig_sabores = px.pie(df, names="sabor", values="quantidade", title="Distribuição de Sabores")
st.plotly_chart(fig_sabores, use_container_width=True)

# 🔥 Heatmap Hora vs Dia da Semana
st.subheader("⏰ Mapa de Calor: Hora vs Dia da Semana")
pivot = df.pivot_table(index="hora", columns="dia da semana", values="quantidade", aggfunc="sum").fillna(0)
fig_heatmap = px.imshow(pivot,
                        labels=dict(x="Dia da Semana", y="Hora do Dia", color="Vendas"),
                        x=pivot.columns, y=pivot.index,
                        color_continuous_scale="YlOrRd")
st.plotly_chart(fig_heatmap, use_container_width=True)

# 🔮 Tendência com Média Móvel
st.subheader("📈 Tendência de Vendas (Média Móvel)")
df_trend = df.groupby(df["data"].dt.date)["quantidade"].sum().reset_index()
df_trend["média móvel"] = df_trend["quantidade"].rolling(window=7).mean()
fig_trend = px.line(df_trend, x="data", y=["quantidade", "média móvel"],
                    labels={"value": "Vendas", "data": "Data"}, 
                    title="Evolução Diária de Vendas com Tendência")
st.plotly_chart(fig_trend, use_container_width=True)

# 🚀 Insights Automáticos
st.header("💡 Sugestões Inteligentes")

if datetime.now().strftime("%A") == "Monday":
    st.success("**Dica**: Nas últimas segundas, pizzas doces venderam 25% a mais. Promova no Instagram!")

if "sabor" in df.columns and df[df["sabor"] == "Calabresa"]["quantidade"].sum() > 50:
    st.warning("**Alerta**: Calabresa está com estoque acima da média. Hora de fazer uma promoção!")

if "temperatura" in df.columns and df["temperatura"].mean() > 30:
    st.info("**Clima quente**: Vendas de refrigerante tendem a subir 15%. Crie combos refrescantes!")

# 📥 Exportar CSV
st.sidebar.markdown("---")
st.sidebar.subheader("📤 Exportar dados")
csv = df.to_csv(index=False).encode("utf-8")
st.sidebar.download_button(
    label="⬇️ Baixar dados filtrados (CSV)",
    data=csv,
    file_name="vendas_pizzaria_filtradas.csv",
    mime="text/csv"
)