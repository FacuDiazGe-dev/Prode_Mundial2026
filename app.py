import streamlit as st
import pandas as pd
import io
import requests

st.set_page_config(page_title="Prode Mundial 2026", page_icon="⚽", layout="wide")

URL_RESULTADOS = "https://google.com"
URL_PRONOSTICOS = "https://google.com"

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
        df.columns = df.columns.str.strip().str.upper()
        return df
    except: return None

df_res = cargar_datos(URL_RESULTADOS)
df_pro = cargar_datos(URL_PRONOSTICOS)

if df_res is not None and df_pro is not None:
    st.title("🏆 Prode Familiar - Mundial 2026")
    
    # --- AYUDA VISUAL (Puedes borrar esto cuando funcione) ---
    with st.expander("Verificar nombres de columnas"):
        st.write("Columnas Resultados:", list(df_res.columns))
        st.write("Columnas Pronósticos:", list(df_pro.columns))
    # ---------------------------------------------------------

    opcion = st.sidebar.radio("Sección:", ["Ranking", "Detalle Jugador"])

    if opcion == "Ranking":
        ranking = []
        for i in range(1, 11):
            puntos_totales = 0
            for _, partido in df_res.iterrows():
                n_p = partido['N_PARTIDO']
                # Filtramos la fila del partido en pronósticos
                fila_pro = df_pro[df_pro['N_PARTIDO'] == n_p]
                
                if not fila_pro.empty:
                    # Usamos .iloc[0] para obtener la fila y luego el nombre de la columna
                    p1 = fila_pro.iloc[0][f'JUGADOR_{i}_E1']
                    p2 = fila_pro.iloc[0][f'JUGADOR_{i}_E2']
                    puntos_totales += calcular_puntos(partido['R1'], partido['R2'], p1, p2)
            
            ranking.append({"Familiar": f"Jugador {i}", "Puntos": int(puntos_totales)})
        
        df_rank = pd.DataFrame(ranking).sort_values(by="Puntos", ascending=False)
        st.table(df_rank)
        st.bar_chart(df_rank.set_index("Familiar"))

    else:
        jug_n = st.selectbox("Elegí el Jugador:", range(1, 11), format_func=lambda x: f"Jugador {x}")
        detalle = []
        for _, partido in df_res.iterrows():
            n_p = partido['N_PARTIDO']
            fila_pro = df_pro[df_pro['N_PARTIDO'] == n_p]
            
            if not fila_pro.empty:
                p1 = fila_pro.iloc[0][f'JUGADOR_{jug_n}_E1']
                p2 = fila_pro.iloc[0][f'JUGADOR_{jug_n}_E2']
                pts = calcular_puntos(partido['R1'], partido['R2'], p1, p2)
                
                detalle.append({
                    "Partido": f"{partido['EQUIPO_1']} vs {partido['EQUIPO_2']}",
                    "Real": f"{int(partido['R1'])} - {int(partido['R2'])}" if not pd.isna(partido['R1']) else "⏳",
                    "Prode": f"{int(p1)} - {int(p2)}",
                    "Pts": pts
                })
        st.dataframe(pd.DataFrame(detalle), hide_index=True)
else:
    st.error("No se pudieron cargar los datos.")
