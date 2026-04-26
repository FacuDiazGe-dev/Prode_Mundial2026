import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection
from datetime import datetime
from datetime import datetime, timedelta


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
#--------------------------------cargar foto drive----------------------------------

from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload
from google.oauth2 import service_account
import io

def upload_image_to_drive(file_bytes, file_name):
    try:
        from googleapiclient.discovery import build
        from googleapiclient.http import MediaIoBaseUpload
        from google.oauth2 import service_account
        import io

        creds_info = st.secrets["connections"]["gsheets"]
        # Importante incluir el scope de Drive
        SCOPES = ['https://googleapis.com']
        creds = service_account.Credentials.from_service_account_info(creds_info, scopes=SCOPES)
        service = build('drive', 'v3', credentials=creds)
        
        folder_id = "1xlP71aJSTIKpFUqBA7eYe47MKOQA43jU"
        
        file_metadata = {
            'name': file_name,
            'parents': [folder_id]
        }
        
        fh = io.BytesIO(file_bytes)
        media = MediaIoBaseUpload(fh, mimetype='image/jpeg', resumable=True)
        
        # supportsAllDrives=True es vital para usar el espacio de TU carpeta
        file = service.files().create(
            body=file_metadata,
            media_body=media,
            fields='id',
            supportsAllDrives=True 
        ).execute()
        
        file_id = file.get('id')
        service.permissions().create(fileId=file_id, body={'type': 'anyone', 'role': 'reader'}).execute()

        return f"https://google.com{file_id}"
    except Exception as e:
        # Evitamos que el error bloquee la app, solo devolvemos el mensaje
        return f"Error: {e}"

# ----LOGIN---
# --- CONEXIÓN ---
conn = st.connection("gsheets", type=GSheetsConnection)

# --- FUNCIÓN DE REGISTRO BLINDADA ---
def registrar_usuario(datos_nuevos):
    try:
        # 1. Leer la tabla actual (sin usar caché para ver lo real)
        df_actual = conn.read(worksheet="USUARIOS", ttl=0)
        
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

# --- LÓGICA DE INTERFAZ (LOGIN / REGISTRO) ---
if 'autenticado' not in st.session_state:
    st.session_state['autenticado'] = False
if 'registro_exitoso' not in st.session_state:
    st.session_state['registro_exitoso'] = False

if not st.session_state['autenticado']:
    st.title("🏆 Prode Mundial 2026")
    
    # Manejo de pestañas
    tab_login, tab_reg = st.tabs(["🔐 Entrar", "📝 Registrarse"])
    
    with tab_login:
        if st.session_state['registro_exitoso']:
            st.success("¡Registro completado! Ya puedes ingresar.")
            
        with st.form("login_form"):
            u = st.text_input("Usuario")
            p = st.text_input("Contraseña", type="password")
            if st.form_submit_button("Iniciar Sesión"):
                df_u = conn.read(worksheet="USUARIOS", ttl=0)
                # Validación exacta
                user_match = df_u[(df_u['USUARIO'].astype(str) == str(u)) & (df_u['CONTRASEÑA'].astype(str) == str(p))]
                
                if not user_match.empty:
                    st.session_state['autenticado'] = True
                    st.session_state['user_data'] = user_match.iloc[0].to_dict()
                    st.session_state['registro_exitoso'] = False
                    st.rerun()
                else:
                    st.error("Usuario o contraseña incorrectos")

    with tab_reg:
        with st.form("reg_form", clear_on_submit=True):
            r_u = st.text_input("Nick de Usuario")
            r_p = st.text_input("Contraseña", type="password")
            r_n = st.text_input("Nombre Completo")
            r_e = st.number_input("Edad", 1, 100, 25)
            r_f = st.selectbox("Equipo Favorito", ["Argentina", "México", "Canadá", "EEUU", "Brasil", "España", "Otro"])
            r_d = st.text_area("Breve descripción")
            
            if st.form_submit_button("Crear mi cuenta"):
                if r_u and r_p and r_n:
                    if registrar_usuario({
                        "USUARIO": r_u, "CONTRASEÑA": r_p, "NOMBRE": r_n,
                        "EDAD": r_e, "EQUIPO FAVORITO": r_f, "DESCRIPCION": r_d
                    }):
                        st.session_state['registro_exitoso'] = True
                        st.rerun()
                else:
                    st.error("Completa Usuario, Contraseña y Nombre.")
    st.stop()

# --- SIDEBAR DE BIENVENIDA ---
st.sidebar.write(f"Hola, **{st.session_state['user_data']['NOMBRE']}**")
if st.sidebar.button("Cerrar Sesión"):
    st.session_state['autenticado'] = False
    st.rerun()
    
# --- CARGA DE DATOS ---

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

# --- FUNCIÓN DE CÁLCULO MEJORADA ---
def calcular_detalle(r1, r2, p1, p2):
    if pd.isna(r1) or pd.isna(r2) or pd.isna(p1) or pd.isna(p2):
        return 0, 0, 0 # Puntos, Exactos, Generales
    
    puntos, exactos, generales = 0, 0, 0
    r1, r2, p1, p2 = int(r1), int(r2), int(p1), int(p2)
    
    tendencia_real = 1 if r1 > r2 else (2 if r2 > r1 else 0)
    tendencia_pron = 1 if p1 > p2 else (2 if p2 > p1 else 0)
    
    if tendencia_real == tendencia_pron:
        if r1 == p1 and r2 == p2:
            exactos = 1
            puntos = 3 # 1 de tendencia + 2 de bonus
        else:
            generales = 1
            puntos = 1
            
    return puntos, exactos, generales
    
# --- LÓGICA DE RANKING ACTUALIZADA (VERTICAL) ---

# 1. Cargamos los datos más recientes
df_res_oficial = df_res # Ya cargado por tu función load_data()
df_pro_total = conn.read(worksheet="PRONOSTICOS", ttl=0)
df_users_list = conn.read(worksheet="USUARIOS", ttl=0)

ranking_data = []

# Función de cálculo (la mantenemos igual)
def calcular_puntos_pro(r1, r2, p1, p2):
    if pd.isna(r1) or pd.isna(r2) or pd.isna(p1) or pd.isna(p2):
        return 0, 0, 0
    pts, exa, gen = 0, 0, 0
    r1, r2, p1, p2 = int(r1), int(r2), int(p1), int(p2)
    t_real = 1 if r1 > r2 else (2 if r2 > r1 else 0)
    t_pron = 1 if p1 > p2 else (2 if p2 > p1 else 0)
    if t_real == t_pron:
        if r1 == p1 and r2 == p2:
            exa = 1
            pts = 3 # 1 de tendencia + 2 de bonus
        else:
            gen = 1
            pts = 1
    return pts, exa, gen

# 2. Procesamos el Ranking por cada usuario registrado
ranking_data = []

# Iteramos sobre la lista de usuarios reales
for _, u_row in df_users_list.iterrows():
    u_nick = u_row['USUARIO']
    u_nombre = u_row['NOMBRE']
    
    total_pts, total_exa, total_gen = 0, 0, 0
    
    # Filtramos todos los pronósticos de este usuario de una vez
    pronos_usuario = df_pro_total[df_pro_total['USUARIO'] == u_nick]
    
# Iteramos sobre la lista de usuarios reales
for _, u_row in df_users_list.iterrows():
    u_nick = u_row['USUARIO']
    u_nombre = u_row['NOMBRE']
    
    total_pts, total_exa, total_gen = 0, 0, 0
    
    # Filtramos todos los pronósticos de este usuario
    pronos_usuario = df_pro_total[df_pro_total['USUARIO'] == u_nick]
    
    # Comparamos con cada resultado oficial cargado
    for _, res_row in df_res_oficial.iterrows():
        id_p = res_row['N_PARTIDO']
                    
        # Buscamos el pronóstico de este usuario para este partido
        p_row = pronos_usuario[pronos_usuario['N_PARTIDO'] == id_p]
        
        # Este IF debe estar DENTRO del for de los partidos
        if not p_row.empty:
            # Usamos tu función calcular_detalle()
            # Accedemos con iloc[0] para obtener los valores de la fila
            pts, exa, gen = calcular_detalle(
                res_row['R1'], res_row['R2'],
                p_row.iloc[0]['P1'], p_row.iloc[0]['P2']
            )
            total_pts += pts
            total_exa += exa
            total_gen += gen
            
    # Este APPEND debe estar FUERA del for de partidos, pero DENTRO del for de usuarios
    ranking_data.append({
        "JUGADOR": u_nombre,
        "PUNTOS": total_pts,
        "EXACTOS": total_exa,
        "GENERALES": total_gen
    })


# 3. Creamos el DataFrame y ordenamos (Puntos y luego Exactos como desempate)
df_ranking = pd.DataFrame(ranking_data).sort_values(by=["PUNTOS", "EXACTOS"], ascending=False).reset_index(drop=True)
df_ranking.index = df_ranking.index + 1
df_ranking.insert(0, "Nº", df_ranking.index.map(lambda x: "👑" if x == 1 else str(x)))

# Reordenar columnas
df_ranking = df_ranking[["Nº", "JUGADOR", "PUNTOS", "EXACTOS", "GENERALES"]]

# --- VISUALIZACIÓN ---
# --- NAVEGACIÓN EN SIDEBAR (OPTIMIZADO PARA MÓVILES) ---
# --- ESTRUCTURA PRINCIPAL DE DISEÑO (PROPORCIONES 60/40) ---
col_principal, col_derecha = st.columns([0.6, 0.4])

# 1. NAVEGACIÓN EN EL SIDEBAR (Ideal para móviles y PC)
with st.sidebar:
    st.subheader("📍 Navegación")
    opciones = ["🏠 Inicio", "📝 Mis Pronósticos", "👥 Jugadores", "💬 Foro"]
    if st.session_state['user_data']['ROL'] == 'admin':
        opciones.append("⚙️ Panel Control")
    
    # Creamos el menú aquí adentro
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
        
        # 1. Limpieza y Filtro de Visibilidad
        # Aseguramos que la columna VIZ exista y sea booleana
        if 'VIZ' in df_res.columns:
            df_res['VIZ'] = df_res['VIZ'].fillna(False).astype(bool)
            df_mostrar = df_res[df_res['VIZ'] == True].iloc[::-1]
        else:
            # Si aún no creaste la columna en Excel, mostramos todo para no dar error
            df_mostrar = df_res.iloc[::-1]

        with st.container(height=500):
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

                    st.markdown(f"""
                    <div style="border: 1px solid #ddd; border-top: 5px solid {color_tema}; border-radius: 12px; padding: 15px; margin-bottom: 20px; background-color: white; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
                        <div style="display: flex; justify-content: space-between; margin-bottom: 10px; align-items: center;">
                            <span style="font-size: 0.75em; font-weight: bold; color: {color_tema}; text-transform: uppercase;">PARTIDO {int(row['N_PARTIDO'])}</span>
                            <span style="font-size: 0.75em; color: #666; font-weight: bold;">📅 {dia_p} | 🕒 {hora_p}</span>
                        </div>
                        <div style="display: flex; justify-content: space-between; align-items: center;">
                            <div style="width: 38%; text-align: center;">
                                <div style="margin-bottom: 8px;">{i1}</div>
                                <div style="font-weight: bold; font-size: 1.1em; color: #333;">{row['Equipo_1']}</div>
                            </div>
                            <div style="width: 24%; text-align: center;">
                                <div style="background: #f8f9fa; border: 1px solid #ddd; color: #333; font-size: 1.8em; font-weight: bold; border-radius: 8px; padding: 5px 0;">{r1} : {r2}</div>
                            </div>
                            <div style="width: 38%; text-align: center;">
                                <div style="margin-bottom: 8px;">{i2}</div>
                                <div style="font-weight: bold; font-size: 1.1em; color: #333;">{row['Equipo_2']}</div>
                            </div>
                        </div>
                    </div>""", unsafe_allow_html=True)

        # --- BLOQUE 2: FORO (Actividad Reciente) ---------------------------------------------------------------------------------------
        st.subheader("💬 Actividad Reciente")
        df_foro_inicio = conn.read(worksheet="FORO", ttl=0)
        df_u_ref = conn.read(worksheet="USUARIOS", ttl=0) 
        
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

#---------- MENU MIS PRONOSTICOS ----------------------------------------------------

elif menu == "📝 Mis Pronósticos":
    with col_principal:
        st.subheader("📝 Mis Predicciones")
        
        # Ajuste de hora Argentina
        ahora_arg = datetime.now() - timedelta(hours=3)        
        fecha_limite = datetime(2026, 6, 8, 23, 59, 59)
        es_tiempo_valido = ahora_arg < fecha_limite
        
        # Carga de datos
        user_actual = st.session_state['user_data']['USUARIO']
        df_res_p = conn.read(worksheet="RESULTADOS", ttl=0)
        df_pro_all = conn.read(worksheet="PRONOSTICOS", ttl=0)
        df_user_pro = df_pro_all[df_pro_all['USUARIO'] == user_actual]

        # Avisos visuales optimizados
        if es_tiempo_valido:
            st.success(f"⏳ Tienes tiempo hasta el 08/06. (Hora Arg: {ahora_arg.strftime('%H:%M')})")
            modo_edicion = st.toggle("🔓 Editar mis resultados", help="Activa para modificar")
        else:
            st.error("🔒 Plazo finalizado. No se permiten más cambios.")
            modo_edicion = False
        
        esta_bloqueado = not (es_tiempo_valido and modo_edicion)

        with st.form("form_pronosticos_v2"):
            lista_nuevos_pro = []
            
            for i, row in df_res_p.iterrows():
                id_p = int(row['N_PARTIDO'])
                match = df_user_pro[df_user_pro['N_PARTIDO'] == id_p]
                
                # Valores seguros de Pandas
                v1 = int(match.iloc[0]['P1']) if not match.empty and pd.notna(match.iloc[0]['P1']) else 0
                v2 = int(match.iloc[0]['P2']) if not match.empty and pd.notna(match.iloc[0]['P2']) else 0
                
                # DISEÑO OPTIMIZADO PARA MÓVIL (Tarjeta compacta)
                st.markdown(f"""
                    <div style='background-color:#f8f9fa; border-radius:10px; padding:10px; border-left:5px solid #007bff; margin-bottom:5px;'>
                        <small style='color:gray;'>PARTIDO {id_p}</small><br>
                        <b>{row['Equipo_1']} vs {row['Equipo_2']}</b>
                    </div>
                """, unsafe_allow_html=True)
                
                # Usamos columnas pequeñas solo para los inputs
                c1, c_vs, c2 = st.columns([1, 0.2, 1])
                with c1:
                    p1_val = st.number_input(f"{row['Equipo_1']}", 0, 15, v1, key=f"f1_{id_p}", disabled=esta_bloqueado)
                with c_vs:
                    st.write("<br><center>-</center>", unsafe_allow_html=True)
                with c2:
                    p2_val = st.number_input(f"{row['Equipo_2']}", 0, 15, v2, key=f"f2_{id_p}", disabled=esta_bloqueado)
                
                lista_nuevos_pro.append({"N_PARTIDO": id_p, "USUARIO": user_actual, "P1": p1_val, "P2": p2_val})

            if es_tiempo_valido and modo_edicion:
                if st.form_submit_button("💾 GUARDAR TODO", use_container_width=True):
                    # Lógica de guardado robusta
                    df_otros = df_pro_all[df_pro_all['USUARIO'] != user_actual]
                    df_final = pd.concat([df_otros, pd.DataFrame(lista_nuevos_pro)], ignore_index=True)
                    conn.update(worksheet="PRONOSTICOS", data=df_final)
                    st.cache_data.clear()
                    st.success("✅ ¡Pronósticos guardados!")
                    st.balloons()
                    st.rerun()
            else:
                st.form_submit_button("🔒 Edición Bloqueada", disabled=True, use_container_width=True)

    with col_derecha:
        st.subheader("👤 Mi Perfil")
        u_data = st.session_state['user_data']
        
        if 'editando_perfil' not in st.session_state:
            st.session_state.editando_perfil = False

        if not st.session_state.editando_perfil:
            foto = u_data['AVATAR_URL'] if u_data['AVATAR_URL'] else "https://flaticon.com"
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
            with st.form("form_edit_perfil"):
                st.write("### 📝 Editar Perfil")
                # Quitamos el file_uploader de Drive y ponemos un texto
                n_foto = st.text_input("Link de tu foto (opcional)", value=u_data['AVATAR_URL'], placeholder="https://ejemplo.com")
                n_nom = st.text_input("Nombre Real", value=u_data['NOMBRE'])
                n_equ = st.selectbox("Hincha de", ["Argentina", "México", "España", "Brasil", "Uruguay", "Colombia", "Otro"])
                n_bio = st.text_area("Bio", value=u_data['DESCRIPCION'], max_chars=100)
                
                c_b1, c_b2 = st.columns(2)
                if c1.form_submit_button("✅ Guardar"):
                    nueva_url_foto = u_data['AVATAR_URL']
    
                    if archivo_perfil: # El st.file_uploader
                        with st.spinner("Subiendo foto a Drive..."):
            # LLAMADA A LA FUNCIÓN
                            res_url = upload_image_to_drive(archivo_perfil.getvalue(), f"perfil_{u_data['USUARIO']}.jpg")
            
                            if "Error" not in res_url:
                                nueva_url_foto = res_url
                            else:
                                st.error(res_url)

                    df_u = conn.read(worksheet="USUARIOS", ttl=0)
                    df_u.loc[df_u['USUARIO'] == u_data['USUARIO'], ['NOMBRE', 'AVATAR_URL', 'EQUIPO FAVORITO', 'DESCRIPCION']] = [n_nom, nueva_url, n_equ, n_bio]
                    conn.update(worksheet="USUARIOS", data=df_u)
                    st.session_state['user_data'].update({'NOMBRE': n_nom, 'AVATAR_URL': nueva_url, 'EQUIPO FAVORITO': n_equ, 'DESCRIPCION': n_bio})
                    st.session_state.editando_perfil = False
                    st.cache_data.clear()
                    st.rerun()
                
                if c_b2.form_submit_button("❌ Cancelar"):
                    st.session_state.editando_perfil = False
                    st.rerun()
                    
# ---------- MENU JUGADORES ----------------------------------------------------
# --- NO DEBE HABER NINGÚN ESPACIO ANTES DE ESTE ELIF ---
elif menu == "👥 Jugadores":
    with col_principal:
        st.subheader("👥 Jugadores Inscritos")
        df_usuarios = conn.read(worksheet="USUARIOS", ttl=0)
        
        if not df_usuarios.empty:
            nombres_jugadores = df_usuarios['NOMBRE'].tolist()
            nombre_sel = st.selectbox("Selecciona un jugador:", nombres_jugadores)
            # Buscamos la fila del usuario seleccionado
            user_sel_row = df_usuarios[df_usuarios['NOMBRE'] == nombre_sel]
            if not user_sel_row.empty:
                user_sel = user_sel_row.iloc[0]
            
                st.markdown("---")
                st.subheader(f"📈 Evolución de {nombre_sel}")
                
                df_pro_total = conn.read(worksheet="PRONOSTICOS", ttl=0)
                partidos_jugados = df_res.dropna(subset=['R1']).sort_values('N_PARTIDO')
                
                if partidos_jugados.empty:
                    st.info("La evolución aparecerá con el primer resultado oficial.")
                else:
                    evolucion_data = []
                    suma_user, suma_liga = 0, 0
                    total_jugadores = len(df_usuarios)

                    for _, res_row in partidos_jugados.iterrows():
                        id_p = int(res_row['N_PARTIDO'])
                        u_pr = df_pro_total[(df_pro_total['USUARIO'] == user_sel['USUARIO']) & (df_pro_total['N_PARTIDO'] == id_p)]
                        if not u_pr.empty:
                            pts, _, _ = calcular_detalle(res_row['R1'], res_row['R2'], u_pr.iloc[0]['P1'], u_pr.iloc[0]['P2'])
                            suma_user += pts
                        
                        pts_liga_partido = 0
                        todos_pro_partido = df_pro_total[df_pro_total['N_PARTIDO'] == id_p]
                        for _, p_row in todos_pro_partido.iterrows():
                            p_pts, _, _ = calcular_detalle(res_row['R1'], res_row['R2'], p_row['P1'], p_row['P2'])
                            pts_liga_partido += p_pts
                        
                        suma_liga += (pts_liga_partido / total_jugadores) if total_jugadores > 0 else 0
                        evolucion_data.append({"Partido": id_p, "Tus Puntos": suma_user, "Promedio Liga": round(suma_liga, 1)})

                    df_evo = pd.DataFrame(evolucion_data).sort_values("Partido").set_index("Partido")
                    st.area_chart(df_evo, color=["#28a745", "#adb5bd"])

                st.markdown("---")
                st.write("### 📋 Lista General")
                st.dataframe(df_usuarios[['NOMBRE', 'EQUIPO FAVORITO']], use_container_width=True, hide_index=True)
                
    with col_derecha:
        if 'user_sel' in locals():
            # --- LÓGICA DE MEDALLAS ---
            user_sel_name = user_sel['NOMBRE']
            datos_rank_user = df_ranking[df_ranking['JUGADOR'] == user_sel_name]
            foto_jugador = user_sel['AVATAR_URL'] if pd.notna(user_sel['AVATAR_URL']) and user_sel['AVATAR_URL'] != "" else "https://flaticon.com"

            if not datos_rank_user.empty:
                # 1. 🏆 PUNTERO
                es_puntero = "👑" in str(datos_rank_user.iloc[0]['Nº'])
                css_puntero = "" if es_puntero else "filter: grayscale(100%); opacity: 0.15;"

                # 2. 🎯 MASTER
                es_master = int(datos_rank_user.iloc[0]['EXACTOS']) >= 5
                css_master = "" if es_master else "filter: grayscale(100%); opacity: 0.15;"

                # 3. 🧙‍♂️ MENTALISTA
                max_gen = df_ranking['GENERALES'].max()
                es_mentalista = int(datos_rank_user.iloc[0]['GENERALES']) == max_gen and max_gen > 0
                css_mentalista = "" if es_mentalista else "filter: grayscale(100%); opacity: 0.15;"
            else:
                css_puntero = css_master = css_mentalista = "filter: grayscale(100%); opacity: 0.15;"

            # 4. 🥇 FUNDADOR
            es_fundador = int(user_sel['ID']) <= 3
            css_fundador = "" if es_fundador else "filter: grayscale(100%); opacity: 0.15;"

            # 5. 🐌 EL MÁS LENTO
            es_lento = not datos_rank_user.empty and (user_sel_name == df_ranking.iloc[-1]['JUGADOR']) and len(df_ranking) > 2
            css_lento = "" if es_lento else "filter: grayscale(100%); opacity: 0.15;"
            
            # 6. 🔥 ON FIRE
            user_pro_sorted = df_pro_total[df_pro_total['USUARIO'] == user_sel['USUARIO']].sort_values('N_PARTIDO')
            racha_act, racha_max = 0, 0
            for _, p in user_pro_sorted.iterrows():
                # Corregido acceso a iloc[0]
                partido_ref = df_res[df_res['N_PARTIDO'] == p['N_PARTIDO']]
                if not partido_ref.empty:
                    res_p = partido_ref.iloc[0]
                    if pd.notna(res_p['R1']):
                        _, exa, _ = calcular_detalle(res_p['R1'], res_p['R2'], p['P1'], p['P2'])
                        if exa == 1:
                            racha_act += 1
                            racha_max = max(racha_max, racha_act)
                        else: racha_act = 0
            
            es_onfire = racha_max >= 2
            css_onfire = "" if es_onfire else "filter: grayscale(100%); opacity: 0.15;"
            label_fire = f"x{racha_max}" if es_onfire else ""

            # --- RENDERIZADO DEL PERFIL ---
            st.markdown(f"""
                <div style="background-color: #f8f9fa; border-radius: 15px; border: 1px solid #ddd; padding: 15px; margin-bottom: 20px;">
                    <div style="display: flex; align-items: center; gap: 15px;">
                        <div style="flex: 1; text-align: center; border-right: 1px solid #eee; padding-right: 10px;">
                            <img src="{foto_jugador}" style="border-radius: 50%; width: 80px; height: 80px; object-fit: cover; border: 3px solid #1f3b4d;">
                            <div style="font-weight: bold; font-size: 1em; margin-top:5px;">{user_sel['NOMBRE']}</div>
                        </div>
                        <div style="flex: 2; text-align: left;">
                            <div style="display: flex; flex-wrap: wrap; gap: 8px; margin-bottom: 10px;">
                                <span title="Puntero" style="font-size: 1.5em; {css_puntero}">🏆</span>
                                <span title="Master" style="font-size: 1.5em; {css_master}">🎯</span>
                                <span title="On Fire" style="font-size: 1.5em; {css_onfire}">🔥<small style="font-size:0.5em;">{label_fire}</small></span>
                                <span title="Mentalista" style="font-size: 1.5em; {css_mentalista}">🧙‍♂️</span>
                                <span title="Fundador" style="font-size: 1.5em; {css_fundador}">🥇</span>
                                <span title="Lento" style="font-size: 1.5em; {css_lento}">🐌</span>
                            </div>
                            <div style="font-size: 0.85em; color: #444;"><i>"{user_sel['DESCRIPCION']}"</i></div>
                        </div>
                    </div>
                </div>
            """, unsafe_allow_html=True)
            
            # --- PREDICCIONES DEL USUARIO ---
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


# ---------- MENU FORO ----------------------------------------------------
elif menu == "💬 Foro":
    df_foro = conn.read(worksheet="FORO", ttl=0)
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
            df_res_admin = conn.read(worksheet="RESULTADOS", ttl=0)
            
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

        # COLUMNA DERECHA: GESTIÓN DE USUARIOS (40%)
        with col_derecha:
            st.subheader("👥 Gestión de Usuarios")
            df_users_adm = conn.read(worksheet="USUARIOS", ttl=0)
            df_pro_adm = conn.read(worksheet="PRONOSTICOS", ttl=0)

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
                    confirmado = st.checkbox("Confirmo que deseo borrar este usuario y sus pronósticos", key="conf_borrar")
                    
                    if st.button("❌ BORRAR PERMANENTEMENTE", type="primary", use_container_width=True, disabled=not confirmado):
                        df_users_final = df_users_adm[df_users_adm['USUARIO'] != user_a_eliminar]
                        df_pro_final = df_pro_adm[df_pro_adm['USUARIO'] != user_a_eliminar]
                        
                        conn.update(worksheet="USUARIOS", data=df_users_final)
                        conn.update(worksheet="PRONOSTICOS", data=df_pro_final)
                        
                        st.cache_data.clear()
                        st.success(f"✅ {user_a_eliminar} eliminado.")
                        st.rerun()
    else:
        st.error("No tienes permisos para acceder a esta sección.")
        pass
