import streamlit as st
import pandas as pd
from sqlalchemy import create_engine, text

# 1. Configuración de la página para Móvil
st.set_page_config(page_title="Stats Ventas Vehículos", layout="centered")

# Conexión flexible (Nube o Local)

# 1. Conexión a la base de datos
engine = create_engine(st.secrets["db_url"])

st.title("🚗 Dashboard de Ventas x Modelo")

try:
    # --- PASO 1: Cargar maestros (Nombres de vendedores y vehículos) ---
    # Asumo que tienes una tabla 'vendedores' (id_vendedor, nombre)
    # y una tabla 'vehiculos' (key_vehiculo, modelo_nombre)
    df_vendedores = pd.read_sql("SELECT user_dni, nombre || ' ' || apellido as nombre FROM users ", engine)
    
    # --- PASO 2: Sidebar para filtros ---
    st.sidebar.header("Filtros")
    
    # Selector de Vendedor
    vendedor_dict = dict(zip(df_vendedores['nombre'], df_vendedores['user_dni']))
    nombre_sel = st.sidebar.selectbox("Selecciona Vendedor", options=list(vendedor_dict.keys()))
    id_vendedor_sel = vendedor_dict[nombre_sel]

    # --- PASO 3: Consulta de Ventas filtrada ---
    query = text("""
        SELECT v.fecha, vh.vehiculo_det as vehiculo 
        FROM vtpa_suscs v
        JOIN vtpa_sencom vh ON v.key_vehiculo = vh.nano_id
        WHERE v.id_vendedor = :id
    """)
    df_ventas = pd.read_sql(query, engine.connect(), params={"id": id_vendedor_sel})
    
    if not df_ventas.empty:
        # Preparación de datos temporales
        df_ventas['fecha'] = pd.to_datetime(df_ventas['fecha'])
        df_ventas['mes'] = df_ventas['fecha'].dt.to_period('M').astype(str)

        # --- ESTADÍSTICA 1: Por Mes ---
        st.subheader(f"📅 Ventas Mensuales: {nombre_sel}")
        ventas_mes = df_ventas.groupby('mes').size().reset_index(name='cantidad')
        st.line_chart(ventas_mes.set_index('mes'))

        # --- ESTADÍSTICA 2: Por Vehículo (Key) ---
        # 
        st.subheader("🚘 Ventas por Modelo (Key)")
        ventas_key = df_ventas.groupby('vehiculo').size().sort_values(ascending=False)
        st.bar_chart(ventas_key)

        # --- ESTADÍSTICA 3: Tabla Detallada ---
        with st.expander("Ver lista de ventas"):
            st.dataframe(df_ventas[['fecha', 'vehiculo']].sort_values('fecha', ascending=False))

    else:
        st.info("El vendedor seleccionado no tiene ventas registradas aún.")

except Exception as e:
    st.error(f"Error en la conexión o datos: {e}")
