import streamlit as st
import pandas as pd
import io
import requests

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

def cargar_datos(url):
    try:
        r = requests.get(url, timeout=10)
        df = pd.read_csv(io.StringIO(r.text))
        # LIMPIEZA EXTREMA DE COLUMNAS
        # Quita espacios, mayúsculas, puntos y caracteres invisibles
        df.columns = df.columns.str.replace(r'[^a-zA-Z0-9_]', '', regex=True).str.upper()
        return df
    except: return None

df_res = cargar_datos(URL_RES)
df_pro = cargar_datos(URL_PRO)

if df_res is not None and df_pro is not None:
    st.title("🏆 Prode Familiar 2026")
    
    # En el Excel se llama N_Partido, pero tras la limpieza será N_PARTIDO
    col_id = "NPARTIDO" if "NPARTIDO" in df_res.columns else "N_PARTIDO"

    seccion = st.sidebar.radio("Menú:", ["Ranking General", "Detalle por Jugador"])

    if seccion == "Ranking General":
        ranking = []
        for i in range(1, 11):
            total = 0
            # Generamos los nombres de columnas esperados tras la limpieza
            c1, c2 = f"JUGADOR{i}E1", f"JUGADOR{i}E2" 
            
            for _, part in df_res.iterrows():
                try:
                    n_p = part[col_id]
                    fila_pro = df_pro[df_pro[col_id] == n_p]
                    if not fila_pro.empty:
                        # Usamos [0] para asegurar que tomamos el primer valor encontrado
                        p1 = fila_pro[c1].values[0]
                        p2 = fila_pro[c2].values[0]
                        total += calcular_puntos(part['R1'], part['R2'], p1, p2)
                except: continue
            ranking.append({"Familiar": f"Jugador {i}", "Puntos": int(total)})
        
        df_rank = pd.DataFrame(ranking).sort_values(by="Puntos", ascending=False)
        st.table(df_rank.reset_index(drop=True))
        st.bar_chart(df_rank.set_index("Familiar"))

    else:
        jug_sel = st.selectbox("Elegí el Jugador:", range(1, 11), format_func=lambda x: f"Jugador {x}")
        st.info("Revisá primero si el Ranking ya funciona.")

else:
    st.error("Error al cargar los datos.")
