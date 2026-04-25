import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection

# CONFIGURACIÓN
st.set_page_config(page_title="Prode Mundial 2026", page_icon="⚽", layout="wide")

# URL de tu Google Sheet (la normal que usas en el navegador)
URL_HOJA = "https://google.com"

def calcular_puntos(r1_real, r2_real, r1_prode, r2_prode):
    if pd.isna(r1_real) or pd.isna(r2_real) or pd.isna(r1_prode) or pd.isna(r2_prode):
        return 0
    pts = 0
    if (r1_real > r2_real and r1_prode > r2_prode) or \
       (r1_real < r2_real and r1_prode < r2_prode) or \
       (r1_real == r2_real and r1_prode == r2_prode):
        pts += 1
        if int(r1_real) == int(r1_prode) and int(r2_real) == int(r2_prode):
            pts += 2
    return pts

try:
    # CONEXIÓN OFICIAL
    conn = st.connection("gsheets", type=GSheetsConnection)
    
    # Lectura de pestañas por nombre exacto
    df_res = conn.read(spreadsheet=URL_HOJA, worksheet="RESULTADOS")
    df_pro = conn.read(spreadsheet=URL_HOJA, worksheet="PRONOSTICOS")

    st.sidebar.title("Navegación")
    seccion = st.sidebar.radio("Ir a:", ["Ranking General", "Detalle por Jugador"])

    if seccion == "Ranking General":
        st.title("🏆 Ranking Prode Familiar")
        ranking = []
        for i in range(1, 11):
            total = 0
            for _, part in df_res.iterrows():
                n = part['N_Partido']
                prode = df_pro[df_pro['N_Partido'] == n]
                if not prode.empty:
                    p1 = prode[f'Jugador_{i}_E1'].values[0]
                    p2 = prode[f'Jugador_{i}_E2'].values[0]
                    total += calcular_puntos(part['R1'], part['R2'], p1, p2)
            ranking.append({"Familiar": f"Jugador {i}", "Puntos": int(total)})
        
        df_rank = pd.DataFrame(ranking).sort_values(by="Puntos", ascending=False)
        c1, c2 = st.columns(2)
        with c1: st.table(df_rank.reset_index(drop=True))
        with c2: st.bar_chart(df_rank.set_index("Familiar"))

    else:
        st.title("🔍 Detalle de Pronósticos")
        jugador_sel = st.selectbox("Selecciona un familiar:", [f"Jugador {i}" for i in range(1, 11)])
        num = jugador_sel.split(" ")[1] # Extrae el número
        
        detalle = []
        for _, part in df_res.iterrows():
            n = part['N_Partido']
            prode = df_pro[df_pro['N_Partido'] == n]
            if not prode.empty:
                p1 = prode[f'Jugador_{num}_E1'].values[0]
                p2 = prode[f'Jugador_{num}_E2'].values[0]
                pts = calcular_puntos(part['R1'], part['R2'], p1, p2)
                detalle.append({
                    "Partido": f"{part['Equipo_1']} vs {part['Equipo_2']}",
                    "Real": f"{int(part['R1'])} - {int(part['R2'])}" if not pd.isna(part['R1']) else "Pendiente",
                    "Pronóstico": f"{int(p1)} - {int(p2)}",
                    "Pts": pts
                })
        st.dataframe(pd.DataFrame(detalle), use_container_width=True, hide_index=True)

except Exception as e:
    st.error(f"Error de conexión: {e}")
    st.info("Asegúrate de que la hoja de Google Sheets sea pública para cualquiera con el enlace.")
