import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection

# 1. CONFIGURACIÓN DE LA PÁGINA
st.set_page_config(page_title="Prode Mundial 2026", page_icon="⚽", layout="wide")

# URL de tu Google Sheet (Asegúrate de que sea pública: "Cualquier persona con el enlace")
URL_SHEET = "https://google.com"

# 2. FUNCIÓN DE CÁLCULO DE PUNTOS
def calcular_puntos(r1_real, r2_real, r1_prode, r2_prode):
    try:
        if pd.isna(r1_real) or pd.isna(r2_real): return 0
        r1_r, r2_r = int(r1_real), int(r2_real)
        r1_p, r2_p = int(r1_prode), int(r2_prode)
        
        pts = 0
        # Acierto de tendencia (Ganador o Empate)
        if (r1_r > r2_r and r1_p > r2_p) or (r1_r < r2_r and r1_p < r2_p) or (r1_r == r2_r and r1_p == r2_p):
            pts += 1
            # Bono por resultado exacto (Total 3 puntos)
            if r1_r == r1_p and r2_r == r2_p:
                pts += 2
        return pts
    except:
        return 0

# 3. CONEXIÓN Y CARGA DE DATOS
conn = st.connection("gsheets", type=GSheetsConnection)

try:
    # Intentamos cargar por nombres comunes. Si fallan, cámbiar "RESULTADOS" por el nombre real de tu solapa.
    df_res = conn.read(spreadsheet=URL_SHEET, worksheet="0") # GID 0 suele ser la primera hoja
    df_pro = conn.read(spreadsheet=URL_SHEET, worksheet="394071446") # GID de Pronósticos

    # 4. INTERFAZ DE USUARIO
    st.sidebar.title("🏆 Menú Prode")
    seccion = st.sidebar.radio("Ir a:", ["Ranking General", "Detalle por Jugador"])

    if seccion == "Ranking General":
        st.title("📊 Tabla de Posiciones")
        ranking = []
        
        # Calculamos puntos para los 10 jugadores definidos en tu Excel
        for i in range(1, 11):
            total_jugador = 0
            for _, partido in df_res.iterrows():
                n_p = partido['N_Partido']
                prode_partido = df_pro[df_pro['N_Partido'] == n_p]
                
                if not prode_partido.empty:
                    col_e1 = f'Jugador_{i}_E1'
                    col_e2 = f'Jugador_{i}_E2'
                    # Verificamos que las columnas existan en el prode
                    if col_e1 in prode_partido.columns and col_e2 in prode_partido.columns:
                        p1 = prode_partido.iloc[0][col_e1]
                        p2 = prode_partido.iloc[0][col_e2]
                        total_jugador += calcular_puntos(partido['R1'], partido['R2'], p1, p2)
            
            ranking.append({"Participante": f"Jugador {i}", "Puntos": int(total_jugador)})
        
        df_rank = pd.DataFrame(ranking).sort_values(by="Puntos", ascending=False)
        
        c1, c2 = st.columns([1, 1])
        with c1:
            st.subheader("Puntajes")
            st.dataframe(df_rank, hide_index=True, use_container_width=True)
        with c2:
            st.subheader("Gráfico")
            st.bar_chart(df_rank.set_index("Participante"), color="#2e7d32")

    else:
        st.title("🔍 Detalle Individual")
        jugador_idx = st.selectbox("Selecciona un jugador:", range(1, 11), format_func=lambda x: f"Jugador {x}")
        
        detalles = []
        for _, partido in df_res.iterrows():
            n_p = partido['N_Partido']
            prode_partido = df_pro[df_pro['N_Partido'] == n_p]
            
            if not prode_partido.empty:
                col_e1 = f'Jugador_{jugador_idx}_E1'
                col_e2 = f'Jugador_{jugador_idx}_E2'
                
                if col_e1 in prode_partido.columns:
                    p1_v = prode_partido.iloc[0][col_e1]
                    p2_v = prode_partido.iloc[0][col_e2]
                    pts = calcular_puntos(partido['R1'], partido['R2'], p1_v, p2_v)
                    
                    res_real = f"{int(partido['R1'])} - {int(partido['R2'])}" if not pd.isna(partido['R1']) else "⏳ Pendiente"
                    res_prode = f"{int(p1_v)} - {int(p2_v)}" if not pd.isna(p1_v) else "-"
                    
                    detalles.append({
                        "Partido": f"{partido['Equipo_1']} vs {partido['Equipo_2']}",
                        "Real": res_real,
                        "Tu Prode": res_prode,
                        "Puntos": pts
                    })
        
        st.dataframe(pd.DataFrame(detalles), use_container_width=True, hide_index=True)

except Exception as e:
    st.error("⚠️ Error de conexión o formato")
    st.write(f"Detalle: {e}")
    st.info("Revisa que los nombres de las columnas en el Excel coincidan (N_Partido, R1, R2, etc.)")
