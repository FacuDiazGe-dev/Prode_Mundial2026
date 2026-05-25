import streamlit as st
import pandas as pd
import plotly.express as px
import streamlit.components.v1 as components
import re

from datetime import datetime, timedelta
from html import escape

from ranking_logic import calcular_detalle

from styles_config import (
    AVATAR_GENERICO,
    HEADER_BACKGROUND,
    SIDEBAR_BANNER,
    EVOL_HEADER_BACKGROUND
)

from tools import upload_profile_picture

from services.supabase_service import (
    guardar_pronosticos_supabase,
    actualizar_usuario_supabase,
    get_config_app
)


def render_mis_pronosticos(
    df_res,
    df_usuarios,
    df_pro,
    df_ranking,
    mapa_banderas
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
    position: relative;
    overflow: hidden;

    background:
        linear-gradient(
            180deg,
            rgba(255,255,255,0.76),
            rgba(248,250,252,0.60)
        ),
        url("__FONDO_CARD_INICIO__");

    background-size: cover;
    background-position: center;
    background-repeat: no-repeat;

    border: 1px solid rgba(148,163,184,0.34);
    border-radius: 16px;

    padding: 13px 14px;
    margin-bottom: 11px;

    box-shadow:
        0 8px 18px rgba(15,23,42,0.05),
        inset 0 1px 0 rgba(255,255,255,0.75);

    transition:
        transform 0.18s ease,
        box-shadow 0.18s ease,
        border-color 0.18s ease;
}

.pred-match-card-v2::before {
    content: "";

    position: absolute;
    inset: 0;

    background:
        radial-gradient(
            circle at 0% 0%,
            rgba(244,197,66,0.08),
            transparent 38%
        ),
        linear-gradient(
            90deg,
            rgba(255,255,255,0.24),
            rgba(255,255,255,0.08)
        );

    pointer-events: none;
    z-index: 0;
}

.pred-match-card-v2 > * {
    position: relative;
    z-index: 1;
}

.pred-match-card-v2:hover {
    transform: translateY(-1px);
    border-color: rgba(244,197,66,0.44);

    box-shadow:
        0 12px 24px rgba(15,23,42,0.085),
        0 0 14px rgba(244,197,66,0.08),
        inset 0 1px 0 rgba(255,255,255,0.82);
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


/* ============================================================
   SELECTOR DE FECHA — OSCURO TEXTURADO ESTABLE
   ============================================================ */

/* Cápsula general */
div[aria-label="Fecha de fase de grupos"] {
    display: flex !important;
    align-items: center !important;
    justify-content: space-between !important;
    gap: 8px !important;

    width: 100% !important;
    max-width: none !important;

    padding: 8px !important;
    margin: 8px 0 6px 0 !important;

    background:
        linear-gradient(
            90deg,
            rgba(7,17,31,0.74) 0%,
            rgba(15,23,42,0.62) 52%,
            rgba(30,41,59,0.46) 100%
        ),
        url("__FONDO_CARD_INICIO3__");

    background-size: cover;
    background-position: center;
    background-repeat: no-repeat;

    border: 1px solid rgba(244,197,66,0.22);
    border-radius: 999px;

    box-shadow:
        inset 0 1px 0 rgba(255,255,255,0.08),
        0 10px 22px rgba(15,23,42,0.12);
}

/* Cada opción */
div[aria-label="Fecha de fase de grupos"] label {
    flex: 1 1 0 !important;
    min-width: 0 !important;
    min-height: 40px !important;

    display: flex !important;
    align-items: center !important;
    justify-content: center !important;

    padding: 0 16px !important;

    border-radius: 999px;

    color: rgba(248,250,252,0.92) !important;
    white-space: nowrap !important;

    cursor: pointer;

    transition:
        background 0.18s ease,
        color 0.18s ease,
        box-shadow 0.18s ease,
        transform 0.18s ease;
}

/* Ocultar indicador nativo del radio */
div[aria-label="Fecha de fase de grupos"] label > div:first-child {
    display: none !important;
}

/* Texto */
div[aria-label="Fecha de fase de grupos"] label p {
    margin: 0 !important;
    font-family: 'Inter', sans-serif !important;
    font-size: 13px !important;
    font-weight: 900 !important;
    color: FFFFFF !important;
    opacity: 1 !important;
}

/* Hover */
div[aria-label="Fecha de fase de grupos"] label:hover {
    background: rgba(255,255,255,0.08);
    color: #FFFFFF !important;
    transform: translateY(-1px);
}

/* Opción activa */
div[aria-label="Fecha de fase de grupos"] label:has(input:checked) {
    background:
        radial-gradient(
            circle at 20% 0%,
            rgba(255,255,255,0.24),
            transparent 44%
        ),
        linear-gradient(
            180deg,
            rgba(244,197,66,0.98),
            rgba(255,220,105,0.94)
        );

    color: #07111F !important;

    box-shadow:
        0 8px 16px rgba(244,197,66,0.20),
        inset 0 1px 0 rgba(255,255,255,0.42);
}

div[aria-label="Fecha de fase de grupos"] label:has(input:checked) p {
    color: #07111F !important;
    font-weight: 900 !important;
}

/* Mobile */
@media (max-width: 768px) {
    div[aria-label="Fecha de fase de grupos"] {
        gap: 5px !important;
        padding: 6px !important;
        margin: 6px 0 4px 0 !important;
    }

    div[aria-label="Fecha de fase de grupos"] label {
        min-height: 36px !important;
        padding: 0 10px !important;
    }

    div[aria-label="Fecha de fase de grupos"] label p {
        font-size: 11px !important;
    }
    .pred-scroll {
        height: 430px;
        padding: 8px 9px 3px 9px;
        margin: 0 0 10px 0;
        border-radius: 15px;
    }
}

    .pred-scroll {
        height: 430px;
        padding: 8px 9px 3px 9px;
        margin: 0 0 10px 0;
        border-radius: 15px;
    }
}
.pred-panel-header-v2 {
    position: relative;
    overflow: hidden;

    padding: 13px 15px 14px 15px;
    margin-bottom: 14px;

    border-radius: 16px;

    background-image:
        radial-gradient(
            circle at 0% 0%,
            rgba(244,197,66,0.18),
            transparent 36%
        ),
        linear-gradient(
            90deg,
            rgba(7,17,31,0.96) 0%,
            rgba(15,23,42,0.84) 58%,
            rgba(15,23,42,0.48) 100%
        ),
        url("__SIDEBAR_BANNER__");

    background-size: cover;
    background-position: center;

    border: 1px solid rgba(244,197,66,0.22);

    box-shadow:
        inset 0 1px 0 rgba(255,255,255,0.08),
        0 10px 22px rgba(15,23,42,0.12);
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
    color: #34D399;
    font-weight: 800;
}

.pred-panel-subtitle.locked {
    color: #CBD5E1;
    font-weight: 800;
}

/* ============================================================
   SCROLL PREMIUM — MIS PRONÓSTICOS
   ============================================================ */

.pred-scroll {
    height: 520px;

    overflow-y: auto;
    overflow-x: hidden;

    padding: 12px 12px 4px 12px;
    margin-bottom: 12px;
    margin-top: 0 !important;

    border-radius: 16px;

    background:
        linear-gradient(
            180deg,
            rgba(255,255,255,0.56),
            rgba(248,250,252,0.38)
        );

    border: 1px solid rgba(203,213,225,0.72);

    box-shadow:
        inset 0 1px 0 rgba(255,255,255,0.70),
        0 8px 18px rgba(15,23,42,0.035);

    scrollbar-width: thin;
    scrollbar-color: #0F2D63 rgba(226,232,240,0.55);
}

.pred-scroll::-webkit-scrollbar {
    width: 8px;
}

.pred-scroll::-webkit-scrollbar-track {
    background: linear-gradient(
        180deg,
        rgba(226,232,240,0.55),
        rgba(241,245,249,0.85)
    );
    border-radius: 999px;
    box-shadow: inset 0 0 0 1px rgba(148,163,184,0.18);
}

.pred-scroll::-webkit-scrollbar-thumb {
    background: linear-gradient(
        180deg,
        #0F2D63 0%,
        #173F86 55%,
        #D4A017 100%
    );
    border-radius: 999px;
    border: 1px solid rgba(255,255,255,0.45);
    box-shadow:
        inset 0 1px 0 rgba(255,255,255,0.25),
        0 2px 6px rgba(15,23,42,0.18);
}

.pred-scroll::-webkit-scrollbar-thumb:hover {
    background: linear-gradient(
        180deg,
        #173F86 0%,
        #1D4FA8 55%,
        #E2B93B 100%
    );
}

@media (max-width: 768px) {
    .pred-scroll {
        height: 430px;
        padding: 10px 9px 3px 9px;
        border-radius: 15px;
    }
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
        background-position: center !important;
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
   MI PERFIL — CARD PREMIUM / MISMO LENGUAJE QUE PLANTEL
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
            rgba(7,17,31,0.50),
            rgba(7,17,31,0.22)
        ),
        var(--profile-hero-bg);

    background-size: cover;
    background-position: center;
    background-repeat: no-repeat;

    border: 1px solid rgba(244,197,66,0.22);
    border-radius: 18px;
    padding: 18px 16px 15px 16px;

    box-shadow:
        inset 0 1px 0 rgba(255,255,255,0.08),
        0 12px 26px rgba(15,23,42,0.16);
}

.profile-hero-top {
    display: grid;
    grid-template-columns: minmax(0, 1fr) 170px;
    align-items: center;
    gap: 18px;
}

.profile-hero-main {
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

    border-radius: 13px;
    background: rgba(255,255,255,0.62);
    border: 1px solid rgba(255,255,255,0.70);

    box-shadow:
        inset 0 1px 0 rgba(255,255,255,0.72),
        0 6px 14px rgba(15,23,42,0.16);
}

.profile-badge-mini.earned {
    border-color: rgba(244,197,66,0.42);
    background: rgba(255,255,255,0.72);

    box-shadow:
        inset 0 1px 0 rgba(255,255,255,0.82),
        0 8px 18px rgba(244,197,66,0.12);
}

.profile-badge-mini.locked {
    opacity: 0.88;
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
    width: 108px;
    height: 108px;
    object-fit: cover;
    border-radius: 50%;

    border: 5px solid #F4C542;

    box-shadow:
        0 14px 34px rgba(15,23,42,0.28),
        0 0 28px rgba(244,197,66,0.32);
}

.profile-name {
    font-family: 'Montserrat', sans-serif;
    font-size: 24px;
    font-weight: 900;
    color: #F8FAFC;

    margin-top: 11px;
    line-height: 1.05;

    text-shadow: 0 2px 8px rgba(0,0,0,0.60);
}

.profile-user {
    color: rgba(226,232,240,0.78);
    font-size: 13px;
    font-weight: 900;
    margin-top: 4px;

    text-shadow: 0 1px 6px rgba(0,0,0,0.50);
}

.profile-rank-pill {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    gap: 6px;

    margin-top: 11px;
    padding: 7px 12px;

    background: rgba(7,17,31,0.92);
    border: 1px solid rgba(244,197,66,0.34);
    border-radius: 999px;

    color: #F8FAFC;
    font-size: 12px;
    font-weight: 900;

    box-shadow:
        inset 0 1px 0 rgba(255,255,255,0.08),
        0 8px 18px rgba(15,23,42,0.16);
}

.profile-rank-pill strong {
    color: #F4C542;
}

/* Stats integrados al hero */

.profile-stats {
    display: grid;
    grid-template-columns: repeat(3, minmax(0, 1fr));
    gap: 8px;

    margin: 15px 0 0 0;
    padding: 10px;

    border-radius: 16px;

    background:
        linear-gradient(
            90deg,
            rgba(7,17,31,0.78),
            rgba(15,23,42,0.58)
        );

    border: 1px solid rgba(244,197,66,0.18);

    box-shadow:
        inset 0 1px 0 rgba(255,255,255,0.08),
        0 8px 18px rgba(15,23,42,0.12);
}

.profile-stat {
    border: 0;
    border-radius: 13px;
    padding: 8px 6px;

    background: rgba(255,255,255,0.055);
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
    font-size: 18px;
    font-weight: 900;
    color: #F8FAFC;
    line-height: 1;

    text-shadow: 0 2px 8px rgba(0,0,0,0.65);
}

.profile-stat-label {
    margin-top: 4px;
    font-size: 9px;
    color: rgba(226,232,240,0.72);
    font-weight: 900;
    text-transform: uppercase;
}

/* Bio integrada al hero */

.profile-hero-bio {
    margin-top: 11px;
    padding: 11px 13px;

    border-radius: 14px;

    background:
        linear-gradient(
            90deg,
            rgba(7,17,31,0.82),
            rgba(15,23,42,0.62)
        );

    border: 1px solid rgba(244,197,66,0.22);

    color: rgba(248,250,252,0.86);
    font-size: 12.5px;
    font-weight: 650;
    line-height: 1.42;

    text-align: left;

    box-shadow:
        inset 0 1px 0 rgba(255,255,255,0.08),
        0 8px 18px rgba(15,23,42,0.10);
}

.profile-hero-bio-label {
    display: inline-flex;
    align-items: center;
    gap: 6px;

    margin-right: 5px;

    color: #F4C542;
    font-weight: 900;
}

.profile-hero-bio-icon {
    font-size: 15px;
    line-height: 1;
}

/* Se conserva por seguridad para usos auxiliares */
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
    .profile-hero {
        padding: 15px 13px 13px 13px;
        border-radius: 16px;
    }

    .profile-hero-top {
        grid-template-columns: 1fr;
        justify-items: center;
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
        padding: 8px;
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

    .profile-hero-bio {
        margin-top: 10px;
        padding: 10px 11px;
        font-size: 12px;
        line-height: 1.36;
    }

    .profile-info-row {
        grid-template-columns: 1fr;
        gap: 2px;
    }
}

/* ============================================================
   MI EVOLUCIÓN — PANEL COMPACTO
   ============================================================ */
/* ============================================================
   MI EVOLUCIÓN — PANEL COMPACTO
   ============================================================ */

.evolution-panel {
    background: rgba(255,255,255,0.94);
    border: 1px solid rgba(226,232,240,0.9);
    border-radius: 18px;
    padding: 16px;
    margin-top: 14px;
    box-shadow: 0 12px 30px rgba(15,23,42,0.06);
}

.evolution-header {
    display: flex;
    align-items: center;
    gap: 10px;

    padding: 4px 4px 12px 4px;
    margin-bottom: 10px;

    border-bottom: 1px solid rgba(226,232,240,0.75);
}

.evolution-icon {
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

.evolution-title {
    font-family: 'Montserrat', sans-serif;
    font-size: 18px;
    font-weight: 900;
    color: #0f172a;
    line-height: 1.05;
}

.evolution-subtitle {
    color: #64748b;
    font-size: 12px;
    font-weight: 700;
    margin-top: 3px;
}

.evolution-empty {
    background: rgba(248,250,252,0.86);
    border: 1px solid rgba(226,232,240,0.88);
    border-radius: 14px;
    padding: 12px;

    color: #64748b;
    font-size: 13px;
    font-weight: 750;
    line-height: 1.35;
}

.evolution-stats {
    display: grid;
    grid-template-columns: repeat(3, minmax(0, 1fr));
    gap: 8px;
    margin-top: 10px;
}

.evolution-stat {
    background:
        linear-gradient(
            135deg,
            rgba(7,17,31,0.98),
            rgba(15,23,42,0.94)
        );

    border: 1px solid rgba(244,197,66,0.16);
    border-radius: 13px;
    padding: 9px 6px;
    text-align: center;
}

.evolution-stat-number {
    font-family: 'Montserrat', sans-serif;
    font-size: 16px;
    font-weight: 900;
    color: #F8FAFC;
    line-height: 1;
}

.evolution-stat-label {
    margin-top: 4px;
    color: rgba(226,232,240,0.64);
    font-size: 8px;
    font-weight: 900;
    text-transform: uppercase;
    letter-spacing: 0.03em;
}

@media (max-width: 768px) {
    .evolution-panel {
        padding: 13px;
        border-radius: 16px;
    }

    .evolution-title {
        font-size: 16px;
    }

    .evolution-subtitle {
        font-size: 11px;
    }

    .evolution-stats {
        gap: 6px;
    }

    .evolution-stat {
        padding: 8px 4px;
    }

    .evolution-stat-number {
        font-size: 14px;
    }

    .evolution-stat-label {
        font-size: 7px;
    }
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
    
    FONDO_CARD_INICIO = "https://storage.googleapis.com/foto-prode2026/Banners/FONDO_CARD_INICIO.png"
    FONDO_CARD_INICIO3 = "https://storage.googleapis.com/foto-prode2026/Banners/FONDO_CARD_INICIO3.png"
    
    css_mis_pronosticos = (
        css_mis_pronosticos
        .replace("__SIDEBAR_BANNER__", SIDEBAR_BANNER)
        .replace("__HEADER_BACKGROUND__", HEADER_BACKGROUND)
        .replace("__FONDO_CARD_INICIO__", FONDO_CARD_INICIO)
        .replace("__FONDO_CARD_INICIO3__", FONDO_CARD_INICIO3)
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
    def render_evolucion_puntos_premium(usuario_actual):
        """
        Renderiza la evolución de puntos con el mismo estilo visual que Inicio.
        Muestra usuario actual + Top 5 del ranking.
        """

        if df_res is None or df_res.empty:
            st.markdown("""
<div class="evol-panel">
<div class="evol-panel-header">
<div class="evol-panel-icon">📈</div>
<div class="evol-panel-title">Mi Evolución</div>
</div>
<div class="evol-empty">Esperando el silbato inicial para mostrar estadísticas.</div>
</div>
""", unsafe_allow_html=True)
            return

        df_res_check = df_res.copy()

        if "VIZ" not in df_res_check.columns:
            df_res_check["VIZ"] = "FALSE"

        df_res_check["VIZ_CHECK"] = (
            df_res_check["VIZ"]
            .astype(str)
            .str.strip()
            .str.upper()
        )

        partidos_visibles = (
            df_res_check[
                df_res_check["VIZ_CHECK"].isin(
                    ["TRUE", "1", "1.0", "VERDADERO", "T"]
                )
            ]
            .sort_values("N_PARTIDO")
        )

        evol_html_inicio = (
            '<div class="evol-panel">'
            '<div class="evol-panel-header">'
            '<div class="evol-panel-icon">📈</div>'
            '<div class="evol-panel-title">Mi Evolución</div>'
            '</div>'
        )

        if partidos_visibles.empty:
            evol_html = evol_html_inicio
            evol_html += '<div class="evol-empty">Esperando el silbato inicial para mostrar estadísticas.</div>'
            evol_html += '</div>'

            st.markdown(evol_html, unsafe_allow_html=True)
            return

        evol_list = []
        usuarios_lista = df_usuarios["USUARIO"].unique()
        ids_visibles = partidos_visibles["N_PARTIDO"].tolist()

        for user in usuarios_lista:
            pts_acc = 0
            user_pro = df_pro[
                df_pro["USUARIO"].astype(str) == str(user)
            ]

            for id_p in ids_visibles:
                part_row = partidos_visibles[
                    partidos_visibles["N_PARTIDO"] == id_p
                ]

                u_p = user_pro[
                    user_pro["N_PARTIDO"] == id_p
                ]

                if not part_row.empty and not u_p.empty:
                    r1_g = part_row["R1"].iloc[0]
                    r2_g = part_row["R2"].iloc[0]
                    p1_g = u_p["P1"].iloc[0]
                    p2_g = u_p["P2"].iloc[0]

                    if (
                        pd.notna(r1_g)
                        and pd.notna(r2_g)
                        and pd.notna(p1_g)
                        and pd.notna(p2_g)
                    ):
                        pts_g, _, _ = calcular_detalle(
                            r1_g,
                            r2_g,
                            p1_g,
                            p2_g
                        )

                        pts_acc += pts_g

                evol_list.append(
                    {
                        "N_Partido": int(id_p),
                        "Jugador": str(user),
                        "Puntos": pts_acc
                    }
                )

        if not evol_list:
            evol_html = evol_html_inicio
            evol_html += '<div class="evol-empty">Todavía no hay datos suficientes para mostrar la evolución.</div>'
            evol_html += '</div>'

            st.markdown(evol_html, unsafe_allow_html=True)
            return

        df_ev = pd.DataFrame(evol_list)

        usuario_actual = str(usuario_actual)

        top5_usuarios = (
            df_ranking
            .head(5)["USUARIO"]
            .astype(str)
            .tolist()
            if df_ranking is not None
            and not df_ranking.empty
            and "USUARIO" in df_ranking.columns
            else []
        )

        usuarios_grafico = []

        for u in top5_usuarios:
            if u not in usuarios_grafico:
                usuarios_grafico.append(u)

        if usuario_actual not in usuarios_grafico:
            usuarios_grafico.append(usuario_actual)

        def nombre_visible_usuario(usuario):
            usuario = str(usuario)

            if (
                df_ranking is not None
                and not df_ranking.empty
                and "USUARIO" in df_ranking.columns
            ):
                match_rank = df_ranking[
                    df_ranking["USUARIO"].astype(str) == usuario
                ]
            else:
                match_rank = pd.DataFrame()

            if not match_rank.empty:
                return str(match_rank.iloc[0].get("JUGADOR", usuario))

            match_user = df_usuarios[
                df_usuarios["USUARIO"].astype(str) == usuario
            ]

            if not match_user.empty:
                return str(match_user.iloc[0].get("NOMBRE", usuario))

            return usuario

        nombre_map = {
            u: nombre_visible_usuario(u)
            for u in usuarios_grafico
        }

        df_ev_plot = df_ev[
            df_ev["Jugador"].astype(str).isin(usuarios_grafico)
        ].copy()

        df_ev_plot["Refe"] = (
            df_ev_plot["Jugador"]
            .astype(str)
            .map(nombre_map)
        )

        df_user_ev = (
            df_ev[df_ev["Jugador"].astype(str) == usuario_actual]
            .sort_values("N_Partido")
        )

        if not df_user_ev.empty:
            puntos_actuales = int(df_user_ev["Puntos"].iloc[-1])

            if len(df_user_ev) >= 5:
                puntos_previos = int(df_user_ev["Puntos"].iloc[-5])
                variacion_reciente = puntos_actuales - puntos_previos
            else:
                puntos_previos = int(df_user_ev["Puntos"].iloc[0])
                variacion_reciente = puntos_actuales - puntos_previos
        else:
            puntos_actuales = 0
            variacion_reciente = 0

        try:
            row_user_rank = df_ranking[
                df_ranking["USUARIO"].astype(str) == usuario_actual
            ]

            posicion_actual = int(row_user_rank.index[0])
        except Exception:
            posicion_actual = "-"

        usuario_safe = escape(str(usuario_actual))
        signo_tendencia = "+" if variacion_reciente >= 0 else ""

        evol_header_html = evol_html_inicio
        evol_header_html += (
            f'<div class="evol-summary-dark">'
            f'<div class="evol-user-name">{usuario_safe}</div>'
            f'<div class="evol-main-row">'
            f'<div class="evol-main-number">{puntos_actuales}<span>pts</span></div>'
            f'<div class="evol-position-pill">{posicion_actual}° puesto</div>'
            f'</div>'
            f'<div class="evol-meta">Última tendencia: <strong>{signo_tendencia}{variacion_reciente} pts</strong></div>'
            f'</div>'
            f'<div class="evol-chart-shell">'
        )

        paleta_top5 = [
            "#93C5FD",
            "#A7F3D0",
            "#C4B5FD",
            "#FCA5A5",
            "#FDBA74",
        ]

        color_map = {}

        for idx, usuario in enumerate(usuarios_grafico):
            nombre_label = nombre_map.get(usuario, usuario)

            if usuario == usuario_actual:
                color_map[nombre_label] = "#F4C542"
            else:
                color_map[nombre_label] = paleta_top5[
                    idx % len(paleta_top5)
                ]

        orden_labels = [
            nombre_map.get(u, u)
            for u in usuarios_grafico
        ]

        fig = px.line(
            df_ev_plot,
            x="N_Partido",
            y="Puntos",
            color="Refe",
            markers=True,
            color_discrete_map=color_map,
            category_orders={
                "Refe": orden_labels
            }
        )

        fig.update_layout(
            height=255,
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font=dict(
                family="Inter, sans-serif",
                size=11,
                color="#64748b"
            ),
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.04,
                xanchor="left",
                x=0,
                font=dict(
                    size=10,
                    color="#475569"
                ),
                bgcolor="rgba(255,255,255,0.72)",
                bordercolor="rgba(226,232,240,0.90)",
                borderwidth=1
            ),
            margin=dict(
                l=38,
                r=14,
                t=42,
                b=24
            ),
            showlegend=True,
            hovermode=False,
            dragmode=False
        )

        fig.update_xaxes(
            title_text="",
            showgrid=False,
            showline=False,
            zeroline=False,
            tickmode="linear",
            dtick=1,
            fixedrange=True,
            color="#94a3b8",
            tickfont=dict(size=10)
        )

        fig.update_yaxes(
            title_text="",
            gridcolor="rgba(148,163,184,0.18)",
            showline=False,
            zeroline=False,
            fixedrange=True,
            color="#94a3b8",
            tickfont=dict(size=10)
        )

        usuario_actual_label = nombre_map.get(usuario_actual, usuario_actual)

        for trace in fig.data:
            if trace.name == usuario_actual_label:
                trace.update(
                    line=dict(
                        width=5,
                        color="#F4C542"
                    ),
                    marker=dict(
                        size=8,
                        color="#F4C542",
                        line=dict(
                            width=2,
                            color="white"
                        )
                    ),
                    opacity=1,
                    hoverinfo="skip",
                    hovertemplate=None
                )
            else:
                trace.update(
                    line=dict(
                        width=2.4
                    ),
                    marker=dict(
                        size=5,
                        line=dict(
                            width=1,
                            color="white"
                        )
                    ),
                    opacity=0.72,
                    hoverinfo="skip",
                    hovertemplate=None
                )

        plot_html = fig.to_html(
            full_html=False,
            include_plotlyjs="cdn",
            config={
                "displayModeBar": False,
                "staticPlot": True,
                "scrollZoom": False,
                "responsive": True
            }
        )

        evol_component_css = f"""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@500;600;700;800;900&family=Montserrat:wght@800;900&display=swap');

        body {{
            margin: 0;
            padding: 0;
            font-family: Inter, Montserrat, sans-serif;
            background: transparent;
        }}

        .evol-panel {{
            background: rgba(255, 255, 255, 0.94);
            border: 1px solid rgba(226, 232, 240, 0.9);
            border-radius: 18px;
            padding: 14px;
            box-shadow: 0 12px 30px rgba(15, 23, 42, 0.06);
            overflow: hidden;
        }}

        .evol-panel-header {{
            display: flex;
            align-items: center;
            gap: 10px;
            padding: 4px 4px 14px 4px;
            margin-bottom: 8px;
            border-bottom: 1px solid rgba(226, 232, 240, 0.75);
        }}

        .evol-panel-icon {{
            width: 30px;
            height: 30px;
            border-radius: 10px;
            display: flex;
            align-items: center;
            justify-content: center;
            background: rgba(244, 197, 66, 0.16);
            color: #0f172a;
            font-size: 16px;
        }}

        .evol-panel-title {{
            font-family: Montserrat, Inter, sans-serif;
            font-size: 17px;
            font-weight: 900;
            color: #0f172a;
            text-transform: uppercase;
            letter-spacing: 0.01em;
        }}

        .evol-empty {{
            height: 315px;
            display: flex;
            align-items: center;
            justify-content: center;
            text-align: center;
            color: #94a3b8;
            font-family: Inter, sans-serif;
            font-size: 13px;
            font-weight: 800;
        }}

        .evol-summary-dark {{
            background-image:
                linear-gradient(
                    90deg,
                    rgba(7,17,31,0.98) 0%,
                    rgba(7,17,31,0.86) 48%,
                    rgba(7,17,31,0.50) 100%
                ),
                url("{EVOL_HEADER_BACKGROUND}");
            background-size: cover;
            background-position: center right;
            border: 1px solid rgba(255,255,255,0.08);
            border-radius: 15px 15px 0 0;
            padding: 16px 18px 13px 18px;
        }}

        .evol-user-name {{
            font-size: 11px;
            font-weight: 900;
            color: rgba(255,255,255,0.58);
            text-transform: uppercase;
            letter-spacing: 0.07em;
            margin-bottom: 6px;
        }}

        .evol-main-row {{
            display: flex;
            justify-content: space-between;
            align-items: flex-end;
            gap: 14px;
        }}

        .evol-main-number {{
            font-family: Montserrat, Inter, sans-serif;
            font-size: 36px;
            font-weight: 900;
            color: #F8FAFC;
            line-height: 1;
        }}

        .evol-main-number span {{
            font-size: 14px;
            color: rgba(255,255,255,0.55);
            font-weight: 800;
            margin-left: 4px;
        }}

        .evol-position-pill {{
            background: rgba(244,197,66,0.14);
            border: 1px solid rgba(244,197,66,0.35);
            color: #F4C542;
            border-radius: 999px;
            padding: 6px 10px;
            font-size: 11px;
            font-weight: 900;
            white-space: nowrap;
        }}

        .evol-meta {{
            margin-top: 10px;
            font-size: 12px;
            font-weight: 700;
            color: rgba(255,255,255,0.65);
        }}

        .evol-meta strong {{
            color: #F4C542;
        }}

        .evol-chart-shell {{
            background: rgba(248, 250, 252, 0.96);
            border: 1px solid rgba(226, 232, 240, 0.9);
            border-top: none;
            border-radius: 0 0 15px 15px;
            padding: 0 8px 4px 8px;
        }}

        @media (max-width: 768px) {{
            .evol-panel {{
                padding: 12px;
                border-radius: 16px;
            }}

            .evol-panel-title {{
                font-size: 15px;
            }}

            .evol-main-number {{
                font-size: 30px;
            }}
        }}
        </style>
        """

        evol_full_html = (
            evol_component_css
            + evol_header_html
            + plot_html
            + "</div></div>"
        )

        components.html(
            evol_full_html,
            height=495,
            scrolling=False
        )
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
    FONDO_CARD_INICIO = "https://storage.googleapis.com/foto-prode2026/Banners/FONDO_CARD_INICIO.png"

    df_user_pro = df_pro[df_pro["USUARIO"] == user_actual]

    ahora_arg = datetime.utcnow() - timedelta(hours=3)
    
    # ============================================================
    # CONFIGURACIÓN DE CIERRE DE PRONÓSTICOS
    # Se controla desde Supabase / Panel de Control.
    # ============================================================
    
    def parse_fecha_cierre(valor):
        """
        Convierte el texto guardado en config a datetime.
        Formatos aceptados:
        - 2026-06-11 15:00
        - 2026-06-11 15:00:00
        - 11/06/2026 15:00
        """
    
        valor = str(valor).strip()
    
        formatos = [
            "%Y-%m-%d %H:%M",
            "%Y-%m-%d %H:%M:%S",
            "%d/%m/%Y %H:%M",
            "%d/%m/%Y %H:%M:%S",
        ]
    
        for formato in formatos:
            try:
                return datetime.strptime(valor, formato)
            except Exception:
                pass
    
        # Fallback seguro si la fecha está mal escrita.
        return datetime(2026, 6, 11, 15, 0, 0)
    
    
    try:
        df_config_pronosticos = get_config_app()
    
        estado_pronosticos = (
            str(df_config_pronosticos.iloc[0].get("PRONOSTICOS_ESTADO", "ON"))
            .strip()
            .upper()
        )
    
        cierre_pronosticos_txt = (
            str(df_config_pronosticos.iloc[0].get("CIERRE_PRONOSTICOS", "2026-06-11 15:00"))
            .strip()
        )
    
    except Exception:
        estado_pronosticos = "ON"
        cierre_pronosticos_txt = "2026-06-11 15:00"
    
    fecha_limite = parse_fecha_cierre(cierre_pronosticos_txt)
    
    fecha_limite_visible = fecha_limite.strftime("%d/%m/%Y %H:%M")
    
    es_tiempo_valido = (
        estado_pronosticos == "ON"
        and ahora_arg < fecha_limite
    )

    # ============================================================
    # TÍTULO DE PÁGINA
    # ============================================================

    st.markdown("""
<div class="page-section-title">
    <h1>Mi Prode</h1>
    <p>Tu tablero personal: perfil, predicciones y estado en el juego.</p>
</div>
""", unsafe_allow_html=True)

    c_pron, c_perfil = st.columns([1.35, 1], gap="large")

    # ============================================================
    # COLUMNA IZQUIERDA — MIS PRONÓSTICOS
    # ============================================================

    with c_pron:

        modo_edicion = st.session_state.permitir_edicion

        if not es_tiempo_valido:
            if estado_pronosticos != "ON":
                estado_txt = "Carga cerrada por administración · modo lectura"
            else:
                estado_txt = f"Plazo finalizado el {fecha_limite_visible} · modo lectura"
        
            estado_class = "locked"
            modo_edicion = False
            st.session_state.permitir_edicion = False
        
        else:
            estado_txt = f"Edición abierta hasta el {fecha_limite_visible}"
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

        # ------------------------------------------------------------
        # SELECTOR DE FECHA / TANDA DE CARGA
        # ------------------------------------------------------------

        tanda_seleccionada = st.radio(
            "Fecha de fase de grupos",
            [
                "Fecha 1",
                "Fecha 2",
                "Fecha 3"
            ],
            horizontal=True,
            key="tanda_pronosticos_mi_prode",
            label_visibility="collapsed"
        )

        fecha_num = int(
            tanda_seleccionada.replace("Fecha ", "")
        )

        # ------------------------------------------------------------
        # FILTRO DE PARTIDOS POR FECHA
        # ------------------------------------------------------------

        df_res_tanda = df_res.copy()

        if "FECHA" not in df_res_tanda.columns:
            st.error("No se encontró la columna FECHA en la hoja RESULTADOS.")
            st.stop()

        df_res_tanda["FECHA_NUM"] = pd.to_numeric(
            df_res_tanda["FECHA"],
            errors="coerce"
        )

        df_res_tanda = df_res_tanda[
            df_res_tanda["FECHA_NUM"] == fecha_num
        ].copy()

        df_res_tanda["N_PARTIDO"] = pd.to_numeric(
            df_res_tanda["N_PARTIDO"],
            errors="coerce"
        )

        df_res_tanda = df_res_tanda.dropna(
            subset=["N_PARTIDO"]
        ).copy()

        df_res_tanda["N_PARTIDO"] = df_res_tanda["N_PARTIDO"].astype(int)

        fecha_key = f"fecha_{fecha_num}"


        # ============================================================
        # PREPARACIÓN DE DATOS COMÚN
        # ============================================================

        lista_pronosticos_actuales = []
        filas_editor = []

        for _, row in df_res_tanda.sort_values("N_PARTIDO").iterrows():
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

            cards_html = '<div class="pred-scroll">'

            for _, row in df_res_tanda.sort_values("N_PARTIDO").iterrows():
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

                cards_html += f"""
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
"""

            cards_html += '</div>'

            st.markdown(cards_html, unsafe_allow_html=True)

            if es_tiempo_valido:
                if st.button(
                    f"✏️ Editar pronósticos de {tanda_seleccionada}",
                    use_container_width=True
                ):
                    st.session_state.permitir_edicion = True
                    st.rerun()
            else:
                st.warning(
                    f"⛔ La carga de pronósticos está cerrada. "
                    f"Podés ver tus pronósticos, pero ya no editarlos."
                )
            
                st.button(
                    "🔒 Edición de pronósticos bloqueada",
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

            with st.form(
                key=f"form_pronosticos_editor_{fecha_key}_{st.session_state.pron_editor_version}",
                clear_on_submit=False
            ):

                edited_df = st.data_editor(
                    df_editor,
                    hide_index=True,
                    use_container_width=True,
                    key=f"pronosticos_editor_{fecha_key}_{st.session_state.pron_editor_version}",
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
                    cancelar = st.form_submit_button(
                        "❌ Cancelar",
                        use_container_width=True
                    )

                with c_guardar:
                    guardar = st.form_submit_button(
                        f"💾 Guardar cambios de {tanda_seleccionada}",
                        use_container_width=True
                    )

            # ------------------------------------------------------------
            # ACCIONES DEL FORMULARIO
            # ------------------------------------------------------------

            if cancelar:
                st.session_state.permitir_edicion = False
                st.session_state.pron_editor_version += 1
                st.rerun()

            if guardar:
                try:
                    # Segunda validación de seguridad:
                    # evita guardar si el cierre ocurrió mientras el formulario estaba abierto.
                    ahora_arg_guardar = datetime.utcnow() - timedelta(hours=3)
            
                    if estado_pronosticos != "ON" or ahora_arg_guardar >= fecha_limite:
                        st.session_state.permitir_edicion = False
                        st.session_state.pron_editor_version += 1
            
                        st.error(
                            "⛔ La carga de pronósticos ya está cerrada. "
                            "No se guardaron los cambios."
                        )
            
                        st.rerun()
            
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
                    ].copy()

                    ok, msg = guardar_pronosticos_supabase(nuevos_pro)

                    if ok:
                        st.cache_data.clear()
                        st.session_state.permitir_edicion = False
                        st.session_state.pron_editor_version += 1

                        st.success("✅ ¡Pronósticos guardados correctamente!")
                        st.balloons()
                        st.rerun()

                    else:
                        st.error(msg)

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
<div class="profile-user">@{usuario} ({edad} años) · {equipo}</div>

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

<div class="profile-hero-bio">
<span class="profile-hero-bio-label">
<span class="profile-hero-bio-icon">💬</span>
Bio:
</span>
{bio}
</div>

</div>

</div>
""",
                unsafe_allow_html=True
            )

            if st.button("✏️ Editar Perfil", use_container_width=True):
                st.session_state.editando_perfil = True
                st.rerun()

            # ------------------------------------------------------------
            # MI EVOLUCIÓN — MISMO COMPONENTE QUE INICIO
            # ------------------------------------------------------------

            render_evolucion_puntos_premium(user_actual)

        else:
            st.markdown("""
<div class="profile-panel">
<div class="panel-header">
    <div class="panel-icon">✏️</div>
    <div class="panel-title">Editar Perfil</div>
</div>
<div class="profile-edit-box">
""", unsafe_allow_html=True)

            nombre_actual_form = str(u_data.get("NOMBRE", ""))
            equipo_actual_form = str(u_data.get("EQUIPO FAVORITO", ""))
            edad_actual_form = u_data.get("EDAD", 0)
            descripcion_actual_form = str(u_data.get("DESCRIPCION", ""))
            avatar_actual_form = str(u_data.get("AVATAR_URL", ""))

            try:
                edad_actual_form = int(float(edad_actual_form))
            except Exception:
                edad_actual_form = 0

            with st.form("form_editar_perfil", clear_on_submit=False):

                nuevo_nombre = st.text_input(
                    "Nombre",
                    value=nombre_actual_form
                )

                nuevo_equipo = st.selectbox(
                    "Equipo favorito",
                    [
                        "Argentina",
                        "Brasil",
                        "Uruguay",
                        "México",
                        "España",
                        "Francia",
                        "Alemania",
                        "Italia",
                        "Inglaterra",
                        "Portugal",
                        "Otro"
                    ],
                    index=(
                        [
                            "Argentina",
                            "Brasil",
                            "Uruguay",
                            "México",
                            "España",
                            "Francia",
                            "Alemania",
                            "Italia",
                            "Inglaterra",
                            "Portugal",
                            "Otro"
                        ].index(equipo_actual_form)
                        if equipo_actual_form in [
                            "Argentina",
                            "Brasil",
                            "Uruguay",
                            "México",
                            "España",
                            "Francia",
                            "Alemania",
                            "Italia",
                            "Inglaterra",
                            "Portugal",
                            "Otro"
                        ]
                        else 0
                    )
                )

                nueva_edad = st.number_input(
                    "Edad",
                    min_value=0,
                    max_value=120,
                    value=edad_actual_form,
                    step=1
                )

                nueva_descripcion = st.text_area(
                    "Bio / descripción",
                    value=(
                        "" 
                        if descripcion_actual_form.lower() == "nan" 
                        else descripcion_actual_form
                    ),
                    max_chars=240
                )

                nueva_foto_file = st.file_uploader(
                    "Cambiar foto de perfil",
                    type=["jpg", "jpeg", "png", "webp"]
                )

                c_cancelar_perfil, c_guardar_perfil = st.columns([0.35, 0.65])

                with c_cancelar_perfil:
                    cancelar_perfil = st.form_submit_button(
                        "❌ Cancelar",
                        use_container_width=True
                    )

                with c_guardar_perfil:
                    guardar_perfil = st.form_submit_button(
                        "💾 Guardar perfil",
                        use_container_width=True
                    )

            if cancelar_perfil:
                st.session_state.editando_perfil = False
                st.rerun()

            if guardar_perfil:
                try:
                    if not nuevo_nombre.strip():
                        st.error("El nombre no puede quedar vacío.")
                        st.stop()

                    nueva_foto_url = avatar_actual_form

                    if nueva_foto_file is not None:
                        nueva_foto_url = upload_profile_picture(
                            nueva_foto_file,
                            user_actual
                        )

                        if str(nueva_foto_url).startswith("Error:"):
                            st.error(nueva_foto_url)
                            st.stop()

                    datos_update = {
                        "NOMBRE": nuevo_nombre.strip(),
                        "EQUIPO FAVORITO": nuevo_equipo,
                        "EDAD": int(nueva_edad),
                        "DESCRIPCION": nueva_descripcion.strip(),
                        "AVATAR_URL": nueva_foto_url
                    }

                    ok, msg = actualizar_usuario_supabase(
                        usuario=user_actual,
                        datos=datos_update
                    )

                    if ok:
                        st.cache_data.clear()

                        st.session_state["user_data"]["NOMBRE"] = nuevo_nombre.strip()
                        st.session_state["user_data"]["EQUIPO FAVORITO"] = nuevo_equipo
                        st.session_state["user_data"]["EDAD"] = int(nueva_edad)
                        st.session_state["user_data"]["DESCRIPCION"] = nueva_descripcion.strip()
                        st.session_state["user_data"]["AVATAR_URL"] = nueva_foto_url

                        st.session_state.editando_perfil = False

                        st.success("✅ Perfil actualizado correctamente.")
                        st.rerun()

                    else:
                        st.error(msg)

                except Exception as e:
                    st.error(f"Error al actualizar perfil: {e}")

            st.markdown("""
</div>
</div>
""", unsafe_allow_html=True)
