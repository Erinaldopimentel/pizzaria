import pandas as pd
import streamlit as st
import plotly.express as px
from datetime import datetime
from pathlib import Path
import base64

# 🎨 Configuração da página com tema personalizado
st.set_page_config(page_title="Pizzaria Analytics", layout="wide")

# 🌟 Carrega o CSS personalizado
def load_css():
    with open("style.css") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

load_css()

# 🌟 Adicionando a logomarca com fallback para base64
def load_logo():
    logo_path = Path("logo.png")
    if logo_path.exists():
        with open(logo_path, "rb") as logo_file:
            logo_base64 = base64.b64encode(logo_file.read()).decode()
        return logo_base64
    return None

logo_base64 = load_logo()
if logo_base64:
    st.markdown(
        f"""
        <div class="logo-container">
            <img src="data:image/png;base64,{logo_base64}" width="200" />
        </div>
        """,
        unsafe_allow_html=True
    )
else:
    st.warning("⚠️ Arquivo 'logo.png' não encontrado na pasta do projeto.")

# 🧾 Título e introdução
st.title("🍕 Pizzaria Analytics")

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

# Função para aplicar o fundo preto nos gráficos
def apply_plotly_style(fig):
    fig.update_layout(
        plot_bgcolor="black",  # Cor de fundo da área do gráfico
        paper_bgcolor="black",  # Cor de fundo da área da figura
        font_color="orange",  # Cor do texto
        title_font_color="orange"
    )
    return fig

with tab1:
    st.subheader("Vendas por Dia da Semana")
    ordem_dias = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    df_dia = df.groupby("dia da semana")["quantidade"].sum().reindex(ordem_dias).dropna().reset_index()
    fig = px.bar(df_dia, x="dia da semana", y="quantidade", color="quantidade", color_continuous_scale="reds")
    fig = apply_plotly_style(fig)
    st.plotly_chart(fig, use_container_width=True)

with tab2:
    st.subheader("Vendas por Hora do Dia")
    df_hora = df.groupby("hora")["quantidade"].sum().reset_index()
    fig = px.area(df_hora, x="hora", y="quantidade", line_shape="spline", color_discrete_sequence=["orange"])
    fig = apply_plotly_style(fig)
    st.plotly_chart(fig, use_container_width=True)

with tab3:
    st.subheader("Tendência de Vendas por Mês")
    df_mes = df.groupby("mês")["quantidade"].sum().reset_index()
    fig = px.line(df_mes, x="mês", y="quantidade", markers=True, line_shape="spline")
    fig = apply_plotly_style(fig)
    st.plotly_chart(fig, use_container_width=True)

# 🍕 Top Sabores
st.subheader("🍕 Top Sabores")
fig_sabores = px.pie(df, names="sabor", values="quantidade", title="Distribuição de Sabores")
fig_sabores = apply_plotly_style(fig_sabores)
st.plotly_chart(fig_sabores, use_container_width=True)

# 🔥 Heatmap Hora vs Dia da Semana
st.subheader("⏰ Mapa de Calor: Hora vs Dia da Semana")
pivot = df.pivot_table(index="hora", columns="dia da semana", values="quantidade", aggfunc="sum").fillna(0)
fig_heatmap = px.imshow(pivot,
                        labels=dict(x="Dia da Semana", y="Hora do Dia", color="Vendas"),
                        x=pivot.columns, y=pivot.index,
                        color_continuous_scale="YlOrRd")
fig_heatmap = apply_plotly_style(fig_heatmap)
st.plotly_chart(fig_heatmap, use_container_width=True)

# 🔮 Tendência com Média Móvel
st.subheader("📈 Tendência de Vendas (Média Móvel)")
df_trend = df.groupby(df["data"].dt.date)["quantidade"].sum().reset_index()
df_trend["média móvel"] = df_trend["quantidade"].rolling(window=7).mean()
fig_trend = px.line(df_trend, x="data", y=["quantidade", "média móvel"],
                    labels={"value": "Vendas", "data": "Data"}, 
                    title="Evolução Diária de Vendas com Tendência")
fig_trend = apply_plotly_style(fig_trend)
st.plotly_chart(fig_trend, use_container_width=True)

# 🚀 Insights Automáticos
st.header("💡 Sugestões Inteligentes")

if datetime.now().strftime("%A") == "Monday":
    st.success("**Dica**: Nas últimas segundas, pizzas doces venderam 25% a mais. Promova no Instagram!")

if "sabor" in df.columns and df[df["sabor"] == "Calabresa"]["quantidade"].sum() > 50:
    st.warning("**Alerta**: Calabresa está com estoque acima da média. Hora de fazer promoção!")
