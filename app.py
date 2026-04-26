import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection
from datetime import datetime


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
    
# --- CÁLCULO DEL RANKING ---
ranking = []
for j in range(1, 11):
    total_pts, total_ex, total_gen = 0, 0, 0
    col_e1, col_e2 = f"Jugador_{j}_E1", f"Jugador_{j}_E2"
    
    if col_e1 in df_pro.columns:
        df_pro[col_e1] = pd.to_numeric(df_pro[col_e1], errors='coerce')
        df_pro[col_e2] = pd.to_numeric(df_pro[col_e2], errors='coerce')

        for i in range(len(df_res)):
            partido_id = df_res.loc[i, 'N_PARTIDO']
            row_pro = df_pro[df_pro['N_PARTIDO'] == partido_id].iloc[0]
            
            pts, ex, gen = calcular_detalle(df_res.loc[i, 'R1'], df_res.loc[i, 'R2'], row_pro[col_e1], row_pro[col_e2])
            total_pts += pts
            total_ex += ex
            total_gen += gen
    
    ranking.append({"JUGADOR": f"Jugador {j}", "PUNTOS": total_pts, "EXACTOS": total_ex, "GENERALES": total_gen})

# Crear DataFrame y ordenar
df_ranking = pd.DataFrame(ranking).sort_values(by=["PUNTOS", "EXACTOS"], ascending=False).reset_index(drop=True)

# Agregar columna de posición con la corona
df_ranking.index = df_ranking.index + 1
df_ranking["Nº"] = df_ranking.index.map(lambda x: f"👑" if x == 1 else str(x))

# Reordenar columnas
df_ranking = df_ranking[["Nº", "JUGADOR", "PUNTOS", "EXACTOS", "GENERALES"]]

# --- VISUALIZACIÓN ---

# --- ESTRUCTURA PRINCIPAL DE DISEÑO (PROPORCIONES 20/50/30) ---
col_nav, col_principal, col_derecha = st.columns([0.2, 0.5, 0.3])

# 1. PANEL IZQUIERDO: SIEMPRE FIJO (20%)
with col_nav:
    st.subheader("📍 Navegación")
    opciones = ["🏠 Inicio", "📝 Mis Pronósticos", "👥 Jugadores", "💬 Foro"]
    if st.session_state['user_data']['ROL'] == 'admin':
        opciones.append("⚙️ Panel Control")
    
    menu = st.radio("Ir a:", opciones, key="menu_navegacion")
    st.markdown("---")
    # Botón de cerrar sesión al final del menú
    if st.button("🚪 Cerrar Sesión", use_container_width=True):
        st.session_state['autenticado'] = False
        st.rerun()

# --- LÓGICA DE CONTENIDO SEGÚN EL MENÚ ---

if menu == "🏠 Inicio":
    # 1. COLUMNA CENTRAL (50%)
    with col_principal: 
        col_tit, col_btn = st.columns([0.85, 0.15])
        with col_tit:
            st.subheader("⚽ Resultados Oficiales")
        with col_btn:
            if st.session_state['user_data']['ROL'] == 'admin':
                if st.button("🔄", help="Actualizar datos", key="btn_refresco_inicio"):
                    st.cache_data.clear()
                    st.rerun()

        # Bucle de los 24 partidos
        for i, row in df_res.iterrows():
            r1 = int(row['R1']) if pd.notna(row['R1']) else "-"
            r2 = int(row['R2']) if pd.notna(row['R2']) else "-"
            
            data_flag1 = get_flag_img(row['Equipo_1'])
            data_flag2 = get_flag_img(row['Equipo_2'])
            
            img1_html = f'<img src="{data_flag1}" width="25">' if "data:image" in data_flag1 else data_flag1
            img2_html = f'<img src="{data_flag2}" width="25">' if "data:image" in data_flag2 else data_flag2

            st.markdown(f"""
            <div style="border: 1px solid #ddd; border-radius: 10px; padding: 10px; margin-bottom: 10px; background-color: white; color: #333;">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <div style="width: 40%; text-align: right; display: flex; align-items: center; justify-content: flex-end; gap: 8px;">
                        <span style="font-weight: bold;">{row['Equipo_1']}</span>
                        {img1_html}
                    </div>
                    <div style="width: 15%; text-align: center; background: #f0f0f0; border-radius: 4px; font-weight: bold; padding: 3px;">
                        {r1} - {r2}
                    </div>
                    <div style="width: 40%; text-align: left; display: flex; align-items: center; justify-content: flex-start; gap: 8px;">
                        {img2_html}
                        <span style="font-weight: bold;">{row['Equipo_2']}</span>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)

    # 2. COLUMNA DERECHA (30%) - NOTA: Esta línea debe estar alineada con "with col_principal"
    with col_derecha:
        st.subheader("📊 Ranking")
        st.dataframe(
            df_ranking,
            use_container_width=True,
            hide_index=True,
            column_config={
                "Nº": st.column_config.TextColumn("Nº", width="small"),
                "PUNTOS": st.column_config.NumberColumn("PUNTOS"),
                "EXACTOS": st.column_config.NumberColumn("🎯"),
                "GENERALES": st.column_config.NumberColumn("✅")
            }
        )
        
        st.markdown("---")
        st.subheader("📈 Estadísticas")
        if not df_ranking.empty:
            total_ex = df_ranking["EXACTOS"].sum()
            total_gr = df_ranking["GENERALES"].sum()
            st.metric("Total Exactos", int(total_ex))
            st.metric("Total Generales", int(total_gr))


elif menu == "📝 Mis Pronósticos":
    with col_principal:
        st.subheader("📝 Mis Predicciones")
        
        # --- CONFIGURACIÓN DE FECHA LÍMITE ---
        # Fecha límite: 8 de junio de 2026 a las 23:59:59
        fecha_limite = datetime(2026, 4, 25, 22, 55, 00)
        ahora = datetime.now()
        es_tiempo_valido = ahora < fecha_limite
        
        # --- CARGA DE DATOS ---
        user_actual = st.session_state['user_data']['USUARIO']
        df_res_p = conn.read(worksheet="RESULTADOS", ttl=0)
        df_pro_all = conn.read(worksheet="PRONOSTICOS", ttl=0)
        df_user_pro = df_pro_all[df_pro_all['USUARIO'] == user_actual]

        # --- AVISOS DE TIEMPO ---
        if es_tiempo_valido:
            dias_restantes = (fecha_limite - ahora).days
            st.success(f"⏳ Tienes tiempo para editar hasta el 08/06/2026 (Faltan {dias_restantes} días).")
        else:
            st.error("🔒 El plazo de carga ha finalizado. Los pronósticos están congelados.")

        # --- LÓGICA DE EDICIÓN ---
        # Solo permitimos el toggle de edición si estamos dentro del plazo
        modo_edicion = False
        if es_tiempo_valido:
            modo_edicion = st.toggle("🔓 Habilitar Edición", help="Activa para modificar tus resultados guardados")
        
        # El formulario se bloquea si pasó la fecha O si el usuario no activó el toggle
        esta_bloqueado = not (es_tiempo_valido and modo_edicion)

        with st.form("form_pronosticos_v2"):
            lista_nuevos_pro = []
            
            for i, row in df_res_p.iterrows():
                id_p = int(row['N_PARTIDO'])
                match = df_user_pro[df_user_pro['N_PARTIDO'] == id_p]
                
                # Valores recuperados del Sheet
                v1 = int(match.iloc[0]['P1']) if not match.empty else 0
                v2 = int(match.iloc[0]['P2']) if not match.empty else 0
                
                st.markdown(f"""
                    <div style='text-align:center; background-color:#f1f3f4; border-radius:5px; padding:2px; margin-top:10px;'>
                        <small style='color:#5f6368;'>PARTIDO {id_p}</small>
                    </div>
                """, unsafe_allow_html=True)
                
                c1, v, c2 = st.columns([3, 1, 3])
                with c1:
                    st.write(f"**{row['Equipo_1']}**")
                    p1_val = st.number_input(f"G1_{id_p}", 0, 15, v1, key=f"f1_{id_p}", label_visibility="collapsed", disabled=esta_bloqueado)
                with v: 
                    st.write("<h4 style='text-align:center;'>-</h4>", unsafe_allow_html=True)
                with c2:
                    st.write(f"**{row['Equipo_2']}**")
                    p2_val = st.number_input(f"G2_{id_p}", 0, 15, v2, key=f"f2_{id_p}", label_visibility="collapsed", disabled=esta_bloqueado)
                
                lista_nuevos_pro.append({"N_PARTIDO": id_p, "USUARIO": user_actual, "P1": p1_val, "P2": p2_val})

            # --- BOTÓN DE GUARDADO DINÁMICO ---
            if es_tiempo_valido and modo_edicion:
                if st.form_submit_button("💾 Guardar Cambios", use_container_width=True):
                    # Filtrar para no borrar a los demás usuarios
                    df_otros = df_pro_all[df_pro_all['USUARIO'] != user_actual]
                    df_final = pd.concat([df_otros, pd.DataFrame(lista_nuevos_pro)], ignore_index=True)
                    
                    conn.update(worksheet="PRONOSTICOS", data=df_final)
                    st.cache_data.clear()
                    st.success("✅ ¡Pronósticos actualizados exitosamente!")
                    st.rerun()
            else:
                st.form_submit_button("🔒 Bloqueado", disabled=True, use_container_width=True)


    with col_derecha:
        st.subheader("👤 Mi Perfil")
        u_data = st.session_state['user_data']
        foto = u_data['AVATAR_URL'] if u_data['AVATAR_URL'] else "https://flaticon.com"
        
        st.markdown(f"""
            <div style="text-align: center;">
                <img src="{foto}" style="border-radius: 50%; width: 120px; height: 120px; object-fit: cover; border: 3px solid #007bff;">
                <h3 style="margin-bottom: 0;">{u_data['NOMBRE']}</h3>
                <p style="color: gray;">@{u_data['USUARIO']}</p>
            </div>
            <hr>
            <p><b>🎂 Edad:</b> {u_data['EDAD']} años</p>
            <p><b>⚽ Equipo:</b> {u_data['EQUIPO FAVORITO']}</p>
            <p><b>📝 Bio:</b> <i>"{u_data['DESCRIPCION']}"</i></p>
        """, unsafe_allow_html=True)
    
    
