import pandas as pd
import streamlit as st

# 1. FUNCIÓN DE CÁLCULO DE PUNTOS (Tu versión exacta)
def calcular_detalle(r1, r2, p1, p2):
    """
    Calcula puntos según: +1 por tendencia, +2 adicional por exacto (Total 3).
    """
    if pd.isna(r1) or pd.isna(r2) or pd.isna(p1) or pd.isna(p2):
        return 0, 0, 0 
    
    puntos, exactos, generales = 0, 0, 0
    r1, r2, p1, p2 = int(r1), int(r2), int(p1), int(p2)
    
    tendencia_real = 1 if r1 > r2 else (2 if r2 > r1 else 0)
    tendencia_pron = 1 if p1 > p2 else (2 if p2 > p1 else 0)
    
    # Si acertó la tendencia (Ganador o Empate)
    if tendencia_real == tendencia_pron:
        generales = 1
        puntos = 1 
        # Si además acertó el marcador exacto
        if r1 == p1 and r2 == p2:
            exactos = 1
            puntos = 3 
    return puntos, exactos, generales

# 2. FUNCIÓN DE APOYO PARA PROCESAR INSIGNIAS (Tu versión exacta)
def procesar_badges_ranking(row, df_rank_base):
    """
    Devuelve una lista de badges nuevos para mostrar visualmente en el ranking.
    No modifica el nombre del jugador.
    """

    badges = []

    posicion = row.name + 1

    puntos = int(row.get("PUNTOS", 0))
    exactos = int(row.get("EXACTOS", 0))
    generales = int(row.get("GENERALES", 0))

    max_puntos = int(df_rank_base["PUNTOS"].max()) if not df_rank_base.empty else 0
    max_exactos = int(df_rank_base["EXACTOS"].max()) if "EXACTOS" in df_rank_base.columns else 0
    max_generales = int(df_rank_base["GENERALES"].max()) if "GENERALES" in df_rank_base.columns else 0

    # 1. Puntero
    if posicion == 1 and puntos > 0:
        badges.append("Puntero")

    # 2. Sr. Prode
    if exactos == max_exactos and max_exactos > 0:
        badges.append("Sr. Prode")

    # 3. Siempre Suma
    if generales == max_generales and max_generales > 0:
        badges.append("Siempre Suma")

    return badges


# 3. FUNCIÓN PRINCIPAL DE RANKING (Tu versión exacta)
@st.cache_data(ttl=60)
def obtener_ranking_global(df_users, df_pro, df_res):
    ranking_data = []
    
    if 'VIZ' in df_res.columns:
        df_res['VIZ_STR'] = df_res['VIZ'].fillna('FALSE').astype(str)
        res_visibles = df_res[df_res['VIZ_STR'].str.upper().str.contains('TRUE|1|1.0', na=False)]
    else:
        res_visibles = df_res[df_res['R1'].notna()]
    
    for _, u in df_users.iterrows():
        u_nick = u['USUARIO']
        pts_t, exa_t, gen_t = 0, 0, 0
        pro_usr = df_pro[df_pro['USUARIO'] == u_nick]
        
        for _, part in res_visibles.iterrows():
            id_p = int(part['N_PARTIDO'])
            p_match = pro_usr[pro_usr['N_PARTIDO'] == id_p]
            
            if not p_match.empty:
                r1, r2 = part['R1'], part['R2']
                p1, p2 = p_match.iloc[0]['P1'], p_match.iloc[0]['P2']
                
                if pd.notna(r1) and pd.notna(r2):
                    pts, exa, gen = calcular_detalle(r1, r2, p1, p2)
                    pts_t += pts
                    exa_t += exa
                    gen_t += gen
                    
        ranking_data.append({
            'ID_PARA_FOTO': u['ID'],
            'JUGADOR': u['NOMBRE'], 
            'PUNTOS': pts_t, 
            'EXACTOS': exa_t, 
            'GENERALES': gen_t,
            'USUARIO': u_nick
        })
    
    if not ranking_data:
        return pd.DataFrame(columns=['Nº', 'JUGADOR', 'PUNTOS', 'EXACTOS', 'GENERALES'])

    df_rank = pd.DataFrame(ranking_data).sort_values(by=['PUNTOS', 'EXACTOS'], ascending=False).reset_index(drop=True)
    
    # IMPORTANTE: Aplicar insignias antes de formatear el índice
    # Nueva columna de insignias visuales.
    # JUGADOR queda limpio, sin emojis agregados al nombre.
    df_rank["BADGES"] = df_rank.apply(
        lambda r: procesar_badges_ranking(r, df_rank),
        axis=1
    )
    
    df_rank.index = df_rank.index + 1
    
    # Si querés quitar también la corona vieja del Nº:
    df_rank.insert(0, "Nº", df_rank.index.map(lambda x: str(x)))
    
    # Si querés conservar la corona solo en el número 1, dejá esta línea en vez de la anterior:
    # df_rank.insert(0, "Nº", df_rank.index.map(lambda x: "👑" if x == 1 else str(x)))
