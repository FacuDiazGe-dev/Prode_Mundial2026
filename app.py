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
        # Convertimos a número entero de forma segura
        r1_r, r2_r = int(float(r1_real)), int(float(r2_real))
        r1_p, r2_p = int(float(r1_prode)), int(float(r2_prode))
        
        pts = 0
        # Acierto de ganador o empate
        if (r1_r > r2_r and r1_p > r2_p) or (r1_r < r2_r and r1_p < r2_p) or (r1_r == r2_r and r1_p == r2_p):
            pts += 1
            # Bono por resultado exacto
            if r1_r == r1_p and r2_r == r2_p:
                pts += 2
        return pts
    except:
        return 0

@st.cache_data(ttl=60)
def cargar_datos(url):
    try:
        r = requests.get(url, timeout=10)
        df = pd.read_csv(io.StringIO(r.text))
        # LIMPIEZA CRUCIAL: Quita espacios y pasa a MAYÚSCULAS
        df.columns = df.columns.str.strip().str.upper()
        return df
    except:
        return None

df_res = cargar_datos(URL_RES)
df_pro = cargar_datos(URL_PRO)

if df_res is not None and df_pro is not None:
    st.title("🏆 Prode Mundial 2026")
    
    seccion = st.sidebar.radio("Ir a:", ["Ranking General", "Detalle por Jugador"])

    # Aunque tu campo sea "N_Partido", tras la limpieza el código lo busca como "N_PARTIDO"
    if seccion == "Ranking General":
        ranking = []
        for i in range(1, 11):
            total = 0
            # Generamos los nombres de columnas (JUGADOR_1_E1, etc.)
            col_e1, col_e2 = f"JUGADOR_{i}_E1", f"JUGADOR_{i}_E2"
            
            for _, part in df_res.iterrows():
                n_p = part['N_PARTIDO'] # Nombre estandarizado
                fila_pro = df_pro[df_pro['N_PARTIDO'] == n_p]
                
                if not fila_pro.empty:
                    # Extraemos el primer valor encontrado con .values
                    p1 = fila_pro[col_e1].values
                    p2 = fila_pro[col_e2].values
                    total += calcular_puntos(part['R1'], part['R2'], p1, p2)
            
            ranking.append({"Participante": f"Jugador {i}", "Puntos": total})
        
        df_rank = pd.DataFrame(ranking).sort_values(by="Puntos", ascending=False)
        st.table(df_rank.reset_index(drop=True))
        st.bar_chart(df_rank.set_index("Participante"))

    else:
        jug_sel = st.selectbox("Elegí el Jugador:", range(1, 11), format_func=lambda x: f"Jugador {x}")
        # Lógica de detalle siguiendo la misma limpieza
        st.info("Ranking funcionando. Verificá si suma correctamente.")

else:
    st.error("Error al cargar los datos.")
    
