import streamlit as st
import pandas as pd
import plotly.express as px
from streamlit_gsheets import GSheetsConnection
from datetime import datetime
from datetime import datetime, timedelta
from google.auth.transport.requests import Request
from googleapiclient.http import MediaIoBaseUpload
from ranking_logic import obtener_ranking_global, calcular_detalle
from styles_config import aplicar_estilos_globales, dibujar_banner, mostrar_decalogo, AVATAR_GENERICO
from tools import get_flag_img_cached, upload_profile_picture
from io import BytesIO

st.set_page_config(page_title="Prode Mundial 2026", layout="wide")
#st.title("🏆 Prode Mundial 2026 - Fase de Grupos")

#--------------FECHA DE FIN DE REGISTRO---------------------        
ahora_arg = datetime.now() - timedelta(hours=3)
fecha_limite_reg = datetime(2026, 6, 7, 23, 59, 59)
registro_permitido_fecha = ahora_arg < fecha_limite_reg


#---------------------------MANTENIMIENTO -  True (Activado)  False (Desactivo)------------------------------------------------------------------
MANTENIMIENTO_ACTIVO = False 
MENSAJE_MANTENIMIENTO = "⚠️ Estamos actualizando los servidores para la próxima fecha. ¡Volvemos en unos minutos!"

# ----LOGIN---
# --- CONEXIÓN ---
conn = st.connection("gsheets", type=GSheetsConnection)

#-----carga de insignias de ranking----


# --- LECTURA DE CONFIGURACIÓN DE MANTENIMIENTO ---
try:
    df_config = conn.read(worksheet="CONFIG", ttl=10)
    # Leemos la celda A2 (primera fila de la columna MANTENIMIENTO)
    estado_mantenimiento = str(df_config["MANTENIMIENTO"].iloc[0]).strip().upper()
except Exception:
    # Si la hoja no existe o falla, por defecto la web queda abierta
    estado_mantenimiento = "OFF"

# --- FILTRO DE ACCESO (PROTECCIÓN) ---
# Este bloque se activa solo si ya hay alguien logueado (para saber si es admin)
if 'user_data' in st.session_state and st.session_state.get('autenticado'):
    if estado_mantenimiento == "ON" and st.session_state['user_data'].get('ROL') != 'admin':
        st.title("🏆 Prode Mundial 2026")
        st.markdown(f"""
            <div style="background-color: #fff3cd; padding: 20px; border-radius: 10px; border-left: 5px solid #ffc107;">
                <h2 style="color: #856404; margin: 0;">⚠️ Estamos en mantenimiento</h2>
                <p style="color: #856404; margin-top: 10px;">Estamos realizando ajustes técnicos para mejorar la estabilidad. ¡Volvemos en unos minutos!</p>
            </div>
        """, unsafe_allow_html=True)
        st.info("Solo el Administrador tiene acceso en este momento.")
        if st.button("🔄 Reintentar acceso"):
            st.rerun()
        st.stop()## FRENO


# --- FUNCIÓN DE REGISTRO BLINDADA -------------------------------------------------------------------------------------
def registrar_usuario(datos_nuevos):
    try:
        # 1. Leer la tabla actual (sin usar caché para ver lo real)
        df_actual = conn.read(worksheet="USUARIOS", ttl=10)
        
        # 2. Limpiar nombres para comparar (evita duplicados por espacios o mayúsculas)
        nuevo_u_clean = str(datos_nuevos["USUARIO"]).strip().lower()
        usuarios_existentes = df_actual["USUARIO"].astype(str).str.strip().str.lower().tolist()
        
        if nuevo_u_clean in usuarios_existentes:
            st.error(f"❌ El usuario '{datos_nuevos['USUARIO']}' ya existe. Elige otro nick.")
            return False

        # 3. Preparar los datos del nuevo usuario
        # ID automático: Si está vacío empieza en 1, sino Max + 1
        nuevo_id = int(df_actual["ID"].max() + 1) if not df_actual.empty else 1
        
        # Creamos un diccionario limpio con el orden exacto de las columnas
        nuevo_registro = {
            "ID": nuevo_id,
            "USUARIO": datos_nuevos["USUARIO"].strip(),
            "CONTRASEÑA": str(datos_nuevos["CONTRASEÑA"]),
            "NOMBRE": datos_nuevos["NOMBRE"].strip(),
            "EDAD": datos_nuevos["EDAD"],
            "EQUIPO FAVORITO": datos_nuevos["EQUIPO FAVORITO"],
            "DESCRIPCION": datos_nuevos["DESCRIPCION"],
            "ROL": "jugador",
            "FECHA_REG": datetime.now().strftime("%d/%m/%Y"),
            "AVATAR_URL": ""
        }
        
        # 4. Concatenar: El nuevo usuario se suma al final del DataFrame actual
        df_para_subir = pd.concat([df_actual, pd.DataFrame([nuevo_registro])], ignore_index=True)
        
        # 5. ACTUALIZAR GOOGLE SHEETS (Sobrescribe la pestaña con la lista actualizada)
        conn.update(worksheet="USUARIOS", data=df_para_subir)
        
        # Limpiamos caché de Streamlit para que la próxima lectura vea al nuevo usuario
        st.cache_data.clear()
        st.success("✅ ¡Usuario creado con éxito!")
        return True

    except Exception as e:
        st.error(f"Error técnico: {e}")
        return False

# --- LÓGICA DE INTERFAZ (LOGIN / REGISTRO) --------------------------------------------------------

if 'autenticado' not in st.session_state:
    st.session_state['autenticado'] = False
if 'mostrar_registro' not in st.session_state:
    st.session_state['mostrar_registro'] = False
if 'registro_exitoso' not in st.session_state:
    st.session_state['registro_exitoso'] = False

if not st.session_state['autenticado']:
    # 1. LEER CONFIGURACIÓN (Dentro del bloque de no autenticados)
    try:
        df_config = conn.read(worksheet="CONFIG", ttl=10)
        estado_registro_manual = df_config.iloc[0]['REGISTRO']
    except:
        estado_registro_manual = "OFF" # Por seguridad, si falla la conexión, bloqueamos

    if not st.session_state['mostrar_registro']:
        
        # --- SECCIÓN DE LOGIN ---
        if st.session_state['registro_exitoso']:
            st.success("✅ ¡Registro completado! Ya puedes ingresar.")
            
        with st.form("login_form"):
            st.subheader("🔐 Iniciar Sesión")
            u = st.text_input("Usuario")
            p = st.text_input("Contraseña", type="password")
            
            if st.form_submit_button("Entrar"):
                # Leemos la base de usuarios
                df_u = conn.read(worksheet="USUARIOS", ttl=10)
                
                # --- NORMALIZACIÓN PARA IGNORAR MAYÚSCULAS/MINÚSCULAS ---
                # Comparamos usuario en minúsculas. La contraseña se mantiene exacta por seguridad.
                user_match = df_u[
                    (df_u['USUARIO'].astype(str).str.lower() == u.lower().strip()) & 
                    (df_u['CONTRASEÑA'].astype(str) == str(p))
                ]
                
                if not user_match.empty:
                    st.session_state['autenticado'] = True
                    # Guardamos los datos de la primera coincidencia encontrada
                    st.session_state['user_data'] = user_match.iloc[0].to_dict()
                    st.session_state['registro_exitoso'] = False
                    st.rerun()
                else:
                    st.error("Usuario o contraseña incorrectos")
                    
                # --- AQUÍ COLOCAS LA LÓGICA DE BLOQUEO ---

        # Botón para ir a registro (fuera del form)
                estado_registro_manual = df_config.iloc[0]['REGISTRO'] 

                if st.button("🆕 ¿No tienes cuenta? Regístrate aquí"):
                    # VALIDACIÓN TRIPLE: Fecha límite + Estado Manual + Mantenimiento
                    if not registro_permitido_fecha:
                        st.error("🔒 El período de inscripción finalizó el 07/06/2026.")
                    elif estado_registro_manual == "OFF":
                        st.error("🚫 El administrador ha cerrado las inscripciones temporalmente.")
                    elif 'estado_mantenimiento' in locals() and estado_mantenimiento == "ON":
                        st.warning("⚠️ Web en mantenimiento. Intenta más tarde.")
                    else:
                        # Si todo está OK, lo dejamos pasar al formulario
                        st.session_state['mostrar_registro'] = True
                        st.session_state['registro_exitoso'] = False
                        st.rerun()
    
    else:
        # --- SECCIÓN DE REGISTRO ---
        st.subheader("📝 Crear nueva cuenta")
        with st.form("reg_form", clear_on_submit=True):
            r_u = st.text_input("Nick de Usuario")
            r_p = st.text_input("Contraseña", type="password")
            r_n = st.text_input("Nombre Completo")
            r_e = st.number_input("Edad", 1, 100, 25)
            r_f = st.selectbox("Equipo Favorito", ["Argentina", "México", "España", "Brasil", "EEUU", "Otro"])
            r_d = st.text_area("Breve descripción")
            
            if st.form_submit_button("Crear mi cuenta"):
                if r_u and r_p and r_n:
                    # Usamos tu función registrar_usuario
                    if registrar_usuario({
                        "USUARIO": r_u, "CONTRASEÑA": r_p, "NOMBRE": r_n,
                        "EDAD": r_e, "EQUIPO FAVORITO": r_f, "DESCRIPCION": r_d
                    }):
                        # TRUCO FINAL: Cambiamos los estados para que al recargar muestre el Login
                        st.session_state['registro_exitoso'] = True
                        st.session_state['mostrar_registro'] = False 
                        st.rerun()
                else:
                    st.error("Completa Usuario, Contraseña y Nombre.")
        
        if st.form_submit_button("Finalizar Registro"):
            # Re-chequeamos antes de guardar en el Excel
            if registro_permitido_fecha and estado_registro_manual == "ON":
                # ... Aquí va tu código actual de guardar usuario ...
                pass 
            else:
                st.error("Lo sentimos, el registro ya no está disponible.")
                st.stop() # Detenemos la ejecución

    st.stop()
#---------------------- SI Mantenimiento esta activo ---------------------------
if MANTENIMIENTO_ACTIVO and st.session_state['user_data']['ROL'] != 'admin':
    st.warning(MENSAJE_MANTENIMIENTO)
    st.info("Solo el Administrador tiene acceso en este momento.")
    
    # Detenemos la ejecución para que no vean nada más
    if st.button("🔄 Reintentar"):
        st.rerun()
    st.stop() 


aplicar_estilos_globales()
dibujar_banner()
# --- SIDEBAR DE BIENVENIDA ---
st.sidebar.write(f"Hola, **{st.session_state['user_data']['NOMBRE']}**")


@st.cache_data(ttl=300) # Los resultados y usuarios se guardan por 5 minutos
def load_static_data():
    # Solo leemos lo que casi no cambia
    df_res = conn.read(worksheet="RESULTADOS")
    df_users = conn.read(worksheet="USUARIOS")
    
    # Limpieza de datos una sola vez
    df_res['R1'] = pd.to_numeric(df_res['R1'], errors='coerce')
    df_res['R2'] = pd.to_numeric(df_res['R2'], errors='coerce')
    return df_res, df_users

@st.cache_data(ttl=60) # Los pronósticos se refrescan cada 1 minuto
def load_dynamic_data():
    df_pro = conn.read(worksheet="PRONOSTICOS")
    df_pro['P1'] = pd.to_numeric(df_pro['P1'], errors='coerce')
    df_pro['P2'] = pd.to_numeric(df_pro['P2'], errors='coerce')
    return df_pro

# Ejecución inteligente
try:
    df_res, df_usuarios = load_static_data()
    df_pro = load_dynamic_data()

    equipos_unicos = pd.concat([df_res['Equipo_1'], df_res['Equipo_2']]).unique()
    mapa_banderas = {eq: get_flag_img_cached(eq) for eq in equipos_unicos}
    
except Exception as e:
    st.warning("⚠️ La conexión con Google es lenta...")
    mapa_banderas = {}

# =============================================================================
# 3. EJECUCIÓN
# =============================================================================
# Asegúrate de que df_usuarios, df_pro y df_res estén cargados antes
df_ranking = obtener_ranking_global(df_usuarios, df_pro, df_res)

# --- NAVEGACIÓN EN SIDEBAR (OPTIMIZADO PARA MÓVILES) ---
# --- ESTRUCTURA PRINCIPAL DE DISEÑO (PROPORCIONES 60/40) ---
col_principal, col_derecha = st.columns([0.6, 0.4])

# 1. NAVEGACIÓN EN EL SIDEBAR (Ideal para móviles y PC)
# --- 1. NAVEGACIÓN EN EL SIDEBAR ---
with st.sidebar:
    st.subheader("📍 Navegación")
    opciones = ["🏠 Inicio", "📝 Mis Pronósticos", "👥 Jugadores", "💬 Foro"]
    if st.session_state['user_data']['ROL'] == 'admin':
        opciones.append("⚙️ Panel Control")
 
        # --- SOLO VISIBLE PARA EL ADMIN ---
    if st.session_state['user_data']['ROL'] == 'admin':
        if st.button("🔄 Sincronizar Datos (Admin)", use_container_width=True):
            st.cache_data.clear()
            st.rerun()

    menu = st.radio("Ir a:", opciones, key="menu_navegacion_unificado")
    
    st.markdown("---")
    # Botón de cerrar sesión
    if st.button("🚪 Cerrar Sesión", use_container_width=True):
        st.session_state['autenticado'] = False
        st.rerun()

# --- LÓGICA DE CONTENIDO SEGÚN EL MENÚ ---
#------------------------------------------------MENU INICIO-----------------------------------------------

if menu == "🏠 Inicio":
    with col_principal:
        st.subheader("⚽ Cronograma y Resultados")
        
        # 1. FILTRADO ULTRA SEGURO DE VIZ (Igual al que usamos en el ranking)
        # Normalizamos la columna para que acepte TRUE, True, 1, etc.
        df_res['VIZ_CHECK'] = df_res['VIZ'].astype(str).str.strip().str.upper()
        
        # Filtramos los partidos que el Admin decidió mostrar
        df_mostrar = df_res[df_res['VIZ_CHECK'].isin(['TRUE', '1', '1.0', 'VERDADERO', 'T'])].sort_values('N_PARTIDO', ascending=False)

        with st.container(height=430):
            if df_mostrar.empty:
                st.info("⚽ ¡Bienvenidos! Los resultados oficiales aparecerán aquí a medida que avance el mundial.")
            else:
                for i, row in df_mostrar.iterrows():
                    # Definición de Goles (Si no hay valor oficial, ponemos un guion)
                    r1 = int(row['R1']) if pd.notna(row['R1']) else "-"
                    r2 = int(row['R2']) if pd.notna(row['R2']) else "-"
                    dia_p = str(row['DIA']) if pd.notna(row['DIA']) else "---"
                    hora_p = str(row['HORA']) if pd.notna(row['HORA']) else "--:--"
                    
                    # Usamos el mapa de banderas optimizado
                    f1 = mapa_banderas.get(row['Equipo_1'], AVATAR_GENERICO)
                    f2 = mapa_banderas.get(row['Equipo_2'], AVATAR_GENERICO)
                    
                    # Color del tema: Azul si ya terminó (tiene goles), Gris si es próximo
                    color_tema = "#007bff" if r1 != "-" else "#6c757d"
                    
                    st.markdown(f"""
                    <div style="border: 1px solid #ddd; border-top: 3px solid {color_tema}; border-radius: 8px; padding: 10px; margin-bottom: 10px; background-color: white;">
                        <div style="display: flex; justify-content: space-between; margin-bottom: 5px; align-items: center;">
                            <span style="font-size: 0.7em; font-weight: bold; color: {color_tema}; text-transform: uppercase;">PARTIDO {int(row['N_PARTIDO'])}</span>
                            <span style="font-size: 0.7em; color: #666; font-weight: bold;">📅 {dia_p} | 🕒 {hora_p}</span>
                        </div>
                        <div style="display: flex; justify-content: space-between; align-items: center;">
                            <div style="width: 35%; text-align: center;">
                                <img src="{f1}" width="28" style="margin-bottom:2px;"><br>
                                <span style="font-weight: bold; font-size: 0.9em; color: #333;">{row['Equipo_1']}</span>
                            </div>
                            <div style="width: 25%; text-align: center; background: #f8f9fa; border-radius: 5px; font-weight: bold; font-size: 1.25em; border: 1px solid #eee; color: #333;">
                                {r1} : {r2}
                            </div>
                            <div style="width: 35%; text-align: center;">
                                <img src="{f2}" width="28" style="margin-bottom:2px;"><br>
                                <span style="font-weight: bold; font-size: 0.9em; color: #333;">{row['Equipo_2']}</span>
                            </div>
                        </div>
                    </div>""", unsafe_allow_html=True)
    
        # --- BLOQUE 2: FORO (Actividad Reciente en el Inicio) ---------------------------------------------------------------------------------------
        st.subheader("💬 En los pasillos de la Villa se comenta")
        
        # 1. CARGA DE DATOS
        df_foro_inicio = conn.read(worksheet="FORO", ttl=10) # ttl=10 para ver mensajes al instante
        df_u_ref = df_usuarios # Usamos el df que ya cargaste al inicio de la app
        user_actual = st.session_state['user_data']['USUARIO']
        
        # 2. CONTENEDOR DE MENSAJES (Scrollable)
        with st.container(height=350):
            if df_foro_inicio.empty:
                st.info("No hay mensajes aún.")
            else:
                # Mostramos los últimos 15 mensajes
                for idx, m in df_foro_inicio.tail(15).iloc[::-1].iterrows():
                    u_match = df_u_ref[df_u_ref['USUARIO'] == m['USUARIO']]
                    foto_url = u_match.iloc[0]['AVATAR_URL'] if not u_match.empty and pd.notna(u_match.iloc[0]['AVATAR_URL']) else AVATAR_GENERICO
                    
                    es_m = m['USUARIO'] == user_actual
                    aln = "flex-end" if es_m else "flex-start"
                    bg = "#dcf8c6" if es_m else "#ffffff"
                    
                    st.markdown(f"""
                        <div style="display: flex; flex-direction: column; align-items: {aln}; margin-bottom: 10px; width: 100%;">
                            <div style="display: flex; align-items: center; gap: 8px; flex-direction: {'row-reverse' if es_m else 'row'};">
                                <img src="{foto_url}" style="border-radius: 50%; width: 30px; height: 30px; object-fit: cover; border: 1px solid #ddd;">
                                <div style="max-width: 85%; background-color: {bg}; padding: 8px 12px; border-radius: 15px; border: 1px solid #ddd; box-shadow: 1px 1px 2px rgba(0,0,0,0.05);">
                                    <div style="font-size: 0.75em; color: #555; font-weight: bold;">{m['NOMBRE']}</div>
                                    <div style="font-size: 0.95em; color: #333; line-height: 1.2;">{m['MENSAJE']}</div>
                                </div>
                            </div>
                        </div>
                    """, unsafe_allow_html=True)
    
        # 3. CAJA DE COMENTARIO RÁPIDO (Debajo del contenedor)
        with st.form("quick_chat", clear_on_submit=True):
            c_txt, c_btn = st.columns([0.8, 0.2])
            with c_txt:
                msg_rapido = st.text_input("Escribe algo...", placeholder="¿Quién gana hoy?", label_visibility="collapsed")
            with c_btn:
                enviar = st.form_submit_button("🚀")
            
            if enviar and msg_rapido.strip():
                nuevo_msg = {
                    "FECHA": (datetime.now() - timedelta(hours=3)).strftime("%d/%m %H:%M"),
                    "USUARIO": user_actual,
                    "NOMBRE": st.session_state['user_data']['NOMBRE'],
                    "MENSAJE": msg_rapido.strip(),
                    "PARTIDO_ID": 0
                }
                # Guardamos y actualizamos
                df_update = pd.concat([df_foro_inicio, pd.DataFrame([nuevo_msg])], ignore_index=True)
                conn.update(worksheet="FORO", data=df_update)
                st.cache_data.clear()
                st.rerun()


    # --- COLUMNA DERECHA: RANKING Y ESTADÍSTICAS (30%) ---
    with col_derecha:
        # --- PODIO VISUAL ESTILO REAL (2º - 1º - 3º) ---
        with col_derecha:
            st.markdown("---")
            st.subheader("🏆 Podio del Torneo")
            
            # Tomamos los 3 primeros y los reordenamos para el podio: [2, 1, 3]
            top_3 = df_ranking.head(3).copy()
            
            if len(top_3) >= 3:
                # Reordenamos el DataFrame para que el 1º quede en el medio visualmente
                # Índice 1 (Plata), Índice 0 (Oro), Índice 2 (Bronce)
                podio_orden = [top_3.iloc[1], top_3.iloc[0], top_3.iloc[2]]
                medallas = ["🥈", "🥇", "🥉"]
                tamanos = [70, 100, 50]  # Tamaños de foto: El 1º es el más grande
                alturas = ["30px", "0px", "50px"] # Margen superior para escalonar
                colores = ["#C0C0C0", "#FFD700", "#CD7F32"]
                
                # Columnas para el podio
                cols_p = st.columns([1, 1.2, 1]) # La del centro es un poco más ancha
                
                df_u_info = conn.read(worksheet="USUARIOS", ttl=10)
                
                for i, row in enumerate(podio_orden):
                    target_id = row['ID_PARA_FOTO']
                    user_match = df_u_info[df_u_info['ID'] == target_id]
                    
                    url_f = AVATAR_GENERICO
                    if not user_match.empty:
                        foto = user_match.iloc[0]['AVATAR_URL']
                        if pd.notna(foto) and str(foto).strip() != "":
                            url_f = str(foto).strip()
                    
                    with cols_p[i]:
                        # Definimos el HTML en una variable para que sea más limpio
                        html_podio = f"""
                        <div style="text-align: center; margin-top: {alturas[i]};">
                            <p style="font-size: 2em; margin:0;">{medallas[i]}</p>
                            <div style="display: flex; justify-content: center;">
                                <img src="{url_f}" style="
                                    border-radius: 50%; 
                                    width: {tamanos[i]}px; 
                                    height: {tamanos[i]}px; 
                                    object-fit: cover; 
                                    border: 4px solid {colores[i]};
                                    box-shadow: 0px 8px 15px rgba(0,0,0,0.3);
                                    background-color: white;">
                            </div>
                            <div style="background-color: rgba(255, 255, 255, 0.85); border-radius: 8px; padding: 5px; margin-top: 10px; border: 1px solid {colores[i]};">
                                <p style="font-size: 0.85em; font-weight: bold; margin: 0; color: #1e1e1e;">
                                    {row['JUGADOR']}
                                </p>
                                <p style="font-size: 1em; color: #004d40; font-weight: bold; margin: 0;">
                                    {int(row['PUNTOS'])} pts
                                </p>
                            </div>
                        </div>
                        """
                        # Ejecutamos el renderizado
                        st.markdown(html_podio, unsafe_allow_html=True)
            else:
                st.info("Necesitamos al menos 3 jugadores para armar el podio real.")
                
#-----------RANKING ------------------------------------------------
    
        st.subheader("📊 Ranking")
        st.dataframe(
            df_ranking,
            use_container_width=True,
            hide_index=True,
            column_config={
                "ID_PARA_FOTO": None,
                "Nº": st.column_config.TextColumn("Nº", width="small"),
                "PUNTOS": st.column_config.NumberColumn("PUNTOS"),
                "EXACTOS": st.column_config.NumberColumn("🎯"),
                "GENERALES": st.column_config.NumberColumn("✅")
            }
        )

        # --- GRÁFICO DE EVOLUCIÓN (SINCRO TOTAL) ---
        st.markdown("---")
        st.subheader("📈 Evolución de Puntos")
        
        # 1. Filtro flexible para VIZ (detecta TRUE, True, 1, etc.)
        df_res['VIZ_AUX'] = df_res['VIZ'].astype(str).str.strip().str.upper()
        partidos_visibles = df_res[df_res['VIZ_AUX'].isin(['TRUE', '1', '1.0', 'VERDADERO'])].sort_values('N_PARTIDO')
        
        if not partidos_visibles.empty:
            evol_list = []
            usuarios_lista = df_usuarios["USUARIO"].unique()
            ids_visibles = partidos_visibles['N_PARTIDO'].tolist()
            
            for user in usuarios_lista:
                pts_acc = 0
                user_pro = df_pro[df_pro['USUARIO'] == user]
                
                for id_p in ids_visibles:
                    part = partidos_visibles[partidos_visibles['N_PARTIDO'] == id_p].iloc[0]
                    u_p = user_pro[user_pro['N_PARTIDO'] == id_p]
                    
                    if not u_p.empty:
                        # Extraemos valores con iloc[0] para evitar errores de Series
                        r1, r2 = part['R1'], part['R2']
                        p1, p2 = u_p.iloc[0]['P1'], u_p.iloc[0]['P2']
                        
                        # Solo sumamos si hay goles cargados
                        if pd.notna(r1) and pd.notna(r2):
                            pts, _, _ = calcular_detalle(r1, r2, p1, p2)
                            pts_acc += pts
                    
                    evol_list.append({
                        "N_Partido": int(id_p), 
                        "Jugador": user, 
                        "Puntos": pts_acc
                    })
            
            if evol_list:
                df_ev = pd.DataFrame(evol_list)
                # Pivotamos y ordenamos el índice para que la línea sea continua
                df_ev_pivot = df_ev.pivot(index="N_Partido", columns="Jugador", values="Puntos").sort_index()
                
                fig = px.line(
                    df_ev_pivot, 
                    labels={"N_Partido": "Nº Partido", "value": "Puntos", "variable": "Jugador"},
                    markers=True
                )

                fig.update_layout(
                    xaxis=dict(fixedrange=True, tickmode='linear', dtick=1),
                    yaxis=dict(fixedrange=True),
                    dragmode=False,
                    hovermode="x unified",
                    legend=dict(orientation="h", yanchor="bottom", y=1.1, xanchor="center", x=0.5),
                    margin=dict(l=20, r=20, t=50, b=20),
                    height=450
                )

                st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
        else:
            st.info("💡 La evolución aparecerá cuando haya partidos visibles con resultados cargados.")


        # --- CURIOSIDADES ---
        st.markdown("---")
        st.subheader("💡 ¿Mira Vo...?")
        
        # Usamos la variable partidos_visibles que definimos en el bloque del gráfico
        if not partidos_visibles.empty:
            aciertos_list = []
            for _, p in partidos_visibles.iterrows():
                id_p = p['N_PARTIDO']
                total_ac = 0
                
                # CORRECCIÓN: Cambiamos df_pro_all por df_pro
                pros_p = df_pro[df_pro['N_PARTIDO'] == id_p]
                
                # Determinamos tendencia real (1=Local, 2=Visitante, 0=Empate)
                r1, r2 = p['R1'], p['R2']
                t_real = 1 if r1 > r2 else (2 if r2 > r1 else 0)
                
                for _, pr in pros_p.iterrows():
                    # Tendencia pronosticada
                    p1, p2 = pr['P1'], pr['P2']
                    t_pron = 1 if p1 > p2 else (2 if p2 > p1 else 0)
                    
                    if t_pron == t_real:
                        total_ac += 1
                        
                aciertos_list.append({"Partido": f"{p['Equipo_1']} vs {p['Equipo_2']}", "Cant": total_ac})
            
            if aciertos_list:
                df_h = pd.DataFrame(aciertos_list)
                # Mostramos los datos con íconos descriptivos
                st.write(f"✅ **Más fácil (más aciertos de tendencia):** {df_h.loc[df_h['Cant'].idxmax()]['Partido']}")
                st.write(f"😱 **Sorpresa (menos aciertos de tendencia):** {df_h.loc[df_h['Cant'].idxmin()]['Partido']}")

        # --- ESTADÍSTICAS GLOBALES ---
        st.markdown("---")
        st.subheader("📊 Global")
        c1, c2 = st.columns(2)
        # Aseguramos que sume sobre df_ranking que ya está calculado arriba
        c1.metric("🎯 Total Exactos", int(df_ranking["EXACTOS"].sum()))
        c2.metric("✅ Total Grales", int(df_ranking["GENERALES"].sum()))

#---------- MENU MIS PRONOSTICOS (CÓDIGO CORREGIDO Y COMPLETO) ----------------------------------

elif menu == "📝 Mis Pronósticos":
    with col_principal:
        st.subheader("📝 Mis Predicciones")
        
        # 1. Inicializamos la variable de control de edición si no existe
        if 'permitir_edicion' not in st.session_state:
            st.session_state.permitir_edicion = False
        
        user_actual = st.session_state['user_data']['USUARIO']
        
        # Filtramos localmente los pronósticos del usuario
        df_user_pro = df_pro[df_pro['USUARIO'] == user_actual]

        # --- Lógica de tiempo ---
        ahora_arg = datetime.utcnow() - timedelta(hours=3)
        fecha_limite = datetime(2026, 6, 8, 23, 59, 59)
        es_tiempo_valido = ahora_arg < fecha_limite

        if es_tiempo_valido:
            st.success(f"⏳ Tienes tiempo hasta el 08/06.")
            # El valor del toggle depende de la variable en session_state
            modo_edicion = st.toggle("🔓 Editar resultados", value=st.session_state.permitir_edicion)
            # Sincronizamos la variable con lo que el usuario mueva en el toggle
            st.session_state.permitir_edicion = modo_edicion
        else:
            st.error("🔒 Plazo finalizado.")
            modo_edicion = False
            st.session_state.permitir_edicion = False
        
        # Definimos si los inputs deben estar bloqueados
        esta_bloqueado = not (es_tiempo_valido and modo_edicion)

        # Formulario de pronósticos
        with st.form("form_pronosticos_v3"):
            lista_nuevos_pro = []
            
            # Ordenamos por número de partido para mostrar en orden
            for i, row in df_res.sort_values('N_PARTIDO').iterrows():
                id_p = int(row['N_PARTIDO'])
                match = df_user_pro[df_user_pro['N_PARTIDO'] == id_p]
                
                # Extraemos valores actuales (seguros con iloc[0])
                v1 = int(match.iloc[0]['P1']) if not match.empty and pd.notna(match.iloc[0]['P1']) else 0
                v2 = int(match.iloc[0]['P2']) if not match.empty and pd.notna(match.iloc[0]['P2']) else 0
                
                bandera1 = mapa_banderas.get(row['Equipo_1'], AVATAR_GENERICO)
                bandera2 = mapa_banderas.get(row['Equipo_2'], AVATAR_GENERICO)
                            
                # Diseño de la tarjeta de partido
                st.markdown(f"""
                    <div style='background-color:#f8f9fa; border-radius:8px; padding:6px 12px; border-left:4px solid #007bff; margin-bottom:2px; display: flex; align-items: center; justify-content: space-between;'>
                        <div style='display: flex; align-items: center; gap: 8px; width: 45%;'>
                            <img src="{bandera1}" width="22">
                            <span style='font-size: 0.9em; font-weight: bold;'>{row['Equipo_1']}</span>
                        </div>
                        <div style='font-size: 0.7em; color: #999; font-weight: bold; width: 10%; text-align: center;'>VS</div>
                        <div style='display: flex; align-items: center; gap: 8px; width: 45%; justify-content: flex-end;'>
                            <span style='font-size: 0.9em; font-weight: bold;'>{row['Equipo_2']}</span>
                            <img src="{bandera2}" width="22">
                        </div>
                    </div>
                """, unsafe_allow_html=True)
                
                # Inputs de goles
                c1, c_vs, c2 = st.columns([1, 0.2, 1])
                with c1:
                    p1_val = st.number_input(f"G1_{id_p}", 0, 15, v1, key=f"f1_{id_p}", label_visibility="collapsed", disabled=esta_bloqueado)
                with c_vs:
                    st.write("<div style='text-align:center; margin-top:5px; font-weight:bold;'>:</div>", unsafe_allow_html=True)
                with c2:
                    p2_val = st.number_input(f"G2_{id_p}", 0, 15, v2, key=f"f2_{id_p}", label_visibility="collapsed", disabled=esta_bloqueado)
                
                # Guardamos los valores en la lista
                lista_nuevos_pro.append({"N_PARTIDO": id_p, "USUARIO": user_actual, "P1": p1_val, "P2": p2_val})

            # Botón de envío (Siempre presente dentro del form)
            texto_boton = "💾 GUARDAR TODO EL PRODE" if not esta_bloqueado else "LECTURA (EDICIÓN DESHABILITADA)"
            
            if st.form_submit_button(texto_boton, use_container_width=True, disabled=esta_bloqueado):
                try:
                    # 1. Leer datos actuales de la base
                    df_pro_full = conn.read(worksheet="PRONOSTICOS", ttl=5)
                    
                    # 2. Filtrar para quitar lo viejo del usuario y concatenar lo nuevo
                    df_otros = df_pro_full[df_pro_full['USUARIO'] != user_actual]
                    df_final = pd.concat([df_otros, pd.DataFrame(lista_nuevos_pro)], ignore_index=True)
                    
                    # 3. Actualizar Google Sheets
                    conn.update(worksheet="PRONOSTICOS", data=df_final)
                    st.cache_data.clear()
                    
                    # 4. RESET de la edición: Apagamos el permiso en session_state
                    st.session_state.permitir_edicion = False
                    
                    st.success("✅ ¡Pronósticos guardados correctamente!")
                    st.balloons()
                    st.rerun() 
                    
                except Exception as e:
                    st.error(f"Error al guardar: {e}")

    # --- COLUMNA DERECHA: PERFIL EDITABLE ---
    with col_derecha:
        st.subheader("👤 Mi Perfil")
        u_data = st.session_state['user_data']
        
        if 'editando_perfil' not in st.session_state:
            st.session_state.editando_perfil = False

        if not st.session_state.editando_perfil:
            # Avatar con respaldo de UI-Avatars si está vacío
            foto_actual = u_data.get('AVATAR_URL')
            if not foto_actual or pd.isna(foto_actual):
                foto = f"https://ui-avatars.com/api/?name={u_data['NOMBRE']}&background=random"
            else:
                foto = foto_actual
            
            st.markdown(f"""
                <div style="text-align: center;">
                    <img src="{foto}" style="border-radius: 50%; width: 110px; height: 110px; object-fit: cover; border: 3px solid #007bff;">
                    <h3 style="margin-bottom: 0;">{u_data['NOMBRE']}</h3>
                    <p style="color: gray;">@{u_data['USUARIO']}</p>
                </div>
                <hr>
                <p><b>⚽ Equipo:</b> {u_data['EQUIPO FAVORITO']}</p>
                <p><b>🎂 Edad:</b> {u_data['EDAD']} años</p>
                <p><b>📝 Bio:</b> <i>"{u_data['DESCRIPCION']}"</i></p>
            """, unsafe_allow_html=True)
            
            if st.button("⚙️ Editar Perfil", use_container_width=True):
                st.session_state.editando_perfil = True
                st.rerun()
        else:
            with st.form("form_edit_perfil_v3"):
                st.write("### 📝 Editar Perfil")
                archivo_perfil = st.file_uploader("Actualizar foto de perfil", type=['jpg', 'jpeg', 'png'])
                n_nom = st.text_input("Nombre Real", value=u_data['NOMBRE'])
                
                # Lógica de índice para el equipo
                equipos = ["Argentina", "México", "España", "Brasil", "Uruguay", "Colombia", "Otro"]
                idx_equipo = equipos.index(u_data['EQUIPO FAVORITO']) if u_data['EQUIPO FAVORITO'] in equipos else 0
                n_equ = st.selectbox("Hincha de", equipos, index=idx_equipo)
                
                n_bio = st.text_area("Bio", value=u_data['DESCRIPCION'], max_chars=100)
                
                c_b1, c_b2 = st.columns(2)
                
                if c_b1.form_submit_button("✅ Guardar"):
                    nueva_url = u_data['AVATAR_URL']
                    if archivo_perfil:
                        with st.spinner("Subiendo foto al servidor..."):
                            ts = datetime.now().strftime('%H%M%S')
                            nombre_archivo = f"perfil_{u_data['USUARIO']}_{ts}.jpg"
                            res_url = upload_profile_picture(archivo_perfil, nombre_archivo)
                            if res_url and "Error" not in res_url:
                                nueva_url = res_url
                            else:
                                st.error(f"Error al subir: {res_url}")

                    try:
                        df_u = conn.read(worksheet="USUARIOS", ttl=10)
                        df_u.loc[df_u['USUARIO'] == u_data['USUARIO'], ['NOMBRE', 'AVATAR_URL', 'EQUIPO FAVORITO', 'DESCRIPCION']] = [n_nom, nueva_url, n_equ, n_bio]
                        conn.update(worksheet="USUARIOS", data=df_u)
                        
                        st.session_state['user_data'].update({
                            'NOMBRE': n_nom, 'AVATAR_URL': nueva_url, 
                            'EQUIPO FAVORITO': n_equ, 'DESCRIPCION': n_bio
                        })
                        st.session_state.editando_perfil = False
                        st.cache_data.clear()
                        st.success("¡Perfil actualizado!")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error: {e}")
                
                if c_b2.form_submit_button("❌ Cancelar"):
                    st.session_state.editando_perfil = False
                    st.rerun()

# ---------- MENU JUGADORES ----------------------------------------------------
elif menu == "👥 Jugadores":
    # --- COLUMNA CENTRAL ---
    with col_principal:
        st.subheader("👥 Lista de Jugadores")
        
        # 1. Creamos el selector de nombres
        nombres_usuarios = df_usuarios['NOMBRE'].tolist()
        nombre_elegido = st.selectbox("Selecciona un jugador para ver su perfil:", nombres_usuarios)
        
        # 2. Definimos user_sel buscando en el dataframe de usuarios
        user_sel_query = df_usuarios[df_usuarios['NOMBRE'] == nombre_elegido]
        
        if not user_sel_query.empty:
            user_sel = user_sel_query.iloc[0] # Aquí es donde se define para que lo vea la col_derecha
        else:
            user_sel = None

        st.markdown("---")
        st.write("### Lista de Participantes")
        # Tarjetas simples de referencia
        for _, u in df_usuarios.iterrows():
            foto_mini = u['AVATAR_URL'] if pd.notna(u['AVATAR_URL']) and u['AVATAR_URL'] != "" else AVATAR_GENERICO
            st.markdown(f"""
                <div style="background: rgba(255,255,255,0.8); padding: 8px; border-radius: 10px; margin-bottom: 5px; display: flex; align-items: center; gap: 12px; border: 1px solid #ddd;">
                    <img src="{foto_mini}" width="35" height="35" style="border-radius: 50%; object-fit: cover;">
                    <span style="color:#333;"><b>{u['NOMBRE']}</b> — <small>{u['EQUIPO FAVORITO']}</small></span>
                </div>
            """, unsafe_allow_html=True)
            
    with col_derecha:
        st.subheader("👤 Perfil Seleccionado")
        
        if user_sel is not None:
            # Buscamos su rendimiento en el ranking
            match_rank = df_ranking[df_ranking['JUGADOR'].str.contains(user_sel['NOMBRE'], na=False)]
            
            if not match_rank.empty:
                datos_vivos = match_rank.iloc[0]
                idx_real = match_rank.index[0]
                
                # --- LÓGICA DE INSIGNIAS ---
                css = {k: "filter: grayscale(100%); opacity: 0.15;" for k in ["puntero", "master", "mentalista", "lento", "onfire", "fundador"]}
                
                if "👑" in str(datos_vivos['Nº']): css["puntero"] = ""
                if int(datos_vivos['EXACTOS']) >= 5: css["master"] = ""
                if int(datos_vivos['GENERALES']) == df_ranking['GENERALES'].max() and df_ranking['GENERALES'].max() > 0:
                    css["mentalista"] = ""
                if len(df_ranking) > 2 and idx_real == (len(df_ranking) - 1): css["lento"] = ""
                if int(user_sel['ID']) <= 3: css["fundador"] = ""

                # Racha (On Fire)
                u_pro_sorted = df_pro[df_pro['USUARIO'] == user_sel['USUARIO']].sort_values('N_PARTIDO')
                r_act, r_max = 0, 0
                for _, p in u_pro_sorted.iterrows():
                    p_ref = df_res[df_res['N_PARTIDO'] == p['N_PARTIDO']]
                    if not p_ref.empty and pd.notna(p_ref.iloc[0]['R1']):
                        pts, exa, gen = calcular_detalle(p_ref.iloc[0]['R1'], p_ref.iloc[0]['R2'], p['P1'], p['P2'])
                        if exa == 1:
                            r_act += 1
                            r_max = max(r_max, r_act)
                        else: r_act = 0
                if r_max >= 3: css["onfire"] = ""
                
                # --- RENDERIZADO DE PERFIL ---
                foto_perfil = user_sel['AVATAR_URL'] if pd.notna(user_sel['AVATAR_URL']) and user_sel['AVATAR_URL'] != "" else "https://via.placeholder.com/100"
                
# --- RENDERIZADO DE PERFIL ---
                html_perfil = f"""<div style="background: white; padding: 20px; border-radius: 15px; box-shadow: 0 4px 10px rgba(0,0,0,0.1); text-align: center; color: #333;">
<img src="{foto_perfil}" style="border-radius: 50%; width: 100px; height: 100px; object-fit: cover; border: 3px solid #007bff; margin-bottom: 10px;">
<h4 style="margin:0;">{user_sel['NOMBRE']}</h4>
<div style="color: #007bff; font-weight: bold; margin-bottom: 15px;">{user_sel['EQUIPO FAVORITO']}</div>
<div style="display: flex; justify-content: center; gap: 10px; flex-wrap: wrap; background: #f8f9fa; padding: 10px; border-radius: 10px;">
    <span title="Puntero" style="font-size: 1.5em; {css['puntero']}">🏆</span>
    <span title="Master Exactos" style="font-size: 1.5em; {css['master']}">🎯</span>
    <span title="Mentalista" style="font-size: 1.5em; {css['mentalista']}">🧙‍♂️</span>
    <span title="Fundador" style="font-size: 1.5em; {css['fundador']}">🏅</span>
    <span title="On Fire" style="font-size: 1.5em; {css['onfire']}">🔥</span>
    <span title="El más lento" style="font-size: 1.5em; {css['lento']}">🐌</span>
</div>
<div style="margin-top: 15px; text-align: left; font-size: 0.85em; line-height: 1.3;">
    <b style="color:#333;">Bio:</b> <i style="color:#555;">"{user_sel['DESCRIPCION']}"</i>
</div>
</div>"""
                st.markdown(html_perfil, unsafe_allow_html=True)

            else:
                st.warning("El jugador no tiene puntos suficientes para mostrar rendimiento.")

            # --- PREDICCIONES DEL USUARIO ---
            st.markdown("---")
            st.write(f"🗳️ **Pronosticos de {user_sel['NOMBRE']}:**")
            pro_user_sel = df_pro[df_pro['USUARIO'] == user_sel['USUARIO']]
            
            if pro_user_sel.empty:
                st.warning("Sin pronósticos.")
            else:
                with st.container(height=400):
                    for _, p in pro_user_sel.sort_values('N_PARTIDO').iterrows():
                        p_match = df_res[df_res['N_PARTIDO'] == p['N_PARTIDO']]
                        if not p_match.empty:
                            p_inf = p_match.iloc[0]
                            f1, f2 = get_flag_img(p_inf['Equipo_1']), get_flag_img(p_inf['Equipo_2'])
                            i1 = f'<img src="{f1}" width="18">' if "data" in f1 else f1
                            i2 = f'<img src="{f2}" width="18">' if "data" in f2 else f2
                            
                            st.markdown(f"""
                            <div style="display: flex; justify-content: space-between; align-items: center; padding: 6px; border-bottom: 1px solid #eee; font-size: 0.8em;">
                                <div style="width: 10%; color: #999; font-weight: bold;">{int(p['N_PARTIDO'])}</div>
                                <div style="width: 35%; text-align: right;">{p_inf['Equipo_1']} {i1}</div>
                                <div style="width: 20%; text-align: center; background: #1f3b4d; color: white; border-radius: 4px; font-weight: bold; margin: 0 5px;">
                                    {int(p['P1'])} - {int(p['P2'])}
                                </div>
                                <div style="width: 35%; text-align: left;">{i2} {p_inf['Equipo_2']}</div>
                            </div>
                            """, unsafe_allow_html=True)


        
# ---------- MENU FORO (DISEÑO OPTIMIZADO) ----------------------------------------------------

elif menu == "💬 Foro":
    df_foro = conn.read(worksheet="FORO", ttl=0)
    df_u_ref = df_usuarios 
    user_actual = st.session_state['user_data']['USUARIO']
    
    with col_principal:
        st.subheader("💬 Muro de la Comunidad")
        
        # Formulario de publicación (Mismo que ya tienes)
        with st.expander("✍️ Escribir algo en el muro"):
            with st.form("nuevo_post_full", clear_on_submit=True):
                texto = st.text_area("¿Qué tienes en mente?", max_chars=250)
                if st.form_submit_button("🚀 Publicar", use_container_width=True):
                    if texto.strip():
                        nuevo_msg = {"FECHA": (datetime.now() - timedelta(hours=3)).strftime("%d/%m %H:%M"),
                                     "USUARIO": user_actual, "NOMBRE": st.session_state['user_data']['NOMBRE'],
                                     "MENSAJE": texto.strip(), "PARTIDO_ID": 0, "LIKES": 0, "DISLIKES": 0}
                        df_update = pd.concat([df_foro, pd.DataFrame([nuevo_msg])], ignore_index=True)
                        conn.update(worksheet="FORO", data=df_update)
                        st.cache_data.clear()
                        st.rerun()

        st.markdown("---")

        for idx, m in df_foro.iloc[::-1].iterrows():
            u_match = df_u_ref[df_u_ref['USUARIO'] == m['USUARIO']]
            foto_msg = u_match.iloc[0]['AVATAR_URL'] if not u_match.empty and pd.notna(u_match.iloc[0]['AVATAR_URL']) else AVATAR_GENERICO
            es_mio = m['USUARIO'] == user_actual
            aln = "flex-end" if es_mio else "flex-start"
            bg = "#dcf8c6" if es_mio else "#ffffff"
            
            # BURBUJA DE MENSAJE
            st.markdown(f"""
                <div style="display: flex; flex-direction: column; align-items: {aln}; margin-bottom: 2px; width: 100%;">
                    <div style="display: flex; align-items: flex-end; gap: 10px; flex-direction: {'row-reverse' if es_mio else 'row'};">
                        <img src="{foto_msg}" style="border-radius: 50%; width: 40px; height: 40px; object-fit: cover; border: 2px solid #007bff;">
                        <div style="max-width: 80%; background-color: {bg}; padding: 12px 16px; border-radius: 18px; border: 1px solid #ddd; position: relative;">
                            <div style="display: flex; justify-content: space-between; align-items: baseline; gap: 15px; margin-bottom: 4px;">
                                <span style="font-size: 0.85em; color: #007bff; font-weight: bold;">{m['NOMBRE']}</span>
                                <span style="font-size: 0.7em; color: #999;">{m['FECHA']}</span>
                            </div>
                            <div style="font-size: 1.05em; color: #333;">{m['MENSAJE']}</div>
                        </div>
                    </div>
                </div>
            """, unsafe_allow_html=True)
            
            # --- FILA DE REACCIONES (CON BLOQUEO DE AUTO-REACCIÓN) ---
            l_count = int(m['LIKES']) if pd.notna(m.get('LIKES')) else 0
            d_count = int(m['DISLIKES']) if pd.notna(m.get('DISLIKES')) else 0

            # Definimos la distribución de columnas
            distribucion = [0.10, 0.90] if not es_mio else [0.55, 0.45]
            col_espacio, col_botones = st.columns(distribucion)

            with col_botones:
                # Si el mensaje es de OTRO, mostramos Likes, Dislikes y (si es admin) Borrar
                if not es_mio:
                    r1, r2, r3, _ = st.columns([0.1, 0.1, 0.1, 0.7], gap="small")
                    
                    with r1:
                        if st.button(f"👍{l_count}", key=f"lk_{idx}"):
                            df_foro.at[idx, 'LIKES'] = l_count + 1
                            conn.update(worksheet="FORO", data=df_foro); st.cache_data.clear(); st.rerun()
                    with r2:
                        if st.button(f"👎{d_count}", key=f"ds_{idx}"):
                            df_foro.at[idx, 'DISLIKES'] = d_count + 1
                            conn.update(worksheet="FORO", data=df_foro); st.cache_data.clear(); st.rerun()
                    with r3:
                        # Un Admin puede borrar mensajes de otros
                        if st.session_state['user_data']['ROL'] == 'admin':
                            if st.button("🗑️", key=f"del_{idx}"):
                                df_f = df_foro.drop(idx)
                                conn.update(worksheet="FORO", data=df_f); st.cache_data.clear(); st.rerun()
                
                # Si el mensaje es MÍO, solo mostramos el botón de borrar
                else:
                    # Empujamos el botón de borrar hacia la derecha de la burbuja
                    _, r_del = st.columns([0.85, 0.15])
                    with r_del:
                        if st.button("🗑️", key=f"del_{idx}", help="Eliminar mi mensaje"):
                            df_f = df_foro.drop(idx)
                            conn.update(worksheet="FORO", data=df_f); st.cache_data.clear(); st.rerun()

    # 3. COLUMNA DERECHA DIVIDIDA
    with col_derecha:
        st.subheader("📢 Comunidad")
        
        # Subdivisión 15% y 15%
        col_com_izq, col_com_der = st.columns(2)
        
        with col_com_izq:
            st.write("**Top Agitadores**")
            top_com = df_foro['NOMBRE'].value_counts().head(3)
            for nombre, cant in top_com.items():
                st.write(f"💬 {nombre} ({cant})")

        with col_com_der:
            st.write("**Popularidad**")
            top_likes = df_foro.groupby('NOMBRE')['LIKES'].sum().sort_values(ascending=False).head(1)
            for n, t in top_likes.items():
                st.write(f"🌟 {n}" if t > 0 else "Sin likes")
            
            top_dis = df_foro.groupby('NOMBRE')['DISLIKES'].sum().sort_values(ascending=False).head(1)
            for n, t in top_dis.items():
                st.write(f"🍋 {n}" if t > 0 else "Sin polémicas")
        
        st.markdown("---")
        
        
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
