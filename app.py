import streamlit as st
import pandas as pd

# 1. CONFIGURACIÓN
st.set_page_config(page_title="Prode Mundial 2026", page_icon="⚽", layout="wide")

# Tu ID de hoja (sacado de tu link)
SHEET_ID = "16GQN19xyzi_9jRKsaryNMhB80meX9RsJhyHlAU3Ek4c"

# URLs directas de exportación (Formato garantizado para Streamlit)
URL_RES = f"https://google.com{SHEET_ID}/export?format=csv&gid=0"
URL_PRO = f"https://google.com{SHEET_ID}/export?format=csv&gid=394071446"

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

try:
    # Carga directa
    df_res = pd.read_csv(URL_RES)
    df_pro = pd.read_csv(URL_PRO)

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
                    p1 = prode[f'Jugador_{i}_E1'].values[0]
                    p2 = prode[f'Jugador_{i}_E2'].values[0]
                    total += calcular_puntos(partido['R1'], partido['R2'], p1, p2)
            ranking.append({"Familiar": f"Jugador {i}", "Puntos": total})
        
        df_ranking = pd.DataFrame(ranking).sort_values(by="Puntos", ascending=False)
        col1, col2 = st.columns(2)
        with col1: st.table(df_ranking.reset_index(drop=True))
        with col2: st.bar_chart(df_ranking.set_index("Familiar"))

    else:
        st.title("🔍 Detalle de Pronósticos")
        jugador_sel = st.selectbox("Selecciona un familiar:", [f"Jugador {i}" for i in range(1, 11)])
        num = jugador_sel.split(" ")[1]
        
        detalle = []
        for _, partido in df_res.iterrows():
            n = partido['N_Partido']
            prode = df_pro[df_pro['N_Partido'] == n]
            if not prode.empty:
                p1 = prode[f'Jugador_{num}_E1'].values[0]
                p2 = prode[f'Jugador_{num}_E2'].values[0]
                pts = calcular_puntos(partido['R1'], partido['R2'], p1, p2)
                detalle.append({
                    "Partido": f"{partido['Equipo_1']} vs {partido['Equipo_2']}",
                    "Real": f"{int(partido['R1']) if not pd.isna(partido['R1']) else '-'} - {int(partido['R2']) if not pd.isna(partido['R2']) else '-'}",
                    "Pronóstico": f"{int(p1)} - {int(p2)}",
                    "Pts": pts
                })
        st.table(pd.DataFrame(detalle))

except Exception as e:
    st.error(f"Error técnico: {e}")
