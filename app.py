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
def calcular_puntos(r1, r2, p1, p2):
    # Verificación de datos faltantes
    if pd.isna(r1) or pd.isna(r2) or pd.isna(p1) or pd.isna(p2):
        return 0
    
    puntos = 0
    # Convertir a int para asegurar comparación matemática
    r1, r2, p1, p2 = int(r1), int(r2), int(p1), int(p2)
    
    # 1. Determinar tendencia (1: E1 gana, 2: E2 gana, 0: Empate)
    tendencia_real = 1 if r1 > r2 else (2 if r2 > r1 else 0)
    tendencia_pron = 1 if p1 > p2 else (2 if p2 > p1 else 0)
    
    # Acierto de tendencia (+1 punto)
    if tendencia_real == tendencia_pron:
        puntos += 1
        # Acierto exacto (+2 puntos adicionales)
        if r1 == p1 and r2 == p2:
            puntos += 2
            
    return puntos

# --- CÁLCULO DEL RANKING ---
ranking = []
# Iteramos por los 10 jugadores definidos
for j in range(1, 11):
    total_puntos = 0
    col_e1 = f"Jugador_{j}_E1"
    col_e2 = f"Jugador_{j}_E2"
    
    # Aseguramos que las columnas existan en la pestaña Pronósticos
    if col_e1 in df_pro.columns and col_e2 in df_pro.columns:
        # Convertimos pronósticos del jugador a números
        df_pro[col_e1] = pd.to_numeric(df_pro[col_e1], errors='coerce')
        df_pro[col_e2] = pd.to_numeric(df_pro[col_e2], errors='coerce')

        for i in range(len(df_res)):
            n_partido = df_res.loc[i, 'N_PARTIDO']
            
            # Buscamos el pronóstico para este partido específico
            row_pro = df_pro[df_pro['N_PARTIDO'] == n_partido]
            
            if not row_pro.empty:
                total_puntos += calcular_puntos(
                    df_res.loc[i, 'R1'], 
                    df_res.loc[i, 'R2'],
                    row_pro.iloc[0][col_e1], 
                    row_pro.iloc[0][col_e2]
                )
    
    ranking.append({"Jugador": f"Jugador {j}", "Puntos": total_puntos})

# Crear y ordenar DataFrame
df_ranking = pd.DataFrame(ranking).sort_values(by="Puntos", ascending=False).reset_index(drop=True)

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
    st.subheader("📊 Ranking de Puntos")
    # Mostramos el ranking con un estilo más llamativo
    st.dataframe(
        df_ranking.reset_index(drop=True), 
        use_container_width=True,
        height=850 # Ajusta según la cantidad de jugadores para evitar scroll
    )

with col_extra:
    st.subheader("➕ Extras")
    st.info("Espacio reservado para futuras funcionalidades (gráficas, perfiles, etc.)")
    # Aquí puedes agregar lo que quieras más adelante
