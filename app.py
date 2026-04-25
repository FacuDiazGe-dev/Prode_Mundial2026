import streamlit as st
import pandas as pd
import time

# 1. CONFIGURACIÓN INICIAL
st.set_page_config(page_title="Prode Mundial 2026", page_icon="⚽", layout="wide")

# Tus enlaces de Google Sheets
SHEET_ID = "16GQN19xyzi_9jRKsaryNMhB80meX9RsJhyHlAU3Ek4c"
URL_RESULTADOS = f"https://google.com{SHEET_ID}/gviz/tq?tqx=out:csv&sheet=RESULTADOS"
URL_PRONOSTICOS = f"https://google.com{SHEET_ID}/gviz/tq?tqx=out:csv&sheet=PRONOSTICOS"

# 2. FUNCIONES DE APOYO
def cargar_datos_seguro(url):
    for i in range(3):
        try:
            return pd.read_csv(url)
        except Exception:
            time.sleep(1)
    return None

def calcular_puntos(r1_real, r2_real, r1_prode, r2_prode):
    if pd.isna(r1_real) or pd.isna(r2_real) or pd.isna(r1_prode) or pd.isna(r2_prode):
        return 0
    pts = 0
    if (r1_real > r2_real and r1_prode > r2_prode) or \
       (r1_real < r2_real and r1_prode < r2_prode) or \
       (r1_real == r2_real and r1_prode == r2_prode):
        pts += 1
        if int(r1_real) == int(r1_prode) and int(r2_real) == int(r2_prode):
            pts += 2
    return pts

# 3. CARGA Y LÓGICA PRINCIPAL
try:
    df_res = cargar_datos_seguro(URL_RESULTADOS)
    df_pro = cargar_datos_seguro(URL_PRONOSTICOS)

    if df_res is None or df_pro is None:
        st.error("Error de conexión con Google Sheets. Refresca la página.")
        st.stop()

    st.sidebar.title("Navegación")
    seccion = st.sidebar.radio("Ir a:", ["Ranking General", "Detalle por Jugador"])

    if seccion == "Ranking General":
        st.title("🏆 Ranking Prode Familiar")
        ranking = []
        for i in range(1, 11):
            total = 0
            for _, partido in df_res.iterrows():
                n = partido['N_Partido']
                prode = df_pro[df_pro['N_Partido'] == n]
                if not prode.empty:
                    puntos = calcular_puntos(partido['R1'], partido['R2'], prode[f'Jugador_{i}_E1'].iloc[0], prode[f'Jugador_{i}_E2'].iloc[0])
                    total += puntos
            ranking.append({"Familiar": f"Jugador {i}", "Puntos": total})
        
        df_ranking = pd.DataFrame(ranking).sort_values(by="Puntos", ascending=False)
        col1, col2 = st.columns([1, 2])
        with col1:
            st.dataframe(df_ranking.reset_index(drop=True), use_container_width=True)
        with col2:
            st.bar_chart(df_ranking.set_index("Familiar"))

    else:
        st.title("🔍 Detalle de Pronósticos")
        jugador_sel = st.selectbox("Selecciona un familiar:", [f"Jugador {i}" for i in range(1, 11)])
        # Extraemos el número del jugador seleccionado
        num_jugador = jugador_sel.split(" ")[1]
        
        detalle = []
        for _, partido in df_res.iterrows():
            n = partido['N_Partido']
            prode = df_pro[df_pro['N_Partido'] == n]
            
            p_r1 = prode[f'Jugador_{num_jugador}_E1'].iloc[0]
            p_r2 = prode[f'Jugador_{num_jugador}_E2'].iloc[0]
            pts = calcular_puntos(partido['R1'], partido['R2'], p_r1, p_r2)
            
            detalle.append({
                "Partido": f"{partido['Equipo_1']} vs {partido['Equipo_2']}",
                "Real": f"{int(partido['R1']) if not pd.isna(partido['R1']) else '-'} - {int(partido['R2']) if not pd.isna(partido['R2']) else '-'}",
                "Pronóstico": f"{int(p_r1)} - {int(p_r2)}",
                "Pts": pts
            })
        st.table(pd.DataFrame(detalle))

except Exception as e:
    st.error(f"Error crítico: {e}")
