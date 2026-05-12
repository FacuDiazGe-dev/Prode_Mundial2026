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
def procesar_nombres_ranking(row, df_rank_base, df_pro, df_res, df_usuarios):
    nombre = row['JUGADOR']
    posicion = row.name + 1 
    insignias = ""
    
    df_res['VIZ_CHECK'] = df_res['VIZ'].astype(str).str.strip().str.upper()
    res_visibles = df_res[df_res['VIZ_CHECK'].isin(['TRUE', '1', '1.0', 'VERDADERO', 'T'])]

    try:
        u_info = df_usuarios[df_usuarios['NOMBRE'] == nombre].iloc[0]
        u_nick = u_info['USUARIO']
        u_id = int(u_info['ID'])
    except:
        return nombre

    if posicion == 1: insignias += " 👑"
    if row['EXACTOS'] >= 5: insignias += " 🎯"
    
    max_gen = df_rank_base['GENERALES'].max()
    if row['GENERALES'] == max_gen and max_gen > 0: insignias += " 🧙‍♂️"
    if u_id <= 3: insignias += " 🏅"
    if len(df_rank_base) > 2 and posicion == len(df_rank_base): insignias += " 🐌"
        
    user_pro = df_pro[df_pro['USUARIO'] == u_nick]
    
    r_act, r_max = 0, 0
    for _, part_v in res_visibles.sort_values('N_PARTIDO').iterrows():
        id_p = part_v['N_PARTIDO']
        p_match = user_pro[user_pro['N_PARTIDO'] == id_p]
        
        if not p_match.empty:
            if pd.notna(part_v['R1']) and pd.notna(part_v['R2']):
                _, exa, _ = calcular_detalle(part_v['R1'], part_v['R2'], p_match.iloc[0]['P1'], p_match.iloc[0]['P2'])
                if exa == 1:
                    r_act += 1
                    r_max = max(r_max, r_act)
                else: 
                    r_act = 0
                    
    if r_max >= 3: insignias += f" 🔥x{r_max}"
    return f"{nombre}{insignias}"

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
    df_rank['JUGADOR'] = df_rank.apply(
        lambda r: procesar_nombres_ranking(r, df_rank, df_pro, df_res, df_users), 
        axis=1
    )
    df_rank.index = df_rank.index + 1
    df_rank.insert(0, 'Nº', df_rank.index.map(lambda x: "👑" if x == 1 else str(x)))
    
    return df_rank
