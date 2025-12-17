import streamlit as st
import pandas as pd
from sqlalchemy import create_engine

# Configuración de la página para móviles
st.set_page_config(page_title="Dashboard Ventas", layout="centered")

# 1. Conexión a la base de datos
def conectar_db():
    # Reemplaza con tus credenciales reales
    engine = create_engine('postgresql://jmesca:esme2023d@170.238.127.17:5432/senna')
    return engine

st.title("📊 Reporte de Planes")
st.write("Datos leídos en tiempo real desde PostgreSQL")

try:
    engine = conectar_db()
    
    # 2. Selector de Vendedor (UI Adaptativa)
    vendedores = pd.read_sql("SELECT DISTINCT id_vendedor FROM vtpa_suscs", engine)
    vendedor_sel = st.selectbox("Selecciona un Vendedor", vendedores['vendedor'])

    # 3. Consulta filtrada
    query = f"SELECT fecha, key_vehiculo,valor_cuota FROM ventas_planes WHERE vendedor = '{vendedor_sel}'"
    df = pd.read_sql(query, engine)

    # 4. Métricas rápidas (Se ven geniales en celular)
    col1, col2 = st.columns(2)
    col1.metric("Total Ventas", f"${df['monto'].sum():,.2f}")
    col2.metric("Planes Vendidos", len(df))

    # 5. Gráfico optimizado
    st.subheader("Tendencia")
    st.line_chart(df.set_index('fecha')['monto'])

except Exception as e:
    st.error(f"Error de conexión: {e}")
