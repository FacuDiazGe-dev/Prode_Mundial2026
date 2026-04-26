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
        # Aquí mantienes tu código del Perfil (foto circular, bio, etc.)
        # Es ideal que el perfil esté a la derecha en PC, pero en móvil aparecerá abajo
        st.subheader("👤 Mi Perfil")
        u_data = st.session_state['user_data']
        foto = u_data['AVATAR_URL'] if u_data['AVATAR_URL'] else "https://flaticon.com"
        st.markdown(f"""
            <div style="text-align: center;">
                <img src="{foto}" style="border-radius: 50%; width: 100px; height: 100px; object-fit: cover; border: 3px solid #007bff;">
                <h4>{u_data['NOMBRE']}</h4>
                <p style="color: gray; font-size: 0.8em;">@{u_data['USUARIO']}</p>
            </div>
        """, unsafe_allow_html=True)
        
# ---------- MENU JUGADORES ----------------------------------------------------
elif menu == "👥 Jugadores":
    with col_principal:
        st.subheader("👥 Jugadores Inscritos")
        df_usuarios = conn.read(worksheet="USUARIOS", ttl=0)
        
        if not df_usuarios.empty:
            nombres_jugadores = df_usuarios['NOMBRE'].tolist()
            nombre_sel = st.selectbox("Selecciona un jugador:", nombres_jugadores)
            user_sel = df_usuarios[df_usuarios['NOMBRE'] == nombre_sel].iloc[0]
            
            st.markdown("---")
            st.write("### 📋 Lista General")
            st.dataframe(df_usuarios[['NOMBRE', 'EQUIPO FAVORITO']], use_container_width=True, hide_index=True)

    with col_derecha:
        if 'user_sel' in locals():
            foto_url = user_sel['AVATAR_URL'] if pd.notna(user_sel['AVATAR_URL']) and user_sel['AVATAR_URL'] != "" else "https://flaticon.com"
            st.markdown(f"""
                <div style="text-align: center; background-color: #f8f9fa; padding: 15px; border-radius: 10px; border: 1px solid #ddd;">
                    <img src="{foto_url}" style="border-radius: 50%; width: 90px; height: 90px; object-fit: cover; border: 2px solid #28a745;">
                    <h4 style="margin: 10px 0 0 0;">{user_sel['NOMBRE']}</h4>
                    <p style="color: #666; font-size: 0.8em; margin-bottom: 5px;">@{user_sel['USUARIO']}</p>
                    <hr style="margin: 10px 0;">
                    <p style="font-size: 0.85em; text-align: left; margin: 0;"><b>⚽ Hincha de:</b> {user_sel['EQUIPO FAVORITO']}</p>
                    <p style="font-size: 0.85em; text-align: left; margin: 0;"><b>📝 Bio:</b> <i>"{user_sel['DESCRIPCION']}"</i></p>
                </div>
            """, unsafe_allow_html=True)
            
            # Pronósticos del jugador seleccionado
            st.markdown("---")
            st.write(f"🗳️ **Predicciones de {user_sel['NOMBRE']}:**")
            df_pro_all = conn.read(worksheet="PRONOSTICOS", ttl=0)
            pro_user_sel = df_pro_all[df_pro_all['USUARIO'] == user_sel['USUARIO']]
            
            if not pro_user_sel.empty:
                for _, p in pro_user_sel.sort_values('N_PARTIDO').iterrows():
                    st.write(f"Part {int(p['N_PARTIDO'])}: **{int(p['P1'])} - {int(p['P2'])}**")
            else:
                st.warning("Sin pronósticos.")

# ---------- MENU FORO ----------------------------------------------------
elif menu == "💬 Foro":
    df_foro = conn.read(worksheet="FORO", ttl=0)
    with col_principal:
        st.subheader("💬 Muro de la Comunidad")
        with st.expander("✍️ Publicar un comentario", expanded=False):
            with st.form("nuevo_post_mobile", clear_on_submit=True):
                texto = st.text_area("¿Qué quieres decir?", max_chars=250)
                if st.form_submit_button("🚀 Publicar", use_container_width=True):
                    if texto.strip():
                        nuevo_msg = {
                            "FECHA": (datetime.now() - timedelta(hours=3)).strftime("%d/%m %H:%M"),
                            "USUARIO": st.session_state['user_data']['USUARIO'],
                            "NOMBRE": st.session_state['user_data']['NOMBRE'],
                            "MENSAJE": texto.strip(),
                            "PARTIDO_ID": 0
                        }
                        df_update = pd.concat([df_foro, pd.DataFrame([nuevo_msg])], ignore_index=True)
                        conn.update(worksheet="FORO", data=df_update)
                        st.cache_data.clear()
                        st.rerun()
        
        for index, m in df_foro.iloc[::-1].iterrows():
            with st.chat_message("user"):
                st.write(f"**{m['NOMBRE']}** - <small>{m['FECHA']}</small>", unsafe_allow_html=True)
                st.write(m['MENSAJE'])

# ---------- MENU ADMIN ----------------------------------------------------
elif menu == "⚙️ Panel Control":
    if st.session_state['user_data']['ROL'] == 'admin':
        with col_principal:
            st.subheader("⚙️ Gestión de Resultados Oficiales")
            df_res_admin = conn.read(worksheet="RESULTADOS", ttl=0)
            with st.form("form_admin"):
                upd = []
                for i, row in df_res_admin.iterrows():
                    st.write(f"Part {int(row['N_PARTIDO'])}: {row['Equipo_1']} vs {row['Equipo_2']}")
                    c1, c2 = st.columns(2)
                    r1 = c1.number_input("G1", 0, 20, int(row['R1']) if pd.notna(row['R1']) else 0, key=f"ar1_{i}")
                    r2 = c2.number_input("G2", 0, 20, int(row['R2']) if pd.notna(row['R2']) else 0, key=f"ar2_{i}")
                    fin = st.checkbox("Finalizado", value=pd.notna(row['R1']), key=f"fin_{i}")
                    upd.append({"N_PARTIDO": row['N_PARTIDO'], "Equipo_1": row['Equipo_1'], "R1": r1 if fin else None, "Equipo_2": row['Equipo_2'], "R2": r2 if fin else None})
                if st.form_submit_button("📢 Publicar Resultados"):
                    conn.update(worksheet="RESULTADOS", data=pd.DataFrame(upd))
                    st.cache_data.clear()
                    st.rerun()
                    
# --- SECCIÓN: GESTIÓN DE USUARIOS ----------------------------------------------------------------------------

    with col_derecha:
        st.subheader("👥 Gestión de Usuarios")
        
        # Leemos datos frescos
        df_users_adm = conn.read(worksheet="USUARIOS", ttl=0)
        df_pro_adm = conn.read(worksheet="PRONOSTICOS", ttl=0)

        # Filtramos para que el admin no se borre a sí mismo
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
                st.write("Esta acción eliminará su cuenta y sus 24 pronósticos permanentemente.")
                
                # Casilla de confirmación obligatoria
                confirmado = st.checkbox("Confirmo que deseo borrar este usuario", key="conf_borrar")
                
                # Botón de borrado (solo se activa si el checkbox está marcado)
                if st.button("❌ BORRAR PERMANENTEMENTE", type="primary", use_container_width=True, disabled=not confirmado):
                    try:
                        # 1. Filtramos las tablas para quitar al usuario
                        df_users_final = df_users_adm[df_users_adm['USUARIO'] != user_a_eliminar]
                        df_pro_final = df_pro_adm[df_pro_adm['USUARIO'] != user_a_eliminar]
                        
                        # 2. Subimos los cambios a Google Sheets
                        conn.update(worksheet="USUARIOS", data=df_users_final)
                        conn.update(worksheet="PRONOSTICOS", data=df_pro_final)
                        
                        # 3. Limpieza y reinicio
                        st.cache_data.clear()
                        st.success(f"✅ {user_a_eliminar} ha sido eliminado.")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error al eliminar: {e}")
        pass
