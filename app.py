import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection
from datetime import datetime
from datetime import datetime, timedelta
from google.auth.transport.requests import Request
from googleapiclient.http import MediaIoBaseUpload

st.set_page_config(page_title="Prode Mundial 2026", layout="wide")
st.title("🏆 Prode Mundial 2026 - Fase de Grupos")

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
                df_u = conn.read(worksheet="USUARIOS", ttl=10)
                user_match = df_u[(df_u['USUARIO'].astype(str) == str(u)) & (df_u['CONTRASEÑA'].astype(str) == str(p))]
                
                if not user_match.empty:
                    st.session_state['autenticado'] = True
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



# --- SIDEBAR DE BIENVENIDA ---
st.sidebar.write(f"Hola, **{st.session_state['user_data']['NOMBRE']}**")
if st.sidebar.button("Cerrar Sesión"):
    st.session_state['autenticado'] = False
    st.rerun()
    
# --- CARGA DE DATOS DE TABLAS GSHEET ---------------------------------------------------------------------------------------------
# ----LINK de Tablas
SHEET_ID = "16GQN19xyzi_9jRKsaryNMhB80meX9RsJhyHlAU3Ek4c"
URL_RES = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid=0"
URL_PRO = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid=394071446"

@st.cache_data(ttl=60) # Actualiza cada 1 minuto para pruebas
def load_data():
    # Forzamos la lectura de los resultados y pronósticos
    df_res = pd.read_csv(URL_RES)
    df_pro = pd.read_csv(URL_PRO)
    
    # LIMPIEZA CRÍTICA: Convertir columnas de goles a números, errores se vuelven NaN
    cols_res = ['R1', 'R2']
    for col in cols_res:
        df_res[col] = pd.to_numeric(df_res[col], errors='coerce')
        
    return df_res, df_pro

df_res, df_pro = load_data()
#----------------------------------------------------------

df_res, df_pro = load_data()
df_usuarios = conn.read(worksheet="USUARIOS", ttl=10)

# Inyectar Ranking Global
st.session_state['df_ranking_global'] = obtener_ranking_global(df_usuarios, df_pro, df_res)

# --- FUNCIÓN DE CÁLCULO MEJORADA -------------------------------------------
    
def calcular_detalle(r1, r2, p1, p2):
    if pd.isna(r1) or pd.isna(r2) or pd.isna(p1) or pd.isna(p2):
        return 0, 0, 0 
    
    puntos, exactos, generales = 0, 0, 0
    r1, r2, p1, p2 = int(r1), int(r2), int(p1), int(p2)
    
    tendencia_real = 1 if r1 > r2 else (2 if r2 > r1 else 0)
    tendencia_pron = 1 if p1 > p2 else (2 if p2 > p1 else 0)
    
    # 1. Si acertó la tendencia, SIEMPRE es un acierto general
    if tendencia_real == tendencia_pron:
        generales = 1
        puntos = 1 # Punto base por tendencia
        
        # 2. Si además los goles son idénticos, sumamos el bono de exacto
        if r1 == p1 and r2 == p2:
            exactos = 1
            puntos = 3 # Cambia a 3 (o += 2 si prefieres verlo como bono)
            
    return puntos, exactos, generales
    
# --- LÓGICA DE RANKING ACTUALIZADA (VERTICAL) -------------------------------------

# 1. Cargamos los datos más recientes
df_res_oficial = df_res 
df_pro_total = conn.read(worksheet="PRONOSTICOS", ttl=10)
df_users_list = conn.read(worksheet="USUARIOS", ttl=10)
#----------------------------


@st.cache_data(ttl=60) # Cache de 1 minuto para pruebas
def obtener_ranking_global(df_users, df_pro, df_res):
    ranking_data = []
    for _, u in df_users.iterrows():
        u_nick = u['USUARIO']
        pts_t, exa_t, gen_t = 0, 0, 0
        pro_usr = df_pro[df_pro['USUARIO'] == u_nick]
        
        for _, p in pro_usr.iterrows():
            res_p = df_res[df_res['N_PARTIDO'] == p['N_PARTIDO']]
            if not res_p.empty and pd.notna(res_p.iloc[0]['R1']):
                pts, exa, gen = calcular_detalle(res_p.iloc[0]['R1'], res_p.iloc[0]['R2'], p['P1'], p['P2'])
                pts_t += pts; exa_t += exa; gen_t += gen
        
        ranking_data.append({'USUARIO': u_nick, 'JUGADOR': u['NOMBRE'], 'PUNTOS': pts_t, 'EXACTOS': exa_t, 'GENERALES': gen_t})
    
    df_rank = pd.DataFrame(ranking_data).sort_values(by='PUNTOS', ascending=False).reset_index(drop=True)
    return df_rank

#--------------------------------------------------------
# Función de apoyo para procesar insignias dentro de la tabla
def procesar_nombres_ranking(row, df, df_pro, df_res, df_users):
    nombre = row['JUGADOR']
    posicion = row.name + 1 
    insignias = ""
    
    # Buscamos datos extra del usuario (ID y Nick) para racha y fundador
    u_info = df_users[df_users['NOMBRE'] == nombre].iloc[0]
    u_nick = u_info['USUARIO']
    u_id = int(u_info['ID'])

    if posicion == 1: insignias += " 👑" # Puntero
    if row['EXACTOS'] >= 5: insignias += " 🎯" # Master
    
    max_gen = df['GENERALES'].max()
    if row['GENERALES'] == max_gen and max_gen > 0: insignias += " 🧙‍♂️" # Mentalista
    if u_id <= 3: insignias += " 🏅" # Fundador
    if len(df) > 2 and posicion == len(df): insignias += " 🐌" # Lento
        
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

# 2. Procesamos el Ranking por cada usuario registrado
ranking_data = []

for _, u_row in df_users_list.iterrows():
    u_nick = u_row['USUARIO']
    u_nombre = u_row['NOMBRE']
    total_pts, total_exa, total_gen = 0, 0, 0
    
    pronos_usuario = df_pro_total[df_pro_total['USUARIO'] == u_nick]
    
    for _, res_row in df_res_oficial.iterrows():
        id_p = res_row['N_PARTIDO']
        p_row = pronos_usuario[pronos_usuario['N_PARTIDO'] == id_p]
        
        if not p_row.empty:
            pts, exa, gen = calcular_detalle(
                res_row['R1'], res_row['R2'],
                p_row.iloc[0]['P1'], p_row.iloc[0]['P2']
            )
            total_pts += pts
            total_exa += exa
            total_gen += gen
            
    ranking_data.append({
        "JUGADOR": u_nombre,
        "PUNTOS": total_pts,
        "EXACTOS": total_exa,
        "GENERALES": total_gen
    })

# 3. Creamos el DataFrame, ordenamos y aplicamos insignias
df_ranking = pd.DataFrame(ranking_data).sort_values(by=["PUNTOS", "EXACTOS"], ascending=False).reset_index(drop=True)

if not df_ranking.empty:
    df_ranking['JUGADOR'] = df_ranking.apply(
        lambda row: procesar_nombres_ranking(row, df_ranking, df_pro_total, df_res_oficial, df_users_list), 
        axis=1
    )

# 4. Formateo final de la tabla
df_ranking.index = df_ranking.index + 1
df_ranking.insert(0, "Nº", df_ranking.index.astype(str))
df_ranking = df_ranking[["Nº", "JUGADOR", "PUNTOS", "EXACTOS", "GENERALES"]]


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

        # --- BLOQUE 2: FORO (Actividad Reciente) ---------------------------------------------------------------------------------------
        st.subheader("💬 Actividad Reciente")
        df_foro_inicio = conn.read(worksheet="FORO", ttl=10)
        df_u_ref = conn.read(worksheet="USUARIOS", ttl=10) 
        
        with st.container(height=350):
            if df_foro_inicio.empty:
                st.info("No hay mensajes aún.")
            else:
                u_act = st.session_state['user_data']['USUARIO']
                for idx, m in df_foro_inicio.tail(10).iloc[::-1].iterrows():
                    # Buscamos la foto en la tabla de usuarios
                    u_match = df_u_ref[df_u_ref['USUARIO'] == m['USUARIO']]
                    foto_url = u_match.iloc[0]['AVATAR_URL'] if not u_match.empty and pd.notna(u_match.iloc[0]['AVATAR_URL']) else "https://flaticon.com"
                    
                    es_m = m['USUARIO'] == u_act
                    aln = "flex-end" if es_m else "flex-start"
                    bg = "#dcf8c6" if es_m else "#ffffff"
                    
                    st.markdown(f"""
                        <div style="display: flex; flex-direction: column; align-items: {aln}; margin-bottom: 10px; width: 100%;">
                            <div style="display: flex; align-items: center; gap: 8px; flex-direction: {'row-reverse' if es_m else 'row'};">
                                <img src="{foto_url}" style="border-radius: 50%; width: 30px; height: 30px; object-fit: cover; border: 1px solid #ddd;">
                                <div style="max-width: 85%; background-color: {bg}; padding: 10px 12px; border-radius: 18px; border: 1px solid #ddd;">
                                    <div style="font-size: 0.8em; color: #555; font-weight: bold;">{m['NOMBRE']}</div>
                                    <div style="font-size: 1em; color: #333;">{m['MENSAJE']}</div>
                                </div>
                            </div>
                        </div>
                    """, unsafe_allow_html=True)
#---------------------------------MENU INICIO / RANKING ------------------------------------------------------
    with col_derecha:
        st.subheader("📊 Ranking")
        try:
        # Forzamos lectura fresca
            df_ranking_view = df_ranking.copy()
            st.dataframe(
                df_ranking_view, 
                use_container_width=True, 
                hide_index=True,
                column_config={
                    "Nº": st.column_config.TextColumn("Nº", width="small"),
                    "PUNTOS": st.column_config.NumberColumn("PUNTOS"),
                    "EXACTOS": st.column_config.NumberColumn("🎯"),
                    "GENERALES": st.column_config.NumberColumn("✅")
                }
            )
        except Exception as e:
            st.error("No se pudo cargar el ranking. Reintentando...")
            st.cache_data.clear()

        st.markdown("---")
        st.subheader("📈 Estadísticas")
        if not df_ranking.empty:
            t_ex = df_ranking["EXACTOS"].sum()
            t_gr = df_ranking["GENERALES"].sum()
            st.metric("Total Exactos", int(t_ex))
            st.metric("Total Generales", int(t_gr))

#---------- MENU MIS PRONOSTICOS (FORMATO ESTABLE) ----------------------------------

elif menu == "📝 Mis Pronósticos":
    with col_principal:
        st.subheader("📝 Mis Predicciones")
        
        ahora_arg = datetime.now() - timedelta(hours=3)        
        fecha_limite = datetime(2026, 6, 8, 23, 59, 59)
        es_tiempo_valido = ahora_arg < fecha_limite
        
        # Carga segura con manejo de errores
        try:
            user_actual = st.session_state['user_data']['USUARIO']
            df_res_p = conn.read(worksheet="RESULTADOS", ttl=10)
            df_pro_all = conn.read(worksheet="PRONOSTICOS", ttl=10)
            df_user_pro = df_pro_all[df_pro_all['USUARIO'] == user_actual]
        except Exception:
            st.error("⚠️ Conexión saturada. Por favor, refresca la página.")
            st.stop()

        if es_tiempo_valido:
            st.success(f"⏳ Tienes tiempo hasta el 08/06.")
            modo_edicion = st.toggle("🔓 Editar resultados", help="Activa para modificar")
        else:
            st.error("🔒 Plazo finalizado.")
            modo_edicion = False
        
        esta_bloqueado = not (es_tiempo_valido and modo_edicion)

        # VOLVEMOS AL FORMULARIO PARA ESTABILIDAD
        with st.form("form_pronosticos_v3"):
            lista_nuevos_pro = []
            
            for i, row in df_res_p.sort_values('N_PARTIDO').iterrows():
                id_p = int(row['N_PARTIDO'])
                match = df_user_pro[df_user_pro['N_PARTIDO'] == id_p]
                
                v1 = int(match.iloc[0]['P1']) if not match.empty and pd.notna(match.iloc[0]['P1']) else 0
                v2 = int(match.iloc[0]['P2']) if not match.empty and pd.notna(match.iloc[0]['P2']) else 0
                
                # Banderas
                bandera1 = get_flag_img(row['Equipo_1'])
                bandera2 = get_flag_img(row['Equipo_2'])
                
                # Cabecera Compacta
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
                
                # Inputs de número (El formato que no falla)
                c1, c_vs, c2 = st.columns([1, 0.2, 1])
                with c1:
                    p1_val = st.number_input(f"G1_{id_p}", 0, 15, v1, key=f"f1_{id_p}", label_visibility="collapsed", disabled=esta_bloqueado)
                with c_vs:
                    st.write("<div style='text-align:center; margin-top:5px; font-weight:bold;'>:</div>", unsafe_allow_html=True)
                with c2:
                    p2_val = st.number_input(f"G2_{id_p}", 0, 15, v2, key=f"f2_{id_p}", label_visibility="collapsed", disabled=esta_bloqueado)
                
                lista_nuevos_pro.append({"N_PARTIDO": id_p, "USUARIO": user_actual, "P1": p1_val, "P2": p2_val})
                st.markdown("<div style='margin-bottom:10px;'></div>", unsafe_allow_html=True)

            # Botón de envío del formulario
            if es_tiempo_valido and modo_edicion:
                if st.form_submit_button("💾 GUARDAR TODO EL PRODE", use_container_width=True):
                    df_otros = df_pro_all[df_pro_all['USUARIO'] != user_actual]
                    df_final = pd.concat([df_otros, pd.DataFrame(lista_nuevos_pro)], ignore_index=True)
                    conn.update(worksheet="PRONOSTICOS", data=df_final)
                    st.cache_data.clear()
                    st.success("✅ ¡Pronósticos guardados!")
                    st.balloons()
                    st.rerun()
            else:
                st.form_submit_button("🔒 Edición Bloqueada", disabled=True, use_container_width=True)

                

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
    with col_principal:
        st.subheader("👥 Jugadores Inscritos")
        df_usuarios = conn.read(worksheet="USUARIOS", ttl=10)
        
        if not df_usuarios.empty:
            # 1. Buscador de jugadores
            nombres_jugadores = df_usuarios['NOMBRE'].tolist()
            nombre_sel = st.selectbox("Seleccioná un familiar para ver su perfil:", nombres_jugadores)
            
            # Obtenemos la fila del usuario seleccionado
            user_sel = df_usuarios[df_usuarios['NOMBRE'] == nombre_sel].iloc[0]
            
            # --- ESPACIO PARA GRÁFICO O INFO EXTRA ---
            st.markdown("---")
            st.write("### 📋 Lista General de la Familia")
            # Mostramos una tabla prolija con los datos públicos
            st.dataframe(df_usuarios[['NOMBRE', 'EQUIPO FAVORITO', 'DESCRIPCION']], 
                         use_container_width=True, hide_index=True)

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
        if 'user_sel' in locals():
            u_sel = user_sel
            
            # --- 1. LIMPIEZA DE DATOS PARA EMPAREJAR ---
            # Nombre del usuario seleccionado (limpio)
            nom_sel = str(u_sel['NOMBRE']).strip().lower()
            
            # Buscamos la fila en el ranking (limpiando el ranking también)
            df_rank_tmp = df_ranking.copy()
            df_rank_tmp['JUGADOR_CLEAN'] = df_rank_tmp['JUGADOR'].astype(str).str.strip().str.lower()
            
            user_en_ranking = df_rank_tmp[df_rank_tmp['JUGADOR_CLEAN'] == nom_sel]
            
            # Inicializamos todo en gris (CSS)
            css = {
                "puntero": "filter: grayscale(100%); opacity: 0.15;",
                "master": "filter: grayscale(100%); opacity: 0.15;",
                "mentalista": "filter: grayscale(100%); opacity: 0.15;",
                "lento": "filter: grayscale(100%); opacity: 0.15;",
                "onfire": "filter: grayscale(100%); opacity: 0.15;",
                "fundador": "filter: grayscale(100%); opacity: 0.15;"
            }
            label_fire = ""

            # --- 2. LÓGICA DE INSIGNIAS ---
            if not user_en_ranking.empty:
                idx = user_en_ranking.index[0] # Posición real en el ranking
                row_r = user_en_ranking.iloc[0]
                
                # 🏆 PUNTERO: Si es la primera fila del ranking
                if idx == 0: css["puntero"] = ""

                # 🎯 MASTER: Exactos >= 5
                if int(row_r.get('EXACTOS', 0)) >= 5: css["master"] = ""
                
                # 🧙‍♂️ MENTALISTA: Si coincide con el máximo de generales
                max_gen = pd.to_numeric(df_ranking['GENERALES'], errors='coerce').max()
                if int(row_r.get('GENERALES', 0)) == max_gen and max_gen > 0:
                    css["mentalista"] = ""

                # 🐌 LENTO: Si es el último del ranking (y hay más de 2)
                if len(df_ranking) > 2 and idx == (len(df_ranking) - 1):
                    css["lento"] = ""

            # 🏅 FUNDADOR: (Independiente del ranking)
            if int(u_sel.get('ID', 99)) <= 3: 
                css["fundador"] = ""

            # 🔥 ON FIRE: (Cálculo de racha)
            u_nick = u_sel['USUARIO']
            u_pro = df_pro_total[df_pro_total['USUARIO'] == u_nick].sort_values('N_PARTIDO')
            r_act, r_max = 0, 0
            for _, p in u_pro.iterrows():
                p_ref = df_res[df_res['N_PARTIDO'] == p['N_PARTIDO']]
                if not p_ref.empty and pd.notna(p_ref.iloc[0]['R1']):
                    _, exa, _ = calcular_detalle(p_ref.iloc[0]['R1'], p_ref.iloc[0]['R2'], p['P1'], p['P2'])
                    if exa == 1:
                        r_act += 1
                        r_max = max(r_max, r_act)
                    else: r_act = 0
            
            if r_max >= 3:
                css["onfire"] = ""; label_fire = f"x{r_max}"

            # --- 3. DISEÑO VISUAL ---
            foto = u_sel.get('AVATAR_URL')
            if not foto or pd.isna(foto):
                foto = f"https://ui-avatars.com{u_sel['NOMBRE']}&background=random"

            st.markdown(f"""
                <div style="display: flex; align-items: center; background: white; padding: 15px; border-radius: 12px; border: 1px solid #eee; box-shadow: 0 2px 4px rgba(0,0,0,0.05); margin-bottom: 10px;">
                    <div style="flex: 0 0 90px; text-align: center; border-right: 1px solid #eee; padding-right: 15px; margin-right: 15px;">
                        <img src="{foto}" style="border-radius: 50%; width: 70px; height: 70px; object-fit: cover; border: 2px solid #007bff;">
                        <div style="font-weight: bold; font-size: 0.8em; margin-top: 5px;">{u_sel['NOMBRE']}</div>
                        <div style="font-size: 0.65em; color: #007bff;">{u_sel.get('EQUIPO FAVORITO', '')}</div>
                    </div>
                    <div style="flex: 1; display: flex; flex-wrap: wrap; justify-content: space-around; gap: 5px;">
                        <span title="Puntero" style="font-size: 1.7em; {css['puntero']}">🏆</span>
                        <span title="Master Exactos" style="font-size: 1.7em; {css['master']}">🎯</span>
                        <span title="Mentalista" style="font-size: 1.7em; {css['mentalista']}">🧙‍♂️</span>
                        <span title="Fundador" style="font-size: 1.7em; {css['fundador']}">🏅</span>
                        <span title="On Fire {label_fire}" style="font-size: 1.7em; {css['onfire']}">🔥</span>
                        <span title="El más lento" style="font-size: 1.7em; {css['lento']}">🐌</span>
                    </div>
                </div>
                <div style="padding: 0 10px;">
                    <p style="font-size: 0.8em; color: #666; font-style: italic;">"{u_sel.get('DESCRIPCION', '')}"</p>
                </div>
            """, unsafe_allow_html=True)
                
            # --- 4. PREDICCIONES DEL USUARIO ---
            st.markdown("---")
            st.write(f"🗳️ **Predicciones de {user_sel['NOMBRE']}:**")
            pro_user_sel = df_pro_total[df_pro_total['USUARIO'] == user_sel['USUARIO']]
                
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
        else:
            # Esto aparece si no hay nadie seleccionado
            st.info("Selecciona un jugador del ranking para ver sus logros.")

        
# ---------- MENU FORO ----------------------------------------------------


elif menu == "💬 Foro":
    df_foro = conn.read(worksheet="FORO", ttl=10)
    user_actual = st.session_state['user_data']['USUARIO']
    
    with col_principal:
        st.subheader("💬 Muro de la Comunidad")
        
        # Caja para publicar
        with st.expander("✍️ Publicar un comentario", expanded=False):
            with st.form("nuevo_post_full", clear_on_submit=True):
                texto = st.text_area("¿Qué quieres decir?", max_chars=250)
                if st.form_submit_button("🚀 Publicar", use_container_width=True):
                    if texto.strip():
                        nuevo_msg = {
                            "FECHA": (datetime.now() - timedelta(hours=3)).strftime("%d/%m %H:%M"),
                            "USUARIO": user_actual,
                            "NOMBRE": st.session_state['user_data']['NOMBRE'],
                            "MENSAJE": texto.strip(),
                            "PARTIDO_ID": 0
                        }
                        df_update = pd.concat([df_foro, pd.DataFrame([nuevo_msg])], ignore_index=True)
                        conn.update(worksheet="FORO", data=df_update)
                        st.cache_data.clear()
                        st.rerun()

        st.markdown("---")

        # Listado de mensajes estilo Chat
        if df_foro.empty:
            st.info("No hay mensajes aún.")
        else:
            for index, m in df_foro.iloc[::-1].iterrows():
                es_mio = m['USUARIO'] == user_actual
                align = "flex-end" if es_mio else "flex-start"
                bg_color = "#dcf8c6" if es_mio else "#ffffff"
                
                # Burbuja de mensaje
                st.markdown(f"""
                    <div style="display: flex; flex-direction: column; align-items: {align}; margin-bottom: 15px; width: 100%;">
                        <div style="max-width: 85%; background-color: {bg_color}; padding: 15px; border-radius: 18px; border: 1px solid #ddd; box-shadow: 1px 1px 3px rgba(0,0,0,0.1);">
                            <div style="font-size: 0.9em; color: #555; font-weight: bold; margin-bottom: 5px;">
                                {m['NOMBRE']} <span style="font-weight: normal; color: #999;">• {m['FECHA']}</span>
                            </div>
                            <div style="font-size: 1.1em; color: #222; line-height: 1.5; font-weight: 450;">
                                {m['MENSAJE']}
                            </div>
                        </div>
                    </div>
                """, unsafe_allow_html=True)
                
                # Botón de eliminar (Solo para Admin o dueño del mensaje)
                # Lo ponemos alineado con la burbuja
                col_del_1, col_del_2 = st.columns([0.8, 0.2]) if es_mio else st.columns([0.2, 0.8])
                
                with (col_del_2 if es_mio else col_del_1):
                    if st.session_state['user_data']['ROL'] == 'admin' or es_mio:
                        if st.button("🗑️", key=f"del_full_{index}", help="Eliminar"):
                            df_final = df_foro.drop(index)
                            conn.update(worksheet="FORO", data=df_final)
                            st.cache_data.clear()
                            st.rerun()

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
            st.subheader("🧪 Test: Conexión con Ranking Global")
            
            # 1. Recuperamos el Ranking del Session State (la "Fuente Única de Verdad")
            df_global = st.session_state.get('df_ranking_global')
        
            if df_global is None:
                st.error("⚠️ El Ranking Global no está inicializado en el Session State.")
                # Opcional: Forzar carga si no existe
                if st.button("🔄 Inicializar Ranking Global"):
                    st.session_state['df_ranking_global'] = obtener_ranking_global(df_usuarios, df_pro, df_res)
                    st.rerun()
            else:
                # 2. Selector de usuario (usando el DF global para asegurar que existan)
                nombres_rank = df_global['JUGADOR'].tolist()
                nombre_test = st.selectbox("Selecciona un jugador del ranking:", nombres_rank, index=None)
        
                if nombre_test:
                    # 3. Buscamos los datos DIRECTAMENTE en el DataFrame global
                    match = df_global[df_global['JUGADOR'] == nombre_test]
                    
                    if not match.empty:
                        idx_real = match.index[0]
                        datos_vivos = match.iloc[0]
                        
                        # Buscamos datos extra (Avatar, Bio) en la tabla de usuarios original
                        u_info = df_usuarios[df_usuarios['NOMBRE'] == nombre_test].iloc[0]
        
                        # --- 4. LÓGICA DE INSIGNIAS (Sin cálculos, solo lectura) ---
                        css = {k: "filter: grayscale(100%); opacity: 0.15;" for k in ["puntero", "master", "mentalista", "lento", "onfire", "fundador"]}
                        
                        # Puntero: Posición 1 (índice 0)
                        if idx_real == 0 and datos_vivos['PUNTOS'] > 0: css["puntero"] = ""
                        
                        # Master: Exactos >= 5
                        if int(datos_vivos['EXACTOS']) >= 5: css["master"] = ""
                        
                        # Mentalista: Si tiene el máximo de generales
                        if int(datos_vivos['GENERALES']) == df_global['GENERALES'].max() and df_global['GENERALES'].max() > 0:
                            css["mentalista"] = ""
                        
                        # Lento: Última posición
                        if len(df_global) > 2 and idx_real == (len(df_global) - 1): css["lento"] = ""
        
                        # Fundador: ID <= 3
                        if int(u_info['ID']) <= 3: css["fundador"] = ""
        
                        # --- 5. RENDERIZADO ---
                        foto = u_info.get('AVATAR_URL')
                        if not foto or pd.isna(foto):
                            foto = f"https://ui-avatars.com{nombre_test}&background=random"
        
                        st.markdown(f"""
                            <div style="display: flex; align-items: center; background: #fdfdfd; padding: 15px; border-radius: 12px; border: 1px solid #007bff; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
                                <div style="flex: 0 0 90px; text-align: center; border-right: 1px solid #eee; padding-right: 15px; margin-right: 15px;">
                                    <img src="{foto}" style="border-radius: 50%; width: 70px; height: 70px; object-fit: cover; border: 2px solid #007bff;">
                                    <div style="font-weight: bold; font-size: 0.85em; margin-top: 5px;">{nombre_test}</div>
                                </div>
                                <div style="flex: 1; display: flex; flex-wrap: wrap; justify-content: space-around; gap: 8px;">
                                    <span title="Puntero" style="font-size: 1.7em; {css['puntero']}">🏆</span>
                                    <span title="Master Exactos" style="font-size: 1.7em; {css['master']}">🎯</span>
                                    <span title="Mentalista" style="font-size: 1.7em; {css['mentalista']}">🧙‍♂️</span>
                                    <span title="Fundador" style="font-size: 1.7em; {css['fundador']}">🏅</span>
                                    <span title="On Fire" style="font-size: 1.7em; {css['onfire']}">🔥</span>
                                    <span title="El más lento" style="font-size: 1.7em; {css['lento']}">🐌</span>
                                </div>
                            </div>
                        """, unsafe_allow_html=True)
                        
                        st.success(f"Datos vinculados: Posición #{idx_real + 1} | Puntos: {datos_vivos['PUNTOS']}")
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
                 
