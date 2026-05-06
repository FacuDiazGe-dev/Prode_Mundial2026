import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection
from datetime import datetime
from datetime import datetime, timedelta
from google.auth.transport.requests import Request
from googleapiclient.http import MediaIoBaseUpload

st.set_page_config(page_title="Prode Mundial 2026", layout="wide")
#st.title("🏆 Prode Mundial 2026 - Fase de Grupos")

import base64
import requests
from io import BytesIO

@st.cache_data(ttl=3600)
def get_flag_img(pais):
    # Diccionario de códigos ISO (Mantenemos los que ya tienes)
    codigos = {
        "Alemania": "de", "Arabia Saudita": "sa", "Argelia": "dz", "Argentina": "ar",
        "Australia": "au", "Austria": "at", "Bélgica": "be", "Bosnia y Herzegovina": "ba",
        "Brasil": "br", "Cabo Verde": "cv", "Canadá": "ca", "Catar": "qa",
        "Colombia": "co", "Corea del Sur": "kr", "Costa de Marfil": "ci", "Croacia": "hr",
        "Curazao": "cw", "Ecuador": "ec", "Egipto": "eg", "Escocia": "gb-sct",
        "España": "es", "Estados Unidos": "us", "Francia": "fr", "Ghana": "gh",
        "Haití": "ht", "Inglaterra": "gb-eng", "Irak": "iq", "Irán": "ir",
        "Japón": "jp", "Jordania": "jo", "Marruecos": "ma", "México": "mx",
        "Noruega": "no", "Nueva Zelanda": "nz", "Países Bajos": "nl", "Panamá": "pa",
        "Paraguay": "py", "Portugal": "pt", "República Checa": "cz", 
        "República Democrática del Congo": "cd", "Senegal": "sn", "Sudáfrica": "za",
        "Suecia": "se", "Suiza": "ch", "Túnez": "tn", "Turquía": "tr",
        "Uruguay": "uy", "Uzbekistán": "uz"
    }
    
    code = codigos.get(pais)
    if not code: return "⚽" # Fallback si no hay código

    try:
        # Descargamos la imagen y la convertimos a Base64
        response = requests.get(f"https://flagcdn.com/w40/{code}.png", timeout=5)
        if response.status_code == 200:
            img_b64 = base64.b64encode(response.content).decode()
            return f"data:image/png;base64,{img_b64}"
    except:
        pass
    
    return "⚽" # Fallback si falla la descarga
    
#-------------------------------- CARGAR FOTO STORAGE (GCS) -----------------------------------------------------
from google.cloud import storage
import io 
#Definicion variable carga de la imagen
def upload_profile_picture(archivo, file_name):
    from google.cloud import storage
    import io
    try:
        creds_info = st.secrets["connections"]["gsheets"] 
        client = storage.Client.from_service_account_info(creds_info)
        
        bucket_name = "foto-prode2026" 
        bucket = client.bucket(bucket_name)
        blob = bucket.blob(f"perfiles/{file_name}")
        
        if isinstance(archivo, bytes):
            objeto_archivo = io.BytesIO(archivo)
        else:
            objeto_archivo = archivo
            objeto_archivo.seek(0)
        
        tipo_mimo = getattr(archivo, 'type', 'image/jpeg')

        blob.upload_from_file(objeto_archivo, content_type=tipo_mimo)
        
        return f"https://storage.googleapis.com/{bucket_name}/perfiles/{file_name}"
        
    except Exception as e:
        return f"Error: {e}"

#---------------------------MANTENIMIENTO -  True (Activado)  False (Desactivo)------------------------------------------------------------------
MANTENIMIENTO_ACTIVO = False 
MENSAJE_MANTENIMIENTO = "⚠️ Estamos actualizando los servidores para la próxima fecha. ¡Volvemos en unos minutos!"

# ----LOGIN---
# --- CONEXIÓN ---
conn = st.connection("gsheets", type=GSheetsConnection)

#-----carga de insignias de ranking----


# --- LECTURA DE CONFIGURACIÓN DE MANTENIMIENTO ---
try:
    df_config = conn.read(worksheet="CONFIG", ttl=5)
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
    st.title("🏆 Prode Mundial 2026")
    
    # REEMPLAZO DE TABS POR LÓGICA DE ESTADO
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
        
        # Botón para ir a registro (fuera del form)
        if st.button("🆕 ¿No tienes cuenta? Regístrate aquí"):
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
        
        if st.button("⬅️ Volver al Login"):
            st.session_state['mostrar_registro'] = False
            st.rerun()

    st.stop()
#---------------------- SI Mantenimiento esta activo ---------------------------
if MANTENIMIENTO_ACTIVO and st.session_state['user_data']['ROL'] != 'admin':
    st.warning(MENSAJE_MANTENIMIENTO)
    st.info("Solo el Administrador tiene acceso en este momento.")
    
    # Detenemos la ejecución para que no vean nada más
    if st.button("🔄 Reintentar"):
        st.rerun()
    st.stop() 

# =============================================================================
# --- DISEÑO VISUAL (FONDOS, BANNERS Y CONTRASTE) ---
# =============================================================================
st.markdown(f"""
    <style>
    /* 1. Fondo base del sitio */
    .stApp {{
        background-image: url("https://storage.googleapis.com/foto-prode2026/Banners/FONDO%20BASE.jpg");
        background-attachment: fixed;
        background-size: cover;
    }}

    /* 2. Banner Vertical en el Sidebar y contraste de letras */
    [data-testid="stSidebar"] {{
        background-image: url("https://storage.googleapis.com/foto-prode2026/Banners/BANNER%20VERTICAL_V3.jpg");
        background-size: cover;
        background-position: center;
    }}

    /* Estilo de letras en Sidebar para fondo oscuro */
    [data-testid="stSidebar"] .stMarkdown, 
    [data-testid="stSidebar"] label, 
    [data-testid="stSidebar"] .stRadio p,
    [data-testid="stSidebar"] h3 {{
        color: #FFFFFF !important;
        font-weight: 800 !important;
        text-shadow: 2px 2px 8px #000000, 0px 0px 10px #000000 !important;
    }}

    /* 3. Banner Superior Horizontal */
    .banner-superior {{
        background-image: linear-gradient(rgba(0,0,0,0.3), rgba(0,0,0,0.3)), 
                          url("https://storage.googleapis.com/foto-prode2026/Banners/BANNER%20HORIZONTAL.jpg");
        background-size: cover;
        background-position: center 10%;
        padding: 50px;
        border-radius: 15px;
        text-align: center;
        color: white;
        margin-bottom: 25px;
        box-shadow: 0px 4px 15px rgba(0,0,0,0.5);
    }}
    </style>
    
    <div class="banner-superior">
        <h1 style="font-size: 2.8em; text-shadow: 3px 3px 6px black; margin: 0;">🏆 PRODE MUNDIAL 2026 - Fase de Grupos</h1>
        <p style="font-size: 1.2em; text-shadow: 2px 2px 4px black; margin: 0;">¡La gloria está en tus predicciones!</p>
    </div>
""", unsafe_allow_html=True)


# --- SIDEBAR DE BIENVENIDA ---
st.sidebar.write(f"Hola, **{st.session_state['user_data']['NOMBRE']}**")

# --- CARGA DE DATOS DE TABLAS GSHEET ---------------------------------------------------------------------------------------------
# =============================================================================
# 1. FUNCIÓN DE CÁLCULO DE PUNTOS
# =============================================================================
def calcular_detalle(r1, r2, p1, p2):
    """
    Calcula puntos según: +1 por tendencia, +2 adicional por exacto (Total 3).
    """
    if pd.isna(r1) or pd.isna(r2) or pd.isna(p1) or pd.isna(p2):
        return 0, 0, 0 
    
    puntos, exactos, generales = 0, 0, 0
    r1, r2, p1, p2 = int(r1), int(r2), int(p1), int(p2)
    
    tendencia_real = 1 if r1 > r2 else (2 if r2 > r1 else 0)
    tendencia_pron = 1 if p1 > p2 else (2 if p2 > p1 else 0)
    
    # Si acertó la tendencia (Ganador o Empate)
    if tendencia_real == tendencia_pron:
        generales = 1
        puntos = 1 
        # Si además acertó el marcador exacto
        if r1 == p1 and r2 == p2:
            exactos = 1
            puntos = 3 
    return puntos, exactos, generales

# =============================================================================
# 2. CARGA DE DATOS (FRESH)
# =============================================================================
# --- CARGA DE DATOS OPTIMIZADA ---

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
except Exception as e:
    st.warning("⚠️ La conexión con Google es lenta. Mostrando datos guardados...")
    # Aquí podrías cargar datos por defecto si fallara la primera vez

# =============================================================================
# 1. FUNCIÓN DE APOYO PARA PROCESAR INSIGNIAS
# =============================================================================
def procesar_nombres_ranking(row, df_rank_base, df_pro, df_res, df_usuarios):
    nombre = row['JUGADOR']
    # La posición real es el índice actual + 1
    posicion = row.name + 1 
    insignias = ""
    
    # Buscamos datos extra del usuario
    try:
        u_info = df_usuarios[df_usuarios['NOMBRE'] == nombre].iloc[0]
        u_nick = u_info['USUARIO']
        u_id = int(u_info['ID'])
    except:
        return nombre

    # Reglas de Insignias
    if posicion == 1: insignias += " 👑" # Puntero
    if row['EXACTOS'] >= 5: insignias += " 🎯" # Master
    
    max_gen = df_rank_base['GENERALES'].max()
    if row['GENERALES'] == max_gen and max_gen > 0: insignias += " 🧙‍♂️" # Mentalista
    if u_id <= 3: insignias += " 🏅" # Fundador
    if len(df_rank_base) > 2 and posicion == len(df_rank_base): insignias += " 🐌" # Lento
        
    # Lógica ON FIRE (Racha de 3 o más exactos)
    user_pro_sorted = df_pro[df_pro['USUARIO'] == u_nick].sort_values('N_PARTIDO')
    r_act, r_max = 0, 0
    for _, p in user_pro_sorted.iterrows():
        partido_ref = df_res[df_res['N_PARTIDO'] == p['N_PARTIDO']]
        if not partido_ref.empty:
            res_p = partido_ref.iloc[0]
            if pd.notna(res_p['R1']):
                _, exa, _ = calcular_detalle(res_p['R1'], res_p['R2'], p['P1'], p['P2'])
                if exa == 1:
                    r_act += 1
                    r_max = max(r_max, r_act)
                else: r_act = 0
    if r_max >= 3: insignias += f" 🔥x{r_max}"

    return f"{nombre}{insignias}"

# =============================================================================
# 2. FUNCIÓN PRINCIPAL DE RANKING
# =============================================================================
@st.cache_data(ttl=300)
def obtener_ranking_global(df_users_list, df_pro_total, df_res_oficial):
    ranking_data = []
    
    for _, u in df_users_list.iterrows():
        u_nick = u['USUARIO']
        u_nombre = u['NOMBRE']
        u_id = u['ID']
        pts_t, exa_t, gen_t = 0, 0, 0
        
        pro_usr = df_pro_total[df_pro_total['USUARIO'] == u_nick]
        
        for _, p in pro_usr.iterrows():
            res_p = df_res_oficial[df_res_oficial['N_PARTIDO'] == p['N_PARTIDO']]
            
            if not res_p.empty:
                r1_oficial = res_p.iloc[0]['R1']
                r2_oficial = res_p.iloc[0]['R2']
                
                if pd.notna(r1_oficial) and pd.notna(r2_oficial):
                    pts, exa, gen = calcular_detalle(r1_oficial, r2_oficial, p['P1'], p['P2'])
                    pts_t += pts
                    exa_t += exa
                    gen_t += gen
                    
        ranking_data.append({
            'ID_PARA_FOTO': u_id,
            'JUGADOR': u_nombre, 
            'PUNTOS': pts_t, 
            'EXACTOS': exa_t, 
            'GENERALES': gen_t
        })
    
    # Crear DataFrame base y ordenar
    df_rank = pd.DataFrame(ranking_data).sort_values(
        by=['PUNTOS', 'EXACTOS'], 
        ascending=False
    ).reset_index(drop=True)
    
    # Aplicar insignias a los nombres
    if not df_rank.empty:
        df_rank['JUGADOR'] = df_rank.apply(
            lambda row: procesar_nombres_ranking(row, df_rank, df_pro_total, df_res_oficial, df_users_list), 
            axis=1
        )
        
    # Crear columna de posición Nº
    df_rank.index = df_rank.index + 1
    df_rank.insert(0, 'Nº', df_rank.index.map(lambda x: "👑" if x == 1 else str(x)))
    
    return df_rank

# =============================================================================
# 3. EJECUCIÓN
# =============================================================================
# Asegúrate de que df_usuarios, df_pro y df_res estén cargados antes
df_ranking = obtener_ranking_global(df_usuarios, df_pro, df_res)



# --- VISUALIZACIÓN ---
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
    
    menu = st.radio("Ir a:", opciones, key="menu_navegacion_unificado")
    
    st.markdown("---")
    # Botón de cerrar sesión
    if st.button("🚪 Cerrar Sesión", use_container_width=True):
        st.session_state['autenticado'] = False
        st.rerun()

    # --- LABORATORIO DE PRUEBA: SUBIDA A DRIVE ( OCULTO )---
    #st.markdown("---")
    #st.subheader("🧪 Test de Subida")
    #archivo_test = st.file_uploader("Probá subir una foto aquí", type=['jpg', 'png', 'jpeg'], key="test_uploader")
    #
    #if archivo_test: 
    #    if st.button("🚀 Subir a Drive", use_container_width=True):
    #        with st.spinner("Autenticando y subiendo..."):
    #            # Generamos el nombre
    #            nombre_t = f"test_{datetime.now().strftime('%H%M%S')}.jpg"
    #            
    #            # Intentamos la subida
    #            try:
    #                # USAMOS EL NOMBRE CORRECTO DE LA FUNCIÓN
    #                resultado_url = upload_profile_picture(archivo_test.getvalue(), nombre_t)
    #                
    #                if resultado_url and resultado_url.startswith("https"):
    #                    st.success("✅ ¡Subida exitosa!")
    #                    st.image(resultado_url, caption="Foto desde Drive")
    #                    st.code(resultado_url)
    #                else:
    #                    st.error(f"❌ Error de Google: {resultado_url}")
    #            except NameError:
    #                st.error("❌ Error: La función 'upload_profile_picture' no está definida arriba del código.")
    #            except Exception as e:
    #                st.error(f"❌ Error inesperado: {e}")


# --- LÓGICA DE CONTENIDO SEGÚN EL MENÚ ---
#------------------------------------------------MENU INICIO-----------------------------------------------

if menu == "🏠 Inicio":
    with col_principal:
        st.subheader("⚽ Cronograma y Resultados")
        
        df_pro_all = conn.read(worksheet="PRONOSTICOS", ttl=20)        
        
        # 1. Limpieza y Filtro de Visibilidad
        # Aseguramos que la columna VIZ exista y sea booleana
        if 'VIZ' in df_res.columns:
            df_res['VIZ'] = df_res['VIZ'].fillna(False).astype(bool)
            df_mostrar = df_res[df_res['VIZ'] == True].iloc[::-1]
        else:
            # Si aún no creaste la columna en Excel, mostramos todo para no dar error
            df_mostrar = df_res.iloc[::-1]

        with st.container(height=430):
            if df_mostrar.empty:
                st.info("Próximamente se publicarán los partidos de la jornada.")
            else:
                for i, row in df_mostrar.iterrows():
                    # DEFINICIÓN SEGURA DE VARIABLES (Esto evita el NameError)
                    r1 = int(row['R1']) if pd.notna(row['R1']) else "-"
                    r2 = int(row['R2']) if pd.notna(row['R2']) else "-"
                    dia_p = str(row['DIA']) if pd.notna(row['DIA']) else "---"
                    hora_p = str(row['HORA']) if pd.notna(row['HORA']) else "--:--"
                    
                    f1, f2 = get_flag_img(row['Equipo_1']), get_flag_img(row['Equipo_2'])
                    i1 = f'<img src="{f1}" width="35" style="border-radius:3px;">' if "data" in f1 else f1
                    i2 = f'<img src="{f2}" width="35" style="border-radius:3px;">' if "data" in f2 else f2
                    
                    # Color: Azul si terminó, Gris si es próximo
                    color_tema = "#007bff" if r1 != "-" else "#6c757d"

                    # Definimos los iconos antes para que el HTML sea más simple
                    i1 = f'<img src="{get_flag_img(row["Equipo_1"])}" width="25" style="border-radius:2px;">'
                    i2 = f'<img src="{get_flag_img(row["Equipo_2"])}" width="25" style="border-radius:2px;">'
                    
                    st.markdown(f"""
                    <div style="border: 1px solid #ddd; border-top: 3px solid {color_tema}; border-radius: 8px; padding: 8px; margin-bottom: 10px; background-color: white;">
                        <div style="display: flex; justify-content: space-between; margin-bottom: 5px; align-items: center;">
                            <span style="font-size: 0.65em; font-weight: bold; color: {color_tema}; text-transform: uppercase;">PARTIDO {int(row['N_PARTIDO'])}</span>
                            <span style="font-size: 0.65em; color: #666; font-weight: bold;">📅 {dia_p} | 🕒 {hora_p}</span>
                        </div>
                        <div style="display: flex; justify-content: space-between; align-items: center;">
                            <div style="width: 38%; text-align: center;">
                                <div style="margin-bottom: 3px;">{i1}</div>
                                <div style="font-weight: bold; font-size: 0.85em; color: #333;">{row['Equipo_1']}</div>
                            </div>
                            <div style="width: 24%; text-align: center;">
                                <div style="background: #f8f9fa; border: 1px solid #ddd; color: #333; font-size: 1.2em; font-weight: bold; border-radius: 5px; padding: 2px 0;">{r1}:{r2}</div>
                            </div>
                            <div style="width: 38%; text-align: center;">
                                <div style="margin-bottom: 3px;">{i2}</div>
                                <div style="font-weight: bold; font-size: 0.85em; color: #333;">{row['Equipo_2']}</div>
                            </div>
                        </div>
                    </div>""", unsafe_allow_html=True)
    
        # --- BLOQUE 2: FORO (Actividad Reciente en el Inicio) ---------------------------------------------------------------------------------------
        st.subheader("💬 Actividad Reciente")
        
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
                    foto_url = u_match.iloc[0]['AVATAR_URL'] if not u_match.empty and pd.notna(u_match.iloc[0]['AVATAR_URL']) else "https://flaticon.com"
                    
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
                    
                    url_f = "https://flaticon.com"
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

        # --- GRÁFICO DE EVOLUCIÓN DE PUNTOS (SOLUCIÓN DEFINITIVA AL ORDEN) ---
        st.markdown("---")
        st.subheader("📈 Evolución de Puntos")
        
        # 1. Limpieza y conversión a números (evita errores de Google Sheets)
        df_res['N_PARTIDO'] = pd.to_numeric(df_res['N_PARTIDO'], errors='coerce')
        df_pro_all['N_PARTIDO'] = pd.to_numeric(df_pro_all['N_PARTIDO'], errors='coerce')
        
        # 2. Filtrar solo partidos con resultado oficial
        partidos_jugados = df_res[df_res['R1'].notna()].sort_values('N_PARTIDO')
        
        if not partidos_jugados.empty:
            evol_list = []
            usuarios_lista = df_pro_all["USUARIO"].unique()
            
            for user in usuarios_lista:
                pts_acc = 0
                user_pro = df_pro_all[df_pro_all['USUARIO'] == user]
                
                for _, part in partidos_jugados.iterrows():
                    id_p = int(part['N_PARTIDO'])
                    u_p = user_pro[user_pro['N_PARTIDO'] == id_p]
                    
                    if not u_p.empty:
                        r1, r2 = part['R1'], part['R2']
                        p1, p2 = u_p.iloc[0]['P1'], u_p.iloc[0]['P2']
                        
                        # Cálculo de puntos
                        t_real = 1 if r1 > r2 else (2 if r2 > r1 else 0)
                        t_pron = 1 if p1 > p2 else (2 if p2 > p1 else 0)
                        
                        if t_real == t_pron:
                            pts_acc += 3 if (r1 == p1 and r2 == p2) else 1
                    
                    # GUARDAR: Usamos el ID numérico puro
                    evol_list.append({
                        "N_Partido": id_p, 
                        "Jugador": user, 
                        "Puntos": pts_acc
                    })
            
            if evol_list:
                df_ev = pd.DataFrame(evol_list)
                df_ev_pivot = df_ev.pivot(index="N_Partido", columns="Jugador", values="Puntos").sort_index()
                
                # --- CONFIGURACIÓN DE GRÁFICO ESTÁTICO Y OPTIMIZADO ---
                import plotly.express as px

                fig = px.line(
                    df_ev_pivot, 
                    labels={"N_Partido": "Nº de Partido", "value": "Puntos Acumulados", "variable": "Jugador"},
                    markers=True # Agrega puntos en cada partido para mejor lectura
                )

                # BLOQUEO DE ESCALA Y SCROLL
                fig.update_layout(
                    xaxis=dict(fixedrange=True, tickmode='linear', dtick=1), # Bloquea zoom X y fuerza números 1,2,3...
                    yaxis=dict(fixedrange=True), # Bloquea zoom Y
                    dragmode=False, # Impide arrastrar el gráfico
                    hovermode="x unified", # Muestra todos los puntos al pasar el mouse por la línea de tiempo
                    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1), # Leyenda horizontal arriba
                    margin=dict(l=20, r=20, t=30, b=20), # Ajusta márgenes para aprovechar espacio
                    height=400 # Altura fija para que no varíe al cargar
                )

                # Renderizar con la barra de herramientas oculta
                st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
                
        else:
            st.info("💡 La evolución aparecerá cuando haya resultados en la tabla.")

        # --- CURIOSIDADES ---
        st.markdown("---")
        st.subheader("💡 ¿Sabías que...?")
        if not partidos_jugados.empty:
            aciertos_list = []
            for _, p in partidos_jugados.iterrows():
                id_p = p['N_PARTIDO']
                total_ac = 0
                pros_p = df_pro_all[df_pro_all['N_PARTIDO'] == id_p]
                t_real = 1 if p['R1'] > p['R2'] else (2 if p['R2'] > p['R1'] else 0)
                for _, pr in pros_p.iterrows():
                    if (1 if pr['P1'] > pr['P2'] else (2 if pr['P2'] > pr['P1'] else 0)) == t_real:
                        total_ac += 1
                aciertos_list.append({"Partido": f"{p['Equipo_1']} vs {p['Equipo_2']}", "Cant": total_ac})
            
            df_h = pd.DataFrame(aciertos_list)
            st.write(f"✅ **Más fácil:** {df_h.loc[df_h['Cant'].idxmax()]['Partido']}")
            st.write(f"😱 **Sorpresa:** {df_h.loc[df_h['Cant'].idxmin()]['Partido']}")

        # --- ESTADÍSTICAS GLOBALES ---
        st.markdown("---")
        st.subheader("📊 Global")
        c1, c2 = st.columns(2)
        c1.metric("🎯 Exactos", int(df_ranking["EXACTOS"].sum()))
        c2.metric("✅ Grales", int(df_ranking["GENERALES"].sum()))

#---------- MENU MIS PRONOSTICOS (FORMATO ESTABLE) ----------------------------------

elif menu == "📝 Mis Pronósticos":
    with col_principal:
        st.subheader("📝 Mis Predicciones")
        
        # 1. USAR DATOS YA CARGADOS (Sin llamar a la API de nuevo)
        # Estas variables ya las definimos arriba de todo en la App
        user_actual = st.session_state['user_data']['USUARIO']
        
        # Filtramos localmente (esto es instantáneo y no consume API)
        df_user_pro = df_pro[df_pro['USUARIO'] == user_actual]

        # --- Lógica de tiempo (se mantiene igual) ---
        ahora_arg = datetime.utcnow() - timedelta(hours=3)
        fecha_limite = datetime(2026, 6, 8, 23, 59, 59)
        es_tiempo_valido = ahora_arg < fecha_limite

        if es_tiempo_valido:
            st.success(f"⏳ Tienes tiempo hasta el 08/06.")
            modo_edicion = st.toggle("🔓 Editar resultados")
        else:
            st.error("🔒 Plazo finalizado.")
            modo_edicion = False
        
        esta_bloqueado = not (es_tiempo_valido and modo_edicion)

        with st.form("form_pronosticos_v3"):
            lista_nuevos_pro = []
            
            for i, row in df_res.sort_values('N_PARTIDO').iterrows():
                id_p = int(row['N_PARTIDO'])
                match = df_user_pro[df_user_pro['N_PARTIDO'] == id_p]
                
                v1 = int(match.iloc[0]['P1']) if not match.empty and pd.notna(match.iloc[0]['P1']) else 0
                v2 = int(match.iloc[0]['P2']) if not match.empty and pd.notna(match.iloc[0]['P2']) else 0
                
                bandera1 = get_flag_img(row['Equipo_1'])
                bandera2 = get_flag_img(row['Equipo_2'])
                            
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
                
                c1, c_vs, c2 = st.columns([1, 0.2, 1])
                with c1:
                    p1_val = st.number_input(f"G1_{id_p}", 0, 15, v1, key=f"f1_{id_p}", label_visibility="collapsed", disabled=esta_bloqueado)
                with c_vs:
                    st.write("<div style='text-align:center; margin-top:5px; font-weight:bold;'>:</div>", unsafe_allow_html=True)
                with c2:
                    p2_val = st.number_input(f"G2_{id_p}", 0, 15, v2, key=f"f2_{id_p}", label_visibility="collapsed", disabled=esta_bloqueado)
                
                lista_nuevos_pro.append({"N_PARTIDO": id_p, "USUARIO": user_actual, "P1": p1_val, "P2": p2_val})

            # EL BOTÓN DEBE IR AQUÍ (Indentado igual que el 'for')
            if es_tiempo_valido and modo_edicion:
                if st.form_submit_button("💾 GUARDAR TODO EL PRODE", use_container_width=True):
                    # 1. Intentamos la operación técnica
                    try:
                        df_pro_full = conn.read(worksheet="PRONOSTICOS", ttl=0)
                        df_otros = df_pro_full[df_pro_full['USUARIO'] != user_actual]
                        df_final = pd.concat([df_otros, pd.DataFrame(lista_nuevos_pro)], ignore_index=True)
                        
                        conn.update(worksheet="PRONOSTICOS", data=df_final)
                        st.cache_data.clear()
                        # Si llegamos aquí, los datos ya están en Google
                        exito = True 
                    except Exception as e:
                        st.error(f"Error de conexión: {e}")
                        exito = False
                    
                    # 2. Si fue exitoso, mostramos globos y reiniciamos FUERA del try
                    if exito:
                        st.success("✅ ¡Pronósticos guardados correctamente!")
                        st.balloons()
                        st.rerun()

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
        st.subheader("👥 Comunidad de Jugadores")
        
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
            foto_mini = u['AVATAR_URL'] if pd.notna(u['AVATAR_URL']) and u['AVATAR_URL'] != "" else "https://flaticon.com"
            st.markdown(f"""
                <div style="background: rgba(255,255,255,0.8); padding: 8px; border-radius: 10px; margin-bottom: 5px; display: flex; align-items: center; gap: 12px; border: 1px solid #ddd;">
                    <img src="{foto_mini}" width="35" height="35" style="border-radius: 50%; object-fit: cover;">
                    <span style="color:#333;"><b>{u['NOMBRE']}</b> — <small>{u['EQUIPO FAVORITO']}</small></span>
                </div>
            """, unsafe_allow_html=True)

    # with col_derecha:
    #     if 'user_sel' in locals():
    #         # Traemos la foto del usuario seleccionado (GCS o genérica)
    #         foto_j = user_sel['AVATAR_URL'] if pd.notna(user_sel['AVATAR_URL']) else "https://w3schools.com"
            
    #         # Mostramos la tarjeta del jugador
    #         st.markdown(f"""
    #             <div style="text-align: center; background-color: #f8f9fa; padding: 20px; border-radius: 15px; border: 1px solid #ddd;">
    #                 <img src="{foto_j}" style="border-radius: 50%; width: 100px; height: 100px; object-fit: cover; border: 3px solid #28a745;">
    #                 <h3 style="margin-bottom: 0;">{user_sel['NOMBRE']}</h3>
    #                 <p style="color: gray; font-size: 0.9em;">@{user_sel['USUARIO']}</p>
    #                 <p style="margin-top: 10px;"><b>⚽ Hincha de:</b> {user_sel['EQUIPO FAVORITO']}</p>
    #                 <p style="font-size: 0.85em; color: #555;"><i>"{user_sel['DESCRIPCION']}"</i></p>
    #             </div>
    #         """, unsafe_allow_html=True)
            
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
            st.write(f"🗳️ **Predicciones de {user_sel['NOMBRE']}:**")
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
            foto_msg = u_match.iloc[0]['AVATAR_URL'] if not u_match.empty and pd.notna(u_match.iloc[0]['AVATAR_URL']) else "https://flaticon.com"
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
        
        # --- EL DECÁLOGO DEL PRODE 2026 (ESTILO SOBRIO AZUL PROFUNDO) ---
        st.markdown("""
        <div style="background: rgba(240, 242, 246, 0.85); padding: 25px; border-radius: 15px; border: 1px solid rgba(3, 41, 73, 0.2); backdrop-filter: blur(10px); box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.15);">
            <h4 style="text-align: center; color: rgb(3, 41, 73); margin-top: 0; margin-bottom: 25px; font-family: sans-serif; letter-spacing: 2px; font-weight: 800; text-transform: uppercase;">📜 EL DECÁLOGO DEL PRODE</h4>
            <ol style="font-size: 0.95em; color: #333333; padding-left: 25px; font-family: sans-serif;">
                <li style="margin-bottom: 15px; line-height: 1.6; font-weight: bold; color: rgb(3, 41, 73);">
                    <span style="font-weight: normal; color: #333333;"><b style="color: rgb(3, 41, 73);">Respetar al rival:</b> La chicana es parte del juego, la falta de respeto no.</span>
                </li>
                <li style="margin-bottom: 15px; line-height: 1.6; font-weight: bold; color: rgb(3, 41, 73);">
                    <span style="font-weight: normal; color: #333333;"><b style="color: rgb(3, 41, 73);">Ley del VAR:</b> ¡Prohibido llorar por el VAR!, a Pe-la-se!.</span>
                </li>
                <li style="margin-bottom: 15px; line-height: 1.6; font-weight: bold; color: rgb(3, 41, 73);">
                    <span style="font-weight: normal; color: #333333;"><b style="color: rgb(3, 41, 73);">Fair Play:</b> No tontié, no pidas que te editen un resultado después del 8/6.</span>
                </li>
                <li style="margin-bottom: 15px; line-height: 1.6; font-weight: bold; color: rgb(3, 41, 73);">
                    <span style="font-weight: normal; color: #333333;"><b style="color: rgb(3, 41, 73);">El Puntero:</b> Al que va primero en el ranking se le respeta... o se le envidia.</span>
                </li>
                <li style="margin-bottom: 15px; line-height: 1.6; font-weight: bold; color: rgb(3, 41, 73);">
                    <span style="font-weight: normal; color: #333333;"><b style="color: rgb(3, 41, 73);">Grito de Gol:</b> Se permite escribir "¡GOOOOL!" en mayúsculas.</span>
                </li>
                <li style="margin-bottom: 15px; line-height: 1.6; font-weight: bold; color: rgb(3, 41, 73);">
                    <span style="font-weight: normal; color: #333333;"><b style="color: rgb(3, 41, 73);">La Cábala:</b> No se revelan las cábalas personales.</span>
                </li>
                <li style="margin-bottom: 15px; line-height: 1.6; font-weight: bold; color: rgb(3, 41, 73);">
                    <span style="font-weight: normal; color: #333333;"><b style="color: rgb(3, 41, 73);">Oliver Atom:</b> Recuerda que: "¡El balón está vivo!" y que "El partido no se termina hasta que se termina" .</span>
                </li>
                <li style="margin-bottom: 15px; line-height: 1.6; font-weight: bold; color: rgb(3, 41, 73);">
                    <span style="font-weight: normal; color: #333333;"><b style="color: rgb(3, 41, 73);">Sabiduría:</b> Si no sabes de fútbol, fingí que sí; los puntos no mienten wachx.</span>
                </li>
                <li style="margin-bottom: 15px; line-height: 1.6; font-weight: bold; color: rgb(3, 41, 73);">
                    <span style="font-weight: normal; color: #333333;"><b style="color: rgb(3, 41, 73);">Puntualidad:</b> No dejes para mañana el pronóstico que puedes cargar hoy, amen.</span>
                </li>
                <li style="margin-bottom: 15px; line-height: 1.6; font-weight: bold; color: rgb(3, 41, 73);">
                    <span style="font-weight: normal; color: #333333;"><b style="color: rgb(3, 41, 73);">La Gloria:</b> ¡Disfrutar el mundial! ⚽</span>
                </li>
            </ol>
        </div>
        """, unsafe_allow_html=True)
        
# ---------- MENU ADMIN ----------------------------------------------------

elif menu == "⚙️ Panel Control":
    if st.session_state['user_data']['ROL'] == 'admin':
        with col_principal:
            st.subheader("⚙️ Gestión de Resultados y Horarios")
            df_res_admin = conn.read(worksheet="RESULTADOS", ttl=10)
            
            with st.form("form_admin_full"):
                upd = []
                # --- DENTRO DEL FORM DE ADMIN ---
                for i, row in df_res_admin.iterrows():
                    st.markdown(f"**Partido Nº {int(row['N_PARTIDO'])}: {row['Equipo_1']} vs {row['Equipo_2']}**")
    
                    c_dia, c_hora, c_viz = st.columns([1, 1, 1])
                    n_dia = c_dia.text_input("Día", value=row['DIA'] if pd.notna(row['DIA']) else "", key=f"d_{i}")
                    n_hora = c_hora.text_input("Hora", value=row['HORA'] if pd.notna(row['HORA']) else "", key=f"h_{i}")
    # Checkbox para visibilidad
                    v_actual = bool(row['VIZ']) if pd.notna(row['VIZ']) else False
                    n_viz = c_viz.checkbox("👁️ Visible", value=v_actual, key=f"v_{i}")
    
                    c1, c2, c3 = st.columns([1, 1, 1])
                    r1 = c1.number_input("G1", 0, 20, int(row['R1']) if pd.notna(row['R1']) else 0, key=f"ar1_{i}")
                    r2 = c2.number_input("G2", 0, 20, int(row['R2']) if pd.notna(row['R2']) else 0, key=f"ar2_{i}")
                    fin = c3.checkbox("¿Finalizado?", value=pd.notna(row['R1']), key=f"fin_{i}")
    
                    upd.append({
                    "N_PARTIDO": row['N_PARTIDO'], "Equipo_1": row['Equipo_1'], 
                    "R1": r1 if fin else None, "Equipo_2": row['Equipo_2'], "R2": r2 if fin else None,
                    "DIA": n_dia, "HORA": n_hora, "VIZ": n_viz # Guardamos la visibilidad
                    })
                    st.markdown("---")
                
                if st.form_submit_button("📢 Guardar Cambios Globales", use_container_width=True):
                    conn.update(worksheet="RESULTADOS", data=pd.DataFrame(upd))
                    st.cache_data.clear()
                    st.success("✅ ¡Base de datos actualizada!")
                    st.rerun()

        # --- COLUMNA DERECHA: GESTIÓN DE USUARIOS (40%) ---
        with col_derecha:
#---------------------------test
            # st.subheader("🧪 Test: Conexión con Ranking Global")
            
            # # 1. Recuperamos el Ranking del Session State (la "Fuente Única de Verdad")
            # df_global = st.session_state.get('df_ranking_global')
        
            # if df_global is None:
            #     st.error("⚠️ El Ranking Global no está inicializado en el Session State.")
            #     # Opcional: Forzar carga si no existe
            #     if st.button("🔄 Inicializar Ranking Global"):
            #         st.session_state['df_ranking_global'] = obtener_ranking_global(df_usuarios, df_pro, df_res)
            #         st.rerun()
            # else:
            #     # 2. Selector de usuario (usando el DF global para asegurar que existan)
            #     nombres_rank = df_global['JUGADOR'].tolist()
            #     nombre_test = st.selectbox("Selecciona un jugador del ranking:", nombres_rank, index=None)
        
            #     if nombre_test:
            #         # 3. Buscamos los datos DIRECTAMENTE en el DataFrame global
            #         match = df_global[df_global['JUGADOR'] == nombre_test]
                    
            #         if not match.empty:
            #             idx_real = match.index[0]
            #             datos_vivos = match.iloc[0]
                        
            #             # Buscamos datos extra (Avatar, Bio) en la tabla de usuarios original
            #             u_info = df_usuarios[df_usuarios['NOMBRE'] == nombre_test].iloc[0]
        
            #             # --- 4. LÓGICA DE INSIGNIAS (Sin cálculos, solo lectura) ---
            #             css = {k: "filter: grayscale(100%); opacity: 0.15;" for k in ["puntero", "master", "mentalista", "lento", "onfire", "fundador"]}
                        
            #             # Puntero: Posición 1 (índice 0)
            #             if idx_real == 0 and datos_vivos['PUNTOS'] > 0: css["puntero"] = ""
                        
            #             # Master: Exactos >= 5
            #             if int(datos_vivos['EXACTOS']) >= 5: css["master"] = ""
                        
            #             # Mentalista: Si tiene el máximo de generales
            #             if int(datos_vivos['GENERALES']) == df_global['GENERALES'].max() and df_global['GENERALES'].max() > 0:
            #                 css["mentalista"] = ""
                        
            #             # Lento: Última posición
            #             if len(df_global) > 2 and idx_real == (len(df_global) - 1): css["lento"] = ""
        
            #             # Fundador: ID <= 3
            #             if int(u_info['ID']) <= 3: css["fundador"] = ""
        
            #             # --- 5. RENDERIZADO ---
            #             foto = u_info.get('AVATAR_URL')
            #             if not foto or pd.isna(foto):
            #                 foto = f"https://ui-avatars.com{nombre_test}&background=random"
        
            #             st.markdown(f"""
            #                 <div style="display: flex; align-items: center; background: #fdfdfd; padding: 15px; border-radius: 12px; border: 1px solid #007bff; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
            #                     <div style="flex: 0 0 90px; text-align: center; border-right: 1px solid #eee; padding-right: 15px; margin-right: 15px;">
            #                         <img src="{foto}" style="border-radius: 50%; width: 70px; height: 70px; object-fit: cover; border: 2px solid #007bff;">
            #                         <div style="font-weight: bold; font-size: 0.85em; margin-top: 5px;">{nombre_test}</div>
            #                     </div>
            #                     <div style="flex: 1; display: flex; flex-wrap: wrap; justify-content: space-around; gap: 8px;">
            #                         <span title="Puntero" style="font-size: 1.7em; {css['puntero']}">🏆</span>
            #                         <span title="Master Exactos" style="font-size: 1.7em; {css['master']}">🎯</span>
            #                         <span title="Mentalista" style="font-size: 1.7em; {css['mentalista']}">🧙‍♂️</span>
            #                         <span title="Fundador" style="font-size: 1.7em; {css['fundador']}">🏅</span>
            #                         <span title="On Fire" style="font-size: 1.7em; {css['onfire']}">🔥</span>
            #                         <span title="El más lento" style="font-size: 1.7em; {css['lento']}">🐌</span>
            #                     </div>
            #                 </div>
            #             """, unsafe_allow_html=True)
                        
            #             st.success(f"Datos vinculados: Posición #{idx_real + 1} | Puntos: {datos_vivos['PUNTOS']}")
#---------------------------------------
        
            st.subheader("👥 Gestión de Usuarios")
            df_users_adm = conn.read(worksheet="USUARIOS", ttl=10)
            df_pro_adm = conn.read(worksheet="PRONOSTICOS", ttl=10)

            # Filtramos para no borrar al admin logueado
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

        # --- SECCIÓN DE MANTENIMIENTO (Alineada con el inicio del Panel de Control) ---
        st.markdown("---")
        st.subheader("🚧 Control de Mantenimiento")
        
        col_m1, col_m2 = st.columns([2, 1])
        
        with col_m1:
            if estado_mantenimiento == "ON":
                st.error("LA WEB ESTÁ BLOQUEADA PARA USUARIOS")
                if st.button("✅ DESACTIVAR MANTENIMIENTO (ABRIR WEB)", use_container_width=True):
                    df_up_m = pd.DataFrame({"MANTENIMIENTO": ["OFF"]})
                    conn.update(worksheet="CONFIG", data=df_up_m)
                    st.cache_data.clear()
                    st.rerun()
            else:
                st.success("LA WEB ESTÁ FUNCIONANDO NORMALMENTE")
                if st.button("🚫 ACTIVAR MANTENIMIENTO (CERRAR WEB)", use_container_width=True):
                    df_up_m = pd.DataFrame({"MANTENIMIENTO": ["ON"]})
                    conn.update(worksheet="CONFIG", data=df_up_m)
                    st.cache_data.clear()
                    st.rerun()
    else:
        # Este else pertenece al chequeo de ROL == 'admin' inicial
        st.error("No tienes permisos para acceder a esta sección.")
                 
