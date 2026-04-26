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

# Configuración de columnas según tus porcentajes: 20%, 50%, 30%
col_extra, col_res, col_rank = st.columns([0.2, 0.5, 0.3])

# 1. LATERAL IZQUIERDO: MENÚ DE NAVEGACIÓN (20%)
with col_extra:
    st.subheader("📍 Navegación")
    
    # Definimos las opciones del menú
    opciones = ["🏠 Inicio", "📝 Mis Pronósticos", "👥 Jugadores", "💬 Foro"]
    if st.session_state['user_data']['ROL'] == 'admin':
        opciones.append("⚙️ Panel Control")
    
    menu = st.radio("Ir a:", opciones, key="menu_navegacion")
    st.markdown("---")
    
    # --- LÓGICA DE SECCIONES ---
    if menu == "🏠 Inicio":
        st.write(f"¡Hola **{st.session_state['user_data']['NOMBRE']}**!")
        st.info("Selecciona 'Mis Pronósticos' para cargar tus resultados.")
        
    elif menu == "📝 Mis Pronósticos":
        st.subheader("Mis Predicciones")
        # Cargamos datos frescos de ambas tablas
        df_res = conn.read(worksheet="RESULTADOS", ttl=0)
        df_pro_all = conn.read(worksheet="PRONOSTICOS", ttl=0)
        user_actual = st.session_state['user_data']['USUARIO']
        
        # Filtramos lo que ya tiene el usuario
        df_user_pro = df_pro_all[df_pro_all['USUARIO'] == user_actual]

        with st.form("form_pronosticos"):
            st.caption("Carga tus goles para los 24 partidos:")
            lista_nuevos_pro = []
            
            for i, row in df_res.iterrows():
                id_p = int(row['N_PARTIDO'])
                # Buscamos si ya existe el pronóstico para este partido
                match = df_user_pro[df_user_pro['N_PARTIDO'] == id_p]
                v1 = int(match.iloc[0]['P1']) if not match.empty else 0
                v2 = int(match.iloc[0]['P2']) if not match.empty else 0
                
                # Diseño compacto para el lateral
                st.write(f"**P{id_p}:** {row['Equipo_1']} vs {row['Equipo_2']}")
                c1, v, c2 = st.columns([1, 0.5, 1])
                with c1:
                    p1_val = st.number_input("G1", 0, 15, v1, key=f"p1_{id_p}", label_visibility="collapsed")
                with v: st.write("-")
                with c2:
                    p2_val = st.number_input("G2", 0, 15, v2, key=f"p2_{id_p}", label_visibility="collapsed")
                
                lista_nuevos_pro.append({"N_PARTIDO": id_p, "USUARIO": user_actual, "P1": p1_val, "P2": p2_val})
                st.markdown("<hr style='margin:2px'>", unsafe_allow_html=True)

            if st.form_submit_button("💾 Guardar Todo", use_container_width=True):
                # Quitamos lo viejo y ponemos lo nuevo
                df_otros = df_pro_all[df_pro_all['USUARIO'] != user_actual]
                df_final = pd.concat([df_otros, pd.DataFrame(lista_nuevos_pro)], ignore_index=True)
                
                conn.update(worksheet="PRONOSTICOS", data=df_final)
                st.cache_data.clear()
                st.success("¡Pronósticos guardados!")
                st.rerun()

    elif menu == "👥 Jugadores":
        st.info("Aquí verás el perfil de tus oponentes próximamente.")
        
    elif menu == "💬 Foro":
        st.info("Chat grupal en mantenimiento.")
        
    elif menu == "⚙️ Panel Control":
        st.subheader("Administración")
        st.write("Solo visible para administradores.")

# 2. COLUMNA CENTRAL: RESULTADOS OFICIALES (50%)
with col_res:
    # Creamos una sub-columna interna para alinear el título y el botón
    col_tit, col_btn = st.columns([0.85, 0.15])
    
    with col_tit:
        st.subheader("⚽ Resultados Oficiales")
    
    with col_btn:
        # Botón pequeño con emoji de flechas circulares
        if st.button("🔄", help="Actualizar datos desde Google Sheets"):
            st.cache_data.clear() # Limpia el cache
            st.rerun() # Recarga la página con datos nuevos
            
    for i, row in df_res.iterrows():
        
        # DEFINICIÓN DE VARIABLES (Esto faltaba o estaba mal ubicado)
        r1 = int(row['R1']) if pd.notna(row['R1']) else "-"
        r2 = int(row['R2']) if pd.notna(row['R2']) else "-"
        
        # Obtener banderas (usando la función Base64 anterior)
        data_flag1 = get_flag_img(row['Equipo_1'])
        data_flag2 = get_flag_img(row['Equipo_2'])
        
        # Preparar el HTML de la imagen
        img1_html = f'<img src="{data_flag1}" width="25">' if "data:image" in data_flag1 else data_flag1
        img2_html = f'<img src="{data_flag2}" width="25">' if "data:image" in data_flag2 else data_flag2

        # Renderizado
        st.markdown(f"""
        <div style="border: 1px solid #ddd; border-radius: 10px; padding: 10px; margin-bottom: 10px; background-color: white; color: #333;">
            <div style="text-align: center; font-size: 0.7em; color: #999; margin-bottom: 5px;">PARTIDO {int(row['N_PARTIDO'])}</div>
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

# 3. LATERAL DERECHO: RANKING Y ESTADÍSTICAS (30%)
with col_rank:
    st.subheader("📊 Ranking")
    
    # Tabla de Ranking sin el fuego en puntos
    st.dataframe(
        df_ranking,
        use_container_width=True,
        hide_index=True,
        column_config={
            "Nº": st.column_config.TextColumn("Nº", width="small"),
            "PUNTOS": st.column_config.NumberColumn("PUNTOS"), # Sin fuego
            "EXACTOS": st.column_config.NumberColumn("🎯"),
            "GENERALES": st.column_config.NumberColumn("✅")
        }
    )
    
    # SECCIÓN DE ESTADÍSTICAS
    st.markdown("---")
    st.subheader("📈 Estadísticas Globales")
    
    total_exactos = df_ranking["EXACTOS"].sum()
    total_generales = df_ranking["GENERALES"].sum()
    promedio_puntos = df_ranking["PUNTOS"].mean()
    
    st.metric(label="Total Resultados Exactos", value=int(total_exactos))
    st.metric(label="Total Aciertos Generales", value=int(total_generales))
    st.metric(label="Promedio de Puntos", value=f"{promedio_puntos:.1f}")
