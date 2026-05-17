import streamlit as st
import pandas as pd
from html import escape

from styles_config import AVATAR_GENERICO
from ranking_logic import calcular_detalle
from tools import get_flag_img_cached


def render_jugadores(
    df_usuarios,
    df_ranking,
    df_pro,
    df_res,
    df_foro=None
):
    # ============================================================
    # ESTILOS — JUGADORES
    # ============================================================

    st.markdown("""
<style>

/* ============================================================
   1. TÍTULO GENERAL DE LA SECCIÓN
   ============================================================ */

.players-title {
    margin-bottom: 22px;
}

.players-title h1 {
    font-family: 'Montserrat', sans-serif;
    font-size: 34px;
    font-weight: 900;
    color: #07111F;
    margin: 0;
    letter-spacing: -0.04em;
}

.players-title p {
    margin: 6px 0 0 0;
    color: #64748b;
    font-size: 15px;
    font-weight: 600;
}


/* ============================================================
   2. PANELES BASE Y ENCABEZADOS
   Usados en ficha, muro de insignias y pronósticos.
   ============================================================ */

/* ============================================================
   2. PANELES BASE Y ENCABEZADOS
   Usados en ficha, muro de insignias y pronósticos.
   ============================================================ */

.players-panel,
.player-profile-panel,
.badges-wall-panel,
.player-preds-panel {
    background: rgba(255,255,255,0.94);
    border: 1px solid rgba(226,232,240,0.9);
    border-radius: 18px;
    padding: 16px;
    box-shadow: 0 12px 30px rgba(15,23,42,0.06);
}

.players-panel-header {
    display: flex;
    align-items: center;
    gap: 10px;
    padding: 4px 4px 14px 4px;
    margin-bottom: 12px;
    border-bottom: 1px solid rgba(226,232,240,0.75);
}

.players-panel-icon {
    width: 32px;
    height: 32px;
    border-radius: 10px;
    display: flex;
    align-items: center;
    justify-content: center;
    background: rgba(244,197,66,0.16);
    color: #0f172a;
    font-size: 16px;
    flex-shrink: 0;
}

.players-panel-title {
    font-family: 'Montserrat', sans-serif;
    font-size: 18px;
    font-weight: 900;
    color: #0f172a;
}

.players-panel-subtitle {
    color: #64748b;
    font-size: 12px;
    font-weight: 700;
    margin-top: 2px;
}
/* ============================================================
   3. LISTADO SELECTOR DE JUGADORES
   Estructura: botón pequeño + card visual del jugador.
   ============================================================ */

.player-select-row {
    margin-bottom: 8px;
}

.player-list-card {
    background: rgba(248,250,252,0.92);
    border: 1px solid rgba(226,232,240,0.9);
    border-radius: 14px;
    padding: 9px 10px;

    display: flex;
    align-items: center;
    gap: 10px;

    min-height: 54px;
    transition: all 0.16s ease;
}

.player-list-card.selected {
    border: 1px solid rgba(244,197,66,0.85);
    background:
        linear-gradient(
            90deg,
            rgba(244,197,66,0.20),
            rgba(248,250,252,0.96)
        );
    box-shadow:
        inset 0 1px 0 rgba(255,255,255,0.6),
        0 8px 18px rgba(244,197,66,0.10);
}

.player-list-avatar {
    width: 38px;
    height: 38px;
    border-radius: 50%;
    object-fit: cover;
    border: 2px solid rgba(244,197,66,0.75);
    flex-shrink: 0;
}

.player-list-main {
    flex: 1;
    min-width: 0;
}

.player-list-name {
    color: #0f172a;
    font-size: 13px;
    font-weight: 900;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
}

.player-list-team {
    color: #64748b;
    font-size: 11px;
    font-weight: 800;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
}

.player-list-points {
    background: rgba(7,17,31,0.96);
    color: #F4C542;
    border-radius: 999px;
    padding: 5px 8px;
    font-size: 11px;
    font-weight: 900;
    white-space: nowrap;
}


/* ============================================================
   4. BOTÓN SELECTOR DEL LISTADO
   Botón pequeño de acción: ver / activo.
   ============================================================ */

.player-select-btn button {
    border-radius: 12px !important;
    min-height: 42px !important;
    font-size: 15px !important;
    font-weight: 900 !important;

    border: 1px solid rgba(244,197,66,0.38) !important;
    background: rgba(255,255,255,0.88) !important;
    color: #07111F !important;

    box-shadow: 0 6px 14px rgba(15,23,42,0.05) !important;
}

.player-select-btn button:hover {
    background: rgba(244,197,66,0.14) !important;
    border-color: rgba(244,197,66,0.45) !important;
    color: #07111F !important;
}

.player-select-btn button:disabled {
    background: rgba(255,255,255,0.88) !important;
    color: #64748b !important;
    border: 1px solid rgba(226,232,240,0.95) !important;
    opacity: 1 !important;
    box-shadow: 0 6px 14px rgba(15,23,42,0.04) !important;
}

/* ============================================================
   4B. PANEL UNIFICADO — DETALLE DEL JUGADOR
   Contiene perfil + pronósticos dentro de un mismo recuadro.
   ============================================================ */

.player-detail-panel {
    background: rgba(255,255,255,0.94);
    border: 1px solid rgba(226,232,240,0.9);
    border-radius: 18px;
    padding: 16px;
    box-shadow: 0 12px 30px rgba(15,23,42,0.06);
}

.player-detail-block {
    background: rgba(248,250,252,0.72);
    border: 1px solid rgba(226,232,240,0.85);
    border-radius: 16px;
    padding: 14px;
    margin-bottom: 14px;
}

.player-detail-block:last-child {
    margin-bottom: 0;
}

.player-detail-section-title {
    display: flex;
    align-items: center;
    gap: 8px;

    font-family: 'Montserrat', sans-serif;
    font-size: 15px;
    font-weight: 900;
    color: #0f172a;

    margin-bottom: 10px;
}


/* ============================================================
   5. FICHA DEL JUGADOR SELECCIONADO
   Card principal de perfil.
   ============================================================ */

.player-hero {
    position: relative;
    overflow: hidden;

    background:
        linear-gradient(
            90deg,
            rgba(255,255,255,0.10),
            rgba(255,255,255,0.10)
        ),
        var(--player-hero-bg);

    background-size: cover;
    background-position: center;
    background-repeat: no-repeat;

    border: 1px solid rgba(226,232,240,0.85);
    border-radius: 16px;
    padding: 18px 16px 14px 16px;
}

.player-hero-top {
    display: flex;
    align-items: flex-start;
    justify-content: space-between;
    gap: 18px;
}

.player-hero-profile {
    flex: 1;
    min-width: 0;
    text-align: center;
}

.player-badges-side {
    width: 170px;
    flex-shrink: 0;
}

.player-badges-mini {
    display: grid;
    grid-template-columns: repeat(3, minmax(0, 1fr));
    gap: 8px;
    justify-items: center;
}

.player-badge-mini {
    width: 48px;
    height: 48px;

    display: flex;
    align-items: center;
    justify-content: center;

    border-radius: 12px;
    background: rgba(255,255,255,0.66);
    border: 1px solid rgba(226,232,240,0.90);

    box-shadow:
        inset 0 1px 0 rgba(255,255,255,0.72),
        0 6px 14px rgba(15,23,42,0.05);
}

.player-badge-mini.earned {
    box-shadow:
        inset 0 1px 0 rgba(255,255,255,0.82),
        0 8px 18px rgba(15,23,42,0.08);
}

.player-badge-mini.locked {
    opacity: 0.92;
}

.player-badge-mini-img {
    width: 42px;
    height: 42px;
    object-fit: contain;
    display: block;
}

.player-badge-mini-fallback {
    width: 42px;
    height: 42px;
    border-radius: 10px;

    display: flex;
    align-items: center;
    justify-content: center;

    font-size: 22px;
    background: rgba(241,245,249,0.95);
    color: #64748b;
}


.player-avatar {
    width: 118px;
    height: 118px;
    object-fit: cover;
    border-radius: 50%;
    border: 5px solid #F4C542;
    box-shadow:
        0 14px 34px rgba(15,23,42,0.18),
        0 0 26px rgba(244,197,66,0.30);
}

.player-name {
    font-family: 'Montserrat', sans-serif;
    font-size: 24px;
    font-weight: 900;
    color: #0f172a;
    margin-top: 13px;
    line-height: 1.05;
}

.player-team {
    color: #64748b;
    font-size: 13px;
    font-weight: 900;
    margin-top: 4px;
}

.player-rank-pill {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    gap: 6px;

    margin-top: 12px;
    padding: 7px 12px;

    background: rgba(7,17,31,0.96);
    border: 1px solid rgba(244,197,66,0.24);
    border-radius: 999px;

    color: #F8FAFC;
    font-size: 12px;
    font-weight: 900;
}

.player-rank-pill strong {
    color: #F4C542;
}


/* ============================================================
   6. ESTADÍSTICAS DEL JUGADOR
   Puntos, exactos y generales.
   ============================================================ */

.player-stats {
    display: grid;
    grid-template-columns: repeat(3, minmax(0, 1fr));
    gap: 8px;
    margin: 14px 0;
}

.player-stat {
    border: 1px solid rgba(226,232,240,0.9);
    border-radius: 14px;
    padding: 10px 6px;
    background: rgba(248,250,252,0.78);
    text-align: center;
    min-width: 0;
}

.player-stat-icon {
    font-size: 17px;
    line-height: 1;
    margin-bottom: 4px;
}

.player-stat-number {
    font-family: 'Montserrat', sans-serif;
    font-size: 17px;
    font-weight: 900;
    color: #0f172a;
    line-height: 1;
}

.player-stat-label {
    margin-top: 4px;
    font-size: 9px;
    color: #64748b;
    font-weight: 900;
    text-transform: uppercase;
}


/* ============================================================
   7. BIO DEL JUGADOR
   Texto breve dentro de la ficha.
   ============================================================ */

.player-bio {
    margin-top: 12px;
    padding: 12px;
    border-radius: 14px;
    background: rgba(248,250,252,0.82);
    border: 1px solid rgba(226,232,240,0.85);
    color: #334155;
    font-size: 13px;
    font-weight: 700;
    line-height: 1.35;
}


/* ============================================================
   8. MURO DE INSIGNIAS / LOGROS
   Grid HTML responsive + estilo medallero premium.
   ============================================================ */

.badges-desktop {
    display: block;
    margin-top: 18px;
}

.badges-mobile {
    display: none;
}

/* Panel general del muro */
.badges-wall-panel {
    background:
        radial-gradient(
            circle at 100% 0%,
            rgba(244,197,66,0.10),
            rgba(255,255,255,0.96) 36%
        ),
        rgba(255,255,255,0.96);

    border: 1px solid rgba(226,232,240,0.9);
    border-radius: 18px;
    padding: 16px;

    box-shadow: 0 12px 30px rgba(15,23,42,0.06);
}

/* Grid real de insignias */
.badges-grid {
    display: grid !important;
    grid-template-columns: repeat(3, minmax(0, 1fr)) !important;
    gap: 10px;
}

/* Card de cada insignia */
.badge-card {
    min-width: 0;
    min-height: 124px;

    background:
        linear-gradient(
            180deg,
            rgba(255,255,255,0.98),
            rgba(248,250,252,0.94)
        );

    border: 1px solid rgba(226,232,240,0.95);
    border-radius: 16px;

    padding: 11px 7px;
    text-align: center;

    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;

    box-shadow:
        0 8px 18px rgba(15,23,42,0.04),
        inset 0 1px 0 rgba(255,255,255,0.65);

    transition:
        transform 0.16s ease,
        box-shadow 0.16s ease,
        border-color 0.16s ease;
}

.badge-card:hover {
    transform: translateY(-1px);
    border-color: rgba(244,197,66,0.62);

    box-shadow:
        0 10px 22px rgba(244,197,66,0.12),
        inset 0 1px 0 rgba(255,255,255,0.75);
}

/* =====================================================
   BADGES - MEDALLAS CON IMAGEN
   ===================================================== */

.badge-medal-wrap {
    width: 100%;
    display: flex;
    justify-content: center;
    align-items: center;
    margin-bottom: 6px;
}

.badge-medal-img {
    width: 118px;
    height: 118px;
    object-fit: contain;
    display: block;
    filter: drop-shadow(0 10px 14px rgba(0, 0, 0, 0.20));
    transition: transform 0.18s ease, filter 0.18s ease;
}

.badge-card:hover .badge-medal-img {
    transform: translateY(-2px) scale(1.035);
    filter: drop-shadow(0 14px 18px rgba(0, 0, 0, 0.26));
}

.badge-icon-fallback {
    width: 118px;
    height: 118px;
    margin: 0 auto 6px auto;
    border-radius: 999px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 58px;
    background: radial-gradient(circle at 30% 20%, #ffffff 0%, #eef3fb 38%, #dce5f3 100%);
    box-shadow: 0 10px 18px rgba(8, 25, 52, 0.16);
}


.badge-title {
    color: #07111F;
    font-family: 'Montserrat', sans-serif;
    font-size: 10px;
    font-weight: 900;
    line-height: 1.1;
    text-transform: uppercase;
    letter-spacing: 0.02em;

    margin-bottom: 5px;

    max-width: 100%;
    overflow: hidden;
    text-overflow: ellipsis;
}

.badge-winner {
    color: #0f172a;
    font-size: 11px;
    font-weight: 900;
    line-height: 1.1;

    max-width: 100%;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
}

.badge-detail {
    display: inline-block;

    margin-top: 7px;
    padding: 4px 8px;

    border-radius: 999px;

    background:
        linear-gradient(
            135deg,
            rgba(7,17,31,0.98),
            rgba(15,23,42,0.96)
        );

    border: 1px solid rgba(244,197,66,0.18);

    color: #F4C542;

    font-size: 8px;
    font-weight: 900;
    line-height: 1.1;

    max-width: 100%;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
}

/* Mobile: 2 columnas reales */
@media (max-width: 768px) {
    .badges-desktop {
        display: none;
    }

    .badges-mobile {
        display: block;
        margin-top: 18px;
    }

    .badges-wall-panel {
        padding: 13px;
        border-radius: 16px;
    }

    .badges-grid {
        display: grid !important;
        grid-template-columns: repeat(2, minmax(0, 1fr)) !important;
        gap: 8px;
    }

    .badge-card {
        min-height: 116px;
        padding: 9px 6px;
        border-radius: 14px;
    }

    .badge-medal-img {
        width: 92px;
        height: 92px;
    }

    .badge-icon-fallback {
        width: 92px;
        height: 92px;
        font-size: 44px;
    }

    .badge-title {
        font-size: 0.78rem;
        line-height: 1.05;
    }

    .badge-winner {
        font-size: 0.76rem;
    }

    .badge-detail {
        font-size: 0.72rem;
        padding: 5px 8px;
    }
}

/* ============================================================
   9. PRONÓSTICOS DEL JUGADOR
   Listado compacto de partidos pronosticados.
   ============================================================ */

.player-preds-scroll {
    max-height: 360px;
    overflow-y: auto;
    padding-right: 4px;
}

.player-pred-row {
    display: grid;
    grid-template-columns: 32px 1fr 58px 1fr;
    align-items: center;
    gap: 6px;

    padding: 7px 6px;
    border-bottom: 1px solid rgba(226,232,240,0.75);
    font-size: 11px;
}

.player-pred-num {
    color: #94a3b8;
    font-weight: 900;
}

.player-pred-team-left {
    text-align: right;
    color: #334155;
    font-weight: 800;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
}

.player-pred-team-right {
    text-align: left;
    color: #334155;
    font-weight: 800;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
}

.player-pred-score {
    text-align: center;
    background: rgba(7,17,31,0.96);
    color: #F4C542;
    border-radius: 8px;
    padding: 4px 6px;
    font-weight: 900;
}


/* ============================================================
   10. MOBILE
   Ajustes compactos para celulares.
   ============================================================ */

@media (max-width: 768px) {
    .players-title h1 {
        font-size: 28px;
    }

    .players-title p {
        font-size: 12px;
    }

    .players-panel,
    .player-profile-panel,
    .badges-wall-panel,
    .player-preds-panel {
        padding: 13px;
        border-radius: 16px;
    }

    .players-panel-title {
        font-size: 16px;
    }

    .players-panel-subtitle {
        font-size: 11px;
    }

    .player-list-card {
        padding: 8px;
        min-height: 50px;
    }

    .player-list-avatar {
        width: 34px;
        height: 34px;
    }

    .player-list-name {
        font-size: 12px;
    }

    .player-list-team {
        font-size: 10px;
    }

    .player-list-points {
        font-size: 10px;
        padding: 4px 7px;
    }

    .player-select-btn button {
        min-height: 38px !important;
        font-size: 13px !important;
    }

    .player-avatar {
        width: 104px;
        height: 104px;
    }

    .player-name {
        font-size: 21px;
    }
    
    .player-pred-row {
        grid-template-columns: 28px 1fr 52px 1fr;
        font-size: 10px;
    }
        .player-hero-top {
        flex-direction: column;
        align-items: center;
        gap: 14px;
    }

    .player-hero-profile {
        width: 100%;
    }

    .player-badges-side {
        width: 100%;
        max-width: 210px;
    }

    .player-badges-mini {
        gap: 6px;
    }

    .player-badge-mini {
        width: 44px;
        height: 44px;
        border-radius: 10px;
    }

    .player-badge-mini-img {
        width: 38px;
        height: 38px;
    }
}

</style>
""", unsafe_allow_html=True)
    # ============================================================
    # HELPERS
    # ============================================================

    def safe_int(value, default=0):
        try:
            return int(value)
        except Exception:
            return default

    def flag_html(flag_value):
        """
        Devuelve una bandera como HTML si viene como imagen/base64,
        o como texto/emoji si viene en otro formato.
        """
        flag_value = str(flag_value)

        if flag_value.startswith("http") or flag_value.startswith("data:image"):
            return f'<img src="{flag_value}" width="18" style="vertical-align:middle;">'

        return escape(flag_value)

    def get_avatar(row):
        avatar = row.get("AVATAR_URL", "")
        if pd.notna(avatar) and str(avatar).strip() != "":
            return avatar
        return AVATAR_GENERICO
        
    def get_ranking_row(user_row):
        usuario = str(user_row.get("USUARIO", ""))
        nombre = str(user_row.get("NOMBRE", ""))

        if "USUARIO" in df_ranking.columns:
            match = df_ranking[df_ranking["USUARIO"] == usuario]
            if not match.empty:
                return match.iloc[0], match.index[0]

        if "JUGADOR" in df_ranking.columns:
            match = df_ranking[
                df_ranking["JUGADOR"]
                .astype(str)
                .str.contains(nombre, na=False, regex=False)
            ]
            if not match.empty:
                return match.iloc[0], match.index[0]

        return None, None

    def get_nombre_desde_ranking(rank_row):
        if rank_row is None:
            return "-"

        if "JUGADOR" in rank_row:
            return str(rank_row.get("JUGADOR", "-"))

        if "USUARIO" in rank_row:
            usuario = str(rank_row.get("USUARIO", ""))
            match = df_usuarios[df_usuarios["USUARIO"] == usuario]
            if not match.empty:
                return str(match.iloc[0].get("NOMBRE", usuario))

        return "-"

    def calcular_racha_exactos(user_row):
        r_act = 0
        r_max = 0

        u_pro_sorted = (
            df_pro[df_pro["USUARIO"] == user_row["USUARIO"]]
            .sort_values("N_PARTIDO")
        )

        for _, p in u_pro_sorted.iterrows():
            p_ref = df_res[df_res["N_PARTIDO"] == p["N_PARTIDO"]]

            if not p_ref.empty and pd.notna(p_ref.iloc[0].get("R1")):
                pts, exa, gen = calcular_detalle(
                    p_ref.iloc[0]["R1"],
                    p_ref.iloc[0]["R2"],
                    p["P1"],
                    p["P2"]
                )

                if exa == 1:
                    r_act += 1
                    r_max = max(r_max, r_act)
                else:
                    r_act = 0

        return r_max

    def calcular_logros_globales():
        logros = []

        if df_ranking.empty:
            return logros

        # ------------------------------------------------------------
        # Helpers internos
        # ------------------------------------------------------------

        def nombre_usuario_por_usuario(usuario):
            match = df_usuarios[df_usuarios["USUARIO"].astype(str) == str(usuario)]
            if not match.empty:
                return str(match.iloc[0].get("NOMBRE", usuario))
            return str(usuario)

        def nombre_desde_rank(row):
            if row is None:
                return "-"

            if "JUGADOR" in row:
                return str(row.get("JUGADOR", "-"))

            if "USUARIO" in row:
                return nombre_usuario_por_usuario(row.get("USUARIO", "-"))

            return "-"

        # ------------------------------------------------------------
        # 1. PUNTERO — mayor puntaje
        # ------------------------------------------------------------

        top_row = df_ranking.iloc[0]

        logros.append({
            "icon": "🏆",
            "title": "Puntero",
            "winner": nombre_desde_rank(top_row),
            "detail": f'{safe_int(top_row.get("PUNTOS", 0))} pts'
        })

        # ------------------------------------------------------------
        # 2. SR. PRODE — más exactos
        # ------------------------------------------------------------

        if "EXACTOS" in df_ranking.columns:
            exactos_num = pd.to_numeric(
                df_ranking["EXACTOS"],
                errors="coerce"
            ).fillna(0)

            idx_exactos = exactos_num.idxmax()
            row_exactos = df_ranking.loc[idx_exactos]

            logros.append({
                "icon": "🎯",
                "title": "Sr. Prode",
                "winner": nombre_desde_rank(row_exactos),
                "detail": f'{safe_int(row_exactos.get("EXACTOS", 0))} exactos'
            })
        else:
            logros.append({
                "icon": "🎯",
                "title": "Sr. Prode",
                "winner": "-",
                "detail": "Sin datos"
            })

        # ------------------------------------------------------------
        # 3. SIEMPRE SUMA — más generales
        # ------------------------------------------------------------

        if "GENERALES" in df_ranking.columns:
            generales_num = pd.to_numeric(
                df_ranking["GENERALES"],
                errors="coerce"
            ).fillna(0)

            idx_generales = generales_num.idxmax()
            row_generales = df_ranking.loc[idx_generales]

            logros.append({
                "icon": "✅",
                "title": "Siempre Suma",
                "winner": nombre_desde_rank(row_generales),
                "detail": f'{safe_int(row_generales.get("GENERALES", 0))} generales'
            })
        else:
            logros.append({
                "icon": "✅",
                "title": "Siempre Suma",
                "winner": "-",
                "detail": "Sin datos"
            })

        # ------------------------------------------------------------
        # DATOS DE PRONÓSTICOS POR USUARIO
        # ------------------------------------------------------------

        stats_pronosticos = []

        for _, u in df_usuarios.iterrows():
            usuario = str(u.get("USUARIO", ""))
            nombre = str(u.get("NOMBRE", usuario))

            pro_user = df_pro[df_pro["USUARIO"].astype(str) == usuario]

            if pro_user.empty:
                continue

            p1 = pd.to_numeric(pro_user["P1"], errors="coerce").fillna(0)
            p2 = pd.to_numeric(pro_user["P2"], errors="coerce").fillna(0)

            total_partidos = len(pro_user)
            goles_totales = int((p1 + p2).sum())
            promedio_goles = goles_totales / total_partidos if total_partidos > 0 else 0
            empates = int((p1 == p2).sum())

            stats_pronosticos.append({
                "usuario": usuario,
                "nombre": nombre,
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

            logros.append({
                "icon": "⚽",
                "title": "Optimista del Gol",
                "winner": optimista["nombre"],
                "detail": f'{round(optimista["promedio_goles"], 1)} goles/prom.'
            })
        else:
            logros.append({
                "icon": "⚽",
                "title": "Optimista del Gol",
                "winner": "-",
                "detail": "Sin datos"
            })

        # ------------------------------------------------------------
        # 5. EL CHOLO — menor promedio de goles
        # ------------------------------------------------------------

        if stats_pronosticos:
            cholo = min(
                stats_pronosticos,
                key=lambda x: x["promedio_goles"]
            )

            logros.append({
                "icon": "🧱",
                "title": "El Cholo",
                "winner": cholo["nombre"],
                "detail": f'{round(cholo["promedio_goles"], 1)} goles/prom.'
            })
        else:
            logros.append({
                "icon": "🧱",
                "title": "El Cholo",
                "winner": "-",
                "detail": "Sin datos"
            })

        # ------------------------------------------------------------
        # 6. REY DEL EMPATE — más empates pronosticados
        # ------------------------------------------------------------

        if stats_pronosticos:
            rey_empate = max(
                stats_pronosticos,
                key=lambda x: x["empates"]
            )

            logros.append({
                "icon": "🤝",
                "title": "Rey del Empate",
                "winner": rey_empate["nombre"],
                "detail": f'{rey_empate["empates"]} empates'
            })
        else:
            logros.append({
                "icon": "🤝",
                "title": "Rey del Empate",
                "winner": "-",
                "detail": "Sin datos"
            })

        # ------------------------------------------------------------
        # DATOS DEL FORO
        # ------------------------------------------------------------

        foro_counts = {}

        if df_foro is not None and not df_foro.empty and "USUARIO" in df_foro.columns:
            foro_counts = (
                df_foro["USUARIO"]
                .astype(str)
                .value_counts()
                .to_dict()
            )

        usuarios_foro = []

        for _, u in df_usuarios.iterrows():
            usuario = str(u.get("USUARIO", ""))
            nombre = str(u.get("NOMBRE", usuario))
            cantidad = int(foro_counts.get(usuario, 0))

            usuarios_foro.append({
                "usuario": usuario,
                "nombre": nombre,
                "comentarios": cantidad
            })

        # ------------------------------------------------------------
        # 7. EL MACAYA — más comentarios en el foro
        # ------------------------------------------------------------

        if usuarios_foro and foro_counts:
            macaya = max(
                usuarios_foro,
                key=lambda x: x["comentarios"]
            )

            logros.append({
                "icon": "🎙️",
                "title": "El Macaya",
                "winner": macaya["nombre"],
                "detail": f'{macaya["comentarios"]} comentarios'
            })
        else:
            logros.append({
                "icon": "🎙️",
                "title": "El Macaya",
                "winner": "-",
                "detail": "Sin foro"
            })

        # ------------------------------------------------------------
        # 8. EL MISTERIOSO — menos comentarios en el foro
        # ------------------------------------------------------------

        if usuarios_foro and foro_counts:
            misterioso = min(
                usuarios_foro,
                key=lambda x: x["comentarios"]
            )

            detalle_misterioso = (
                "Sin comentarios"
                if misterioso["comentarios"] == 0
                else f'{misterioso["comentarios"]} comentarios'
            )

            logros.append({
                "icon": "🕵️",
                "title": "El Misterioso",
                "winner": misterioso["nombre"],
                "detail": detalle_misterioso
            })
        else:
            logros.append({
                "icon": "🕵️",
                "title": "El Misterioso",
                "winner": "-",
                "detail": "Sin foro"
            })

        # ------------------------------------------------------------
        # 9. EL DISTINTO — más alejado de la media del grupo
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
                    "nombre": jugador["nombre"],
                    "promedio_goles": jugador["promedio_goles"],
                    "promedio_otros": promedio_otros,
                    "diferencia": diferencia
                })

            if distintos:
                distinto = max(
                    distintos,
                    key=lambda x: x["diferencia"]
                )

                logros.append({
                    "icon": "🧬",
                    "title": "El Distinto",
                    "winner": distinto["nombre"],
                    "detail": f'±{round(distinto["diferencia"], 1)} goles/prom.'
                })
            else:
                logros.append({
                    "icon": "🧬",
                    "title": "El Distinto",
                    "winner": "-",
                    "detail": "Sin datos"
                })

        else:
            logros.append({
                "icon": "🧬",
                "title": "El Distinto",
                "winner": "-",
                "detail": "Sin datos"
            })

        return logros

    # ============================================================
    # TÍTULO
    # ============================================================

    st.markdown("""
<div class="players-title">
<h1>👥 Jugadores</h1>
<p>Plantel, logros y pronósticos de la banda del Prode.</p>
</div>
""", unsafe_allow_html=True)

    nombres_usuarios = df_usuarios["NOMBRE"].fillna("Jugador").tolist()

    if "jugador_seleccionado" not in st.session_state:
        st.session_state.jugador_seleccionado = (
            nombres_usuarios[0] if nombres_usuarios else None
        )

    # ============================================================
    # HTML REUTILIZABLE — MURO DE INSIGNIAS
    # Se renderiza en desktop dentro de la columna izquierda
    # y en mobile después de ficha + pronósticos.
    # ============================================================

    logros = calcular_logros_globales()

    # =====================================================
    # ASSETS DE INSIGNIAS
    # =====================================================

    BADGE_ASSET_BASE_URL = "https://storage.googleapis.com/foto-prode2026/badges"
    PLAYER_HERO_BG_URL = "https://storage.googleapis.com/foto-prode2026/Banners/CAUDRADO1.png"
    
    badge_asset_map = {
        "Puntero": {
            "large": f"{BADGE_ASSET_BASE_URL}/puntero/PUNTERO_LARGE_512.png",
            "mini": f"{BADGE_ASSET_BASE_URL}/puntero/PUNTERO_MINI_128.png",
            "gray": f"{BADGE_ASSET_BASE_URL}/puntero/PUNTERO_GRAY_128.png",
        },
        "Sr. Prode": {
            "large": f"{BADGE_ASSET_BASE_URL}/srprode/SRPRODE_LARGE_512.png",
            "mini": f"{BADGE_ASSET_BASE_URL}/srprode/SRPRODE_MINI_128.png",
            "gray": f"{BADGE_ASSET_BASE_URL}/srprode/SRPRODE_GRAY_128.png",
        },
        "Siempre Suma": {
            "large": f"{BADGE_ASSET_BASE_URL}/suma/SUMA_LARGE_512.png",
            "mini": f"{BADGE_ASSET_BASE_URL}/suma/SUMA_MINI_128.png",
            "gray": f"{BADGE_ASSET_BASE_URL}/suma/SUMA_GRAY_128.png",
        },
        "Optimista del Gol": {
            "large": f"{BADGE_ASSET_BASE_URL}/optimista/OPTIMISTA_LARGE_512.png",
            "mini": f"{BADGE_ASSET_BASE_URL}/optimista/OPTIMISTA_MINI_128.png",
            "gray": f"{BADGE_ASSET_BASE_URL}/optimista/OPTIMISTA_GRAY_128.png",
        },
        "El Cholo": {
            "large": f"{BADGE_ASSET_BASE_URL}/elcholo/ELCHOLO_LARGE_512.png",
            "mini": f"{BADGE_ASSET_BASE_URL}/elcholo/ELCHOLO_MINI_128.png",
            "gray": f"{BADGE_ASSET_BASE_URL}/elcholo/ELCHOLO_GRAY_128.png",
        },
        "Rey del Empate": {
            "large": f"{BADGE_ASSET_BASE_URL}/empate/EMPATE_LARGE_512.png",
            "mini": f"{BADGE_ASSET_BASE_URL}/empate/EMPATE_MINI_128.png",
            "gray": f"{BADGE_ASSET_BASE_URL}/empate/EMPATE_GRAY_128.png",
        },
        "El Macaya": {
            "large": f"{BADGE_ASSET_BASE_URL}/macaya/MACAYA_LARGE_512.png",
            "mini": f"{BADGE_ASSET_BASE_URL}/macaya/MACAYA_MINI_128.png",
            "gray": f"{BADGE_ASSET_BASE_URL}/macaya/MACAYA_GRAY_128.png",
        },
        "El Misterioso": {
            "large": f"{BADGE_ASSET_BASE_URL}/misterioso/MISTERIOSO_LARGE_512.png",
            "mini": f"{BADGE_ASSET_BASE_URL}/misterioso/MISTERIOSO_MINI_128.png",
            "gray": f"{BADGE_ASSET_BASE_URL}/misterioso/MISTERIOSO_GRAY_128.png",
        },
        "El Distinto": {
            "large": f"{BADGE_ASSET_BASE_URL}/distinto/DISTINTO_LARGE_512.png",
            "mini": f"{BADGE_ASSET_BASE_URL}/distinto/DISTINTO_MINI_128.png",
            "gray": f"{BADGE_ASSET_BASE_URL}/distinto/DISTINTO_GRAY_128.png",
        },
    }

    badge_class_map = {
        "Puntero": "puntero",
        "Sr. Prode": "prode",
        "Siempre Suma": "suma",
        "Optimista del Gol": "gol",
        "El Cholo": "cholo",
        "Rey del Empate": "empate",
        "El Macaya": "macaya",
        "El Misterioso": "misterioso",
        "El Distinto": "distinto",
    }

    def normalizar_texto(valor):
        return str(valor).strip().lower()

    def build_player_badges_mini_html(user_row, logros, badge_asset_map):
        jugador_nombre = normalizar_texto(user_row.get("NOMBRE", ""))

        badge_order = [
            "Puntero",
            "Sr. Prode",
            "Siempre Suma",
            "Optimista del Gol",
            "El Cholo",
            "Rey del Empate",
            "El Macaya",
            "El Misterioso",
            "El Distinto",
        ]

        earned_titles = {
            str(logro.get("title", "")).strip()
            for logro in logros
            if normalizar_texto(logro.get("winner", "")) == jugador_nombre
        }

        items = []

        for title in badge_order:
            assets = badge_asset_map.get(title, {})
            is_earned = title in earned_titles

            if is_earned:
                badge_url = assets.get("mini", "")
            else:
                badge_url = assets.get("gray", "") or assets.get("mini", "")

            state_class = "earned" if is_earned else "locked"

            if badge_url:
                visual_html = f'<img src="{escape(badge_url)}" class="player-badge-mini-img" alt="{escape(title)}" loading="lazy">'
            else:
                visual_html = '<div class="player-badge-mini-fallback">🏅</div>'

            items.append(
                f'<div class="player-badge-mini {state_class}" title="{escape(title)}">{visual_html}</div>'
            )

        return "".join(items)

    badges_html = ""

    for logro in logros:
        badge_title = str(logro.get("title", ""))
        badge_type = badge_class_map.get(badge_title, "default")

        badge_img = badge_asset_map.get(
            badge_title,
            {}
        ).get(
            "large",
            ""
        )

        badge_icon_fallback = str(logro.get("icon", "🏅"))

        if badge_img:
            badge_visual_html = f"""
<div class="badge-medal-wrap">
<img 
class="badge-medal-img" 
src="{escape(badge_img)}" 
alt="{escape(badge_title)}"
loading="lazy"
>
</div>
            """
        else:
            badge_visual_html = f"""
<div class="badge-icon-fallback">{escape(badge_icon_fallback)}</div>
            """

        badges_html += f"""
<div class="badge-card badge-{badge_type}">
{badge_visual_html}
<div class="badge-title">{escape(badge_title)}</div>
<div class="badge-winner">👤 {escape(str(logro.get("winner", "-")))}</div>
<div class="badge-detail">{escape(str(logro.get("detail", "")))}</div>
</div>
        """

    badges_panel_html = f"""
<div class="badges-wall-panel">
<div class="players-panel-header">
<div class="players-panel-icon">🏅</div>
<div>
<div class="players-panel-title">Muro de Insignias</div>
<div class="players-panel-subtitle">Logros destacados del Prode</div>
</div>
</div>

<div class="badges-grid">
{badges_html}
</div>
</div>
    """

    # ============================================================
    # ESTRUCTURA PRINCIPAL
    # ============================================================

    c_lista, c_detalle = st.columns([1.05, 1.15], gap="large")

    # ============================================================
    # COLUMNA IZQUIERDA — LISTA DE JUGADORES + MURO DESKTOP
    # ============================================================

    with c_lista:
        with st.container(border=True):

            st.markdown("""
<div class="players-panel-header">
<div class="players-panel-icon">👥</div>
<div>
<div class="players-panel-title">Jugadores</div>
<div class="players-panel-subtitle">Seleccioná a quién querés espiar</div>
</div>
</div>
""", unsafe_allow_html=True)

            with st.container(height=430):
                for _, u in df_usuarios.iterrows():
                    foto_mini = get_avatar(u)

                    rank_row, idx_rank = get_ranking_row(u)
                    pts = (
                        safe_int(rank_row.get("PUNTOS", 0))
                        if rank_row is not None
                        else 0
                    )

                    nombre_raw = str(u.get("NOMBRE", "Jugador"))
                    usuario_raw = str(u.get("USUARIO", nombre_raw))
                    nombre = escape(nombre_raw)
                    equipo = escape(str(u.get("EQUIPO FAVORITO", "-")))

                    es_seleccionado = (
                        st.session_state.jugador_seleccionado == nombre_raw
                    )

                    selected_class = "selected" if es_seleccionado else ""

                    c_btn, c_card = st.columns([0.16, 0.84], gap="small")

                    with c_btn:
                        st.markdown(
                            '<div class="player-select-btn">',
                            unsafe_allow_html=True
                        )

                        if es_seleccionado:
                            st.button(
                                "🔍",
                                key=f"jugador_activo_{usuario_raw}",
                                use_container_width=True,
                                disabled=True
                            )
                        else:
                            if st.button(
                                "🔍",
                                key=f"ver_jugador_{usuario_raw}",
                                use_container_width=True
                            ):
                                st.session_state.jugador_seleccionado = nombre_raw
                                st.rerun()

                        st.markdown("</div>", unsafe_allow_html=True)

                    with c_card:
                        st.markdown(
                            f"""
<div class="player-select-row">
<div class="player-list-card {selected_class}">
<img src="{foto_mini}" class="player-list-avatar">
<div class="player-list-main">
<div class="player-list-name">{nombre}</div>
<div class="player-list-team">⚽ {equipo}</div>
</div>
<div class="player-list-points">{pts} pts</div>
</div>
</div>
""",
                            unsafe_allow_html=True
                        )

            user_sel_query = df_usuarios[
                df_usuarios["NOMBRE"] == st.session_state.jugador_seleccionado
            ]

            user_sel = (
                user_sel_query.iloc[0]
                if not user_sel_query.empty
                else None
            )

        # Muro visible solo en desktop.
        # Va fuera del container de lista, pero dentro de la columna izquierda.
        st.markdown(
            f"""
<div class="badges-desktop">
{badges_panel_html}
</div>
""",
            unsafe_allow_html=True
        )

    with c_detalle:
        if user_sel is None:
            st.warning("Seleccioná un jugador para ver su perfil.")
            return

        datos_vivos, idx_real = get_ranking_row(user_sel)

        foto_perfil = get_avatar(user_sel)
        nombre = escape(str(user_sel.get("NOMBRE", "Jugador")))
        usuario = escape(str(user_sel.get("USUARIO", "")))
        equipo = escape(str(user_sel.get("EQUIPO FAVORITO", "-")))
        bio = escape(str(user_sel.get("DESCRIPCION", "")))
        player_badges_mini_html = build_player_badges_mini_html(
            user_sel,
            logros,
            badge_asset_map
        )
        if bio.strip() == "" or bio.strip().lower() == "nan":
            bio = "Sin bio cargada todavía."

        pts = (
            safe_int(datos_vivos.get("PUNTOS", 0))
            if datos_vivos is not None
            else 0
        )

        exactos = (
            safe_int(datos_vivos.get("EXACTOS", 0))
            if datos_vivos is not None
            else 0
        )

        generales = (
            safe_int(datos_vivos.get("GENERALES", 0))
            if datos_vivos is not None
            else 0
        )

        try:
            posicion = int(idx_real)
        except Exception:
            posicion = "-"
        # ------------------------------------------------------------
        # PRONÓSTICOS DEL JUGADOR
        # Se preparan antes del render unificado.
        # ------------------------------------------------------------

        pro_user_sel = df_pro[df_pro["USUARIO"] == user_sel["USUARIO"]]

        if pro_user_sel.empty:
            rows_html = """
<div class="player-bio">
Sin pronósticos cargados todavía.
</div>
"""
        else:
            rows = []

            for _, p in pro_user_sel.sort_values("N_PARTIDO").iterrows():
                p_match = df_res[df_res["N_PARTIDO"] == p["N_PARTIDO"]]

                if not p_match.empty:
                    p_inf = p_match.iloc[0]

                    f1 = get_flag_img_cached(p_inf["Equipo_1"])
                    f2 = get_flag_img_cached(p_inf["Equipo_2"])

                    i1 = flag_html(f1)
                    i2 = flag_html(f2)

                    rows.append(
                        f"""
<div class="player-pred-row">
<div class="player-pred-num">{int(p["N_PARTIDO"])}</div>
<div class="player-pred-team-left">{escape(str(p_inf["Equipo_1"]))} {i1}</div>
<div class="player-pred-score">{int(p["P1"])} - {int(p["P2"])}</div>
<div class="player-pred-team-right">{i2} {escape(str(p_inf["Equipo_2"]))}</div>
</div>
"""
                    )

            rows_html = "\n".join(rows)

        # ------------------------------------------------------------
        # PANEL UNIFICADO — PERFIL + PRONÓSTICOS
        # ------------------------------------------------------------

        st.markdown(
            f"""
<div class="player-detail-panel">

<div class="players-panel-header">
<div class="players-panel-icon">👤</div>
<div>
<div class="players-panel-title">Detalle del jugador</div>
<div class="players-panel-subtitle">Perfil y pronósticos del seleccionado</div>
</div>
</div>

<div class="player-detail-block">
<div class="player-detail-section-title">👤 Perfil</div>

<div class="player-hero" style="--player-hero-bg: url('{PLAYER_HERO_BG_URL}');">
<div class="player-hero-top">
<div class="player-hero-profile">
<img src="{foto_perfil}" class="player-avatar">
<div class="player-name">{nombre}</div>
<div class="player-team">@{usuario} · {equipo}</div>

<div class="player-rank-pill">
    <span>📊 Posición actual</span>
    <strong>{posicion}°</strong>
</div>
</div>

<div class="player-badges-side">
<div class="player-badges-mini">
{player_badges_mini_html}
</div>
</div>
</div>
</div>

<div class="player-stats">
<div class="player-stat">
<div class="player-stat-icon">🏆</div>
<div class="player-stat-number">{pts}</div>
<div class="player-stat-label">Puntos</div>
</div>

<div class="player-stat">
<div class="player-stat-icon">🎯</div>
<div class="player-stat-number">{exactos}</div>
<div class="player-stat-label">Exactos</div>
</div>

<div class="player-stat">
<div class="player-stat-icon">✅</div>
<div class="player-stat-number">{generales}</div>
<div class="player-stat-label">Generales</div>
</div>
</div>

<div class="player-bio">
<strong>Bio:</strong> {bio}
</div>
</div>

<div class="player-detail-block">
<div class="player-detail-section-title">🗳️ Pronósticos</div>

<div class="player-preds-scroll">
{rows_html}
</div>
</div>

</div>
""",
            unsafe_allow_html=True
        )
    # ============================================================
    # MURO MOBILE
    # Visible solo en mobile, después de perfil + pronósticos.
    # ============================================================

    st.markdown(
        f"""
<div class="badges-mobile">
{badges_panel_html}
</div>
""",
        unsafe_allow_html=True
    )
