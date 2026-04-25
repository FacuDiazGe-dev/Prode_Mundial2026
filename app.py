import streamlit as st
import pandas as pd

# Configuración de la página
st.set_page_config(page_title="Prode Mundial 2026", page_icon="⚽", layout="wide")

# ID de tu documento
SHEET_ID = "16GQN19xyzi_9jRKsaryNMhB80meX9RsJhyHlAU3Ek4c"

# URLs para leer las pestañas específicas como CSV
# IMPORTANTE: En Google Sheets ve a Archivo > Compartir > Compartir con otros 
# y asegúrate de que "Cualquier persona con el enlace" pueda leer.
URL_RESULTADOS = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet=RESULTADOS"
URL_PRONOSTICOS = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet=PRONOSTICOS"

def calcular_puntos(r1_real, r2_real, r1_prode, r2_prode):
    # Si no hay resultado cargado, no suma
    if pd.isna(r1_real) or pd.isna(r2_real):
        return 0
    
    puntos = 0
    # Lógica de Ganador/Empate (+1)
    if (r1_real > r2_real and r1_prode > r2_prode) or \
       (r1_real < r2_real and r1_prode < r2_prode) or \
       (r1_real == r2_real and r1_prode == r2_prode):
        puntos += 1
        # Lógica Exacto (+2 adicionales = Total 3)
        if r1_real == r1_prode and r2_real == r2_prode:
            puntos += 2
    return puntos

try:
    # Carga de datos
    df_res = pd.read_csv(URL_RESULTADOS)
    df_pro = pd.read_csv(URL_PRONOSTICOS)

    st.title("🏆 Mundial 2026 - Ranking Familiar")
    st.write("Resultados actualizados automáticamente desde el Google Sheet.")

    ranking = []
    # Calculamos puntos para los 10 jugadores
    for i in range(1, 11):
        total_puntos = 0
        for _, fila in df_res.iterrows():
            n_partido = fila['N_Partido']
            # Buscamos el pronóstico de este jugador para este partido
            prode_row = df_pro[df_pro['N_Partido'] == n_partido]
            
            if not prode_row.empty:
                p_r1 = prode_row.iloc[0][f'Jugador_{i}_E1']
                p_r2 = prode_row.iloc[0][f'Jugador_{i}_E2']
                
                puntos = calcular_puntos(fila['R1'], fila['R2'], p_r1, p_r2)
                total_puntos += puntos
        
        ranking.append({"Familiar": f"Jugador {i}", "Puntos": total_puntos})

    # Crear y ordenar el Ranking
    df_ranking = pd.DataFrame(ranking).sort_values(by="Puntos", ascending=False).reset_index(drop=True)
    df_ranking.index += 1 # Para que la posición empiece en 1

    # Interfaz Visual
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.subheader("Tabla de Posiciones")
        st.table(df_ranking)

    with col2:
        st.subheader("Gráfico de Rendimiento")
        st.bar_chart(df_ranking.set_index("Familiar"))

    # Mostrar partidos jugados para control
    with st.expander("Ver resultados cargados"):
        st.dataframe(df_res.dropna(subset=['R1']))

except Exception as e:
    st.error(f"Error al conectar con la hoja: {e}")
    st.info("Asegúrate de que el archivo de Google Sheets tenga acceso público para lectura.")
