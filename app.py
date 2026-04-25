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
        # Limpieza profunda de columnas
        df.columns = df.columns.str.strip().str.upper()
        return df
    except Exception as e:
        st.error(f"Error al bajar datos: {e}")
        return None

df_res = cargar_datos(URL_RESULTADOS)
df_pro = cargar_datos(URL_PRONOSTICOS)

if df_res is not None and df_pro is not None:
    st.title("🏆 Prode Familiar - Mundial 2026")
    
    opcion = st.sidebar.radio("Sección:", ["Ranking", "Detalle Jugador"])

    if opcion == "Ranking":
        ranking = []
        # Iterar sobre los 10 jugadores
        for i in range(1, 11):
            puntos_totales = 0
            col_e1 = f"JUGADOR_{i}_E1"
            col_e2 = f"JUGADOR_{i}_E2"
            
            for _, partido in df_res.iterrows():
                n_p = partido['N_PARTIDO']
                # Buscar la fila del partido en el DataFrame de pronósticos
                fila_pro = df_pro[df_pro['N_PARTIDO'] == n_p]
                
                if not fila_pro.empty:
                    # FORMA CORRECTA: fila_pro.iloc[0] toma la primera fila encontrada
                    datos_pro = fila_pro.iloc[0]
                    p1 = datos_pro[col_e1]
                    p2 = datos_pro[col_e2]
                    puntos_totales += calcular_puntos(partido['R1'], partido['R2'], p1, p2)
            
            ranking.append({"Familiar": f"Jugador {i}", "Puntos": int(puntos_totales)})
        
        df_rank = pd.DataFrame(ranking).sort_values(by="Puntos", ascending=False)
        st.subheader("Tabla General")
        st.table(df_rank)
        st.bar_chart(df_rank.set_index("Familiar"))

    else:
        jug_n = st.selectbox("Elegí el Jugador:", range(1, 11), format_func=lambda x: f"Jugador {x}")
        col_e1 = f"JUGADOR_{jug_n}_E1"
        col_e2 = f"JUGADOR_{jug_n}_E2"
        
        detalle = []
        for _, partido in df_res.iterrows():
            n_p = partido['N_PARTIDO']
            fila_pro = df_pro[df_pro['N_PARTIDO'] == n_p]
            
            if not fila_pro.empty:
                datos_pro = fila_pro.iloc[0]
                p1 = datos_pro[col_e1]
                p2 = datos_pro[col_e2]
                pts = calcular_puntos(partido['R1'], partido['R2'], p1, p2)
                
                detalle.append({
                    "Partido": f"{partido['EQUIPO_1']} vs {partido['EQUIPO_2']}",
                    "Real": f"{int(partido['R1'])} - {int(partido['R2'])}" if not pd.isna(partido['R1']) else "⏳",
                    "Pronóstico": f"{int(p1)} - {int(p2)}",
                    "Pts": pts
                })
        
        st.subheader(f"Resumen de Jugador {jug_n}")
        st.dataframe(pd.DataFrame(detalle), hide_index=True, use_container_width=True)

else:
    st.error("Error crítico: No se pudieron cargar las tablas de Google Sheets.")
