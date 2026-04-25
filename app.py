import streamlit as st
import pandas as pd

# 1. CONFIGURACIÓN
st.set_page_config(page_title="Prode Mundial 2026", page_icon="⚽", layout="wide")

# IDs de Google Sheets (URL de descarga directa)
SHEET_ID = "16GQN19xyzi_9jRKsaryNMhB80meX9RsJhyHlAU3Ek4c"
# Forzamos la descarga del CSV por GID (0 para Resultados, 394071446 para Pronósticos)
URL_RES = f"https://google.com{SHEET_ID}/export?format=csv&gid=0"
URL_PRO = f"https://google.com{SHEET_ID}/export?format=csv&gid=394071446"

def calcular_puntos(r1_real, r2_real, r1_prode, r2_prode):
    try:
        if pd.isna(r1_real) or pd.isna(r2_real): return 0
        r1_r, r2_r = int(r1_real), int(r2_real)
        r1_p, r2_p = int(r1_prode), int(r2_prode)
        pts = 0
        if (r1_r > r2_r and r1_p > r2_p) or (r1_r < r2_r and r1_p < r2_p) or (r1_r == r2_r and r1_p == r2_p):
            pts += 1
            if r1_r == r1_p and r2_r == r2_p:
                pts += 2
        return pts
    except: return 0

try:
    # Carga de datos sin caché para forzar la lectura
    df_res = pd.read_csv(URL_RES)
    df_pro = pd.read_csv(URL_PRO)

    st.sidebar.title("Menú Mundial")
    seccion = st.sidebar.radio("Ir a:", ["Ranking General", "Detalle por Jugador"])

    if seccion == "Ranking General":
        st.title("🏆 Ranking Familiar")
        ranking = []
        for i in range(1, 11):
            total = 0
            for _, part in df_res.iterrows():
                n_p = part['N_Partido']
                prode = df_pro[df_pro['N_Partido'] == n_p]
                if not prode.empty:
                    # Acceso seguro a los datos
                    p1 = prode.iloc[0][f'Jugador_{i}_E1']
                    p2 = prode.iloc[0][f'Jugador_{i}_E2']
                    total += calcular_puntos(part['R1'], part['R2'], p1, p2)
            ranking.append({"Familiar": f"Jugador {i}", "Puntos": int(total)})
        
        df_rank = pd.DataFrame(ranking).sort_values(by="Puntos", ascending=False)
        c1, c2 = st.columns(2)
        with c1: st.table(df_rank.reset_index(drop=True))
        with c2: st.bar_chart(df_rank.set_index("Familiar"))

    else:
        st.title("🔍 Detalle por Jugador")
        jugador_sel = st.selectbox("Selecciona un familiar:", [f"Jugador {i}" for i in range(1, 11)])
        # Extraemos el número del texto
        n_jug = jugador_sel.replace("Jugador ", "")
        
        detalle = []
        for _, part in df_res.iterrows():
            n_p = part['N_Partido']
            prode = df_pro[df_pro['N_Partido'] == n_p]
            if not prode.empty:
                p1_val = prode.iloc[0][f'Jugador_{n_jug}_E1']
                p2_val = prode.iloc[0][f'Jugador_{n_jug}_E2']
                pts = calcular_puntos(part['R1'], part['R2'], p1_val, p2_val)
                res_real = f"{int(part['R1'])} - {int(part['R2'])}" if not pd.isna(part['R1']) else "-"
                res_prode = f"{int(p1_val)} - {int(p2_val)}" if not pd.isna(p1_val) else "-"
                detalle.append({
                    "Partido": f"{part['Equipo_1']} vs {part['Equipo_2']}",
                    "Real": res_real,
                    "Pronóstico": res_prode,
                    "Pts": pts
                })
        st.dataframe(pd.DataFrame(detalle), use_container_width=True, hide_index=True)

except Exception as e:
    st.error(f"Error de conexión: {e}")
    st.info("Asegúrate de que el Google Sheet sea público.")
