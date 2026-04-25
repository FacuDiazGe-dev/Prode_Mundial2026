import streamlit as st
import pandas as pd

# 1. CONFIGURACIÓN
st.set_page_config(page_title="Prode Mundial 2026", page_icon="⚽", layout="wide")

# ID de tu Google Sheet
SHEET_ID = "16GQN19xyzi_9jRKsaryNMhB80meX9RsJhyHlAU3Ek4c"

# URLS CORREGIDAS (Importante: deben tener esta estructura exacta)
URL_RES = f"https://google.com{SHEET_ID}/export?format=csv&gid=0"
URL_PRO = f"https://google.com{SHEET_ID}/export?format=csv&gid=394071446"

def calcular_puntos(r1_real, r2_real, r1_prode, r2_prode):
    try:
        # Si no hay resultado real cargado, no suma puntos
        if pd.isna(r1_real) or pd.isna(r2_real): return 0
        
        r1_r, r2_r = int(r1_real), int(r2_real)
        r1_p, r2_p = int(r1_prode), int(r2_prode)
        
        pts = 0
        # Acierto de ganador o empate (1 punto)
        if (r1_r > r2_r and r1_p > r2_p) or (r1_r < r2_r and r1_p < r2_p) or (r1_r == r2_r and r1_p == r2_p):
            pts += 1
            # Acierto exacto (Bono de +2, total 3)
            if r1_r == r1_p and r2_r == r2_p:
                pts += 2
        return pts
    except:
        return 0

try:
    # Usamos st.cache_data para que no cargue la web cada vez que haces un click, 
    # pero con un tiempo de vida (ttl) de 1 minuto para que se actualice solo.
    @st.cache_data(ttl=60)
    def traer_datos(url):
        return pd.read_csv(url)

    df_res = traer_datos(URL_RES)
    df_pro = traer_datos(URL_PRO)

    st.sidebar.title("⚽ Menú Prode")
    seccion = st.sidebar.radio("Ir a:", ["Ranking General", "Detalle por Jugador"])

    if seccion == "Ranking General":
        st.title("🏆 Tabla de Posiciones")
        ranking = []
        # Recorremos los 10 jugadores (Asegúrate de que las columnas en el Excel existan)
        for i in range(1, 11):
            total = 0
            for _, part in df_res.iterrows():
                n_p = part['N_Partido']
                prode = df_pro[df_pro['N_Partido'] == n_p]
                if not prode.empty:
                    p1 = prode.iloc[0][f'Jugador_{i}_E1']
                    p2 = prode.iloc[0][f'Jugador_{i}_E2']
                    total += calcular_puntos(part['R1'], part['R2'], p1, p2)
            ranking.append({"Familiar": f"Jugador {i}", "Puntos": int(total)})
        
        df_rank = pd.DataFrame(ranking).sort_values(by="Puntos", ascending=False)
        
        col_tab, col_gra = st.columns([1, 1])
        with col_tab:
            st.dataframe(df_rank, hide_index=True, use_container_width=True)
        with col_gra:
            st.bar_chart(df_rank.set_index("Familiar"))

    else:
        st.title("🔍 ¿Cómo le fue a cada uno?")
        jug_sel = st.selectbox("Selecciona un familiar:", [f"Jugador {i}" for i in range(1, 11)])
        n_jug = jug_sel.replace("Jugador ", "")
        
        detalles = []
        for _, part in df_res.iterrows():
            n_p = part['N_Partido']
            prode = df_pro[df_pro['N_Partido'] == n_p]
            if not prode.empty:
                p1_val = prode.iloc[0][f'Jugador_{n_jug}_E1']
                p2_val = prode.iloc[0][f'Jugador_{n_jug}_E2']
                pts = calcular_puntos(part['R1'], part['R2'], p1_val, p2_val)
                
                detalles.append({
                    "Partido": f"{part['Equipo_1']} vs {part['Equipo_2']}",
                    "Real": f"{int(part['R1'])} - {int(part['R2'])}" if not pd.isna(part['R1']) else "Pendiente",
                    "Pronóstico": f"{int(p1_val)} - {int(p2_val)}",
                    "Pts": pts
                })
        st.table(pd.DataFrame(detalles))

except Exception as e:
    st.error(f"Error de conexión: {e}")
    st.info("Asegúrate de que el Google Sheet esté compartido como 'Cualquier persona con el enlace puede leer'.")
