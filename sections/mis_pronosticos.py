import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from html import escape
import re

from styles_config import (AVATAR_GENERICO, HEADER_BACKGROUND, SIDEBAR_BANNER)
from tools import upload_profile_picture, get_flag_img


def render_mis_pronosticos(
    df_res,
    df_usuarios,
    df_pro,
    df_ranking,
    mapa_banderas,
    conn
):
    # ============================================================
    # ESTILOS — MIS PRONÓSTICOS / MI PERFIL
    # ============================================================

    css_mis_pronosticos = """
<style>
.page-section-title {
    margin-bottom: 22px;
}

.page-section-title h1 {
    font-family: 'Montserrat', sans-serif;
    font-size: 34px;
    font-weight: 900;
    color: #07111F;
    margin: 0;
    letter-spacing: -0.04em;
}

.page-section-title p {
    margin: 6px 0 0 0;
    color: #64748b;
    font-size: 15px;
    font-weight: 600;
}

.pred-panel,
.profile-panel {
    background: rgba(255,255,255,0.94);
    border: 1px solid rgba(226,232,240,0.9);
    border-radius: 18px;
    padding: 16px;
    box-shadow: 0 12px 30px rgba(15,23,42,0.06);
}

.panel-header {
    display: flex;
    align-items: center;
    gap: 10px;
    padding: 4px 4px 14px 4px;
    margin-bottom: 12px;
    border-bottom: 1px solid rgba(226,232,240,0.75);
}

.panel-icon {
    width: 32px;
    height: 32px;
    border-radius: 10px;
    display: flex;
    align-items: center;
    justify-content: center;
    background: rgba(244,197,66,0.16);
    color: #0f172a;
    font-size: 16px;
}

.panel-title {
    font-family: 'Montserrat', sans-serif;
    font-size: 18px;
    font-weight: 900;
    color: #0f172a;
}

.pred-status {
    background: linear-gradient(90deg, rgba(244,197,66,0.18), rgba(255,255,255,0.95));
    border: 1px solid rgba(244,197,66,0.45);
    color: #92400e;
    border-radius: 14px;
    padding: 12px 14px;
    margin-bottom: 14px;
    font-size: 13px;
    font-weight: 800;
}

.pred-status.locked {
    background: rgba(248,250,252,0.95);
    border: 1px solid rgba(148,163,184,0.35);
    color: #64748b;
}

/* ============================================================
   PARTIDO CARD — ESTILO RESULTADOS OFICIALES
   ============================================================ */

.pred-match-card-v2 {
    background: rgba(248,250,252,0.96);
    border: 1px solid rgba(226,232,240,0.95);
    border-radius: 16px;

    padding: 13px 14px;
    margin-bottom: 11px;

    box-shadow: 0 8px 18px rgba(15,23,42,0.035);
}

.pred-match-meta {
    display: flex;
    justify-content: space-between;
    align-items: center;

    color: #94a3b8;
    font-size: 10px;
    font-weight: 900;
    text-transform: uppercase;
    letter-spacing: 0.06em;

    margin-bottom: 13px;
}

.pred-match-main-row {
    display: grid;
    grid-template-columns: minmax(0, 1fr) auto minmax(0, 1fr);
    align-items: center;
    gap: 12px;
}

.pred-team-inline {
    display: flex;
    align-items: center;
    gap: 8px;
    min-width: 0;
}

.pred-team-inline.left {
    justify-content: flex-end;
    text-align: right;
}

.pred-team-inline.right {
    justify-content: flex-start;
    text-align: left;
}

.pred-team-inline span {
    color: #07111F;
    font-size: 13px;
    font-weight: 900;
    line-height: 1.15;

    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
}

.pred-team-inline img,
.pred-flag {
    width: 30px;
    height: 21px;
    object-fit: cover;
    border-radius: 4px;
    flex-shrink: 0;

    box-shadow:
        0 3px 7px rgba(15,23,42,0.20),
        inset 0 1px 0 rgba(255,255,255,0.25);
}

.pred-score-pill {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    gap: 5px;

    min-width: 78px;
    height: 44px;

    background:
        linear-gradient(
            135deg,
            rgba(7,17,31,0.98),
            rgba(15,23,42,0.96)
        );

    border: 1px solid rgba(244,197,66,0.22);
    border-radius: 11px;

    box-shadow:
        0 8px 18px rgba(15,23,42,0.18),
        inset 0 1px 0 rgba(255,255,255,0.07);
}

.pred-score-pill span {
    font-family: 'Montserrat', sans-serif;
    font-size: 17px;
    font-weight: 900;
    color: #F8FAFC;
    line-height: 1;
}

.pred-score-pill .score-colon {
    color: #F4C542;
    opacity: 0.95;
}

.pred-match-gap {
    height: 2px;
}

/* ============================================================
   RESUMEN OSCURO — ESTADÍSTICAS DE PRONÓSTICOS
   ============================================================ */

.pred-summary-footer {
    background:
        linear-gradient(
            135deg,
            rgba(7,17,31,0.98),
            rgba(15,23,42,0.94)
        );
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 16px;

    padding: 14px 14px;
    margin: 12px 10px 4px 10px;

    box-shadow:
        inset 0 1px 0 rgba(255,255,255,0.05),
        0 10px 24px rgba(15,23,42,0.08);
}

.pred-summary-kicker {
    font-size: 10px;
    font-weight: 900;
    color: rgba(255,255,255,0.55);
    text-transform: uppercase;
    letter-spacing: 0.08em;
    margin-bottom: 9px;
}

.pred-summary-grid {
    display: grid;
    grid-template-columns: repeat(4, minmax(0, 1fr));
    gap: 8px;
}

.pred-summary-item {
    background: rgba(255,255,255,0.06);
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 12px;
    padding: 9px 6px;
    text-align: center;
    min-width: 0;
}

.pred-summary-icon {
    font-size: 16px;
    line-height: 1;
    margin-bottom: 4px;
}

.pred-summary-number {
    font-family: 'Montserrat', sans-serif;
    font-size: 17px;
    font-weight: 900;
    color: #F8FAFC;
    line-height: 1;
}

.pred-summary-label {
    margin-top: 4px;
    font-size: 9px;
    font-weight: 800;
    color: rgba(255,255,255,0.55);
    text-transform: uppercase;
}

.pred-summary-style {
    margin-top: 10px;
    color: rgba(255,255,255,0.72);
    font-size: 11px;
    font-weight: 800;
    text-align: center;
}

.pred-summary-style strong {
    color: #F4C542;
}

.pred-panel-header-v2 {
    padding: 12px 14px 14px 14px;
    margin-bottom: 14px;
    border-bottom: 1px solid rgba(226,232,240,0.75);

    background-image:
        linear-gradient(
            90deg,
            rgba(255,255,255,0.15) 60%,
            rgba(255,255,255,0.25) 80%,
            rgba(255,255,255,0.3) 100%
        ),
        url("__SIDEBAR_BANNER__");

    background-size: cover;
    background-position: center;
    border-radius: 14px;
}

.pred-panel-title-row {
    display: flex;
    align-items: center;
    gap: 10px;
}

.pred-panel-title-row .panel-title {
    color: #F8FAFC;
    margin: 0;
    line-height: 1;
}

.pred-panel-subtitle {
    display: block;
    margin-top: 4px;
    font-size: 12px;
    font-weight: 600;
}

.pred-panel-subtitle.open {
    color: #059669;
}

.pred-panel-subtitle.locked {
    color: #6B7280;
}

/* ============================================================
   MOBILE — VERSION COMPACTA
   ============================================================ */

@media (max-width: 768px) {

    .page-section-title h1 {
        font-size: 27px;
        line-height: 1.05;
    }

    .page-section-title p {
        font-size: 12px;
    }

    .pred-panel-header-v2 {
        padding: 11px 12px;
        border-radius: 14px;
        margin-bottom: 12px;
    }

    .panel-title {
        font-size: 17px;
    }

    .pred-panel-subtitle {
        font-size: 10px;
    }

    /* Card de partido */
    .pred-match-card-v2 {
        padding: 10px 9px !important;
        border-radius: 14px !important;
        margin-bottom: 9px !important;
    }

    .pred-match-meta {
        font-size: 8px !important;
        letter-spacing: 0.03em !important;
        margin-bottom: 9px !important;
    }

    .pred-match-main-row {
        grid-template-columns: minmax(0, 1fr) auto minmax(0, 1fr) !important;
        gap: 6px !important;
    }

    .pred-team-inline {
        gap: 4px !important;
    }

    .pred-team-inline span {
        font-size: 9px !important;
        max-width: 84px !important;
        line-height: 1.15 !important;
    }

    .pred-team-inline img,
    .pred-flag {
        width: 20px !important;
        height: 14px !important;
        border-radius: 3px !important;
    }

    .pred-score-pill {
        min-width: 58px !important;
        height: 36px !important;
        border-radius: 9px !important;
        gap: 3px !important;
    }

    .pred-score-pill span {
        font-size: 14px !important;
    }

    .pred-match-gap {
        height: 4px !important;
    }

    /* Tabla editable */
    div[data-testid="stDataFrame"] {
        font-size: 11px !important;
    }

    /* Resumen inferior */
    .pred-summary-grid {
        grid-template-columns: repeat(4, minmax(0, 1fr)) !important;
        gap: 5px !important;
    }

    .pred-summary-item {
        padding: 7px 3px !important;
    }

    .pred-summary-icon {
        font-size: 13px !important;
    }

    .pred-summary-number {
        font-size: 14px !important;
    }

    .pred-summary-label {
        font-size: 7px !important;
    }

    /* Perfil */
    .profile-stats {
        grid-template-columns: repeat(2, 1fr);
    }

    .profile-info-row {
        grid-template-columns: 1fr;
        gap: 2px;
    }
}
/* ============================================================
   MI PERFIL — CARD PREMIUM / MISMO LENGUAJE QUE JUGADORES
   ============================================================ */

.profile-panel {
    background: rgba(255,255,255,0.94);
    border: 1px solid rgba(226,232,240,0.9);
    border-radius: 18px;
    padding: 16px;
    box-shadow: 0 12px 30px rgba(15,23,42,0.06);
}

.profile-hero {
    position: relative;
    overflow: hidden;

    background:
        linear-gradient(
            90deg,
            rgba(255,255,255,0.08),
            rgba(255,255,255,0.10)
        ),
        var(--profile-hero-bg);

    background-size: cover;
    background-position: center;
    background-repeat: no-repeat;

    border: 1px solid rgba(226,232,240,0.85);
    border-radius: 16px;
    padding: 18px 16px 14px 16px;
}

.profile-hero-top {
    display: flex;
    align-items: flex-start;
    justify-content: space-between;
    gap: 18px;
}

.profile-hero-main {
    flex: 1;
    min-width: 0;
    text-align: center;
}

.profile-badges-side {
    width: 170px;
    flex-shrink: 0;
}

.profile-badges-mini {
    display: grid;
    grid-template-columns: repeat(3, minmax(0, 1fr));
    gap: 8px;
    justify-items: center;
}

.profile-badge-mini {
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

.profile-badge-mini.earned {
    box-shadow:
        inset 0 1px 0 rgba(255,255,255,0.82),
        0 8px 18px rgba(15,23,42,0.08);
}

.profile-badge-mini.locked {
    opacity: 0.92;
}

.profile-badge-mini-img {
    width: 42px;
    height: 42px;
    object-fit: contain;
    display: block;
}

.profile-badge-mini-fallback {
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

.profile-avatar {
    width: 118px;
    height: 118px;
    object-fit: cover;
    border-radius: 50%;
    border: 5px solid #F4C542;
    box-shadow:
        0 14px 34px rgba(15,23,42,0.18),
        0 0 26px rgba(244,197,66,0.30);
}

.profile-name {
    font-family: 'Montserrat', sans-serif;
    font-size: 24px;
    font-weight: 900;
    color: #F8FAFC;
    margin-top: 13px;
    line-height: 1.05;
}

.profile-user {
    color: #cbd5e1;
    font-size: 13px;
    font-weight: 900;
    margin-top: 4px;
}

.profile-rank-pill {
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

.profile-rank-pill strong {
    color: #F4C542;
}

.profile-stats {
    display: grid;
    grid-template-columns: repeat(3, minmax(0, 1fr));
    gap: 8px;
    margin: 14px 0 14px 0;
}

.profile-stat {
    border: 1px solid rgba(226,232,240,0.9);
    border-radius: 14px;
    padding: 10px 6px;
    background: rgba(248,250,252,0.78);
    text-align: center;
    min-width: 0;
}

.profile-stat-icon {
    font-size: 17px;
    line-height: 1;
    margin-bottom: 4px;
}

.profile-stat-number {
    font-family: 'Montserrat', sans-serif;
    font-size: 17px;
    font-weight: 900;
    color: #0f172a;
    line-height: 1;
}

.profile-stat-label {
    margin-top: 4px;
    font-size: 9px;
    color: #64748b;
    font-weight: 900;
    text-transform: uppercase;
}

.profile-info {
    border-top: 1px solid rgba(226,232,240,0.85);
    margin-top: 12px;
    padding-top: 10px;
}

.profile-info-row {
    display: grid;
    grid-template-columns: 108px 1fr;
    gap: 10px;
    padding: 9px 0;
    border-bottom: 1px solid rgba(226,232,240,0.65);
    font-size: 13px;
}

.profile-info-label {
    color: #64748b;
    font-weight: 900;
}

.profile-info-value {
    color: #0f172a;
    font-weight: 800;
    min-width: 0;
    overflow-wrap: anywhere;
}

.profile-bio {
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

.profile-edit-box {
    background: rgba(248,250,252,0.72);
    border: 1px solid rgba(226,232,240,0.85);
    border-radius: 15px;
    padding: 14px;
}

@media (max-width: 768px) {
    .profile-hero-top {
        flex-direction: column;
        align-items: center;
        gap: 14px;
    }

    .profile-hero-main {
        width: 100%;
    }

    .profile-badges-side {
        width: 100%;
        max-width: 210px;
    }

    .profile-badges-mini {
        gap: 6px;
    }

    .profile-badge-mini {
        width: 44px;
        height: 44px;
        border-radius: 10px;
    }

    .profile-badge-mini-img {
        width: 38px;
        height: 38px;
    }

    .profile-avatar {
        width: 104px;
        height: 104px;
    }

    .profile-name {
        font-size: 21px;
    }

    .profile-stats {
        grid-template-columns: repeat(3, minmax(0, 1fr));
        gap: 6px;
    }

    .profile-stat {
        padding: 8px 4px;
    }

    .profile-stat-number {
        font-size: 15px;
    }

    .profile-stat-label {
        font-size: 7px;
    }

    .profile-info-row {
        grid-template-columns: 1fr;
        gap: 2px;
    }
}
/* Botón normal de Streamlit usado en Editar Perfil */
div[data-testid="stButton"] button {
    border-radius: 13px !important;
    min-height: 42px !important;
    font-family: 'Inter', sans-serif !important;
    font-size: 14px !important;
    font-weight: 900 !important;

    background: linear-gradient(
        135deg,
        rgba(244,197,66,0.95),
        rgba(255,220,105,0.95)
    ) !important;

    color: #07111F !important;
    border: 1px solid rgba(180,130,20,0.28) !important;

    box-shadow:
        0 8px 18px rgba(244,197,66,0.16),
        inset 0 1px 0 rgba(255,255,255,0.38) !important;
}

@media (max-width: 768px) {
    .profile-avatar {
        width: 108px;
        height: 108px;
    }

    .profile-name {
        font-size: 22px;
    }

    .profile-stats {
        grid-template-columns: repeat(4, minmax(0, 1fr));
        gap: 6px;
    }

    .profile-stat {
        padding: 8px 4px;
    }

    .profile-stat-number {
        font-size: 15px;
    }

    .profile-stat-label {
        font-size: 7px;
    }

    .profile-info-row {
        grid-template-columns: 1fr;
        gap: 2px;
    }
}
</style>
"""

    css_mis_pronosticos = (
        css_mis_pronosticos
        .replace("__SIDEBAR_BANNER__", SIDEBAR_BANNER)
        .replace("__HEADER_BACKGROUND__", HEADER_BACKGROUND)
    )

    st.markdown(css_mis_pronosticos, unsafe_allow_html=True)

    # ============================================================
    # HELPERS
    # ============================================================

    def flag_html(flag_value):
        flag_value = str(flag_value)

        if flag_value.startswith("http") or flag_value.startswith("data:image"):
            return f'<img src="{flag_value}" class="pred-flag">'

        return f'<span>{escape(flag_value)}</span>'
        
    def flag_text(flag_value):
        """
        Devuelve bandera como texto para usar en st.data_editor.
        Si la bandera es URL/base64, no se puede mostrar como imagen en la tabla,
        entonces usa una pelota como fallback visual.
        """
        flag_value = str(flag_value)

        if flag_value.startswith("http") or flag_value.startswith("data:image"):
            return "⚽"

        if flag_value.strip() == "" or flag_value.lower() == "nan":
            return "⚽"

        return flag_value     

    def get_user_rank_stats(usuario):
        row_rank = df_ranking[df_ranking["USUARIO"] == usuario]

        if row_rank.empty:
            return {
                "pos": "-",
                "pts": 0,
                "exactos": 0,
                "generales": 0
            }

        row = row_rank.iloc[0]

        try:
            pos = int(row_rank.index[0])
        except:
            pos = "-"

        return {
            "pos": pos,
            "pts": int(row.get("PUNTOS", 0)),
            "exactos": int(row.get("EXACTOS", 0)),
            "generales": int(row.get("GENERALES", 0))
        }

    BADGE_ASSET_BASE_URL = "https://storage.googleapis.com/foto-prode2026/badges"

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

    badge_asset_map = {
        "Puntero": {
            "mini": f"{BADGE_ASSET_BASE_URL}/puntero/PUNTERO_MINI_128.png",
            "gray": f"{BADGE_ASSET_BASE_URL}/puntero/PUNTERO_GRAY_128.png",
        },
        "Sr. Prode": {
            "mini": f"{BADGE_ASSET_BASE_URL}/srprode/SRPRODE_MINI_128.png",
            "gray": f"{BADGE_ASSET_BASE_URL}/srprode/SRPRODE_GRAY_128.png",
        },
        "Siempre Suma": {
            "mini": f"{BADGE_ASSET_BASE_URL}/suma/SUMA_MINI_128.png",
            "gray": f"{BADGE_ASSET_BASE_URL}/suma/SUMA_GRAY_128.png",
        },
        "Optimista del Gol": {
            "mini": f"{BADGE_ASSET_BASE_URL}/optimista/OPTIMISTA_MINI_128.png",
            "gray": f"{BADGE_ASSET_BASE_URL}/optimista/OPTIMISTA_GRAY_128.png",
        },
        "El Cholo": {
            "mini": f"{BADGE_ASSET_BASE_URL}/elcholo/ELCHOLO_MINI_128.png",
            "gray": f"{BADGE_ASSET_BASE_URL}/elcholo/ELCHOLO_GRAY_128.png",
        },
        "Rey del Empate": {
            "mini": f"{BADGE_ASSET_BASE_URL}/empate/EMPATE_MINI_128.png",
            "gray": f"{BADGE_ASSET_BASE_URL}/empate/EMPATE_GRAY_128.png",
        },
        "El Macaya": {
            "mini": f"{BADGE_ASSET_BASE_URL}/macaya/MACAYA_MINI_128.png",
            "gray": f"{BADGE_ASSET_BASE_URL}/macaya/MACAYA_GRAY_128.png",
        },
        "El Misterioso": {
            "mini": f"{BADGE_ASSET_BASE_URL}/misterioso/MISTERIOSO_MINI_128.png",
            "gray": f"{BADGE_ASSET_BASE_URL}/misterioso/MISTERIOSO_GRAY_128.png",
        },
        "El Distinto": {
            "mini": f"{BADGE_ASSET_BASE_URL}/distinto/DISTINTO_MINI_128.png",
            "gray": f"{BADGE_ASSET_BASE_URL}/distinto/DISTINTO_GRAY_128.png",
        },
    }

    def get_user_badges(usuario):
        row_rank = df_ranking[
            df_ranking["USUARIO"].astype(str) == str(usuario)
        ]

        if row_rank.empty or "BADGES" not in row_rank.columns:
            return []

        badges = row_rank.iloc[0].get("BADGES", [])

        if badges is None:
            return []

        if isinstance(badges, list):
            return badges

        if isinstance(badges, str):
            limpio = (
                badges
                .replace("[", "")
                .replace("]", "")
                .replace("'", "")
                .replace('"', "")
            )

            return [
                b.strip()
                for b in limpio.split(",")
                if b.strip()
            ]

        return []

    def build_profile_badges_html(usuario):
        earned_badges = set(get_user_badges(usuario))

        items = []

        for title in badge_order:
            assets = badge_asset_map.get(title, {})
            is_earned = title in earned_badges

            badge_url = (
                assets.get("mini", "")
                if is_earned
                else assets.get("gray", "") or assets.get("mini", "")
            )

            state_class = "earned" if is_earned else "locked"

            if badge_url:
                visual_html = (
                    f'<img src="{escape(badge_url)}" '
                    f'class="profile-badge-mini-img" '
                    f'alt="{escape(title)}" '
                    f'loading="lazy">'
                )
            else:
                visual_html = '<div class="profile-badge-mini-fallback">🏅</div>'

            items.append(
                f'<div class="profile-badge-mini {state_class}" '
                f'title="{escape(title)}">{visual_html}</div>'
            )

        return "".join(items)
    
    def calcular_stats_pronosticos(lista_pronosticos):
        total_partidos = len(lista_pronosticos)

        if total_partidos == 0:
            return {
                "con_ganador": 0,
                "empates": 0,
                "goles": 0,
                "promedio_goles": 0,
                "estilo": "Sin datos"
            }

        con_ganador = 0
        empates = 0
        goles = 0
    
        for p in lista_pronosticos:
            p1 = int(p.get("P1", 0))
            p2 = int(p.get("P2", 0))
    
            goles += p1 + p2
    
            if p1 == p2:
                empates += 1
            else:
                con_ganador += 1
    
        promedio_goles = goles / total_partidos
    
        if promedio_goles >= 3:
            estilo = "Optimista del gol"
        elif promedio_goles <= 1.8:
            estilo = "Bilardista táctico"
        else:
            estilo = "Equilibrado"
    
        return {
            "con_ganador": con_ganador,
            "empates": empates,
            "goles": goles,
            "promedio_goles": round(promedio_goles, 1),
            "estilo": estilo
        }

    def parse_score_input(valor, default_p1=0, default_p2=0):
        """
        Valida un marcador con formato X-X.
        Solo permite un dígito por lado: 0-0 hasta 9-9.
        """
        valor = str(valor).strip()

        if re.fullmatch(r"[0-9]-[0-9]", valor):
            p1, p2 = valor.split("-")
            return int(p1), int(p2), True

        return int(default_p1), int(default_p2), False
   
    # ============================================================
    # DATOS BASE
    # ============================================================

    if "permitir_edicion" not in st.session_state:
        st.session_state.permitir_edicion = False

    if "editando_perfil" not in st.session_state:
        st.session_state.editando_perfil = False

    user_actual = st.session_state["user_data"]["USUARIO"]
    u_data = st.session_state["user_data"]

    PROFILE_HERO_BG_URL = "https://storage.googleapis.com/foto-prode2026/Banners/CAUDRADO1.png"

    df_user_pro = df_pro[df_pro["USUARIO"] == user_actual]

    ahora_arg = datetime.utcnow() - timedelta(hours=3)
    fecha_limite = datetime(2026, 6, 8, 23, 59, 59)
    es_tiempo_valido = ahora_arg < fecha_limite

    # ============================================================
    # TÍTULO DE PÁGINA
    # ============================================================

    st.markdown("""
<div class="page-section-title">
    <h1>Mis Pronósticos / Mi Perfil</h1>
    <p>Gestioná tus predicciones y tu información personal.</p>
</div>
""", unsafe_allow_html=True)

    c_pron, c_perfil = st.columns([1.35, 1], gap="large")

    # ============================================================
    # COLUMNA IZQUIERDA — MIS PRONÓSTICOS
    # ============================================================

    with c_pron:

        modo_edicion = st.session_state.permitir_edicion

        if not es_tiempo_valido:
            estado_txt = "Plazo finalizado · modo lectura"
            estado_class = "locked"
            modo_edicion = False
            st.session_state.permitir_edicion = False
        else:
            estado_txt = "Edición abierta hasta el 08/06/2026"
            estado_class = "open"

        if "pron_editor_version" not in st.session_state:
            st.session_state.pron_editor_version = 0

        # ------------------------------------------------------------
        # HEADER DEL PANEL
        # ------------------------------------------------------------

        st.markdown(f"""
<div class="pred-panel-header-v2">
<div class="pred-panel-title-row">
<div class="panel-icon">📝</div>
<div>
<div class="panel-title">Mis Pronósticos</div>
<div class="pred-panel-subtitle {estado_class}">{estado_txt}</div>
</div>
</div>
</div>
""", unsafe_allow_html=True)

        # ============================================================
        # PREPARACIÓN DE DATOS COMÚN
        # ============================================================

        lista_pronosticos_actuales = []
        filas_editor = []

        for _, row in df_res.sort_values("N_PARTIDO").iterrows():
            id_p = int(row["N_PARTIDO"])
            match = df_user_pro[df_user_pro["N_PARTIDO"] == id_p]

            v1 = (
                int(match.iloc[0]["P1"])
                if not match.empty and pd.notna(match.iloc[0]["P1"])
                else 0
            )

            v2 = (
                int(match.iloc[0]["P2"])
                if not match.empty and pd.notna(match.iloc[0]["P2"])
                else 0
            )

            equipo_1 = str(row.get("Equipo_1", ""))
            equipo_2 = str(row.get("Equipo_2", ""))

            bandera1 = mapa_banderas.get(equipo_1, "⚽")
            bandera2 = mapa_banderas.get(equipo_2, "⚽")

            dia = str(row.get("DIA", ""))
            hora = str(row.get("HORA", ""))

            lista_pronosticos_actuales.append(
                {
                    "N_PARTIDO": id_p,
                    "USUARIO": user_actual,
                    "P1": v1,
                    "P2": v2
                }
            )

            filas_editor.append(
                {
                    "N_PARTIDO": id_p,
                    "Equipo 1": equipo_1,
                    "P1": v1,
                    "P2": v2,
                    "Equipo 2": equipo_2,
                    "DIA": dia,
                    "HORA": hora,
                }
            )

        stats_pronosticos = calcular_stats_pronosticos(lista_pronosticos_actuales)

        # ============================================================
        # MODO VISUAL
        # ============================================================

        if not modo_edicion:

            with st.container(height=520):

                for _, row in df_res.sort_values("N_PARTIDO").iterrows():
                    id_p = int(row["N_PARTIDO"])
                    match = df_user_pro[df_user_pro["N_PARTIDO"] == id_p]

                    v1 = (
                        int(match.iloc[0]["P1"])
                        if not match.empty and pd.notna(match.iloc[0]["P1"])
                        else 0
                    )

                    v2 = (
                        int(match.iloc[0]["P2"])
                        if not match.empty and pd.notna(match.iloc[0]["P2"])
                        else 0
                    )

                    equipo_1 = str(row.get("Equipo_1", ""))
                    equipo_2 = str(row.get("Equipo_2", ""))

                    bandera1 = mapa_banderas.get(equipo_1, "⚽")
                    bandera2 = mapa_banderas.get(equipo_2, "⚽")

                    dia = str(row.get("DIA", ""))
                    hora = str(row.get("HORA", ""))

                    st.markdown(
                        f"""
<div class="pred-match-card-v2">

<div class="pred-match-meta">
<span>Partido #{id_p}</span>
<span>{escape(dia)} | {escape(hora)}</span>
</div>

<div class="pred-match-main-row">

<div class="pred-team-inline left">
<span>{escape(equipo_1)}</span>
{flag_html(bandera1)}
</div>

<div class="pred-score-pill">
<span>{v1}</span>
<span class="score-colon">:</span>
<span>{v2}</span>
</div>

<div class="pred-team-inline right">
{flag_html(bandera2)}
<span>{escape(equipo_2)}</span>
</div>

</div>
</div>
""",
                        unsafe_allow_html=True
                    )

                    st.markdown(
                        "<div class='pred-match-gap'></div>",
                        unsafe_allow_html=True
                    )

            if es_tiempo_valido:
                if st.button(
                    "✏️ Editar pronósticos",
                    use_container_width=True
                ):
                    st.session_state.permitir_edicion = True
                    st.rerun()
            else:
                st.button(
                    "Lectura — edición deshabilitada",
                    use_container_width=True,
                    disabled=True
                )
            # ------------------------------------------------------------
            # RESUMEN OSCURO — MODO VISUAL
            # ------------------------------------------------------------

            st.markdown(
                f"""
<div class="pred-summary-footer">
<div class="pred-summary-kicker">Tus pronósticos</div>

<div class="pred-summary-grid">
<div class="pred-summary-item">
<div class="pred-summary-icon">🏆</div>
<div class="pred-summary-number">{stats_pronosticos["con_ganador"]}</div>
<div class="pred-summary-label">Con ganador</div>
</div>

<div class="pred-summary-item">
<div class="pred-summary-icon">🤝</div>
<div class="pred-summary-number">{stats_pronosticos["empates"]}</div>
<div class="pred-summary-label">Empates</div>
</div>

<div class="pred-summary-item">
<div class="pred-summary-icon">⚽</div>
<div class="pred-summary-number">{stats_pronosticos["goles"]}</div>
<div class="pred-summary-label">Goles</div>
</div>

<div class="pred-summary-item">
<div class="pred-summary-icon">📊</div>
<div class="pred-summary-number">{stats_pronosticos["promedio_goles"]}</div>
<div class="pred-summary-label">Promedio</div>
</div>
</div>

<div class="pred-summary-style">
Estilo de predicción: <strong>{stats_pronosticos["estilo"]}</strong>
</div>
</div>
""",
                unsafe_allow_html=True
            )

        # ============================================================
        # MODO EDICIÓN — TABLA TIPO EXCEL
        # ============================================================

        else:

            st.markdown("""
<div class="pred-status">
✏️ Modo edición activo. Modificá solamente los goles y luego guardá los cambios.
</div>
""", unsafe_allow_html=True)

            df_editor = pd.DataFrame(filas_editor)

            edited_df = st.data_editor(
                df_editor,
                hide_index=True,
                use_container_width=True,
                key=f"pronosticos_editor_{st.session_state.pron_editor_version}",
                disabled=[
                    "N_PARTIDO",
                    "Equipo 1",
                    "Equipo 2",
                    "DIA",
                    "HORA"
                ],
                column_order=[
                    "Equipo 1",
                    "P1",
                    "P2",
                    "Equipo 2"
                ],
                column_config={
                    "Equipo 1": st.column_config.TextColumn(
                        "Equipo 1",
                        width="small"
                    ),
                    "P1": st.column_config.NumberColumn(
                        "P1",
                        min_value=0,
                        max_value=20,
                        step=1,
                        width="small"
                    ),
                    "P2": st.column_config.NumberColumn(
                        "P2",
                        min_value=0,
                        max_value=20,
                        step=1,
                        width="small"
                    ),
                    "Equipo 2": st.column_config.TextColumn(
                        "Equipo 2",
                        width="small"
                    ),
                }
            )
            c_cancelar, c_guardar = st.columns([0.35, 0.65])

            with c_cancelar:
                cancelar = st.button(
                    "❌ Cancelar",
                    use_container_width=True
                )

            with c_guardar:
                guardar = st.button(
                    "💾 Guardar cambios",
                    use_container_width=True
                )

            if cancelar:
                st.session_state.permitir_edicion = False
                st.session_state.pron_editor_version += 1
                st.rerun()

            if guardar:
                try:
                    df_save = edited_df.copy()

                    df_save["P1"] = pd.to_numeric(
                        df_save["P1"],
                        errors="coerce"
                    )

                    df_save["P2"] = pd.to_numeric(
                        df_save["P2"],
                        errors="coerce"
                    )

                    if df_save["P1"].isna().any() or df_save["P2"].isna().any():
                        st.error("Hay valores vacíos o inválidos. Revisá P1 y P2.")
                        st.stop()

                    df_save["P1"] = df_save["P1"].astype(int)
                    df_save["P2"] = df_save["P2"].astype(int)

                    if (
                        (df_save["P1"] < 0).any()
                        or (df_save["P2"] < 0).any()
                        or (df_save["P1"] > 20).any()
                        or (df_save["P2"] > 20).any()
                    ):
                        st.error("Los goles deben estar entre 0 y 20.")
                        st.stop()

                    nuevos_pro = df_save[
                        [
                            "N_PARTIDO",
                            "P1",
                            "P2"
                        ]
                    ].copy()

                    nuevos_pro["USUARIO"] = user_actual

                    nuevos_pro = nuevos_pro[
                        [
                            "N_PARTIDO",
                            "USUARIO",
                            "P1",
                            "P2"
                        ]
                    ]

                    df_pro_full = conn.read(
                        worksheet="PRONOSTICOS",
                        ttl=5
                    )

                    df_otros = df_pro_full[
                        df_pro_full["USUARIO"] != user_actual
                    ]

                    df_final = pd.concat(
                        [df_otros, nuevos_pro],
                        ignore_index=True
                    )

                    conn.update(
                        worksheet="PRONOSTICOS",
                        data=df_final
                    )

                    st.cache_data.clear()
                    st.session_state.permitir_edicion = False
                    st.session_state.pron_editor_version += 1

                    st.success("✅ ¡Pronósticos guardados correctamente!")
                    st.balloons()
                    st.rerun()

                except Exception as e:
                    st.error(f"Error al guardar: {e}")

    # ============================================================
    # COLUMNA DERECHA — MI PERFIL
    # ============================================================

    with c_perfil:
        stats = get_user_rank_stats(user_actual)

        foto_actual = u_data.get("AVATAR_URL")

        if not foto_actual or pd.isna(foto_actual):
            foto = AVATAR_GENERICO
        else:
            foto = foto_actual

        if not st.session_state.editando_perfil:
            nombre = escape(str(u_data.get("NOMBRE", "Jugador")))
            usuario = escape(str(u_data.get("USUARIO", "")))
            equipo = escape(str(u_data.get("EQUIPO FAVORITO", "-")))
            edad = escape(str(u_data.get("EDAD", "-")))
            bio = escape(str(u_data.get("DESCRIPCION", "")))

            pts = stats["pts"]
            exactos = stats["exactos"]
            generales = stats["generales"]
            posicion = stats["pos"]

            profile_badges_mini_html = build_profile_badges_html(user_actual)

            if bio.strip() == "" or bio.strip().lower() == "nan":
                bio = "Todavía no cargaste una bio. Contanos tu estilo de juego, tus cábalas o a quién ves campeón."

            st.markdown(
                f"""
<div class="profile-panel">

<div class="panel-header">
<div class="panel-icon">👤</div>
<div>
<div class="panel-title">Mi Perfil</div>
<div class="pred-panel-subtitle">Tu ficha personal del Prode</div>
</div>
</div>

<div class="profile-hero" style="--profile-hero-bg: url('{PROFILE_HERO_BG_URL}');">
<div class="profile-hero-top">

<div class="profile-hero-main">
<img src="{foto}" class="profile-avatar">
<div class="profile-name">{nombre}</div>
<div class="profile-user">@{usuario} · {equipo}</div>

<div class="profile-rank-pill">
<span>📊 Posición actual</span>
<strong>{posicion}°</strong>
</div>
</div>

<div class="profile-badges-side">
<div class="profile-badges-mini">
{profile_badges_mini_html}
</div>
</div>

</div>
</div>

<div class="profile-stats">
<div class="profile-stat">
<div class="profile-stat-icon">🏆</div>
<div class="profile-stat-number">{pts}</div>
<div class="profile-stat-label">Puntos</div>
</div>

<div class="profile-stat">
<div class="profile-stat-icon">🎯</div>
<div class="profile-stat-number">{exactos}</div>
<div class="profile-stat-label">Exactos</div>
</div>

<div class="profile-stat">
<div class="profile-stat-icon">✅</div>
<div class="profile-stat-number">{generales}</div>
<div class="profile-stat-label">Generales</div>
</div>
</div>

<div class="profile-info">
<div class="profile-info-row">
<div class="profile-info-label">⚽ Equipo favorito</div>
<div class="profile-info-value">{equipo}</div>
</div>

<div class="profile-info-row">
<div class="profile-info-label">🎂 Edad</div>
<div class="profile-info-value">{edad} años</div>
</div>
</div>

<div class="profile-bio">
<strong>Bio:</strong> {bio}
</div>

</div>
""",
                unsafe_allow_html=True
            )

            if st.button("✏️ Editar Perfil", use_container_width=True):
                st.session_state.editando_perfil = True
                st.rerun()

        else:
            st.markdown("""
<div class="profile-panel">
<div class="panel-header">
    <div class="panel-icon">✏️</div>
    <div class="panel-title">Editar Perfil</div>
</div>
<div class="profile-edit-box">
""", unsafe_allow_html=True)

            with st.form("form_edit_perfil_v4"):
                archivo_perfil = st.file_uploader(
                    "Actualizar foto de perfil",
                    type=["jpg", "jpeg", "png"]
                )

                n_nom = st.text_input(
                    "Nombre Real",
                    value=str(u_data.get("NOMBRE", ""))
                )

                equipos = [
                    "Argentina",
                    "México",
                    "España",
                    "Brasil",
                    "Uruguay",
                    "Colombia",
                    "Otro"
                ]

                equipo_actual = u_data.get("EQUIPO FAVORITO", "Argentina")
                idx_equipo = equipos.index(equipo_actual) if equipo_actual in equipos else 0

                n_equ = st.selectbox(
                    "Hincha de",
                    equipos,
                    index=idx_equipo
                )

                n_bio = st.text_area(
                    "Bio",
                    value=str(u_data.get("DESCRIPCION", "")),
                    max_chars=100
                )

                c_b1, c_b2 = st.columns(2)

                guardar = c_b1.form_submit_button("✅ Guardar")
                cancelar = c_b2.form_submit_button("❌ Cancelar")

                if guardar:
                    nueva_url = u_data.get("AVATAR_URL", AVATAR_GENERICO)

                    if archivo_perfil:
                        with st.spinner("Subiendo foto al servidor..."):
                            ts = datetime.now().strftime("%H%M%S")
                            nombre_archivo = f"perfil_{u_data['USUARIO']}_{ts}.jpg"
                            res_url = upload_profile_picture(
                                archivo_perfil,
                                nombre_archivo
                            )

                            if res_url and "Error" not in res_url:
                                nueva_url = res_url
                            else:
                                st.error(f"Error al subir: {res_url}")

                    try:
                        df_u = conn.read(worksheet="USUARIOS", ttl=10)

                        df_u.loc[
                            df_u["USUARIO"] == u_data["USUARIO"],
                            ["NOMBRE", "AVATAR_URL", "EQUIPO FAVORITO", "DESCRIPCION"]
                        ] = [n_nom, nueva_url, n_equ, n_bio]

                        conn.update(
                            worksheet="USUARIOS",
                            data=df_u
                        )

                        st.session_state["user_data"].update(
                            {
                                "NOMBRE": n_nom,
                                "AVATAR_URL": nueva_url,
                                "EQUIPO FAVORITO": n_equ,
                                "DESCRIPCION": n_bio
                            }
                        )

                        st.session_state.editando_perfil = False
                        st.cache_data.clear()

                        st.success("¡Perfil actualizado!")
                        st.rerun()

                    except Exception as e:
                        st.error(f"Error: {e}")

                if cancelar:
                    st.session_state.editando_perfil = False
                    st.rerun()

            st.markdown("</div></div>", unsafe_allow_html=True)
