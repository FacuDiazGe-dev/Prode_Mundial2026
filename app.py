import streamlit as st
import pandas as pd

st.set_page_config(page_title="Prode Mundial 2026", layout="wide")
st.title("🏆 Prode Mundial 2026 - Fase de Grupos")

def obtener_url_bandera(pais):
    # Diccionario de códigos ISO para cada país
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
    if code:
        # Usamos flagcdn.com que es gratuita y rápida
        return f"https://flagcdn.com{code}.png"
    return "https://flagcdn.comun.png" # Bandera genérica (ONU)

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

# 1. LATERAL IZQUIERDO: EXTRAS (20%)
with col_extra:
    st.subheader("➕ Extras")
    st.info("Espacio para futuras secciones")

# 2. COLUMNA CENTRAL: RESULTADOS OFICIALES (50%)
with col_res:
    st.subheader("⚽ Resultados Oficiales")
    for i, row in df_res.iterrows():
        r1 = int(row['R1']) if not pd.isna(row['R1']) else "-"
        r2 = int(row['R2']) if not pd.isna(row['R2']) else "-"
        
        # Obtenemos URLs de las imágenes
        url1 = obtener_url_bandera(row['Equipo_1'])
        url2 = obtener_url_bandera(row['Equipo_2'])
        
        st.markdown(f"""
        <div style="border: 1px solid #ddd; border-radius: 10px; padding: 10px; margin-bottom: 10px; background-color: white; color: #333;">
            <div style="text-align: center; font-size: 0.7em; color: #999; margin-bottom: 5px;">PARTIDO {int(row['N_PARTIDO'])}</div>
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <div style="width: 40%; text-align: right; display: flex; align-items: center; justify-content: flex-end; gap: 8px;">
                    <span style="font-weight: bold;">{row['Equipo_1']}</span>
                    <img src="{url1}" width="25" style="border: 1px solid #eee">
                </div>
                <div style="width: 15%; text-align: center; background: #f0f0f0; border-radius: 4px; font-weight: bold; padding: 3px;">
                    {r1} - {r2}
                </div>
                <div style="width: 40%; text-align: left; display: flex; align-items: center; justify-content: flex-start; gap: 8px;">
                    <img src="{url2}" width="25" style="border: 1px solid #eee">
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
