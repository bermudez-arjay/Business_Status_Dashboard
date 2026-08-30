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
    st.error("No se encontró el archivo 'TEF_chile.csv'. Asegúrate de guardarlo en la misma carpeta.")
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
st.title("Dashboard Integral de Control de Fraude")
st.caption("Estado actual de indicadores clave de negocio e impacto operativo basado en transacciones registradas.")
st.markdown("---")

# Segmentar datos
total_tx = len(df)
fraudes = df[df['is_fraud'] == 1]
legitimos = df[df['is_fraud'] == 0]
casos_fraude = len(fraudes)

# --- CREACIÓN DE PESTAÑAS (TABS) ---
tab1, tab2, tab3, tab4 = st.tabs([
    " 1. Impacto Financiero", 
    " 2. Análisis Temporal", 
    " 3. Riesgo de Cuenta",
    " 4. Análisis Geográfico"
])

# ==========================================
# PESTAÑA 1: IMPACTO FINANCIERO (Tu código original)
# ==========================================
with tab1:
    perdidas_totales = fraudes['amount'].sum()
    tasa_fraude = (casos_fraude / total_tx * 100) if total_tx > 0 else 0
    ticket_promedio_leg = legitimos['amount'].mean() if len(legitimos) > 0 else 0
    ticket_promedio_fraud = fraudes['amount'].mean() if casos_fraude > 0 else 0

    st.subheader("Situación Actual y KPIs")
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

    col_chart1, col_chart2 = st.columns(2)

    with col_chart1:
        st.subheader("Pérdidas Monetarias por Canal")
        if casos_fraude > 0:
            perdidas_tx = fraudes.groupby('transaction_type')['amount'].sum().reset_index()
            perdidas_tx = perdidas_tx.sort_values(by='amount', ascending=True)
            
            fig_bar = px.bar(
                perdidas_tx, x='amount', y='transaction_type', orientation='h',
                labels={'amount': 'Monto Perdido (CLP)', 'transaction_type': 'Tipo de Transacción'},
                text_auto=',.0f', color='amount', color_continuous_scale='Reds'
            )
            fig_bar.update_layout(showlegend=False, height=380, margin=dict(l=10, r=10, t=20, b=10), xaxis_title=None, yaxis_title=None)
            fig_bar.update_traces(texttemplate='$%{x:,.0f}', textposition='outside')
            st.plotly_chart(fig_bar, use_container_width=True)
        else:
            st.info("No hay transacciones fraudulentas para los filtros seleccionados.")

    with col_chart2:
        st.subheader("Distribución por Tipología de Fraude")
        if casos_fraude > 0:
            tipos_fraude = fraudes[fraudes['fraud_type'] != 'none'].groupby('fraud_type').size().reset_index(name='Casos')
            
            fig_donut = px.pie(
                tipos_fraude, names='fraud_type', values='Casos', hole=0.5,
                color_discrete_sequence=px.colors.sequential.RdBu
            )
            fig_donut.update_traces(textposition='inside', textinfo='percent+label')
            fig_donut.update_layout(showlegend=False, height=380, margin=dict(l=10, r=10, t=20, b=10))
            st.plotly_chart(fig_donut, use_container_width=True)
        else:
            st.info("No hay datos de tipos de fraude disponibles.")

    st.markdown("---")
    st.subheader("Registro de Transacciones Fraudulentas")
    if casos_fraude > 0:
        st.dataframe(
            fraudes[['transaction_id', 'timestamp', 'transaction_type', 'fraud_type', 'amount']]
            .head(100)
            .style.format({'amount': '${:,.0f} CLP'}),
            use_container_width=True, height=300
        )

# ==========================================
# PESTAÑA 2: ANÁLISIS TEMPORAL
# ==========================================
with tab2:
    st.subheader("Evolución del Fraude por Hora del Día")
    if casos_fraude > 0:
        df['hora'] = df['timestamp'].dt.hour
        fraude_hora = df[df['is_fraud'] == 1].groupby('hora').size().reset_index(name='Casos')
        
        fig_hora = px.line(
            fraude_hora, x='hora', y='Casos', markers=True, 
            title="Frecuencia de Fraude a lo largo del día",
            labels={'hora': 'Hora del Día (0-23)', 'Casos': 'Número de Casos'},
            color_discrete_sequence=['#EF4444']
        )
        fig_hora.update_xaxes(dtick=1)
        st.plotly_chart(fig_hora, use_container_width=True)
    else:
        st.info("No hay datos suficientes.")
        
    st.markdown("---")
    st.subheader("⏳ Desviación del Comportamiento Habitual (Monto vs Promedio Últimos 7 Días)")
    if casos_fraude > 0:
        fig_scatter = px.scatter(
            fraudes, x='avg_amount_last_7d', y='amount', color='fraud_type',
            title="Monto de la Transacción Fraudulenta vs. Promedio Histórico del Cliente",
            labels={'avg_amount_last_7d': 'Monto Promedio 7 Días (CLP)', 'amount': 'Monto Transacción (CLP)'},
            opacity=0.7
        )
        # Añadir línea de referencia 1:1
        fig_scatter.add_shape(type="line", x0=0, y0=0, x1=fraudes['avg_amount_last_7d'].max(), y1=fraudes['avg_amount_last_7d'].max(), line=dict(color="White", dash="dash"))
        st.plotly_chart(fig_scatter, use_container_width=True)

# ==========================================
# PESTAÑA 3: RIESGO DE CUENTA
# ==========================================
with tab3:
    col_riesgo1, col_riesgo2 = st.columns(2)
    
    with col_riesgo1:
        st.subheader("Fraude tras Cambios en la Cuenta")
        if casos_fraude > 0:
            cambios = fraudes.groupby('sender_recent_account_changes').size().reset_index(name='Casos')
            fig_cambios = px.bar(
                cambios, x='sender_recent_account_changes', y='Casos',
                title="Casos de Fraude según Cambio de Datos Reciente",
                labels={'sender_recent_account_changes': 'Tipo de Cambio', 'Casos': 'Casos de Fraude'},
                color='Casos', color_continuous_scale='Reds'
            )
            st.plotly_chart(fig_cambios, use_container_width=True)
            
    with col_riesgo2:
        st.subheader("Incidencia de Canales de Comunicación (Ingeniería Social)")
        if casos_fraude > 0:
            canales = fraudes.groupby('sender_communication_channel_flag').size().reset_index(name='Casos')
            fig_canales = px.bar(
                canales, x='sender_communication_channel_flag', y='Casos',
                title="Alertas de Canales de Comunicación",
                labels={'sender_communication_channel_flag': 'Canal/Alerta', 'Casos': 'Casos de Fraude'},
                color_discrete_sequence=['#F59E0B']
            )
            st.plotly_chart(fig_canales, use_container_width=True)

# ==========================================
# PESTAÑA 4: ANÁLISIS GEOGRÁFICO (Con Mapa)
# ==========================================
with tab4:
    st.subheader("📍 Geolocalización y Dispersión de Transacciones")
    st.markdown("Mapa de ubicación del emisor diferenciando las transacciones legítimas de los fraudes en tiempo real.")
    
    if casos_fraude > 0:
        # Usamos px.scatter_map (o compatibilidad con Plotly moderno)
        try:
            fig_map = px.scatter_map(
                df,
                lat="sender_location_lat",
                lon="sender_location_lon",
                color="is_fraud",
                color_discrete_map={0: "#3B82F6", 1: "#EF4444"},
                size="amount",
                hover_name="fraud_type",
                hover_data={
                    "amount": ":$,.0f CLP",
                    "distance_from_home": ":.1f km",
                    "is_fraud": True,
                    "sender_location_lat": False,
                    "sender_location_lon": False
                },
                zoom=3,
                center={"lat": -35.6751, "lon": -71.5430}, # Centrado en Chile
                map_style="carto-darkmatter", # Estilo oscuro
                title="Distribución Geográfica del Emisor (Rojo = Fraude | Azul = Legítimo)"
            )
        except AttributeError:
            # Fallback si estás ejecutando una versión previa de Plotly (v5.x)
            fig_map = px.scatter_mapbox(
                df,
                lat="sender_location_lat",
                lon="sender_location_lon",
                color="is_fraud",
                color_discrete_map={0: "#3B82F6", 1: "#EF4444"},
                size="amount",
                hover_name="fraud_type",
                hover_data={
                    "amount": ":$,.0f CLP",
                    "distance_from_home": ":.1f km",
                    "is_fraud": True,
                    "sender_location_lat": False,
                    "sender_location_lon": False
                },
                zoom=3,
                center={"lat": -35.6751, "lon": -71.5430},
                mapbox_style="carto-darkmatter",
                title="Distribución Geográfica del Emisor (Rojo = Fraude | Azul = Legítimo)"
            )
        
        fig_map.update_layout(
            height=500,
            margin=dict(l=0, r=0, t=40, b=0)
        )
        st.plotly_chart(fig_map, use_container_width=True)
        
        st.markdown("---")
        
        # Histograma Complementario
        st.subheader("📏 Distribución de Distancia al Domicilio")
        fig_dist = px.histogram(
            df, 
            x='distance_from_home', 
            color='is_fraud', 
            barmode='overlay',
            labels={'distance_from_home': 'Distancia al Domicilio (km)', 'is_fraud': 'Es Fraude'},
            color_discrete_map={0: '#3B82F6', 1: '#EF4444'},
            opacity=0.7
        )
        fig_dist.update_layout(yaxis_type="log", height=350)
        st.plotly_chart(fig_dist, use_container_width=True)
        
    else:
        st.info("No hay datos geográficos suficientes para mostrar.")
