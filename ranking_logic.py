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

# 2. FUNCIÓN DE APOYO PARA PROCESAR INSIGNIAS NUEVAS
def calcular_badges_globales_ranking(df_rank, df_pro):
    """
    Calcula qué usuario gana cada badge disponible para mostrar en el ranking.
    No modifica el nombre del jugador.
    """

    badge_por_usuario = {}

    def add_badge(usuario, badge):
        usuario = str(usuario)

        if usuario not in badge_por_usuario:
            badge_por_usuario[usuario] = []

        if badge not in badge_por_usuario[usuario]:
            badge_por_usuario[usuario].append(badge)

    if df_rank.empty:
        return badge_por_usuario

    # ------------------------------------------------------------
    # 1. PUNTERO — mayor puntaje
    # ------------------------------------------------------------

    top_row = df_rank.iloc[0]

    if int(top_row.get("PUNTOS", 0)) > 0:
        add_badge(
            top_row.get("USUARIO", ""),
            "Puntero"
        )

    # ------------------------------------------------------------
    # 2. SR. PRODE — más exactos
    # ------------------------------------------------------------

    if "EXACTOS" in df_rank.columns:
        max_exactos = int(df_rank["EXACTOS"].max())

        if max_exactos > 0:
            usuarios_exactos = (
                df_rank[df_rank["EXACTOS"] == max_exactos]["USUARIO"]
                .astype(str)
                .tolist()
            )

            for usuario in usuarios_exactos:
                add_badge(usuario, "Sr. Prode")

    # ------------------------------------------------------------
    # 3. SIEMPRE SUMA — más generales
    # ------------------------------------------------------------

    if "GENERALES" in df_rank.columns:
        max_generales = int(df_rank["GENERALES"].max())

        if max_generales > 0:
            usuarios_generales = (
                df_rank[df_rank["GENERALES"] == max_generales]["USUARIO"]
                .astype(str)
                .tolist()
            )

            for usuario in usuarios_generales:
                add_badge(usuario, "Siempre Suma")

    # ------------------------------------------------------------
    # DATOS DE PRONÓSTICOS POR USUARIO
    # ------------------------------------------------------------

    stats_pronosticos = []

    for _, row in df_rank.iterrows():
        usuario = str(row.get("USUARIO", ""))

        pro_user = df_pro[
            df_pro["USUARIO"].astype(str) == usuario
        ]

        if pro_user.empty:
            continue

        p1 = pd.to_numeric(
            pro_user["P1"],
            errors="coerce"
        ).fillna(0)

        p2 = pd.to_numeric(
            pro_user["P2"],
            errors="coerce"
        ).fillna(0)

        total_partidos = len(pro_user)

        goles_totales = int(
            (p1 + p2).sum()
        )

        promedio_goles = (
            goles_totales / total_partidos
            if total_partidos > 0
            else 0
        )

        empates = int(
            (p1 == p2).sum()
        )

        stats_pronosticos.append({
            "usuario": usuario,
            "total_partidos": total_partidos,
            "goles_totales": goles_totales,
            "promedio_goles": promedio_goles,
            "empates": empates
        })

    # ------------------------------------------------------------
    # 4. OPTIMISTA DEL GOL — mayor promedio de goles
    # ------------------------------------------------------------

    if stats_pronosticos:
        optimista = max(
            stats_pronosticos,
            key=lambda x: x["promedio_goles"]
        )

        add_badge(
            optimista["usuario"],
            "Optimista del Gol"
        )

    # ------------------------------------------------------------
    # 5. EL CHOLO — menor promedio de goles
    # ------------------------------------------------------------

    if stats_pronosticos:
        cholo = min(
            stats_pronosticos,
            key=lambda x: x["promedio_goles"]
        )

        add_badge(
            cholo["usuario"],
            "El Cholo"
        )

    # ------------------------------------------------------------
    # 6. REY DEL EMPATE — más empates pronosticados
    # ------------------------------------------------------------

    if stats_pronosticos:
        rey_empate = max(
            stats_pronosticos,
            key=lambda x: x["empates"]
        )

        add_badge(
            rey_empate["usuario"],
            "Rey del Empate"
        )

    # ------------------------------------------------------------
    # 7. EL DISTINTO — más alejado de la media del grupo
    # ------------------------------------------------------------

    if len(stats_pronosticos) >= 2:
        distintos = []

        for jugador in stats_pronosticos:
            otros = [
                x for x in stats_pronosticos
                if x["usuario"] != jugador["usuario"]
            ]

            if not otros:
                continue

            promedio_otros = (
                sum(x["promedio_goles"] for x in otros) / len(otros)
            )

            diferencia = abs(
                jugador["promedio_goles"] - promedio_otros
            )

            distintos.append({
                "usuario": jugador["usuario"],
                "diferencia": diferencia
            })

        if distintos:
            distinto = max(
                distintos,
                key=lambda x: x["diferencia"]
            )

            add_badge(
                distinto["usuario"],
                "El Distinto"
            )

    return badge_por_usuario


def procesar_badges_ranking(row, badge_por_usuario):
    """
    Devuelve las insignias del usuario para el ranking.
    """

    usuario = str(row.get("USUARIO", ""))

    return badge_por_usuario.get(usuario, [])


# 3. FUNCIÓN PRINCIPAL DE RANKING
@st.cache_data(ttl=60)
def obtener_ranking_global(df_users, df_pro, df_res):
    ranking_data = []

    if df_users is None or df_users.empty:
        return pd.DataFrame(
            columns=[
                "Nº",
                "ID_PARA_FOTO",
                "JUGADOR",
                "PUNTOS",
                "EXACTOS",
                "GENERALES",
                "USUARIO",
                "BADGES"
            ]
        )

    if "VIZ" in df_res.columns:
        df_res = df_res.copy()
        df_res["VIZ_STR"] = df_res["VIZ"].fillna("FALSE").astype(str)

        res_visibles = df_res[
            df_res["VIZ_STR"]
            .str.upper()
            .str.contains("TRUE|1|1.0", na=False)
        ]
    else:
        res_visibles = df_res[
            df_res["R1"].notna()
        ]

    for _, u in df_users.iterrows():
        u_nick = u["USUARIO"]

        pts_t = 0
        exa_t = 0
        gen_t = 0

        pro_usr = df_pro[
            df_pro["USUARIO"] == u_nick
        ]

        for _, part in res_visibles.iterrows():
            id_p = int(part["N_PARTIDO"])

            p_match = pro_usr[
                pro_usr["N_PARTIDO"] == id_p
            ]

            if not p_match.empty:
                r1 = part["R1"]
                r2 = part["R2"]
                p1 = p_match.iloc[0]["P1"]
                p2 = p_match.iloc[0]["P2"]

                if pd.notna(r1) and pd.notna(r2):
                    pts, exa, gen = calcular_detalle(
                        r1,
                        r2,
                        p1,
                        p2
                    )

                    pts_t += pts
                    exa_t += exa
                    gen_t += gen

        ranking_data.append({
            "ID_PARA_FOTO": u["ID"],
            "JUGADOR": u["NOMBRE"],
            "PUNTOS": pts_t,
            "EXACTOS": exa_t,
            "GENERALES": gen_t,
            "USUARIO": u_nick
        })

    if not ranking_data:
        return pd.DataFrame(
            columns=[
                "Nº",
                "ID_PARA_FOTO",
                "JUGADOR",
                "PUNTOS",
                "EXACTOS",
                "GENERALES",
                "USUARIO",
                "BADGES"
            ]
        )

    df_rank = (
        pd.DataFrame(ranking_data)
        .sort_values(
            by=["PUNTOS", "EXACTOS"],
            ascending=False
        )
        .reset_index(drop=True)
    )

    badge_por_usuario = calcular_badges_globales_ranking(
        df_rank,
        df_pro
    )

    df_rank["BADGES"] = df_rank.apply(
        lambda r: procesar_badges_ranking(
            r,
            badge_por_usuario
        ),
        axis=1
    )

    df_rank.index = df_rank.index + 1

    df_rank.insert(
        0,
        "Nº",
        df_rank.index.map(lambda x: str(x))
    )

    return df_rank
    
    # Si querés quitar también la corona vieja del Nº:
    df_rank.insert(0, "Nº", df_rank.index.map(lambda x: str(x)))
    
    # Si querés conservar la corona solo en el número 1, dejá esta línea en vez de la anterior:
    # df_rank.insert(0, "Nº", df_rank.index.map(lambda x: "👑" if x == 1 else str(x)))
    return df_rank
