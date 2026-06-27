import streamlit as st
import pandas as pd

import base64
import hashlib
import hmac
import json
from datetime import datetime, timedelta

from ranking_logic import obtener_ranking_global

from styles_config import (
    aplicar_estilos_globales,
    AVATAR_GENERICO,
    HEADER_BACKGROUND
)

from tools import get_flag_img_cached

from sections.inicio import render_inicio
from sections.inicio_v2 import render_inicio_v2
from sections.mis_pronosticos import render_mis_pronosticos
from sections.mis_pronosticos_v2 import render_mis_pronosticos_v2
from sections.jugadores import render_jugadores
from sections.foro import render_foro
from sections.reglas import render_reglas
from sections.panel_control import render_panel_control

from services.supabase_service import (
    get_resultados_app,
    get_usuarios_app,
    get_pronosticos_app,
    get_foro_app,
    get_noticias_app,
    get_config_app,
    registrar_usuario_supabase
)

try:
    from streamlit_cookies_controller import CookieController
except Exception:
    CookieController = None

# ============================================================
# ARRANQUE GENERAL
# app.py coordina la aplicacion completa:
# 1) carga datos base desde Supabase
# 2) valida configuracion dinamica
# 3) maneja login/registro
# 4) arma el menu lateral y llama a cada pantalla
# ============================================================

# 1. DEFINE LA URL DE TU BUCKET (La usaremos en ambos lados)
URL_ICONO = "https://storage.googleapis.com/foto-prode2026/Banners/ICONOAPP2.png"

# 2. CONFIGURACIÓN DE PÁGINA (¡SIEMPRE DEBE IR PRIMERO!)
st.set_page_config(
    page_title="Prode Mundial 2026",
    page_icon=URL_ICONO,  # Pasamos la URL directamente, es más rápido que PIL
    layout="wide",
    initial_sidebar_state="expanded"
)

AUTH_COOKIE_NAME = "prode_mundial_2026_auth"
AUTH_COOKIE_DAYS = 30


def get_cookie_manager():
    if CookieController is None:
        return None

    return CookieController(key="prode_auth_cookie_manager")


def get_auth_cookie_secret():
    try:
        return str(st.secrets.get("AUTH_COOKIE_SECRET", "")).strip()
    except Exception:
        return ""


def encode_auth_cookie(usuario, secret):
    payload = {
        "usuario": str(usuario),
        "exp": int(
            (datetime.utcnow() + timedelta(days=AUTH_COOKIE_DAYS)).timestamp()
        )
    }
    payload_json = json.dumps(
        payload,
        separators=(",", ":"),
        sort_keys=True
    ).encode("utf-8")
    payload_b64 = base64.urlsafe_b64encode(payload_json).decode("utf-8")
    signature = hmac.new(
        secret.encode("utf-8"),
        payload_b64.encode("utf-8"),
        hashlib.sha256
    ).hexdigest()

    return f"{payload_b64}.{signature}"


def decode_auth_cookie(token, secret):
    try:
        payload_b64, signature = str(token).split(".", 1)
        expected_signature = hmac.new(
            secret.encode("utf-8"),
            payload_b64.encode("utf-8"),
            hashlib.sha256
        ).hexdigest()

        if not hmac.compare_digest(signature, expected_signature):
            return None

        payload_json = base64.urlsafe_b64decode(
            payload_b64.encode("utf-8")
        )
        payload = json.loads(payload_json.decode("utf-8"))

        if int(payload.get("exp", 0)) < int(datetime.utcnow().timestamp()):
            return None

        usuario = str(payload.get("usuario", "")).strip()

        if not usuario:
            return None

        return usuario

    except Exception:
        return None


def restore_session_from_cookie(df_usuarios, cookie_manager, secret):
    if (
        st.session_state.get("autenticado")
        or cookie_manager is None
        or not secret
        or df_usuarios is None
        or df_usuarios.empty
    ):
        return

    token = cookie_manager.get(AUTH_COOKIE_NAME)
    usuario = decode_auth_cookie(token, secret) if token else None

    if not usuario:
        return

    user_match = df_usuarios[
        df_usuarios["USUARIO"].astype(str).str.strip() == usuario
    ]

    if user_match.empty:
        cookie_manager.remove(AUTH_COOKIE_NAME)
        return

    st.session_state["autenticado"] = True
    st.session_state["user_data"] = user_match.iloc[0].to_dict()


def save_auth_cookie(usuario, cookie_manager, secret):
    if cookie_manager is None or not secret:
        return False

    token = encode_auth_cookie(usuario, secret)
    expires_at = datetime.utcnow() + timedelta(days=AUTH_COOKIE_DAYS)
    cookie_manager.set(
        AUTH_COOKIE_NAME,
        token,
        expires=expires_at,
        max_age=AUTH_COOKIE_DAYS * 24 * 60 * 60,
        same_site="lax"
    )

    return True


def clear_auth_cookie(cookie_manager):
    if cookie_manager is not None:
        cookie_manager.remove(AUTH_COOKIE_NAME, same_site="lax")

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

# ============================================================
# CONFIGURACIÓN DINÁMICA DESDE SUPABASE
# ============================================================
# 1. Definimos valores por defecto (Si algo falla, la web queda abierta por seguridad)
estado_mantenimiento = "OFF"
estado_registro_manual = "ON"

try:
    df_config = get_config_app()

    if "MANTENIMIENTO" in df_config.columns:
        estado_mantenimiento = (
            str(df_config["MANTENIMIENTO"].iloc[0])
            .strip()
            .upper()
        )

    if "REGISTRO" in df_config.columns:
        estado_registro_manual = (
            str(df_config["REGISTRO"].iloc[0])
            .strip()
            .upper()
        )

except Exception as e:
    print(f"Aviso: Usando configuración por defecto debido a: {e}")

# --- 3. LÓGICA DE TIEMPOS ---
ahora_arg = datetime.now() - timedelta(hours=3)
fecha_limite_reg = datetime(2026, 7, 20, 23, 59, 59)
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

# ============================================================
# ESTADO DE SESION
# Streamlit vuelve a ejecutar el archivo en cada interaccion.
# Por eso se guardan login, registro y usuario en session_state.
# ============================================================

if 'autenticado' not in st.session_state:
    st.session_state['autenticado'] = False
if 'mostrar_registro' not in st.session_state:
    st.session_state['mostrar_registro'] = False
if 'registro_exitoso' not in st.session_state:
    st.session_state['registro_exitoso'] = False

cookie_manager = get_cookie_manager()
auth_cookie_secret = get_auth_cookie_secret()

if (
    not st.session_state.get("autenticado")
    and cookie_manager is not None
    and auth_cookie_secret
    and not st.session_state.get("auth_cookie_checked")
):
    st.session_state["auth_cookie_checked"] = True
    st.info("Restaurando sesión...")
    st.stop()

restore_session_from_cookie(
    df_usuarios=df_usuarios,
    cookie_manager=cookie_manager,
    secret=auth_cookie_secret
)

if not st.session_state['autenticado']:
    # 1. LEER CONFIGURACIÓN (Solo para no autenticados)
    try:
        df_config = get_config_app()
        estado_registro_manual = (
            str(df_config["REGISTRO"].iloc[0])
            .strip()
            .upper()
        )
    except:
        estado_registro_manual = "OFF"

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
            recordar_login = st.checkbox(
                "Recordarme en este dispositivo",
                value=True,
                disabled=(cookie_manager is None or not auth_cookie_secret)
            )
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

                    if recordar_login:
                        st.session_state["auth_cookie_pending_usuario"] = str(
                            user_match.iloc[0]["USUARIO"]
                        )

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

if st.session_state.get("auth_cookie_pending_usuario"):
    if save_auth_cookie(
        usuario=st.session_state["auth_cookie_pending_usuario"],
        cookie_manager=cookie_manager,
        secret=auth_cookie_secret,
    ):
        st.session_state.pop("auth_cookie_pending_usuario", None)

#---------------------- SI Mantenimiento esta activo ---------------------------
# Usamos estado_mantenimiento desde Supabase y .get para evitar errores de sesión
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

# A partir de aca se dibuja la interfaz para usuarios autenticados.

# ============================================================
# SIDEBAR PREMIUM
# La opcion de Panel Control se agrega solo si el rol es admin.
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

    rol_usuario = str(
        st.session_state.get("user_data", {}).get("ROL", "")
    ).strip().lower()

    opciones = []

    if rol_usuario == "admin":
        opciones.append("Eliminatoria")

    opciones.extend(
        [
            "🏠 Fase de Grupos",
            "📝 Mi Prode",
            "👥 Plantel",
            "💬 Comunidad",
            "📜 Reglas del Juego"
        ]
    )

    if rol_usuario == "admin":
        opciones.append("⚙️ Panel Control")

    if "nav_destino" in st.session_state:
        destino = st.session_state.pop("nav_destino")

        if destino in opciones:
            st.session_state["menu_principal"] = destino

    menu = st.radio(
        "Ir a:",
        opciones,
        label_visibility="collapsed",
        key="menu_principal"
    )

    st.markdown("""
<div class="sidebar-footer">
    <strong>🏆 Prode Mundial 2026</strong><br>
    La gloria está en tus predicciones
</div>
""", unsafe_allow_html=True)

    if st.button("🚪 Cerrar Sesión", use_container_width=True):
        clear_auth_cookie(cookie_manager)
        st.session_state["autenticado"] = False
        st.session_state.pop("user_data", None)
        st.rerun()
# ============================================================
# ROUTER DE PANTALLAS
# Cada opcion del menu llama a una funcion render_* dentro de
# la carpeta sections/.
# ============================================================

if menu == "🏠 Fase de Grupos":
    render_inicio(
        df_ranking=df_ranking,
        df_usuarios=df_usuarios,
        df_pro=df_pro,
        df_res=df_res,
        mapa_banderas=mapa_banderas,
        df_foro=df_foro,
        df_noticias=df_noticias
    )

#---------- MENU MIS PRONOSTICOS (CÓDIGO CORREGIDO Y COMPLETO) ----------------------------------

elif menu == "📝 Mi Prode":
    render_mis_pronosticos_v2(
        df_usuarios=df_usuarios,
        df_ranking=df_ranking,
        mapa_banderas=mapa_banderas
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
        df_usuarios=df_usuarios,
        df_ranking=df_ranking,
        df_foro=df_foro,
        df_noticias=df_noticias
    )
# ---------- MENU REGLAS DEL JUEGO ----------------------------------------------------

elif menu == "📜 Reglas del Juego":
    render_reglas()


# ---------- PANEL DE CONTROL ------------------------

elif menu.endswith("Panel Control"):
    render_panel_control(
        df_res=df_res,
        df_usuarios=df_usuarios,
        df_pro=df_pro,
        df_foro=df_foro,
        df_noticias=df_noticias,
        df_ranking=df_ranking,
        registro_permitido_fecha=registro_permitido_fecha,
        estado_mantenimiento=estado_mantenimiento
    )

elif menu == "Eliminatoria":
    render_inicio_v2(
        usuario_actual=st.session_state.get("user_data", {}).get("USUARIO", ""),
        mapa_banderas=mapa_banderas
    )
