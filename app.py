import streamlit as st
import pandas as pd

st.set_page_config(page_title="Prode Mundial 2026", layout="wide")
st.title("🏆 Prode Mundial 2026 - Fase de Grupos")

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

# Creamos 3 columnas: [proporción 1.2, proporción 1.5, proporción 1.2]
col_res, col_rank, col_extra = st.columns([1.2, 1.5, 1.2])

with col_res:
    st.subheader("⚽ Resultados")
    # Formateamos para que sea una lista compacta y fija
    for i, row in df_res.iterrows():
        # Si tiene resultado, mostrarlo; si no, mostrar vs
        r1 = int(row['R1']) if not pd.isna(row['R1']) else "-"
        r2 = int(row['R2']) if not pd.isna(row['R2']) else "-"
        
        st.markdown(f"""
        <div style="border-bottom: 1px solid #ddd; padding: 5px;">
            <small>Part {int(row['N_PARTIDO'])}</small><br>
            <b>{row['Equipo_1']}</b> {r1} - {r2} <b>{row['Equipo_2']}</b>
        </div>
        """, unsafe_allow_html=True)

with col_rank:
    st.subheader("📊 Tabla de Posiciones")
    st.dataframe(
        df_ranking,
        use_container_width=True,
        hide_index=True, # Ocultamos el índice de pandas para usar nuestra columna Nº
        column_config={
            "Nº": st.column_config.TextColumn("Nº", width="small"),
            "PUNTOS": st.column_config.NumberColumn("PUNTOS", format="%d 🔥"),
            "EXACTOS": st.column_config.NumberColumn("🎯 Exactos"),
            "GENERALES": st.column_config.NumberColumn("✅ Gral")
        }
    )

with col_extra:
    st.subheader("➕ Extras")
    st.info("Espacio reservado para futuras funcionalidades (gráficas, perfiles, etc.)")
    # Aquí puedes agregar lo que quieras más adelante
