import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection

# CONFIGURACIÓN DE LA PÁGINA
st.set_page_config(page_title="Prode Mundial 2026", page_icon="⚽", layout="wide")

# URL de tu Google Sheet (la que copias del navegador)
URL_SHEET = "https://google.com"
df_res = conn.read(spreadsheet=URL_SHEET, worksheet="RESULTADOS")
df_pro = conn.read(spreadsheet=URL_SHEET, worksheet="PRONOSTICOS")

# LÓGICA DE PUNTUACIÓN
def calcular_puntos(r1_real, r2_real, r1_prode, r2_prode):
    try:
        if pd.isna(r1_real) or pd.isna(r2_real): return 0
        r1_r, r2_r = int(r1_real), int(r2_real)
        r1_p, r2_p = int(r1_prode), int(r2_prode)
        
        pts = 0
        # Acierto de tendencia (Ganador o Empate)
        if (r1_r > r2_r and r1_p > r2_p) or (r1_r < r2_r and r1_p < r2_p) or (r1_r == r2_r and r1_p == r2_p):
            pts += 1
            # Bono por resultado exacto
            if r1_r == r1_p and r2_r == r2_p:
                pts += 2
        return pts
    except:
        return 0

# CONEXIÓN Y CARGA DE DATOS
conn = st.connection("gsheets", type=GSheetsConnection)

try:
    # Cargamos datos usando los GID específicos
    df_res = conn.read(spreadsheet=URL_SHEET, worksheet="0")
    df_pro = conn.read(spreadsheet=URL_SHEET, worksheet="394071446")

    # INTERFAZ LATERAL
    st.sidebar.title("🏆 Prode 2026")
    seccion = st.sidebar.radio("Ir a:", ["Ranking General", "Detalle por Jugador"])

    if seccion == "Ranking General":
        st.title("📊 Tabla de Posiciones")
        ranking = []
        
        # Calculamos puntos para 10 jugadores
        for i in range(1, 11):
            total_jugador = 0
            for _, partido in df_res.iterrows():
                n_p = partido['N_Partido']
                prode_partido = df_pro[df_pro['N_Partido'] == n_p]
                
                if not prode_partido.empty:
                    p1 = prode_partido.iloc[0][f'Jugador_{i}_E1']
                    p2 = prode_partido.iloc[0][f'Jugador_{i}_E2']
                    total_jugador += calcular_puntos(partido['R1'], partido['R2'], p1, p2)
            
            ranking.append({"Participante": f"Jugador {i}", "Puntos": int(total_jugador)})
        
        df_rank = pd.DataFrame(ranking).sort_values(by="Puntos", ascending=False)
        
        col1, col2 = st.columns([1, 2])
        with col1:
            st.dataframe(df_rank, hide_index=True, use_container_width=True)
        with col2:
            st.bar_chart(df_rank.set_index("Participante"), color="#2e7d32")

    else:
        st.title("🔍 Detalle Individual")
        jugador_idx = st.selectbox("Selecciona un jugador:", range(1, 11), format_func=lambda x: f"Jugador {x}")
        
        detalles = []
        for _, partido in df_res.iterrows():
            n_p = partido['N_Partido']
            prode_partido = df_pro[df_pro['N_Partido'] == n_p]
            
            if not prode_partido.empty:
                p1_v = prode_partido.iloc[0][f'Jugador_{jugador_idx}_E1']
                p2_v = prode_partido.iloc[0][f'Jugador_{jugador_idx}_E2']
                pts = calcular_puntos(partido['R1'], partido['R2'], p1_v, p2_v)
                
                detalles.append({
                    "Partido": f"{partido['Equipo_1']} vs {partido['Equipo_2']}",
                    "Real": f"{int(partido['R1'])} - {int(partido['R2'])}" if not pd.isna(partido['R1']) else "⏳",
                    "Tu Prode": f"{int(p1_v)} - {int(p2_v)}",
                    "Puntos": pts
                })
        
        st.dataframe(pd.DataFrame(detalles), use_container_width=True, hide_index=True)

except Exception as e:
    st.error("Error al cargar los datos.")
    st.info("Asegúrate de tener el archivo 'requirements.txt' en GitHub y que el Excel sea público.")
