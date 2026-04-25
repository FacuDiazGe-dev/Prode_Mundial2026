import streamlit as st
import pandas as pd
import io
import requests

st.set_page_config(page_title="Prode Mundial 2026", page_icon="⚽", layout="wide")

URL_RES = "https://google.com"
URL_PRO = "https://google.com"

# 1. FUNCIÓN DE PUNTOS CORREGIDA (Acepta cualquier formato de número/texto)
def calcular_puntos(r1_real, r2_real, r1_prode, r2_prode):
    try:
        # Convertimos todo a entero, si falla o es vacío, retorna 0
        r1_r = int(float(r1_real))
        r2_r = int(float(r2_real))
        r1_p = int(float(r1_prode))
        r2_p = int(float(r2_prode))
        
        pts = 0
        # Acierto de tendencia (Ganador o Empate)
        if (r1_r > r2_r and r1_p > r2_p) or (r1_r < r2_r and r1_p < r2_p) or (r1_r == r2_r and r1_p == r2_p):
            pts += 1
            # Bono por acierto exacto
            if r1_r == r1_p and r2_r == r2_p:
                pts += 2
        return pts
    except:
        return 0

def cargar_datos(url):
    try:
        r = requests.get(url, timeout=10)
        df = pd.read_csv(io.StringIO(r.text))
        # Limpieza de nombres de columnas
        df.columns = df.columns.str.replace(r'[^a-zA-Z0-9_]', '', regex=True).str.upper()
        return df
    except:
        return None

df_res = cargar_datos(URL_RES)
df_pro = cargar_datos(URL_PRO)

if df_res is not None and df_pro is not None:
    st.title("🏆 Prode Familiar 2026")
    
    # Identificar la columna de ID (NPARTIDO o N_PARTIDO tras la limpieza)
    col_id = "NPARTIDO" if "NPARTIDO" in df_res.columns else "N_PARTIDO"

    seccion = st.sidebar.radio("Menú:", ["Ranking General", "Detalle por Jugador"])

    if seccion == "Ranking General":
        ranking = []
        for i in range(1, 11):
            total = 0
            c1, c2 = f"JUGADOR{i}E1", f"JUGADOR{i}E2"
            
            for _, part in df_res.iterrows():
                # Buscamos el pronóstico correspondiente
                n_p = part[col_id]
                fila_pro = df_pro[df_pro[col_id] == n_p]
                
                if not fila_pro.empty:
                    # Sacamos los valores individuales
                    p1_val = fila_pro[c1].values[0]
                    p2_val = fila_pro[c2].values[0]
                    
                    puntos = calcular_puntos(part['R1'], part['R2'], p1_val, p2_val)
                    total += puntos
            
            ranking.append({"Familiar": f"Jugador {i}", "Puntos": total})
        
        df_rank = pd.DataFrame(ranking).sort_values(by="Puntos", ascending=False)
        st.table(df_rank.reset_index(drop=True))
        st.bar_chart(df_rank.set_index("Familiar"))

    else:
        st.info("Sección en mantenimiento. Revisa el Ranking para ver los puntos sumados.")

else:
    st.error("Error al cargar los datos.")
