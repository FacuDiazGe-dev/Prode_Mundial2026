import streamlit as st
import pandas as pd

# 1. CONFIGURACIÓN
st.set_page_config(page_title="Prode Mundial 2026", page_icon="⚽", layout="wide")

# ID de tu hoja y GIDs
SHEET_ID = "16GQN19xyzi_9jRKsaryNMhB80meX9RsJhyHlAU3Ek4c"
# GID 0 suele ser la primera pestaña, 394071446 es la que me pasaste
URL_RES = f"https://google.com{SHEET_ID}/export?format=csv&gid=0"
URL_PRO = f"https://google.com{SHEET_ID}/export?format=csv&gid=394071446"

def calcular_puntos(r1_real, r2_real, r1_prode, r2_prode):
    try:
        # Convertimos a entero para evitar errores de comparación
        r1_r, r2_r = int(r1_real), int(r2_real)
        r1_p, r2_p = int(r1_prode), int(r2_prode)
    except:
        return 0
    
    pts = 0
    # Ganador o Empate (+1)
    if (r1_r > r2_r and r1_p > r2_p) or (r1_r < r2_r and r1_p < r2_p) or (r1_r == r2_r and r1_p == r2_p):
        pts += 1
        # Exacto (+2 adicionales)
        if r1_r == r1_p and r2_r == r2_p:
            pts += 2
    return pts

try:
    # CARGA DIRECTA DE CSV
    df_res = pd.read_csv(URL_RES)
    df_pro = pd.read_csv(URL_PRO)

    st.sidebar.title("Menú")
    seccion = st.sidebar.radio("Ir a:", ["Ranking General", "Detalle por Jugador"])

    if seccion == "Ranking General":
        st.title("🏆 Ranking Familiar - Mundial 2026")
        ranking = []
        for i in range(1, 11):
            total = 0
            for _, part in df_res.iterrows():
                n = part['N_Partido']
                prode = df_pro[df_pro['N_Partido'] == n]
                if not prode.empty:
                    # Usamos [0] para obtener el valor escalar
                    p1 = prode[f'Jugador_{i}_E1'].values[0]
                    p2 = prode[f'Jugador_{i}_E2'].values[0]
                    total += calcular_puntos(part['R1'], part['R2'], p1, p2)
            ranking.append({"Familiar": f"Jugador {i}", "Puntos": int(total)})
        
        df_rank = pd.DataFrame(ranking).sort_values(by="Puntos", ascending=False)
        c1, c2 = st.columns(2)
        with c1: st.table(df_rank.reset_index(drop=True))
        with c2: st.bar_chart(df_rank.set_index("Familiar"))

    else:
        st.title("🔍 Detalle por Jugador")
        jugador_sel = st.selectbox("Selecciona un familiar:", [f"Jugador {i}" for i in range(1, 11)])
        num = jugador_sel.split(" ")[1] # Obtenemos solo el número
        
        detalle = []
        for _, part in df_res.iterrows():
            n = part['N_Partido']
            prode = df_pro[df_pro['N_Partido'] == n]
            if not prode.empty:
                p1 = prode[f'Jugador_{num}_E1'].values[0]
                p2 = prode[f'Jugador_{num}_E2'].values[0]
                pts = calcular_puntos(part['R1'], part['R2'], p1, p2)
                detalle.append({
                    "Partido": f"{part['Equipo_1']} vs {part['Equipo_2']}",
                    "Real": f"{int(part['R1'])} - {int(part['R2'])}" if not pd.isna(part['R1']) else "Pendiente",
                    "Pronóstico": f"{int(p1)} - {int(p2)}",
                    "Pts": pts
                })
        st.dataframe(pd.DataFrame(detalle), use_container_width=True, hide_index=True)

except Exception as e:
    st.error(f"Error de conexión: {e}")
    st.info("Verifica que las pestañas se llamen RESULTADOS y PRONOSTICOS exactamente.")
