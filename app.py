import streamlit as st
import pandas as pd
import io
import requests

# 1. CONFIGURACIÓN
st.set_page_config(page_title="Prode Mundial 2026", page_icon="⚽", layout="wide")

URL_RES = "https://google.com"
URL_PRO = "https://google.com"

def calcular_puntos(r1_real, r2_real, r1_prode, r2_prode):
    try:
        if pd.isna(r1_real) or pd.isna(r2_real): return 0
        r1_r, r2_r = int(r1_real), int(r2_real)
        r1_p, r2_p = int(r1_prode), int(r2_prode)
        pts = 0
        if (r1_r > r2_r and r1_p > r2_p) or (r1_r < r2_r and r1_p < r2_p) or (r1_r == r2_r and r1_p == r2_p):
            pts += 1
            if r1_r == r1_p and r2_r == r2_p: pts += 2
        return pts
    except: return 0

@st.cache_data(ttl=60)
def cargar_datos(url):
    try:
        r = requests.get(url, timeout=10)
        df = pd.read_csv(io.StringIO(r.text))
        df.columns = df.columns.str.strip().str.upper()
        return df
    except: return None

df_res = cargar_datos(URL_RES)
df_pro = cargar_datos(URL_PRO)

if df_res is not None and df_pro is not None:
    st.title("🏆 Prode Familiar - Mundial 2026")
    
    seccion = st.sidebar.radio("Ir a:", ["Ranking General", "Detalle por Jugador"])

    if seccion == "Ranking General":
        ranking = []
        for i in range(1, 11):
            total = 0
            col_e1, col_e2 = f"JUGADOR_{i}_E1", f"JUGADOR_{i}_E2"
            for _, part in df_res.iterrows():
                n_p = part['N_PARTIDO']
                fila_pro = df_pro[df_pro['N_PARTIDO'] == n_p]
                if not fila_pro.empty:
                    p1 = fila_pro[col_e1].values[0]
                    p2 = fila_pro[col_e2].values[0]
                    total += calcular_puntos(part['R1'], part['R2'], p1, p2)
            ranking.append({"Familiar": f"Jugador {i}", "Puntos": int(total)})
        
        df_rank = pd.DataFrame(ranking).sort_values(by="Puntos", ascending=False)
        st.table(df_rank.reset_index(drop=True))
        st.bar_chart(df_rank.set_index("Familiar"))

    else:
        jug_sel = st.selectbox("Elegí el Jugador:", range(1, 11), format_func=lambda x: f"Jugador {x}")
        col_e1, col_e2 = f"JUGADOR_{jug_sel}_E1", f"JUGADOR_{jug_sel}_E2"
        detalle = []
        for _, part in df_res.iterrows():
            n_p = part['N_PARTIDO']
            fila_pro = df_pro[df_pro['N_PARTIDO'] == n_p]
            if not fila_pro.empty:
                p1 = fila_pro[col_e1].values[0]
                p2 = fila_pro[col_e2].values[0]
                pts = calcular_puntos(part['R1'], part['R2'], p1, p2)
                detalle.append({
                    "Partido": f"{part['EQUIPO_1']} vs {part['EQUIPO_2']}",
                    "Real": f"{int(part['R1'])} - {int(part['R2'])}" if not pd.isna(part['R1']) else "⏳",
                    "Pronóstico": f"{int(p1)} - {int(p2)}",
                    "Pts": pts
                })
        st.dataframe(pd.DataFrame(detalle), hide_index=True, use_container_width=True)
else:
    st.error("Error al cargar los datos.")
