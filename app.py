import streamlit as st
import pandas as pd
import io
import requests

st.set_page_config(page_title="Prode Mundial 2026", page_icon="⚽", layout="wide")

# URLs de exportación directa
URL_RES = "https://google.com"
URL_PRO = "https://google.com"

def calcular_puntos(r1_real, r2_real, r1_prode, r2_prode):
    try:
        # Convertimos a entero de forma segura
        r1_r, r2_r = int(float(r1_real)), int(float(r2_real))
        r1_p, r2_p = int(float(r1_prode)), int(float(r2_prode))
        
        pts = 0
        # Acierto de tendencia
        if (r1_r > r2_r and r1_p > r2_p) or (r1_r < r2_r and r1_p < r2_p) or (r1_r == r2_r and r1_p == r2_p):
            pts += 1
            # Acierto exacto
            if r1_r == r1_p and r2_r == r2_p:
                pts += 2
        return pts
    except:
        return 0

def cargar_datos(url):
    try:
        r = requests.get(url, timeout=10)
        # Cargamos sin modificar nombres de columnas para evitar KeyErrors
        df = pd.read_csv(io.StringIO(r.text))
        # Quitamos solo espacios en blanco alrededor de los nombres
        df.columns = [c.strip() for c in df.columns]
        return df
    except:
        return None

df_res = cargar_datos(URL_RES)
df_pro = cargar_datos(URL_PRO)

if df_res is not None and df_pro is not None:
    st.title("🏆 Prode Familiar 2026")
    
    seccion = st.sidebar.radio("Menú:", ["Ranking General", "Detalle por Jugador"])

    if seccion == "Ranking General":
        ranking = []
        # Iteramos por los 10 jugadores
        for i in range(1, 11):
            total = 0
            # Nombres de columnas según tu Excel
            c1, c2 = f"Jugador_{i}_E1", f"Jugador_{i}_E2"
            
            for _, part in df_res.iterrows():
                # Acceso por nombre exacto de columna
                n_p = part['N_Partido']
                fila_pro = df_pro[df_pro['N_Partido'] == n_p]
                
                if not fila_pro.empty:
                    # .values[0] extrae el dato exacto de la celda
                    p1 = fila_pro[c1].values[0]
                    p2 = fila_pro[c2].values[0]
                    
                    total += calcular_puntos(part['R1'], part['R2'], p1, p2)
            
            ranking.append({"Participante": f"Jugador {i}", "Puntos": total})
        
        df_rank = pd.DataFrame(ranking).sort_values(by="Puntos", ascending=False)
        st.table(df_rank.reset_index(drop=True))
        st.bar_chart(df_rank.set_index("Participante"))

    else:
        st.info("Ranking funcionando. Verificá si suma correctamente.")

else:
    st.error("Error al cargar los datos.")
