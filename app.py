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
from tools import get_flag_img_cached, upload_profile_picture, registrar_usuario
from io import BytesIO
#import textwrap
#import streamlit.components.v1 as components
from sections.inicio import render_inicio
from sections.mis_pronosticos import render_mis_pronosticos
from sections.jugadores import render_jugadores
#from sections.laboratorio import render_laboratorio
from sections.foro import render_foro

from PIL import Image
import streamlit as st

icono_app = Image.open("https://storage.googleapis.com/foto-prode2026/Banners/ICONOAPP.png")

# --- CONFIGURACIÓN DE PÁGINA ---

st.set_page_config(
    page_title="Prode Mundial 2026",
    page_icon=icono_app,
    layout="wide",
    initial_sidebar_state="expanded"
)

st.logo(
    "https://storage.googleapis.com/foto-prode2026/Banners/ICONOAPP.png",
    icon_image="assets/ICONOAPP.png"
)

# # --- CONFIGURACIÓN DE PÁGINA ---
# st.set_page_config(
#     page_title="Prode Mundial 2026", 
#     page_icon="https://storage.googleapis.com/foto-prode2026/Banners/ICONOAPP.png", 
#     layout="wide"
# )

# --- CONEXIÓN ---
# Conexión única
conn = st.connection("gsheets", type=GSheetsConnection)
# Carga maestra (Llama a nuestro nuevo módulo)
df_res, df_usuarios, df_pro, mapa_banderas = cargar_todo(conn)

if df_res is None:
    st.stop() # Si falla la carga, detenemos la app con el error del módulo

# --- 2. CONFIGURACIÓN DINÁMICA (Desde GSheets) ---
# 1. Definimos valores por defecto (Si algo falla, la web queda abierta por seguridad)
estado_mantenimiento = "OFF"
estado_registro_manual = "ON"

try:
    # Leemos la pestaña CONFIG
    df_config = conn.read(worksheet="CONFIG", ttl=0)
    
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
    if not st.session_state['mostrar_registro']:
        if st.session_state['registro_exitoso']:
            st.success("✅ ¡Registro completado! Ya puedes ingresar.")
            
        with st.form("login_form"):
            st.subheader("🔐 Iniciar Sesión")
            u = st.text_input("Usuario")
            p = st.text_input("Contraseña", type="password")
            
            if st.form_submit_button("Entrar", use_container_width=True):
                # Normalización para ignorar mayúsculas
                user_match = df_usuarios[
                    (df_usuarios['USUARIO'].astype(str).str.lower() == u.lower().strip()) & 
                    (df_usuarios['CONTRASEÑA'].astype(str) == str(p))
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
                        exito, mensaje = registrar_usuario(conn, r_n, r_u, r_p, AVATAR_GENERICO, r_f)
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
# 3. EJECUCIÓN
# =============================================================================
# Asegúrate de que df_usuarios, df_pro y df_res estén cargados antes
df_ranking = obtener_ranking_global(df_usuarios, df_pro, df_res)

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
        "📝 Mis Pronósticos",
        "👥 Jugadores",
        "💬 Foro"#,
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
        conn=conn
    )

#---------- MENU MIS PRONOSTICOS (CÓDIGO CORREGIDO Y COMPLETO) ----------------------------------

elif menu == "📝 Mis Pronósticos":
    render_mis_pronosticos(
        df_res=df_res,
        df_usuarios=df_usuarios,
        df_pro=df_pro,
        df_ranking=df_ranking,
        mapa_banderas=mapa_banderas,
        conn=conn
    )

# ---------- MENU JUGADORES ----------------------------------------------------
elif menu == "👥 Jugadores":

    df_foro = conn.read(
    worksheet="FORO",
    ttl=60
    )
    
    if df_foro is None:
        df_foro = pd.DataFrame()
        
    render_jugadores(
        df_usuarios=df_usuarios,
        df_ranking=df_ranking,
        df_pro=df_pro,
        df_res=df_res,
        df_foro=df_foro
    )
       
# ---------- MENU FORO (DISEÑO OPTIMIZADO) ----------------------------------------------------

elif menu == "💬 Foro":
    render_foro(
        conn=conn,
        df_usuarios=df_usuarios
    )

# ---------- PANEL DE CONTROL------------------------

        
elif menu == "⚙️ Panel Control":
    # --- VALIDACIÓN DE SEGURIDAD ---
    if st.session_state['user_data']['ROL'] == 'admin':
        
        # 1. COLUMNA PRINCIPAL (Gestión Profesional - 72 Partidos)
        with col_principal:
            st.subheader("⚽ Gestión de Jornada (72 Partidos)")
            
            df_res_admin = conn.read(worksheet="RESULTADOS", ttl=5)
            
            with st.form("form_admin_master_72"):
                # --- SOLUCIÓN AL TYPEERROR ---
                # Convertimos VIZ a objeto para que acepte cualquier texto sin chillar
                df_to_update = df_res_admin.copy()
                df_to_update['VIZ'] = df_to_update['VIZ'].astype(object)
                
                t1, t2, t3 = st.tabs(["Fase 1", "Fase 2", "Fase 3"])
                
                def renderizar_bloque(df_grupo, contenedor):
                    with contenedor:
                        for idx_df, row in df_grupo.iterrows():
                            id_p = int(row['N_PARTIDO'])
                            r1_curr = int(row['R1']) if pd.notna(row['R1']) else 0
                            r2_curr = int(row['R2']) if pd.notna(row['R2']) else 0
                            
                            # Normalización de visibilidad para el toggle
                            viz_act = str(row['VIZ']).strip().upper() in ['TRUE', '1', '1.0', 'VERDADERO']

                            st.markdown(f"**P{id_p}:** {row['Equipo_1']} vs {row['Equipo_2']}")
                            c1, c_vs, c2, c_viz = st.columns([1, 0.2, 1, 1.2])
                            
                            with c1:
                                r1_val = st.number_input(f"G1_{id_p}", 0, 20, r1_curr, key=f"r1_{id_p}", label_visibility="collapsed")
                            with c_vs:
                                st.write("<div style='text-align:center; padding-top:5px;'>:</div>", unsafe_allow_html=True)
                            with c2:
                                r2_val = st.number_input(f"G2_{id_p}", 0, 20, r2_curr, key=f"r2_{id_p}", label_visibility="collapsed")
                            with c_viz:
                                viz_val = st.toggle("Visible", value=viz_act, key=f"viz_{id_p}")
                                finalizado = st.checkbox("Fin", value=pd.notna(row['R1']), key=f"fin_{id_p}")

                            # Actualización segura
                            df_to_update.at[idx_df, 'R1'] = r1_val if finalizado else None
                            df_to_update.at[idx_df, 'R2'] = r2_val if finalizado else None
                            # Guardamos como string puro para máxima compatibilidad con el resto de la app
                            df_to_update.at[idx_df, 'VIZ'] = "TRUE" if viz_val else "FALSE"
                            st.markdown("---")

                # Renderizamos los 3 bloques
                renderizar_bloque(df_to_update.iloc[0:24], t1)
                renderizar_bloque(df_to_update.iloc[24:48], t2)
                renderizar_bloque(df_to_update.iloc[48:72], t3)

                # Botón de envío alineado correctamente
                submit = st.form_submit_button("💾 GUARDAR LOS 72 PARTIDOS", use_container_width=True)
                
                if submit:
                    try:
                        conn.update(worksheet="RESULTADOS", data=df_to_update)
                        st.cache_data.clear()
                        st.success("✅ ¡Los 72 partidos han sido actualizados!")
                        st.balloons()
                        st.rerun()
                    except Exception as e:
                        st.error(f"❌ Error al conectar: {e}")



        # 2. COLUMNA DERECHA (Auditoría y Usuarios)
        with col_derecha:
            # --- DENTRO DEL PANEL DE CONTROL (col_derecha) ---
            st.subheader("🚫 Control de Inscripciones")
            
            # 1. Leemos el estado manual actual desde la tabla CONFIG
            # Asumiendo que tu tabla CONFIG tiene una columna 'REGISTRO' con valor 'ON' u 'OFF'
            df_config = conn.read(worksheet="CONFIG", ttl=10)
            estado_manual = df_config.iloc[0]['REGISTRO']
            
            # 2. Lógica combinada (Fecha + Manual)
            if registro_permitido_fecha and estado_manual == "ON":
                st.success("✅ Inscripciones ABIERTAS")
                
                if st.button("🔴 CERRAR REGISTRO MANUALMENTE", use_container_width=True):
                    # Creamos el nuevo DataFrame para actualizar
                    df_config.at[0, 'REGISTRO'] = "OFF"
                    conn.update(worksheet="CONFIG", data=df_config)
                    st.cache_data.clear()
                    st.success("Registro cerrado con éxito")
                    st.rerun()
            else:
                st.error("⛔ Inscripciones CERRADAS")
                
                # Solo mostramos el botón de abrir si aún estamos dentro de la fecha válida
                if registro_permitido_fecha:
                    if st.button("🟢 ABRIR REGISTRO MANUALMENTE", use_container_width=True):
                        df_config.at[0, 'REGISTRO'] = "ON"
                        conn.update(worksheet="CONFIG", data=df_config)
                        st.cache_data.clear()
                        st.success("Registro abierto con éxito")
                        st.rerun()
                else:
                    st.warning("No se puede abrir manualmente: ya pasó la fecha límite (07/06).")

           #----------CONTROL DE CARGAS------------------      
            st.subheader("🕵️ Auditoría de Cargas")
            
            # 1. Contamos cuántos partidos cargó cada usuario
            conteo_pro = df_pro['USUARIO'].value_counts().reset_index()
            conteo_pro.columns = ['USUARIO', 'COMPLETADOS']
            
            # 2. Cruzamos con la lista de usuarios
            df_auditoria = pd.merge(df_usuarios[['USUARIO', 'NOMBRE']], conteo_pro, on='USUARIO', how='left').fillna(0)
            
            # 3. Función de estado
            def estado_carga(cant):
                if cant >= 24: return "✅ Listo"
                if cant > 0: return f"⚠️ Incompleto ({int(cant)})"
                return "❌ No empezó"
    
            df_auditoria['ESTADO'] = df_auditoria['COMPLETADOS'].apply(estado_carga)
            
            # 4. Mostrar Auditoría
            st.dataframe(df_auditoria[['NOMBRE', 'ESTADO']], use_container_width=True, hide_index=True)
            
            if st.button("📢 Escrachar colgados en el Foro"):
                faltantes = df_auditoria[df_auditoria['COMPLETADOS'] < 24]['NOMBRE'].tolist()
                if faltantes:
                    msg_escrache = f"🚨 ATENCIÓN: Faltan completar pronósticos: {', '.join(faltantes)}. ¡El 8/6 se cierra!"
                    st.warning("Copia esto al foro: " + msg_escrache)
                else:
                    st.success("¡Todos los jugadores están al día! 👏")

            st.markdown("---")
            st.subheader("👥 Gestión de Usuarios")
            df_users_adm = conn.read(worksheet="USUARIOS", ttl=10)
            df_pro_adm = conn.read(worksheet="PRONOSTICOS", ttl=10)

            usuarios_borrables = df_users_adm[df_users_adm['USUARIO'] != st.session_state['user_data']['USUARIO']]
            
            if usuarios_borrables.empty:
                st.info("No hay otros usuarios para gestionar.")
            else:
                user_a_eliminar = st.selectbox(
                    "Selecciona un jugador para eliminar:", 
                    usuarios_borrables['USUARIO'].tolist(),
                    index=None,
                    placeholder="Elegir usuario..."
                )

                if user_a_eliminar:
                    st.warning(f"⚠️ Estás por borrar a **{user_a_eliminar}**.")
                    confirmado = st.checkbox("Confirmo borrar usuario y sus pronósticos", key="conf_borrar")
                    
                    if st.button("❌ BORRAR PERMANENTEMENTE", type="primary", use_container_width=True, disabled=not confirmado):
                        df_users_final = df_users_adm[df_users_adm['USUARIO'] != user_a_eliminar]
                        df_pro_final = df_pro_adm[df_pro_adm['USUARIO'] != user_a_eliminar]
                        
                        conn.update(worksheet="USUARIOS", data=df_users_final)
                        conn.update(worksheet="PRONOSTICOS", data=df_pro_final)
                        
                        st.cache_data.clear()
                        st.success(f"✅ {user_a_eliminar} eliminado.")
                        st.rerun()

            # --- SECCIÓN DE MANTENIMIENTO ---
            st.markdown("---")
            st.subheader("🚧 Mantenimiento")
            # (Aquí debes asegurarte de que 'estado_mantenimiento' esté definido arriba)
            if 'estado_mantenimiento' in locals() or 'estado_mantenimiento' in globals():
                if estado_mantenimiento == "ON":
                    st.error("WEB BLOQUEADA")
                    if st.button("✅ ABRIR WEB"):
                        conn.update(worksheet="CONFIG", data=pd.DataFrame({"MANTENIMIENTO": ["OFF"]}))
                        st.cache_data.clear()
                        st.rerun()
                else:
                    st.success("WEB ACTIVA")
                    if st.button("🚫 CERRAR WEB"):
                        conn.update(worksheet="CONFIG", data=pd.DataFrame({"MANTENIMIENTO": ["ON"]}))
                        st.cache_data.clear()
                        st.rerun()
    
    else:
        # Este else ahora sí corresponde al IF inicial de ROL == 'admin'
        st.error("⛔ No tienes permisos para acceder a esta sección.")


# elif menu == "🧪 Laboratorio":
#     render_laboratorio(
#         df_usuarios=df_usuarios,
#         df_ranking=df_ranking
#     )

