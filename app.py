import streamlit as st
import pandas as pd

# 1. CONFIGURACIÓN DE LA PÁGINA
st.set_page_config(page_title="Prode Mundial 2026", page_icon="⚽", layout="wide")

# ID de tu hoja (sacado de tu link)
SHEET_ID = "16GQN19xyzi_9jRKsaryNMhB80meX9RsJhyHlAU3Ek4c"

# URLs usando el motor de visualización (lee las pestañas por su nombre exacto)
URL_RES = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet=RESULTADOS"
URL_PRO = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet=PRONOSTICOS"

def calcular_puntos(r1_real, r2_real, r1_prode, r2_prode):
    try:
        if pd.isna(r1_real) or pd.isna(r2_real): return 0
        # Convertimos a entero para comparar
        r1_r, r2_r = int(r1_real), int(r2_real)
        r1_p, r2_p = int(r1_prode), int(r2_prode)
        
        pts = 0
        # Regla: Ganador o Empate (+1)
        if (r1_r > r2_r and r1_p > r2_p) or (r1_r < r2_r and r1_p < r2_p) or (r1_r == r2_r and r1_p == r2_p):
            pts += 1
            # Regla: Resultado Exacto (+2 adicionales = Total 3)
            if r1_r == r1_p and r2_r == r2_p:
                pts += 2
        return pts
    except:
        return 0

try:
    # Carga de datos desde Google
    df_res = pd.read_csv(URL_RES)
    df_pro = pd.read_csv(URL_PRO)

    st.sidebar.title("Menú Mundial")
    seccion = st.sidebar.radio("Ir a:", ["Ranking General", "Detalle por Jugador"])

    if seccion == "Ranking General":
        st.title("🏆 Ranking Familiar - Mundial 2026")
        ranking = []
        for i in range(1, 11):
            total = 0
            for _, part in df_res.iterrows():
                n_partido = part['N_Partido']
                prode = df_pro[df_pro['N_Partido'] == n_partido]
                if not prode.empty:
                    p1 = prode[f'Jugador_{i}_E1'].values[0]
                    p2 = prode[f'Jugador_{i}_E2'].values[0]
                    total += calcular_puntos(part['R1'], part['R2'], p1, p2)
            ranking.append({"Familiar": f"Jugador {i}", "Puntos": int(total)})
        
        df_rank = pd.DataFrame(ranking).sort_values(by="Puntos", ascending=False)
        
        col1, col2 = st.columns(2)
        with col1:
            st.subheader("Tabla de Posiciones")
            st.table(df_rank.reset_index(drop=True))
        with col2:
            st.subheader("Rendimiento")
            st.bar_chart(df_rank.set_index("Familiar"))

    else:
        st.title("🔍 Detalle de Pronósticos")
        jugador_sel = st.selectbox("Selecciona un familiar:", [f"Jugador {i}" for i in range(1, 11)])
        # Extraemos solo el número del texto "Jugador X"
        n_jug = jugador_sel.split(" ")[1]
        
        detalle = []
        for _, part in df_res.iterrows():
            n_p = part['N_Partido']
            prode = df_pro[df_pro['N_Partido'] == n_p]
            if not prode.empty:
                p1 = prode[f'Jugador_{n_jug}_E1'].values[0]
                p2 = prode[f'Jugador_{n_jug}_E2'].values[0]
                pts = calcular_puntos(part['R1'], part['R2'], p1, p2)
                
                detalle.append({
                    "Partido": f"{part['Equipo_1']} vs {part['Equipo_2']}",
                    "Real": f"{int(part['R1'])} - {int(part['R2'])}" if not pd.isna(part['R1']) else "Pendiente",
                    "Tu Pronóstico": f"{int(p1)} - {int(p2)}",
                    "Pts": pts
                })
        st.dataframe(pd.DataFrame(detalle), use_container_width=True, hide_index=True)

except Exception as e:
    st.error(f"Error al cargar datos: {e}")
    st.info("Asegúrate de que las pestañas en Excel se llamen RESULTADOS y PRONOSTICOS (en mayúsculas).")
