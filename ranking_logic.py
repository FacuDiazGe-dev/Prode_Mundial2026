import pandas as pd
import streamlit as st

RANKING_COLUMNS = [
    "Nº",
    "ID_PARA_FOTO",
    "JUGADOR",
    "PUNTOS",
    "EXACTOS",
    "GENERALES",
    "USUARIO",
    "BADGES"
]


def crear_ranking_vacio():
    return pd.DataFrame(columns=RANKING_COLUMNS)


def safe_int(value, default=0):
    try:
        return int(value)
    except Exception:
        return default


# ============================================================
# CALCULO DE PUNTOS POR PARTIDO
# Regla central del Prode:
# - 1 punto por acertar tendencia
# - 3 puntos si ademas acierta resultado exacto
# Si cambia el sistema de puntos, empezar por esta funcion.
# ============================================================
def calcular_detalle(r1, r2, p1, p2):
    """
    Calcula puntos según: +1 por tendencia, +2 adicional por exacto (Total 3).
    """
    if pd.isna(r1) or pd.isna(r2) or pd.isna(p1) or pd.isna(p2):
        return 0, 0, 0 
    
    puntos, exactos, generales = 0, 0, 0
    r1, r2, p1, p2 = safe_int(r1), safe_int(r2), safe_int(p1), safe_int(p2)
    
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


def calcular_stats_pronosticos_badges(df_rank, df_pro):
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

        goles_totales = safe_int(
            (p1 + p2).sum()
        )

        promedio_goles = (
            goles_totales / total_partidos
            if total_partidos > 0
            else 0
        )

        empates = safe_int(
            (p1 == p2).sum()
        )

        stats_pronosticos.append({
            "usuario": usuario,
            "total_partidos": total_partidos,
            "goles_totales": goles_totales,
            "promedio_goles": promedio_goles,
            "empates": empates
        })

    return stats_pronosticos


# ============================================================
# INSIGNIAS GLOBALES
# Revisa ranking, pronosticos y foro para determinar que badges
# gana cada usuario. No modifica datos en Supabase.
# ============================================================
def calcular_badges_globales_ranking(df_rank, df_pro, df_foro=None, res_visibles=None):
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
    # ACTIVACIÓN DE INSIGNIAS
    # Las badges empiezan a mostrarse recién desde el 5º partido
    # con resultado visible cargado.
    # ------------------------------------------------------------

    partidos_con_resultado = 0

    if (
        res_visibles is not None
        and not res_visibles.empty
        and "R1" in res_visibles.columns
        and "R2" in res_visibles.columns
    ):
        partidos_con_resultado = len(
            res_visibles[
                res_visibles["R1"].notna()
                & res_visibles["R2"].notna()
            ]
        )

    if partidos_con_resultado < 5:
        return badge_por_usuario        

    # ------------------------------------------------------------
    # 1. PUNTERO — mayor puntaje
    # ------------------------------------------------------------

    top_row = df_rank.iloc[0]

    if safe_int(top_row.get("PUNTOS", 0)) > 0:
        add_badge(
            top_row.get("USUARIO", ""),
            "Puntero"
        )

    # ------------------------------------------------------------
    # 2. SR. PRODE — más exactos
    # ------------------------------------------------------------

    if "EXACTOS" in df_rank.columns:
        max_exactos = safe_int(df_rank["EXACTOS"].max())

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
        max_generales = safe_int(df_rank["GENERALES"].max())

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

    stats_pronosticos = calcular_stats_pronosticos_badges(
        df_rank,
        df_pro
    )

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
    # ------------------------------------------------------------
    # 8. EL MACAYA — más comentarios en el foro
    # ------------------------------------------------------------

    if (
        df_foro is not None
        and not df_foro.empty
        and "USUARIO" in df_foro.columns
    ):
        foro_counts = (
            df_foro["USUARIO"]
            .astype(str)
            .value_counts()
            .to_dict()
        )

        usuarios_foro_stats = []

        for _, row in df_rank.iterrows():
            usuario = str(row.get("USUARIO", ""))
            comentarios = safe_int(foro_counts.get(usuario, 0))

            usuarios_foro_stats.append({
                "usuario": usuario,
                "comentarios": comentarios
            })

        if usuarios_foro_stats:
            macaya = max(
                usuarios_foro_stats,
                key=lambda x: x["comentarios"]
            )

            if macaya["comentarios"] > 0:
                add_badge(
                    macaya["usuario"],
                    "El Macaya"
                )

            # ------------------------------------------------------------
            # 9. EL MISTERIOSO — menos comentarios en el foro
            # ------------------------------------------------------------

            misterioso = min(
                usuarios_foro_stats,
                key=lambda x: x["comentarios"]
            )

            add_badge(
                misterioso["usuario"],
                "El Misterioso"
            )
    return badge_por_usuario


def procesar_badges_ranking(row, badge_por_usuario):
    """
    Devuelve las insignias del usuario para el ranking.
    """

    usuario = str(row.get("USUARIO", ""))

    return badge_por_usuario.get(usuario, [])


# ============================================================
# RANKING GENERAL
# Cruza usuarios + pronosticos + resultados visibles y devuelve
# la tabla que consumen Inicio, Plantel y Mi Prode.
# ============================================================
@st.cache_data(ttl=60)
def obtener_ranking_global(df_users, df_pro, df_res, df_foro=None):
    ranking_data = []

    if df_users is None or df_users.empty:
        return crear_ranking_vacio()

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
            id_p = safe_int(part["N_PARTIDO"])

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
        return crear_ranking_vacio()

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
        df_pro,
        df_foro,
        res_visibles
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
