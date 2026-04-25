import streamlit as st
import pandas as pd

# 1. CONFIGURACIÓN
st.set_page_config(page_title="Prode Mundial 2026", page_icon="⚽", layout="wide")

# URLs de exportación directa (Corregidas para evitar el 404)
# Importante: El ID termina en 'Ek4c'
SHEET_ID = "16GQN19xyzi_9jRKsaryNMhB80meX9RsJhyHlAU3Ek4c"
URL_RES = f"https://google.com{SHEET_ID}/export?format=csv&gid=0"
URL_PRO = f"https://google.com{SHEET_ID}/export?format=csv&gid=394071446"

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

try:
    # Carga simple con Pandas (Añadimos almacenamiento en caché de 1 min)
    @st.cache_data(ttl=60)
    def cargar_datos(url):
        return pd.read_csv(url)

    df_res = cargar_datos(URL_RES)
    df_pro = cargar_datos(URL_PRO)

    st.title("🏆 Prode Familiar 2026")

    menu = st.sidebar.radio("Menú", ["Ranking General", "Detalle por Jugador"])

    if menu == "Ranking General":
        ranking = []
        for i in range(1, 11):
            total = 0
            for _, part in df_res.iterrows():
                n_p = part['N_Partido']
                prode = df_pro[df_pro['N_Partido'] == n_p]
                if not prode.empty:
                    # Usamos .values[0] para obtener el dato puro de la celda
                    p1 = prode[f'Jugador_{i}_E1'].values[0]
                    p2 = prode[f'Jugador_{i}_E2'].values[0]
                    total += calcular_puntos(part['R1'], part['R2'], p1, p2)
            ranking.append({"Participante": f"Jugador {i}", "Puntos": int(total)})
        
        df_rank = pd.DataFrame(ranking).sort_values(by="Puntos", ascending=False)
        st.table(df_rank.reset_index(drop=True))
        st.bar_chart(df_rank.set_index("Participante"))

    else:
        jug_sel = st.selectbox("Selecciona Jugador:", range(1, 11), format_func=lambda x: f"Jugador {x}")
        detalle = []
        for _, part in df_res.iterrows():
            n_p = part['N_Partido']
            prode = df_pro[df_pro['N_Partido'] == n_p]
            if not prode.empty:
                p1_v = prode[f'Jugador_{jug_sel}_E1'].values[0]
                p2_v = prode[f'Jugador_{jug_sel}_E2'].values[0]
                pts = calcular_puntos(part['R1'], part['R2'], p1_v, p2_v)
                detalle.append({
                    "Partido": f"{part['Equipo_1']} vs {part['Equipo_2']}",
                    "Real": f"{int(part['R1'])} - {int(part['R2'])}" if not pd.isna(part['R1']) else "⏳",
                    "Tu Prode": f"{int(p1_v)} - {int(p2_v)}",
                    "Pts": pts
                })
        st.dataframe(pd.DataFrame(detalle), use_container_width=True, hide_index=True)

except Exception as e:
    st.error(f"Error de carga: {e}")
    st.info("Verifica que el Google Sheet esté compartido como 'Cualquier persona con el enlace puede leer'.")
