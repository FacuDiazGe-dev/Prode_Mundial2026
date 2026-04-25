import streamlit as st
import pandas as pd

# Configuración inicial
st.set_page_config(page_title="Prode Mundial 2026", layout="wide")
st.title("🏆 Prode Mundial 2026 - Fase de Grupos")

# --- CONEXIÓN DIRECTA ---
# Convertimos el link de edición en link de exportación CSV para cada pestaña
SHEET_ID = "16GQN19xyzi_9jRKsaryNMhB80meX9RsJhyHlAU3Ek4c"
URL_RES = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid=0"
URL_PRO = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid=394071446"

@st.cache_data(ttl=600) # Se actualiza cada 10 minutos
def load_data():
    df_res = pd.read_csv(URL_RES)
    df_pro = pd.read_csv(URL_PRO)
    return df_res, df_pro

try:
    df_res, df_pro = load_data()
except Exception as e:
    st.error("No se pudo leer la planilla. Verifica que el acceso sea 'Cualquier persona con el enlace'")
    st.stop()

# --- LÓGICA DE PUNTUACIÓN ---
def calcular_puntos(r1, r2, p1, p2):
    # Si no hay resultado cargado (NaN), no suma puntos
    if pd.isna(r1) or pd.isna(r2) or pd.isna(p1) or pd.isna(p2):
        return 0
    
    puntos = 0
    # Tendencia real: 1 (Gana E1), -1 (Gana E2), 0 (Empate)
    tendencia_real = 1 if r1 > r2 else (-1 if r2 > r1 else 0)
    tendencia_pron = 1 if p1 > p2 else (-1 if p2 > p1 else 0)
    
    # 1. Acierto de Ganador o Empate (+1 pto)
    if tendencia_real == tendencia_pron:
        puntos += 1
        # 2. Resultado Exacto (+2 ptos adicionales)
        if int(r1) == int(p1) and int(r2) == int(p2):
            puntos += 2
            
    return puntos

# --- PROCESAMIENTO DEL RANKING ---
ranking = []
for j in range(1, 11): # Jugador 1 al 10
    total_jugador = 0
    col_e1 = f"Jugador_{j}_E1"
    col_e2 = f"Jugador_{j}_E2"
    
    # Iterar por cada uno de los 24 partidos
    for i in range(len(df_res)):
        partido_id = df_res.loc[i, 'N_PARTIDO']
        # Buscar el pronóstico correspondiente a ese N_PARTIDO
        pronostico_row = df_pro[df_pro['N_PARTIDO'] == partido_id].iloc[0]
        
        total_jugador += calcular_puntos(
            df_res.loc[i, 'R1'], df_res.loc[i, 'R2'],
            pronostico_row[col_e1], pronostico_row[col_e2]
        )
    ranking.append({"Jugador": f"Jugador {j}", "Puntos": total_jugador})

df_ranking = pd.DataFrame(ranking).sort_values(by="Puntos", ascending=False)

# --- INTERFAZ ---
tab1, tab2 = st.tabs(["📊 Ranking", "⚽ Resultados Oficiales"])

with tab1:
    st.subheader("Tabla de Posiciones")
    # Resaltar al puntero
    st.dataframe(df_ranking.reset_index(drop=True), use_container_width=True)

with tab2:
    st.subheader("Estado de los 24 partidos")
    st.table(df_res[['N_PARTIDO', 'Equipo_1', 'R1', 'R2', 'Equipo_2']])

st.sidebar.success("Datos sincronizados con Google Sheets")
