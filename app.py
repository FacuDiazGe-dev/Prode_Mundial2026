import streamlit as st
import pandas as pd
import time

# 1. CONFIGURACIÓN
st.set_page_config(page_title="Prode Mundial 2026", page_icon="⚽", layout="wide")

# IDs de Google Sheets
SHEET_ID = "16GQN19xyzi_9jRKsaryNMhB80meX9RsJhyHlAU3Ek4c"
URL_RES = f"https://google.com{SHEET_ID}/gviz/tq?tqx=out:csv&sheet=RESULTADOS"
URL_PRO = f"https://google.com{SHEET_ID}/gviz/tq?tqx=out:csv&sheet=PRONOSTICOS"

# 2. FUNCIÓN DE CARGA CON REINTENTOS (Evita el error -2)
@st.cache_data(ttl=300)
def cargar_datos_con_reintento(url):
    for i in range(3): # Intenta 3 veces
        try:
            return pd.read_csv(url, storage_options={"User-Agent": "Mozilla/5.0"})
        except Exception:
            if i < 2: 
                time.sleep(1)
                continue
    return None

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
    except:
        return 0

# 3. LÓGICA PRINCIPAL
df_res = cargar_datos_con_reintento(URL_RES)
df_pro = cargar_datos_con_reintento(URL_PRO)

if df_res is None or df_pro is None:
    st.error("No se pudo conectar con Google Sheets. El servidor está saturado.")
    if st.button("🔄 Reintentar ahora"):
        st.cache_data.clear()
        st.rerun()
else:
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
                    p1 = prode[f'Jugador_{i}_E1'].values[0]
                    p2 = prode[f'Jugador_{i}_E2'].values[0]
                    total += calcular_puntos(part['R1'], part['R2'], p1, p2)
            ranking.append({"Familiar": f"Jugador {i}", "Puntos": int(total)})
        
        df_rank = pd.DataFrame(ranking).sort_values(by="Puntos", ascending=False)
        c1, c2 = st.columns(2)
        with c1: st.table(df_rank.reset_index(drop=True))
        with c2: st.bar_chart(df_rank.set_index("Familiar"))

    else:
        st.title("🔍 Detalle por Jugador")
        jugador_sel = st.selectbox("Selecciona un familiar:", [f"Jugador {i}" for i in range(1, 11)])
        n_jug = jugador_sel.split(" ")[1]
        
        detalle = []
        for _, part in df_res.iterrows():
            n_p = part['N_Partido']
            prode = df_pro[df_pro['N_Partido'] == n_p]
            if not prode.empty:
                p1_val = prode[f'Jugador_{n_jug}_E1'].values[0]
                p2_val = prode[f'Jugador_{n_jug}_E2'].values[0]
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

    if st.sidebar.button("🔄 Actualizar Datos"):
        st.cache_data.clear()
        st.rerun()
