import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

# 1. Configuración de página
st.set_page_config(
    page_title="Dashboard de Fraude",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Estilo CSS personalizado para tarjetas y métricas
st.markdown("""
    <style>
    .metric-card {
        background-color: #1E293B;
        padding: 18px;
        border-radius: 10px;
        border-left: 5px solid #EF4444;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
    }
    .metric-title {
        font-size: 0.85rem;
        color: #94A3B8;
        font-weight: 600;
        text-transform: uppercase;
    }
    .metric-value {
        font-size: 1.6rem;
        font-weight: 700;
        color: #F8FAFC;
        margin-top: 5px;
    }
    .metric-sub {
        font-size: 0.8rem;
        color: #F87171;
        margin-top: 3px;
    }
    </style>
""", unsafe_allow_html=True)

# 2. Carga optimizada de datos usando caché
@st.cache_data
def load_data():
    df = pd.read_csv("TEF_chile.csv")
    if 'timestamp' in df.columns:
        df['timestamp'] = pd.to_datetime(df['timestamp'])
    return df

try:
    df_raw = load_data()
except FileNotFoundError:
    st.error(" No se encontró el archivo 'TEF_chile.csv'. Asegúrate de guardarlo en la misma carpeta.")
    st.stop()

# 3. Sidebar: Filtros Interactivos y Conclusiones
st.sidebar.header("🔍 Filtros de Análisis")

# Filtro por tipo de transacción
tx_types = ["Todos"] + list(df_raw['transaction_type'].dropna().unique())
selected_tx = st.sidebar.selectbox("Tipo de Transacción", tx_types)

# Filtrado dinámico
df = df_raw.copy()
if selected_tx != "Todos":
    df = df[df['transaction_type'] == selected_tx]

st.sidebar.markdown("---")
st.sidebar.header("Conclusiones Inmediatas")
st.sidebar.info("1. **Atención a Transferencias:** Más de un tercio de las pérdidas se fugan por transferencias directas.")
st.sidebar.warning("2. **Educación al Cliente:** La mayoría del fraude ocurre porque el cliente es engañado o su dispositivo es vulnerado. Reforzar 2FA.")

# 4. Encabezado principal
st.title("📊 Dashboard de Control de Fraude")
st.caption("Estado actual de indicadores clave de negocio e impacto operativo basado en transacciones registradas.")
st.markdown("---")

# 5. Procesamiento de KPIs
total_tx = len(df)
fraudes = df[df['is_fraud'] == 1]
legitimos = df[df['is_fraud'] == 0]

casos_fraude = len(fraudes)
perdidas_totales = fraudes['amount'].sum()
tasa_fraude = (casos_fraude / total_tx * 100) if total_tx > 0 else 0
ticket_promedio_leg = legitimos['amount'].mean() if len(legitimos) > 0 else 0
ticket_promedio_fraud = fraudes['amount'].mean() if casos_fraude > 0 else 0

# 6. Sección 1: Impacto Financiero (KPIs estilizados)
st.subheader(" 1. Impacto Financiero y Situación Actual")
c1, c2, c3, c4 = st.columns(4)

c1.markdown(f"""
    <div class="metric-card">
        <div class="metric-title">Pérdidas Totales</div>
        <div class="metric-value">${perdidas_totales:,.0f} CLP</div>
    </div>
""", unsafe_allow_html=True)

c2.markdown(f"""
    <div class="metric-card">
        <div class="metric-title">Casos de Fraude</div>
        <div class="metric-value">{casos_fraude:,.0f}</div>
        <div class="metric-sub">Tasa: {tasa_fraude:.2f}% del total</div>
    </div>
""", unsafe_allow_html=True)

c3.markdown(f"""
    <div class="metric-card" style="border-left-color: #10B981;">
        <div class="metric-title">Ticket Prom. Legítimo</div>
        <div class="metric-value">${ticket_promedio_leg:,.0f} CLP</div>
    </div>
""", unsafe_allow_html=True)

c4.markdown(f"""
    <div class="metric-card">
        <div class="metric-title">Ticket Prom. Fraude</div>
        <div class="metric-value">${ticket_promedio_fraud:,.0f} CLP</div>
    </div>
""", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# 7. Sección 2: Visualizaciones Avanzadas (Plotly Express)
col_chart1, col_chart2 = st.columns(2)

with col_chart1:
    st.subheader("📉 Pérdidas Monetarias por Canal")
    if casos_fraude > 0:
        perdidas_tx = fraudes.groupby('transaction_type')['amount'].sum().reset_index()
        perdidas_tx = perdidas_tx.sort_values(by='amount', ascending=True)
        
        fig_bar = px.bar(
            perdidas_tx,
            x='amount',
            y='transaction_type',
            orientation='h',
            labels={'amount': 'Monto Perdido (CLP)', 'transaction_type': 'Tipo de Transacción'},
            text_auto=',.0f',
            color='amount',
            color_continuous_scale='Reds'
        )
        fig_bar.update_layout(
            showlegend=False,
            height=380,
            margin=dict(l=10, r=10, t=20, b=10),
            xaxis_title=None,
            yaxis_title=None
        )
        fig_bar.update_traces(texttemplate='$%{x:,.0f}', textposition='outside')
        st.plotly_chart(fig_bar, use_container_width=True)
    else:
        st.info("No hay transacciones fraudulentas para los filtros seleccionados.")

with col_chart2:
    st.subheader("🚨 Distribución por Tipología de Fraude")
    if casos_fraude > 0:
        tipos_fraude = fraudes[fraudes['fraud_type'] != 'none'].groupby('fraud_type').size().reset_index(name='Casos')
        
        fig_donut = px.pie(
            tipos_fraude,
            names='fraud_type',
            values='Casos',
            hole=0.5,
            color_discrete_sequence=px.colors.sequential.RdBu
        )
        fig_donut.update_traces(textposition='inside', textinfo='percent+label')
        fig_donut.update_layout(
            showlegend=False,
            height=380,
            margin=dict(l=10, r=10, t=20, b=10)
        )
        st.plotly_chart(fig_donut, use_container_width=True)
    else:
        st.info("No hay datos de tipos de fraude disponibles.")

st.markdown("---")

# 8. Registro de Transacciones Fraudulentas
st.subheader("📄 Registro de Transacciones Fraudulentas")
if casos_fraude > 0:
    st.dataframe(
        fraudes[['transaction_id', 'timestamp', 'transaction_type', 'fraud_type', 'amount']]
        .head(100)
        .style.format({'amount': '${:,.0f} CLP'}),
        use_container_width=True,
        height=300
    )
else:
    st.info("Sin registros de fraude bajo los criterios seleccionados.")
