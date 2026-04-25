import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection

st.set_page_config(page_title="Prode Mundial 2026", page_icon="⚽", layout="wide")

# URL de tu Google Sheet
URL_SHEET = "https://google.com"

# Conexión con el conector oficial de Streamlit
conn = st.connection("gsheets", type=GSheetsConnection)

try:
    # Carga de datos (usa los nombres exactos de tus pestañas)
    df_res = conn.read(spreadsheet=URL_SHEET, worksheet="0") 
    df_pro = conn.read(spreadsheet=URL_SHEET, worksheet="394071446")

    st.title("🏆 Prode Familiar 2026")
    
    # Aquí iría el resto de tu lógica de ranking y detalles...
    st.write("Datos cargados correctamente ✅")
    st.dataframe(df_res.head())

except Exception as e:
    st.error(f"Error al conectar con Google Sheets: {e}")
# 1. CONFIGURACIÓN DE LA PÁGINA
st.set_page_config(page_title="Prode Mundial 2026", page_icon="⚽", layout="wide")

# ID de Google Sheets y URLs de exportación corregidas
SHEET_ID = "16GQN19xyzi_9jRKsaryNMhB80meX9RsJhyHlAU3Ek4c"
URL_RES = f"https://google.com{SHEET_ID}/export?format=csv&gid=0"
URL_PRO = f"https://google.com{SHEET_ID}/export?format=csv&gid=394071446"

# 2. LÓGICA DE PUNTUACIÓN
def calcular_puntos(r1_real, r2_real, r1_prode, r2_prode):
    try:
        # Si no hay resultado real cargado (celda vacía), no suma puntos
        if pd.isna(r1_real) or pd.isna(r2_real): 
            return 0
        
        r1_r, r2_r = int(r1_real), int(r2_real)
        r1_p, r2_p = int(r1_prode), int(r2_prode)
        
        pts = 0
        # Acierto de tendencia (Ganador o Empate) -> 1 punto
        if (r1_r > r2_r and r1_p > r2_p) or (r1_r < r2_r and r1_p < r2_p) or (r1_r == r2_r and r1_p == r2_p):
            pts += 1
            # Acierto de resultado exacto -> +2 puntos adicionales (Total 3)
            if r1_r == r1_p and r2_r == r2_p:
                pts += 2
        return pts
    except:
        return 0

# 3. CARGA DE DATOS
@st.cache_data(ttl=60)  # Se actualiza cada 60 segundos
def cargar_datos(url):
    return pd.read_csv(url)

try:
    df_res = cargar_datos(URL_RES)
    df_pro = cargar_datos(URL_PRO)

    # 4. INTERFAZ LATERAL
    st.sidebar.title("🏆 Prode 2026")
    seccion = st.sidebar.radio("Menú:", ["Ranking General", "Detalle por Jugador"])

    if seccion == "Ranking General":
        st.title("📊 Ranking de Posiciones")
        
        lista_ranking = []
        # Iteramos sobre los 10 jugadores posibles
        for i in range(1, 11):
            total_jugador = 0
            for _, partido in df_res.iterrows():
                n_p = partido['N_Partido']
                # Buscamos el pronóstico para ese número de partido
                prode_partido = df_pro[df_pro['N_Partido'] == n_p]
                
                if not prode_partido.empty:
                    p1 = prode_partido.iloc[0][f'Jugador_{i}_E1']
                    p2 = prode_partido.iloc[0][f'Jugador_{i}_E2']
                    puntos = calcular_puntos(partido['R1'], partido['R2'], p1, p2)
                    total_jugador += puntos
            
            lista_ranking.append({"Participante": f"Jugador {i}", "Puntos": int(total_jugador)})
        
        # Crear DataFrame de ranking y ordenar
        df_ranking_final = pd.DataFrame(lista_ranking).sort_values(by="Puntos", ascending=False)
        
        # Mostrar tabla y gráfico
        col1, col2 = st.columns([1, 1])
        with col1:
            st.dataframe(df_ranking_final, hide_index=True, use_container_width=True)
        with col2:
            st.bar_chart(df_ranking_final.set_index("Participante"))

    elif seccion == "Detalle por Jugador":
        st.title("🔍 Análisis Individual")
        jugador_idx = st.selectbox("Selecciona un jugador:", range(1, 11), format_func=lambda x: f"Jugador {x}")
        
        hoja_detalle = []
        for _, partido in df_res.iterrows():
            n_p = partido['N_Partido']
            prode_partido = df_pro[df_pro['N_Partido'] == n_p]
            
            if not prode_partido.empty:
                p1_v = prode_partido.iloc[0][f'Jugador_{jugador_idx}_E1']
                p2_v = prode_partido.iloc[0][f'Jugador_{jugador_idx}_E2']
                pts_obtenidos = calcular_puntos(partido['R1'], partido['R2'], p1_v, p2_v)
                
                # Formateo de resultados para visualización
                res_real = f"{int(partido['R1'])} - {int(partido['R2'])}" if not pd.isna(partido['R1']) else "⏳"
                res_prode = f"{int(p1_v)} - {int(p2_v)}" if not pd.isna(p1_v) else "-"
                
                hoja_detalle.append({
                    "Partido": f"{partido['Equipo_1']} vs {partido['Equipo_2']}",
                    "Resultado Real": res_real,
                    "Tu Pronóstico": res_prode,
                    "Pts": pts_obtenidos
                })
        
        st.table(pd.DataFrame(hoja_detalle))

except Exception as e:
    st.error("Hubo un problema al cargar los datos.")
    st.write(f"Detalle técnico: {e}")
    st.info("💡 Consejo: Verifica que el archivo de Google Sheets tenga los permisos de 'Lector' para cualquier persona con el enlace.")
