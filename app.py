import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection

# 1. CONFIGURACIÓN
st.set_page_config(page_title="Prode Mundial 2026", page_icon="⚽", layout="wide")

# URL limpia del Sheet
URL_SHEET = "https://google.com"

def calcular_puntos(r1_real, r2_real, r1_prode, r2_prode):
    try:
        if pd.isna(r1_real) or pd.isna(r2_real): return 0
        r1_r, r2_r, r1_p, r2_p = int(r1_real), int(r2_real), int(r1_prode), int(r2_prode)
        pts = 0
        if (r1_r > r2_r and r1_p > r2_p) or (r1_r < r2_r and r1_p < r2_p) or (r1_r == r2_r and r1_p == r2_p):
            pts += 1
            if r1_r == r1_p and r2_r == r2_p: pts += 2
        return pts
    except: return 0

# 2. CONEXIÓN (IMPORTANTE: Se define el spreadsheet aquí)
conn = st.connection("gsheets", type=GSheetsConnection)

try:
    # CARGA DE DATOS: Si los nombres fallan, usa el número de la pestaña
    # Cambia "Resultados" y "Pronósticos" por los nombres reales de tus pestañas abajo
    df_res = conn.read(spreadsheet=URL_SHEET, worksheet="0") 
    df_pro = conn.read(spreadsheet=URL_SHEET, worksheet="394071446")

    st.title("🏆 Prode Familiar 2026")
    
    tab1, tab2 = st.tabs(["Ranking General", "Detalle por Jugador"])

    with tab1:
        ranking = []
        for i in range(1, 11):
            total = 0
            for _, part in df_res.iterrows():
                n_p = part['N_Partido']
                prode = df_pro[df_pro['N_Partido'] == n_p]
                if not prode.empty:
                    p1 = prode.iloc[0][f'Jugador_{i}_E1']
                    p2 = prode.iloc[0][f'Jugador_{i}_E2']
                    total += calcular_puntos(part['R1'], part['R2'], p1, p2)
            ranking.append({"Participante": f"Jugador {i}", "Puntos": int(total)})
        
        df_rank = pd.DataFrame(ranking).sort_values(by="Puntos", ascending=False)
        st.dataframe(df_rank, hide_index=True, use_container_width=True)
        st.bar_chart(df_rank.set_index("Participante"))

    with tab2:
        jug_sel = st.selectbox("Elegí un jugador:", range(1, 11), format_func=lambda x: f"Jugador {x}")
        detalle = []
        for _, part in df_res.iterrows():
            n_p = part['N_Partido']
            prode = df_pro[df_pro['N_Partido'] == n_p]
            if not prode.empty:
                p1_v = prode.iloc[0][f'Jugador_{jug_sel}_E1']
                p2_v = prode.iloc[0][f'Jugador_{jug_sel}_E2']
                pts = calcular_puntos(part['R1'], part['R2'], p1_v, p2_v)
                detalle.append({
                    "Partido": f"{part['Equipo_1']} vs {part['Equipo_2']}",
                    "Real": f"{int(part['R1'])} - {int(part['R2'])}" if not pd.isna(part['R1']) else "⏳",
                    "Prode": f"{int(p1_v)} - {int(p2_v)}",
                    "Pts": pts
                })
        st.table(pd.DataFrame(detalle))

except Exception as e:
    st.error(f"Error técnico: {e}")
    st.info("Revisá que en el Google Sheet las pestañas tengan los GIDs: 0 y 394071446.")
    
