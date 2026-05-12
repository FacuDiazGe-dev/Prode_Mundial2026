import streamlit as st
import pandas as pd
from tools import get_flag_img_cached
from styles_config import AVATAR_GENERICO

# --- CONEXIÓN INICIAL ---
# Esta función asegura que el objeto 'conn' esté disponible si se necesita
def get_connection():
    from streamlit_gsheets import GSheetsConnection
    return st.connection("gsheets", type=GSheetsConnection)

@st.cache_data(ttl=300)
def load_static_data(_conn):
    """Carga resultados y usuarios (Refresh cada 5 min)."""
    df_res = conn.read(worksheet="RESULTADOS")
    df_users = conn.read(worksheet="USUARIOS")
    
    # Limpieza de datos
    df_res['R1'] = pd.to_numeric(df_res['R1'], errors='coerce')
    df_res['R2'] = pd.to_numeric(df_res['R2'], errors='coerce')
    return df_res, df_users

@st.cache_data(ttl=60)
def load_dynamic_data(_conn):
    """Carga pronósticos (Refresh cada 1 min)."""
    df_pro = conn.read(worksheet="PRONOSTICOS")
    df_pro['P1'] = pd.to_numeric(df_pro['P1'], errors='coerce')
    df_pro['P2'] = pd.to_numeric(df_pro['P2'], errors='coerce')
    return df_pro

def generar_mapa_banderas(df_res):
    """Crea el diccionario de banderas para optimizar el renderizado."""
    try:
        equipos_unicos = pd.concat([df_res['Equipo_1'], df_res['Equipo_2']]).unique()
        return {eq: get_flag_img_cached(eq) for eq in equipos_unicos}
    except:
        return {}

def cargar_todo(conn):
    """Función maestra para app.py."""
    try:
        df_res, df_usuarios = load_static_data(conn)
        df_pro = load_dynamic_data(conn)
        mapa = generar_mapa_banderas(df_res)
        return df_res, df_usuarios, df_pro, mapa
    except Exception as e:
        st.error(f"Error crítico en la carga de datos: {e}")
        return None, None, None, {}
