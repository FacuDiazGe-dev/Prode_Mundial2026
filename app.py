import streamlit as st
import pandas as pd
import io
import requests

st.set_page_config(page_title="Prode Mundial 2026", page_icon="⚽", layout="wide")

# URLs de descarga directa
URL_RES = "https://google.com"
URL_PRO = "https://google.com"

def calcular_puntos(r1_real, r2_real, r1_prode, r2_prode):
    try:
        # Convertimos a números enteros
        r1_r, r2_r = int(float(r1_real)), int(float(r2_real))
        r1_p, r2_p = int(float(r1_prode)), int(float(r2_prode))
        
        pts = 0
        # Acierto de ganador o empate (1 pto)
        if (r1_r > r2_r and r1_p > r2_p) or (r1_r < r2_r and r1_p < r2_p) or (r1_r == r2_r and r1_p == r2_p):
            pts += 1
            # Resultado exacto (+2 ptos)
            if r1_r == r1_p and r2_r == r2_p:
                pts += 2
        return pts
    except:
        return 0

def cargar_datos(url):
    try:
        r = requests.get(url, timeout=10)
        df = pd.read_csv(io.StringIO(r.text))
        # Limpiamos solo espacios invisibles alrededor de los nombres
        df.columns = [c.strip() for c in df.columns]
        return df
    except:
        return None

df_res = cargar_datos(URL_RES)
df_pro = cargar_datos(URL_PRO)

if df_res is not None and df_pro is not None:
    st.title("🏆 Prode Familiar 2026")
    
    ranking = []
    # Iteramos por los 10 jugadores
    for i in range(1, 11):
        total_puntos = 0
        col_e1 = f"Jugador_{i}_E1"
        col_e2 = f"Jugador_{i}_E2"
        
        for _, part in df_res.iterrows():
            # USAMOS EL NOMBRE REAL DE TU CAMPO: N_Partido
            num_partido = part['N_Partido']
            
            # Buscamos el pronóstico que coincida con ese N_Partido
            fila_pro = df_pro[df_pro['N_Partido'] == num_partido]
            
            if not fila_pro.empty:
                # Extraemos los goles del pronóstico (usamos [0] para sacar el valor puro)
                p1 = fila_pro[col_e1].values[0]
                p2 = fila_pro[col_e2].values[0]
                
                total_puntos += calcular_puntos(part['R1'], part['R2'], p1, p2)
        
        ranking.append({"Participante": f"Jugador {i}", "Puntos": total_puntos})

    # Crear tabla y ordenar
    df_rank = pd.DataFrame(ranking).sort_values(by="Puntos", ascending=False)
    
    st.subheader("Tabla de Posiciones")
    st.table(df_rank.reset_index(drop=True))
    st.bar_chart(df_rank.set_index("Participante"))

else:
    st.error("No se pudo conectar con el Google Sheet. Verifica que sea público.")
