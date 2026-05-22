import streamlit as st
import pandas as pd
#import plotly.express as px
from streamlit_gsheets import GSheetsConnection
from data_manager import cargar_todo
from datetime import datetime, timedelta
from google.auth.transport.requests import Request
from googleapiclient.http import MediaIoBaseUpload
from ranking_logic import obtener_ranking_global, calcular_detalle
from styles_config import (
    aplicar_estilos_globales,
    mostrar_decalogo,
    AVATAR_GENERICO,
    HEADER_BACKGROUND,
    EVOL_HEADER_BACKGROUND
)
from styles_config import dibujar_banner
from tools import get_flag_img_cached, upload_profile_picture
from io import BytesIO
#import textwrap
#import streamlit.components.v1 as components
from sections.inicio import render_inicio
from sections.mis_pronosticos import render_mis_pronosticos
from sections.jugadores import render_jugadores
#from sections.laboratorio import render_laboratorio
from sections.foro import render_foro
from sections.reglas import render_reglas
from sections.panel_control import render_panel_control

from PIL import Image
import streamlit as st
import streamlit.components.v1 as components
from services.supabase_service import (
    get_resultados_supabase,
    get_usuarios_supabase,
    get_pronosticos_supabase,
    get_resultados_app,
    get_usuarios_app,
    get_pronosticos_app,
    get_foro_app,
    get_noticias_app,
    guardar_pronosticos_supabase,
    registrar_usuario_supabase
)


# 1. DEFINE LA URL DE TU BUCKET (La usaremos en ambos lados)
URL_ICONO = "https://storage.googleapis.com/foto-prode2026/Banners/ICONOAPP2.png"

# 2. CONFIGURACIÓN DE PÁGINA (¡SIEMPRE DEBE IR PRIMERO!)
st.set_page_config(
    page_title="Prode Mundial 2026",
    page_icon=URL_ICONO,  # Pasamos la URL directamente, es más rápido que PIL
    layout="wide",
    initial_sidebar_state="expanded"
)
# --- CONEXIÓN ---
conn = st.connection("gsheets", type=GSheetsConnection)

def leer_sheet_seguro(conn, worksheet, ttl=300):
    try:
        df = conn.read(
            worksheet=worksheet,
            ttl=ttl
        )

        if df is None:
            return pd.DataFrame()

        return df

    except Exception as e:
        st.warning(
            f"No se pudo cargar temporalmente la hoja {worksheet}. "
            "Probá nuevamente en unos minutos."
        )
        return pd.DataFrame()


# ============================================================
# DATOS PRINCIPALES DESDE SUPABASE
# ============================================================

df_res = get_resultados_app()
df_usuarios = get_usuarios_app()
df_pro = get_pronosticos_app()

if df_res is None or df_res.empty:
    st.error("No se pudieron cargar los resultados desde Supabase.")
    st.stop()

# ============================================================
# MAPA DE BANDERAS
# Antes venía desde cargar_todo(conn).
# Ahora lo reconstruimos desde df_res.
# ============================================================

equipos_1 = (
    df_res["Equipo_1"]
    .dropna()
    .astype(str)
    .tolist()
    if "Equipo_1" in df_res.columns
    else []
)

equipos_2 = (
    df_res["Equipo_2"]
    .dropna()
    .astype(str)
    .tolist()
    if "Equipo_2" in df_res.columns
    else []
)

equipos_unicos = sorted(
    set(equipos_1 + equipos_2)
)

mapa_banderas = {}

for equipo in equipos_unicos:
    equipo = str(equipo).strip()

    if equipo == "" or equipo.lower() == "nan":
        continue

    try:
        bandera = get_flag_img_cached(equipo)

        if bandera is None or str(bandera).strip() == "":
            bandera = "⚽"

        mapa_banderas[equipo] = bandera

    except Exception:
        mapa_banderas[equipo] = "⚽"

# --- 2. CONFIGURACIÓN DINÁMICA (Desde GSheets) ---
# 1. Definimos valores por defecto (Si algo falla, la web queda abierta por seguridad)
estado_mantenimiento = "OFF"
estado_registro_manual = "ON"

try:
    # Leemos la pestaña CONFIG
    df_config = conn.read(worksheet="CONFIG", ttl=60)
    
    # Validamos que las columnas existan antes de asignar
    if "MANTENIMIENTO" in df_config.columns:
        estado_mantenimiento = str(df_config["MANTENIMIENTO"].iloc[0]).strip().upper()
    if "REGISTRO" in df_config.columns:
        estado_registro_manual = str(df_config["REGISTRO"].iloc[0]).strip().upper()
except Exception as e:
    # Si falla la lectura de CONFIG, avisamos en consola pero usamos los valores por defecto
    print(f"Aviso: Usando configuración por defecto debido a: {e}")

# --- 3. LÓGICA DE TIEMPOS ---
ahora_arg = datetime.now() - timedelta(hours=3)
fecha_limite_reg = datetime(2026, 6, 7, 23, 59, 59)
registro_permitido_fecha = ahora_arg < fecha_limite_reg
    
# --- 3. FILTRO DE ACCESO (PROTECCIÓN) ---
# Ahora 'estado_mantenimiento' existe sí o sí
if estado_mantenimiento == "ON":
    # Verificamos si el usuario es admin (usando .get para evitar errores si no hay sesión)
    is_admin = st.session_state.get('user_data', {}).get('ROL') == 'admin'
    
    if not is_admin:
        st.title("🏆 Prode Mundial 2026")
        st.warning("⚠️ Mantenimiento en curso. Estamos realizando ajustes técnicos. ¡Volvemos pronto!")
        st.info("Solo el Administrador tiene acceso en este momento.")
        if st.button("🚪 Reintentar / Login Admin"):
            st.rerun()
        st.stop() 

# --- LÓGICA DE INTERFAZ (LOGIN / REGISTRO) --------------------------------------------------------

if 'autenticado' not in st.session_state:
    st.session_state['autenticado'] = False
if 'mostrar_registro' not in st.session_state:
    st.session_state['mostrar_registro'] = False
if 'registro_exitoso' not in st.session_state:
    st.session_state['registro_exitoso'] = False

if not st.session_state['autenticado']:
    # 1. LEER CONFIGURACIÓN (Solo para no autenticados)
    try:
        df_config = conn.read(worksheet="CONFIG", ttl=0)
        estado_registro_manual = str(df_config["REGISTRO"].iloc[0]).strip().upper()
    except:
        estado_registro_manual = "OFF"

    # --- CASO A: PESTAÑA DE LOGIN ---
# --- CASO A: PESTAÑA DE LOGIN ---
    if not st.session_state['mostrar_registro']:
        if st.session_state['registro_exitoso']:
            st.success("✅ ¡Registro completado! Ya puedes ingresar.")
    
        st.markdown(
            f"""
    <style>
    .login-hero-banner {{
        position: relative;
        overflow: hidden;
    
        min-height: 210px;
        margin: 0 auto 24px auto;
        padding: 28px 22px;
    
        border-radius: 22px;
        border: 1px solid rgba(244,197,66,0.24);
    
        background:
            linear-gradient(
                135deg,
                rgba(7,17,31,0.78),
                rgba(15,23,42,0.45)
            ),
            url("{HEADER_BACKGROUND}");
    
        background-size: cover;
        background-position: center;
        background-repeat: no-repeat;
    
        box-shadow:
            0 18px 42px rgba(15,23,42,0.18),
            inset 0 1px 0 rgba(255,255,255,0.08);
    }}
    
    .login-hero-content {{
        position: relative;
        z-index: 2;
        max-width: 620px;
    }}
    
    .login-hero-kicker {{
        display: inline-block;
    
        margin-bottom: 10px;
        padding: 5px 10px;
    
        border-radius: 999px;
        background: rgba(244,197,66,0.16);
        border: 1px solid rgba(244,197,66,0.28);
    
        color: #F4C542;
        font-family: 'Montserrat', sans-serif;
        font-size: 11px;
        font-weight: 900;
        text-transform: uppercase;
        letter-spacing: 0.08em;
    }}
    
    .login-hero-title {{
        margin: 0 !important;
    
        color: #FFFFFF !important;
        font-family: 'Montserrat', sans-serif !important;
        font-size: 34px !important;
        font-weight: 900 !important;
        line-height: 1.02 !important;
        letter-spacing: -0.04em !important;
    
        text-shadow:
            0 2px 8px rgba(0,0,0,0.85),
            0 0 18px rgba(0,0,0,0.55) !important;
    }}

    .login-hero-banner h1.login-hero-title {{
        color: #FFFFFF !important;
    }}
        
    .login-hero-subtitle {{
        margin-top: 9px;
    
        color: rgba(248,250,252,0.78);
        font-size: 14px;
        font-weight: 700;
        line-height: 1.35;
    
        max-width: 460px;
    }}
    
    @media (max-width: 768px) {{
        .login-hero-banner {{
            min-height: 180px;
            padding: 22px 18px;
            border-radius: 18px;
            margin-bottom: 18px;
        }}
    
        .login-hero-title {{
            font-size: 27px;
        }}
    
        .login-hero-subtitle {{
            font-size: 12px;
        }}
    }}
    </style>
    
    <div class="login-hero-banner">
        <div class="login-hero-content">
            <div class="login-hero-kicker">Prode Mundial 2026</div>
            <h1 class="login-hero-title">La gloria está en tus predicciones</h1>
            <div class="login-hero-subtitle">
                Entrá, cargá tus resultados y peleá la punta con la banda.
            </div>
        </div>
    </div>
    """,
            unsafe_allow_html=True
        )
            
        with st.form("login_form"):
            st.subheader("🔐 Iniciar Sesión")
            u = st.text_input("Usuario")
            p = st.text_input("Contraseña", type="password")
            
            if st.form_submit_button("Entrar", use_container_width=True):
                # Normalización para ignorar mayúsculas
                user_match = df_usuarios[
                    (df_usuarios["USUARIO"].astype(str).str.lower().str.strip() == u.lower().strip()) &
                    (df_usuarios["CONTRASEÑA"].astype(str).str.strip() == str(p).strip())
                ]
                
                if not user_match.empty:
                    st.session_state['autenticado'] = True
                    st.session_state['user_data'] = user_match.iloc[0].to_dict()
                    st.session_state['registro_exitoso'] = False
                    st.rerun()
                else:
                    st.error("Usuario o contraseña incorrectos")

        st.markdown("---")
        # BOTÓN DE REGISTRO: Fuera del formulario y alineado con el 'if not mostrar_registro'
        if st.button("🆕 ¿No tienes cuenta? Regístrate aquí", use_container_width=True):
            if not registro_permitido_fecha:
                st.error("🔒 El período de inscripción finalizó el 07/06/2026.")
            elif estado_registro_manual == "OFF":
                st.error("🚫 Inscripciones cerradas temporalmente por el administrador.")
            elif estado_mantenimiento == "ON":
                st.warning("⚠️ Web en mantenimiento. Intenta más tarde.")
            else:
                st.session_state['mostrar_registro'] = True
                st.rerun()

    # --- CASO B: PESTAÑA DE REGISTRO ---
    else:
        st.subheader("📝 Crear nueva cuenta")
        with st.form("reg_form", clear_on_submit=True):
            r_n = st.text_input("Nombre Completo")
            r_u = st.text_input("Nick de Usuario (para el ranking)")
            r_p = st.text_input("Contraseña", type="password")
            r_f = st.selectbox("Equipo Favorito", ["Argentina", "México", "España", "Brasil", "Uruguay", "Otro"])
            
            # Botón único de envío
            if st.form_submit_button("🚀 FINALIZAR REGISTRO", use_container_width=True):
                # Re-chequeo de seguridad
                if registro_permitido_fecha and estado_registro_manual == "ON":
                    if r_u and r_p and r_n:
                        # Usamos la función del módulo TOOLS
                        exito, mensaje = registrar_usuario_supabase(
                            nombre=r_n,
                            usuario=r_u,
                            contrasena=r_p,
                            avatar_url=AVATAR_GENERICO,
                            equipo_favorito=r_f
                        )
                        if exito:
                            st.session_state['registro_exitoso'] = True
                            st.session_state['mostrar_registro'] = False 
                            st.rerun()
                        else:
                            st.error(mensaje)
                    else:
                        st.error("Por favor completa los campos obligatorios.")
                else:
                    st.error("El registro ya no está disponible.")

        if st.button("⬅️ Volver al Login"):
            st.session_state['mostrar_registro'] = False
            st.rerun()

    st.stop() # Freno para que no cargue el resto de la app sin estar logueado

#---------------------- SI Mantenimiento esta activo ---------------------------
# Usamos 'estado_mantenimiento' que viene del Excel y '.get' para evitar errores de sesión
if estado_mantenimiento == "ON" and st.session_state.get('user_data', {}).get('ROL') != 'admin':
    st.warning("⚠️ Estamos actualizando los servidores para la próxima fecha. ¡Volvemos en unos minutos!")
    st.info("Solo el Administrador tiene acceso en este momento.")
    
    # Detenemos la ejecución para que no vean nada más
    if st.button("🔄 Reintentar"):
        st.rerun()
    st.stop()

aplicar_estilos_globales()


# =============================================================================
# 3. EJECUCIÓN — DATOS COMPARTIDOS
# =============================================================================
# ============================================================
# FORO Y NOTICIAS DESDE SUPABASE
# ============================================================

df_foro = get_foro_app()
df_noticias = get_noticias_app()


if df_foro.empty:
    df_foro = pd.DataFrame(
        columns=[
            "FECHA",
            "USUARIO",
            "NOMBRE",
            "MENSAJE",
            "PARTIDO_ID",
            "LIKES",
            "DISLIKES",
            "FORO_IMG_URL"
        ]
    )

for col in [
    "FECHA",
    "USUARIO",
    "NOMBRE",
    "MENSAJE",
    "PARTIDO_ID",
    "LIKES",
    "DISLIKES",
    "FORO_IMG_URL"
]:
    if col not in df_foro.columns:
        if col in ["LIKES", "DISLIKES", "PARTIDO_ID"]:
            df_foro[col] = 0
        else:
            df_foro[col] = ""


if df_noticias.empty:
    df_noticias = pd.DataFrame(
        columns=[
            "FECHA",
            "TIPO",
            "TITULO",
            "TEXTO",
            "AUTOR",
            "VISIBLE",
            "PRIORIDAD",
            "LINK",
            "IMAGEN_URL",
            "FUENTE"
        ]
    )

for col in [
    "FECHA",
    "TIPO",
    "TITULO",
    "TEXTO",
    "AUTOR",
    "VISIBLE",
    "PRIORIDAD",
    "LINK",
    "IMAGEN_URL",
    "FUENTE"
]:
    if col not in df_noticias.columns:
        if col == "PRIORIDAD":
            df_noticias[col] = 99
        elif col == "VISIBLE":
            df_noticias[col] = "TRUE"
        else:
            df_noticias[col] = ""


df_ranking = obtener_ranking_global(
    df_users=df_usuarios,
    df_pro=df_pro,
    df_res=df_res,
    df_foro=df_foro
)
# ============================================================
# SIDEBAR PREMIUM
# ============================================================

with st.sidebar:

    st.markdown("""
<div class="sidebar-brand">
    <div class="sidebar-brand-title">
        🏆 PRODE<br>
        <span>MUNDIAL 2026</span>
    </div>
    <div class="sidebar-brand-subtitle">
        La gloria está en tus predicciones
    </div>
</div>
""", unsafe_allow_html=True)

    nombre_usuario = st.session_state["user_data"].get("NOMBRE", "Jugador")

    st.markdown(f"""
<div class="sidebar-user-box">
    <div class="sidebar-user-label">Bienvenido</div>
    <div class="sidebar-user-name">{nombre_usuario}</div>
</div>
""", unsafe_allow_html=True)

    st.markdown("""
<div class="sidebar-section-label">
    📍 Navegación
</div>
""", unsafe_allow_html=True)

    opciones = [
        "🏠 Inicio",
        "📝 Mi Prode",
        "👥 Plantel",
        "💬 Comunidad",
        "📜 Reglas del Juego"#,
        #"🧪 Laboratorio"
    ]

    if st.session_state["user_data"]["ROL"] == "admin":
        opciones.append("⚙️ Panel Control")

    menu = st.radio(
        "Ir a:",
        opciones,
        label_visibility="collapsed"
    )

    st.markdown("""
<div class="sidebar-footer">
    <strong>🏆 Prode Mundial 2026</strong><br>
    La gloria está en tus predicciones
</div>
""", unsafe_allow_html=True)

    if st.button("🚪 Cerrar Sesión", use_container_width=True):
        st.session_state["autenticado"] = False
        st.rerun()
#--------------------INICIO-----------------------------------------------------------------------

if menu == "🏠 Inicio":
    render_inicio(
        df_ranking=df_ranking,
        df_usuarios=df_usuarios,
        df_pro=df_pro,
        df_res=df_res,
        mapa_banderas=mapa_banderas,
        conn=conn,
        df_foro=df_foro,
        df_noticias=df_noticias
    )

#---------- MENU MIS PRONOSTICOS (CÓDIGO CORREGIDO Y COMPLETO) ----------------------------------

elif menu == "📝 Mi Prode":
    render_mis_pronosticos(
        df_res=df_res,
        df_usuarios=df_usuarios,
        df_pro=df_pro,
        df_ranking=df_ranking,
        mapa_banderas=mapa_banderas,
        conn=conn
    )

# ---------- MENU JUGADORES ----------------------------------------------------
elif menu == "👥 Plantel":

    render_jugadores(
        df_usuarios=df_usuarios,
        df_ranking=df_ranking,
        df_pro=df_pro,
        df_res=df_res,
        df_foro=df_foro
    )
       
# ---------- MENU FORO (DISEÑO OPTIMIZADO) ----------------------------------------------------
elif menu == "💬 Comunidad":
    render_foro(
        conn=conn,
        df_usuarios=df_usuarios,
        df_ranking=df_ranking,
        df_foro=df_foro,
        df_noticias=df_noticias
    )
# ---------- MENU REGLAS DEL JUEGO ----------------------------------------------------

elif menu == "📜 Reglas del Juego":
    render_reglas()


# ---------- PANEL DE CONTROL ------------------------

elif menu == "⚙️ Panel Control":
    render_panel_control(
        conn=conn,
        df_res=df_res,
        df_usuarios=df_usuarios,
        df_pro=df_pro,
        df_foro=df_foro,
        df_noticias=df_noticias,
        df_ranking=df_ranking,
        registro_permitido_fecha=registro_permitido_fecha,
        estado_mantenimiento=estado_mantenimiento
    )
