import streamlit as st
import pandas as pd
import numpy as np

# 1. Configuración de página
st.set_page_config(
    page_title="Dashboard de Fraude",
    page_icon="🚨",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 2. Carga optimizada de datos usando caché
@st.cache_data
def load_data():
    # Lee el archivo CSV que está al mismo nivel que este script
    df = pd.read_csv("TEF_chile.csv")
    return df

try:
    df = load_data()
except FileNotFoundError:
    st.error("🚨 No se encontró el archivo 'TEF_chile.csv'. Asegúrate de guardarlo en la misma carpeta.")
    st.stop()

# 3. Encabezado principal
st.title("📊 Dashboard de Situación Actual: Control de Fraude")
st.markdown("Este panel interactivo presenta el estado de los indicadores clave de negocio y el impacto del fraude, basado en las transacciones registradas.")
st.markdown("---")

# 4. Procesamiento de KPIs
total_tx = len(df)
fraudes = df[df['is_fraud'] == 1]
legitimos = df[df['is_fraud'] == 0]

casos_fraude = len(fraudes)
perdidas_totales = fraudes['amount'].sum()
tasa_fraude = (casos_fraude / total_tx) * 100 if total_tx > 0 else 0
ticket_promedio_leg = legitimos['amount'].mean() if len(legitimos) > 0 else 0
ticket_promedio_fraud = fraudes['amount'].mean() if casos_fraude > 0 else 0

# 5. Sección 1: Impacto Financiero
st.subheader("💰 1. Impacto Financiero y Situación Actual")
col1, col2, col3, col4 = st.columns(4)

col1.metric("Pérdidas Totales (CLP)", f"${perdidas_totales:,.0f}")
col2.metric("Casos de Fraude", f"{casos_fraude:,.0f}", f"{tasa_fraude:.2f}% (Tasa general)", delta_color="inverse")
col3.metric("Ticket Promedio Legítimo", f"${ticket_promedio_leg:,.0f}")
col4.metric("Ticket Promedio Fraude", f"${ticket_promedio_fraud:,.0f}")

st.markdown("---")

# 6. Sección 2 y 3: Gráficos de Análisis de Pérdidas y Tipos de Fraude
col_chart1, col_chart2 = st.columns(2)

with col_chart1:
    st.subheader("📉 2. Pérdidas por Tipo de Transacción")
    if casos_fraude > 0:
        # Agrupar las pérdidas (sum(amount)) por cada tipo de transacción
        perdidas_tx = fraudes.groupby('transaction_type')['amount'].sum().reset_index()
        perdidas_tx = perdidas_tx.sort_values(by='amount', ascending=False)
        perdidas_tx.set_index('transaction_type', inplace=True)
        st.bar_chart(perdidas_tx)
    else:
        st.info("No hay transacciones fraudulentas registradas.")

with col_chart2:
    st.subheader("🚨 3. Tipos de Fraude Más Frecuentes")
    if casos_fraude > 0:
        # Contar casos por cada tipo de fraude ignorando 'none'
        tipos_fraude = fraudes[fraudes['fraud_type'] != 'none'].groupby('fraud_type').size().reset_index(name='Casos')
        tipos_fraude = tipos_fraude.sort_values(by='Casos', ascending=False)
        tipos_fraude.set_index('fraud_type', inplace=True)
        st.bar_chart(tipos_fraude)
    else:
        st.info("No hay datos de tipos de fraude.")

st.markdown("---")

# 7. Detalles (Tabla) y Conclusiones en Sidebar
st.subheader("📄 Registro de Transacciones Fraudulentas (Muestra)")
if casos_fraude > 0:
    st.dataframe(fraudes[['transaction_id', 'timestamp', 'transaction_type', 'fraud_type', 'amount']].head(100), use_container_width=True)

st.sidebar.header("🔑 Conclusiones Inmediatas")
st.sidebar.info("1. **Atención a Transferencias:** Más de un tercio de las pérdidas se fugan por transferencias directas.")
st.sidebar.warning("2. **Educación al Cliente:** La mayoría del fraude ocurre porque el cliente es engañado o su dispositivo es vulnerado. Reforzar 2FA.")
