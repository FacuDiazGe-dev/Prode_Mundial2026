import streamlit as st
import pandas as pd
import io
import requests

# 1. CONFIGURACIÓN
st.set_page_config(page_title="Prode Mundial 2026", page_icon="⚽", layout="wide")

SHEET_ID = "16GQN19xyzi_9jRKsaryNMhB80meX9RsJhyHlAU3Ek4c"

# Función robusta para leer CSV desde Google Sheets
def get_data(gid):
    url = f"https://google.com{SHEET_ID}/export?format=csv&gid={gid}"
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        return pd.read_csv(io.StringIO(response.text))
    except Exception as e:
        st.error(f"Error de red al acceder a la pestaña {gid}: {e}")
        return None

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

# CARGA DE DATOS
df_res = get_data("0")
df_pro = get_data("394071446")

if df_res is not None and df_pro is not None:
    st.title("🏆 Prode Familiar 2026")
    
    seccion = st.sidebar.radio("Ir a:", ["Ranking General", "Detalle por Jugador"])

    if seccion == "Ranking General":
        ranking = []
        for i in range(1, 11):
            total = 0
            for _, part in df_res.iterrows():
                n_p = part['N_Partido']
                prode = df_pro[df_pro['N_Partido'] == n_p]
                if not prode.empty:
                    p1 = prode[f'Jugador_{i}_E1'].values[0]
                    p2 = prode[f'Jugador_{i}_E2'].values[0]
                    total += calcular_puntos(part['R1'], part['R2'], p1, p2)
            ranking.append({"Participante": f"Jugador {i}", "Puntos": int(total)})
        
        df_rank = pd.DataFrame(ranking).sort_values(by="Puntos", ascending=False)
        st.table(df_rank)
        st.bar_chart(df_rank.set_index("Participante"))

    else:
        jug_sel = st.selectbox("Selecciona Jugador:", range(1, 11), format_func=lambda x: f"Jugador {x}")
        detalle = []
        for _, part in df_res.iterrows():
            n_p = part['N_Partido']
            prode = df_pro[df_pro['N_Partido'] == n_p]
            if not prode.empty:
                p1_v = prode[f'Jugador_{jug_sel}_E1'].values[0]
                p2_v = prode[f'Jugador_{jug_sel}_E2'].values[0]
                pts = calcular_puntos(part['R1'], part['R2'], p1_v, p2_v)
                detalle.append({
                    "Partido": f"{part['Equipo_1']} vs {part['Equipo_2']}",
                    "Real": f"{int(part['R1'])} - {int(part['R2'])}" if not pd.isna(part['R1']) else "⏳",
                    "Prode": f"{int(p1_v)} - {int(p2_v)}",
                    "Pts": pts
                })
        st.dataframe(pd.DataFrame(detalle), use_container_width=True, hide_index=True)
