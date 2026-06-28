import re
from html import escape

import pandas as pd
import streamlit as st

from ranking_logic import calcular_detalle_eliminatoria, obtener_ranking_eliminatoria
from services.supabase_service import (
    get_eliminatoria_app,
    get_pronosticos_eliminatoria_app,
    get_usuarios_app,
)
from styles_config import (
    FONDO_CARD_BRONCE,
    FONDO_CARD_GOLD,
    FONDO_CARD_INICIO,
    FONDO_CARD_SILVER,
    HEADER_BACKGROUND,
)


MOCK_ELIMINATORIA = [
    {"partido": 1, "slot": 3, "equipo_1": "Equipo 1", "equipo_2": "Equipo 2", "fase": "16avos", "dia": "28/06/26", "hora": "16:00", "origen_1": None, "origen_2": None, "sig": 18, "lado": "Equipo 1", "llave": "A"},
    {"partido": 2, "slot": 1, "equipo_1": "Equipo 1", "equipo_2": "Equipo 2", "fase": "16avos", "dia": "29/06/26", "hora": "17:30", "origen_1": None, "origen_2": None, "sig": 17, "lado": "Equipo 1", "llave": "A"},
    {"partido": 3, "slot": 4, "equipo_1": "Equipo 1", "equipo_2": "Equipo 2", "fase": "16avos", "dia": "29/06/26", "hora": "22:00", "origen_1": None, "origen_2": None, "sig": 18, "lado": "Equipo 2", "llave": "A"},
    {"partido": 4, "slot": 1, "equipo_1": "Equipo 1", "equipo_2": "Equipo 2", "fase": "16avos", "dia": "29/06/26", "hora": "14:00", "origen_1": None, "origen_2": None, "sig": 19, "lado": "Equipo 1", "llave": "B"},
    {"partido": 5, "slot": 2, "equipo_1": "Equipo 1", "equipo_2": "Equipo 2", "fase": "16avos", "dia": "30/06/26", "hora": "18:00", "origen_1": None, "origen_2": None, "sig": 17, "lado": "Equipo 2", "llave": "A"},
    {"partido": 6, "slot": 2, "equipo_1": "Equipo 1", "equipo_2": "Equipo 2", "fase": "16avos", "dia": "30/06/26", "hora": "14:00", "origen_1": None, "origen_2": None, "sig": 19, "lado": "Equipo 2", "llave": "B"},
    {"partido": 7, "slot": 3, "equipo_1": "Equipo 1", "equipo_2": "Equipo 2", "fase": "16avos", "dia": "30/06/26", "hora": "22:00", "origen_1": None, "origen_2": None, "sig": 20, "lado": "Equipo 1", "llave": "B"},
    {"partido": 8, "slot": 4, "equipo_1": "Equipo 1", "equipo_2": "Equipo 2", "fase": "16avos", "dia": "01/07/26", "hora": "13:00", "origen_1": None, "origen_2": None, "sig": 20, "lado": "Equipo 2", "llave": "B"},
    {"partido": 9, "slot": 7, "equipo_1": "Equipo 1", "equipo_2": "Equipo 2", "fase": "16avos", "dia": "01/07/26", "hora": "21:00", "origen_1": None, "origen_2": None, "sig": 22, "lado": "Equipo 1", "llave": "A"},
    {"partido": 10, "slot": 8, "equipo_1": "Equipo 1", "equipo_2": "Equipo 2", "fase": "16avos", "dia": "01/07/26", "hora": "17:00", "origen_1": None, "origen_2": None, "sig": 22, "lado": "Equipo 2", "llave": "A"},
    {"partido": 11, "slot": 5, "equipo_1": "Equipo 1", "equipo_2": "Equipo 2", "fase": "16avos", "dia": "02/07/26", "hora": "20:00", "origen_1": None, "origen_2": None, "sig": 21, "lado": "Equipo 1", "llave": "A"},
    {"partido": 12, "slot": 6, "equipo_1": "Equipo 1", "equipo_2": "Equipo 2", "fase": "16avos", "dia": "02/07/26", "hora": "16:00", "origen_1": None, "origen_2": None, "sig": 21, "lado": "Equipo 2", "llave": "A"},
    {"partido": 13, "slot": 7, "equipo_1": "Equipo 1", "equipo_2": "Equipo 2", "fase": "16avos", "dia": "03/07/26", "hora": "00:00", "origen_1": None, "origen_2": None, "sig": 24, "lado": "Equipo 1", "llave": "B"},
    {"partido": 14, "slot": 5, "equipo_1": "Equipo 1", "equipo_2": "Equipo 2", "fase": "16avos", "dia": "03/07/26", "hora": "19:00", "origen_1": None, "origen_2": None, "sig": 23, "lado": "Equipo 1", "llave": "B"},
    {"partido": 15, "slot": 8, "equipo_1": "Equipo 1", "equipo_2": "Equipo 2", "fase": "16avos", "dia": "03/07/26", "hora": "22:30", "origen_1": None, "origen_2": None, "sig": 24, "lado": "Equipo 2", "llave": "B"},
    {"partido": 16, "slot": 6, "equipo_1": "Equipo 1", "equipo_2": "Equipo 2", "fase": "16avos", "dia": "03/07/26", "hora": "15:00", "origen_1": None, "origen_2": None, "sig": 23, "lado": "Equipo 2", "llave": "B"},
    {"partido": 17, "slot": 1, "equipo_1": "Ganador 2", "equipo_2": "Ganador 5", "fase": "Octavos", "dia": "04/07/26", "hora": "18:00", "origen_1": 2, "origen_2": 5, "sig": 25, "lado": "Equipo 1", "llave": "A"},
    {"partido": 18, "slot": 2, "equipo_1": "Ganador 1", "equipo_2": "Ganador 3", "fase": "Octavos", "dia": "04/07/26", "hora": "14:00", "origen_1": 1, "origen_2": 3, "sig": 25, "lado": "Equipo 2", "llave": "A"},
    {"partido": 19, "slot": 1, "equipo_1": "Ganador 4", "equipo_2": "Ganador 6", "fase": "Octavos", "dia": "05/07/26", "hora": "17:00", "origen_1": 4, "origen_2": 6, "sig": 27, "lado": "Equipo 1", "llave": "B"},
    {"partido": 20, "slot": 2, "equipo_1": "Ganador 7", "equipo_2": "Ganador 8", "fase": "Octavos", "dia": "05/07/26", "hora": "21:00", "origen_1": 7, "origen_2": 8, "sig": 27, "lado": "Equipo 2", "llave": "B"},
    {"partido": 21, "slot": 3, "equipo_1": "Ganador 11", "equipo_2": "Ganador 12", "fase": "Octavos", "dia": "06/07/26", "hora": "16:00", "origen_1": 11, "origen_2": 12, "sig": 26, "lado": "Equipo 1", "llave": "A"},
    {"partido": 22, "slot": 4, "equipo_1": "Ganador 9", "equipo_2": "Ganador 10", "fase": "Octavos", "dia": "06/07/26", "hora": "21:00", "origen_1": 9, "origen_2": 10, "sig": 26, "lado": "Equipo 2", "llave": "A"},
    {"partido": 23, "slot": 3, "equipo_1": "Ganador 14", "equipo_2": "Ganador 16", "fase": "Octavos", "dia": "07/07/26", "hora": "13:00", "origen_1": 14, "origen_2": 16, "sig": 28, "lado": "Equipo 1", "llave": "B"},
    {"partido": 24, "slot": 4, "equipo_1": "Ganador 13", "equipo_2": "Ganador 15", "fase": "Octavos", "dia": "07/07/26", "hora": "17:00", "origen_1": 13, "origen_2": 15, "sig": 28, "lado": "Equipo 2", "llave": "B"},
    {"partido": 25, "slot": 1, "equipo_1": "Ganador 17", "equipo_2": "Ganador 18", "fase": "Cuartos", "dia": "09/07/26", "hora": "17:00", "origen_1": 17, "origen_2": 18, "sig": 29, "lado": "Equipo 1", "llave": "A"},
    {"partido": 26, "slot": 2, "equipo_1": "Ganador 21", "equipo_2": "Ganador 22", "fase": "Cuartos", "dia": "10/07/26", "hora": "16:00", "origen_1": 21, "origen_2": 22, "sig": 29, "lado": "Equipo 2", "llave": "A"},
    {"partido": 27, "slot": 1, "equipo_1": "Ganador 19", "equipo_2": "Ganador 20", "fase": "Cuartos", "dia": "11/07/26", "hora": "18:00", "origen_1": 19, "origen_2": 20, "sig": 30, "lado": "Equipo 1", "llave": "B"},
    {"partido": 28, "slot": 2, "equipo_1": "Ganador 23", "equipo_2": "Ganador 24", "fase": "Cuartos", "dia": "11/07/26", "hora": "22:00", "origen_1": 23, "origen_2": 24, "sig": 30, "lado": "Equipo 2", "llave": "B"},
    {"partido": 29, "slot": 1, "equipo_1": "Ganador 25", "equipo_2": "Ganador 26", "fase": "Semifinal", "dia": "14/07/26", "hora": "16:00", "origen_1": 25, "origen_2": 26, "sig": 31, "lado": "Equipo 1", "llave": "Semis"},
    {"partido": 30, "slot": 1, "equipo_1": "Ganador 27", "equipo_2": "Ganador 28", "fase": "Semifinal", "dia": "15/07/26", "hora": "16:00", "origen_1": 27, "origen_2": 28, "sig": 31, "lado": "Equipo 2", "llave": "Semis"},
    {"partido": 31, "slot": 1, "equipo_1": "Ganador 29", "equipo_2": "Ganador 30", "fase": "Final", "dia": "19/07/26", "hora": "16:00", "origen_1": 29, "origen_2": 30, "sig": None, "lado": None, "llave": "Final"},
    {"partido": 32, "slot": 1, "equipo_1": "Perdedor 29", "equipo_2": "Perdedor 30", "fase": "Tercer Puesto", "dia": "18/07/26", "hora": "18:00", "origen_1": 29, "origen_2": 30, "sig": None, "lado": None, "llave": "Final"},
]


def _render_css():
    st.markdown(
        """
<style>
.inicio-v2-hero {
    position: relative;
    overflow: hidden;
    border-radius: 22px;
    min-height: 360px;
    padding: 18px 30px 20px;
    margin: 0 auto 22px;
    background:
        linear-gradient(180deg, rgba(3,7,18,0.72), rgba(3,7,18,0.88)),
        url("__HERO_BACKGROUND__");
    background-size: cover;
    background-position: center;
    border: 1px solid rgba(244,197,66,0.22);
    box-shadow:
        0 22px 46px rgba(15,23,42,0.18),
        inset 0 1px 0 rgba(255,255,255,0.12);
}

.inicio-v2-hero::before {
    content: "";
    position: absolute;
    inset: 0;
    background:
        radial-gradient(circle at 14% 78%, rgba(244,197,66,0.16), transparent 30%),
        linear-gradient(90deg, rgba(2,6,23,0.26), transparent 42%, rgba(2,6,23,0.18));
    pointer-events: none;
}

.inicio-v2-hero > * {
    position: relative;
    z-index: 1;
}

.inicio-v2-kicker {
    margin-top: 6px;
    color: rgba(248,250,252,0.72);
    font-size: 12px;
    font-weight: 950;
    letter-spacing: 0.22em;
    text-transform: uppercase;
    text-align: center;
}

.inicio-v2-title {
    margin: 0;
    color: #FFFFFF !important;
    font-family: 'Montserrat', sans-serif;
    font-size: 40px;
    line-height: 1.05;
    font-weight: 950;
    letter-spacing: 0.06em;
    text-align: center;
    text-transform: uppercase;
    text-shadow:
        0 3px 12px rgba(0,0,0,0.72),
        0 0 16px rgba(255,255,255,0.14);
}

.inicio-v2-title-icon {
    margin-right: 12px;
    color: #F4C542;
}

.inicio-v2-stage {
    display: grid;
    grid-template-columns: 210px minmax(0, 1fr);
    gap: 16px;
    align-items: stretch;
    max-width: 970px;
    margin: 16px auto 0;
}

.ko-user-hero-card {
    min-height: 260px;
    padding: 14px 14px;
    border-radius: 18px;
    background: linear-gradient(180deg, rgba(15,23,42,0.80), rgba(15,23,42,0.56));
    border: 1px solid rgba(244,197,66,0.24);
    box-shadow:
        0 14px 30px rgba(0,0,0,0.24),
        inset 0 1px 0 rgba(255,255,255,0.10);
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    text-align: center;
}

.ko-user-avatar {
    width: 82px;
    height: 82px;
    border-radius: 999px;
    object-fit: cover;
    border: 5px solid #F4C542;
    box-shadow:
        0 12px 26px rgba(0,0,0,0.34),
        0 0 18px rgba(244,197,66,0.22);
}

.ko-user-avatar-placeholder {
    width: 82px;
    height: 82px;
    border-radius: 999px;
    display: grid;
    place-items: center;
    background: linear-gradient(135deg, #F4C542, #F59E0B);
    color: #07111F;
    border: 5px solid #F4C542;
    font-family: 'Montserrat', sans-serif;
    font-size: 34px;
    font-weight: 950;
}

.ko-user-name {
    margin-top: 10px;
    color: #ffffff;
    font-family: 'Montserrat', sans-serif;
    font-size: 24px;
    font-weight: 950;
    line-height: 1.05;
}

.ko-user-handle {
    margin-top: 5px;
    color: rgba(226,232,240,0.82);
    font-size: 11px;
    font-weight: 850;
}

.ko-user-position-label {
    margin-top: 14px;
    color: rgba(226,232,240,0.60);
    font-size: 10px;
    font-weight: 950;
    letter-spacing: 0.08em;
    text-transform: uppercase;
}

.ko-user-position {
    margin-top: 2px;
    color: #ffffff;
    font-family: 'Montserrat', sans-serif;
    font-size: 42px;
    line-height: 1;
    font-weight: 950;
}

.ko-user-points-pill {
    margin-top: 9px;
    padding: 7px 13px;
    border-radius: 999px;
    background: rgba(15,23,42,0.76);
    border: 1px solid rgba(244,197,66,0.36);
    color: #F4C542;
    font-family: 'Montserrat', sans-serif;
    font-size: 13px;
    font-weight: 950;
}

.ko-user-gap {
    margin-top: 9px;
    color: rgba(226,232,240,0.78);
    font-size: 11px;
    font-weight: 850;
}

.ko-ranking-panel {
    position: relative;
    overflow: hidden;
    margin: 0;
    padding: 15px;
    border-radius: 18px;
    background: transparent;
    border: 1px solid rgba(255,255,255,0.16);
    box-shadow:
        0 14px 32px rgba(0,0,0,0.12),
        inset 0 1px 0 rgba(255,255,255,0.08);
}

.ko-ranking-header {
    display: flex;
    align-items: center;
    gap: 11px;
    padding: 4px 4px 13px;
    margin-bottom: 10px;
    border-bottom: 1px solid rgba(255,255,255,0.16);
}

.ko-ranking-icon {
    width: 34px;
    height: 34px;
    border-radius: 12px;
    display: grid;
    place-items: center;
    background:
        linear-gradient(180deg, rgba(255,255,255,0.92), rgba(241,245,249,0.80));
    border: 1px solid rgba(148,163,184,0.34);
    box-shadow:
        inset 0 1px 0 rgba(255,255,255,0.78),
        0 6px 14px rgba(15,23,42,0.06);
}

.ko-ranking-title {
    color: #FFFFFF;
    font-family: 'Montserrat', sans-serif;
    font-size: 18px;
    font-weight: 950;
    text-transform: uppercase;
}

.ko-ranking-subtitle {
    margin-top: 2px;
    color: rgba(226,232,240,0.78);
    font-size: 11px;
    font-weight: 850;
}

.ko-ranking-scroll {
    height: 218px;
    overflow-y: auto;
    overflow-x: hidden;
    padding-right: 7px;
    scrollbar-width: thin;
    scrollbar-color: #0F2D63 rgba(226,232,240,0.55);
}

.ko-ranking-row {
    position: relative;
    overflow: hidden;
    display: grid;
    grid-template-columns: 42px minmax(0, 1fr) 74px;
    align-items: center;
    gap: 11px;
    min-height: 61px;
    margin-bottom: 8px;
    padding: 10px 11px;
    border-radius: 16px;
    background:
        linear-gradient(180deg, rgba(255,255,255,0.72), rgba(248,250,252,0.60)),
        url("__FONDO_CARD_INICIO__");
    background-size: cover;
    border: 1px solid rgba(148,163,184,0.34);
    box-shadow:
        0 8px 18px rgba(15,23,42,0.055),
        inset 0 1px 0 rgba(255,255,255,0.78);
}

.ko-ranking-row.me {
    border-color: rgba(244,197,66,0.66);
    box-shadow:
        0 10px 22px rgba(244,197,66,0.12),
        inset 0 1px 0 rgba(255,255,255,0.84);
}

.ko-ranking-row.top-1 {
    background:
        linear-gradient(180deg, rgba(255,255,255,0.70), rgba(255,249,230,0.58)),
        url("__FONDO_CARD_GOLD__");
    background-size: cover;
    border-color: rgba(244,197,66,0.56);
}

.ko-ranking-row.top-2 {
    background:
        linear-gradient(180deg, rgba(255,255,255,0.72), rgba(241,245,249,0.60)),
        url("__FONDO_CARD_SILVER__");
    background-size: cover;
    border-color: rgba(148,163,184,0.52);
}

.ko-ranking-row.top-3 {
    background:
        linear-gradient(180deg, rgba(255,255,255,0.68), rgba(255,244,232,0.56)),
        url("__FONDO_CARD_BRONCE__");
    background-size: cover;
    border-color: rgba(205,127,50,0.48);
}

.ko-rank-pos {
    width: 34px;
    height: 34px;
    border-radius: 999px;
    display: grid;
    place-items: center;
    color: #0f172a;
    background: rgba(241,245,249,0.88);
    border: 1px solid rgba(148,163,184,0.24);
    font-family: 'Montserrat', sans-serif;
    font-size: 13px;
    font-weight: 950;
}

.ko-ranking-row.top-1 .ko-rank-pos {
    background: linear-gradient(135deg, #FFD700, #F4A900);
}

.ko-ranking-row.top-2 .ko-rank-pos {
    background: linear-gradient(135deg, #F8FAFC, #9CA3AF);
}

.ko-ranking-row.top-3 .ko-rank-pos {
    background: linear-gradient(135deg, #CD7F32, #9A5A22);
    color: #ffffff;
}

.ko-player-name {
    min-width: 0;
    color: #0f172a;
    font-family: 'Montserrat', sans-serif;
    font-size: 14px;
    font-weight: 950;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
}

.ko-player-sub {
    margin-top: 4px;
    color: #64748b;
    font-size: 10px;
    font-weight: 850;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
}

.ko-rank-points {
    text-align: right;
}

.ko-points-main {
    color: #07111F;
    font-family: 'Montserrat', sans-serif;
    font-size: 24px;
    line-height: 1;
    font-weight: 950;
}

.ko-points-label {
    margin-top: 2px;
    color: #94a3b8;
    font-size: 9px;
    font-weight: 950;
    text-transform: uppercase;
}

.ko-ranking-empty {
    padding: 18px;
    border-radius: 16px;
    background: rgba(255,255,255,0.70);
    color: #64748b;
    font-size: 12px;
    font-weight: 850;
    text-align: center;
    border: 1px solid rgba(203,213,225,0.72);
}

.inicio-v2-results-header {
    display: inline-flex;
    align-items: center;
    gap: 10px;
    margin: 4px 0 10px;
    padding: 8px 13px 8px 10px;
    border-radius: 13px;
    background: rgba(255,255,255,0.92);
    border: 1px solid rgba(203,213,225,0.70);
    box-shadow: 0 10px 22px rgba(15,23,42,0.06);
}

.inicio-v2-results-icon {
    width: 30px;
    height: 30px;
    border-radius: 11px;
    display: grid;
    place-items: center;
    background: linear-gradient(180deg, rgba(255,255,255,0.92), rgba(241,245,249,0.78));
    border: 1px solid rgba(148,163,184,0.34);
}

.inicio-v2-results-title {
    color: #07111F;
    font-family: 'Montserrat', sans-serif;
    font-size: 17px;
    font-weight: 950;
    text-transform: uppercase;
}

.bracket-stage-note {
    margin: 0 0 10px;
    color: #64748b;
    font-size: 12px;
    font-weight: 800;
}

.bracket-grid {
    display: grid;
    grid-template-columns: repeat(2, minmax(0, 1fr));
    gap: 14px;
}

.bracket-grid.single {
    grid-template-columns: minmax(0, 720px);
    justify-content: center;
}

.bracket-panel {
    border-radius: 17px;
    overflow: hidden;
    padding: 14px 12px 12px;
    background:
        linear-gradient(180deg, rgba(255,255,255,0.96), rgba(248,250,252,0.86));
    border: 1px solid rgba(148,163,184,0.34);
    box-shadow:
        0 12px 28px rgba(15,23,42,0.08),
        inset 0 1px 0 rgba(255,255,255,0.86);
}

.bracket-panel-header {
    display: flex;
    align-items: center;
    gap: 10px;
    padding: 0 0 10px;
    margin-bottom: 10px;
    border-bottom: 1px solid rgba(203,213,225,0.88);
    background: transparent;
}

.bracket-panel-icon {
    width: 30px;
    height: 30px;
    border-radius: 11px;
    display: grid;
    place-items: center;
    background:
        linear-gradient(180deg, rgba(255,255,255,0.92), rgba(241,245,249,0.78));
    border: 1px solid rgba(148,163,184,0.36);
    color: #0f172a;
    font-size: 10px;
    font-weight: 950;
    box-shadow: 0 5px 12px rgba(15,23,42,0.055);
}

.bracket-panel-title {
    color: #07111F;
    font-family: 'Montserrat', sans-serif;
    font-size: 20px;
    font-weight: 950;
    line-height: 1.05;
}

.bracket-panel-subtitle {
    color: #94a3b8;
    font-size: 10px;
    font-weight: 850;
    line-height: 1.1;
}

.bracket-scroll {
    max-height: 480px;
    overflow-y: auto;
    padding: 0 6px 0 0;
    background: transparent;
}

.ko-card {
    position: relative;
    overflow: hidden;
    padding: 9px 11px;
    margin-bottom: 8px;
    border-radius: 16px;
    background:
        linear-gradient(180deg, rgba(255,255,255,0.74), rgba(248,250,252,0.60)),
        url("https://storage.googleapis.com/foto-prode2026/Banners/FONDO_CARD_INICIO.png");
    background-size: cover;
    border: 1px solid rgba(148,163,184,0.38);
    box-shadow:
        0 8px 18px rgba(15,23,42,0.055),
        inset 0 1px 0 rgba(255,255,255,0.75);
}

.ko-card.final-card {
    background:
        linear-gradient(180deg, rgba(255,255,255,0.54), rgba(255,249,230,0.46)),
        url("__FONDO_CARD_GOLD__");
    background-size: cover;
    background-position: center;
    border-color: rgba(244,197,66,0.52);
    box-shadow:
        0 10px 22px rgba(244,197,66,0.12),
        inset 0 1px 0 rgba(255,255,255,0.78);
}

.ko-card.third-place-card {
    background:
        linear-gradient(180deg, rgba(255,255,255,0.58), rgba(241,245,249,0.50)),
        url("__FONDO_CARD_SILVER__");
    background-size: cover;
    background-position: center;
    border-color: rgba(148,163,184,0.52);
    box-shadow:
        0 10px 22px rgba(100,116,139,0.10),
        inset 0 1px 0 rgba(255,255,255,0.78);
}

.ko-card.semifinal-card {
    background:
        linear-gradient(180deg, rgba(255,255,255,0.58), rgba(255,244,232,0.46)),
        url("__FONDO_CARD_BRONCE__");
    background-size: cover;
    background-position: center;
    border-color: rgba(205,127,50,0.48);
    box-shadow:
        0 10px 22px rgba(154,90,34,0.10),
        inset 0 1px 0 rgba(255,255,255,0.78);
}

.ko-meta {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 8px;
    color: #64748b;
    font-size: 9.5px;
    font-weight: 950;
    letter-spacing: 0.065em;
    text-transform: uppercase;
}

.ko-badge {
    display: inline-flex;
    align-items: center;
    gap: 4px;
    margin-left: 6px;
    padding: 3px 7px;
    border-radius: 999px;
    background: rgba(255,255,255,0.70);
    border: 1px solid rgba(148,163,184,0.32);
    color: #334155;
    font-size: 8.5px;
    font-weight: 950;
}

.ko-badge.estado-en-vivo {
    background: linear-gradient(180deg, #22c55e, #16a34a);
    border-color: rgba(22,163,74,0.84);
    color: #ffffff;
    box-shadow: 0 6px 14px rgba(34,197,94,0.24);
}

.ko-badge.estado-en-vivo::before {
    content: "";
    width: 6px;
    height: 6px;
    border-radius: 999px;
    background: #ef4444;
    box-shadow: 0 0 0 2px rgba(255,255,255,0.22);
}

.ko-badge.estado-entretiempo {
    background: linear-gradient(180deg, #f59e0b, #d97706);
    border-color: rgba(217,119,6,0.78);
    color: #ffffff;
    box-shadow: 0 6px 14px rgba(245,158,11,0.18);
}

.ko-badge.estado-finalizado {
    background: rgba(226,232,240,0.82);
    border-color: rgba(148,163,184,0.58);
    color: #475569;
}

.ko-badge.estado-pendiente {
    background: rgba(255,255,255,0.78);
    border-color: rgba(203,213,225,0.78);
    color: #64748b;
}

.ko-body {
    display: grid;
    grid-template-columns: minmax(0, 1fr) 66px minmax(0, 1fr);
    align-items: center;
    gap: 10px;
}

.ko-team {
    display: flex;
    align-items: center;
    gap: 6px;
    min-width: 0;
    color: #0f172a;
    font-size: 13px;
    font-weight: 950;
}

.ko-team-name {
    min-width: 0;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
}

.ko-team.left {
    justify-content: flex-end;
    text-align: right;
}

.ko-team.right {
    justify-content: flex-start;
    text-align: left;
}

.ko-flag {
    width: 25px;
    height: 18px;
    flex: 0 0 auto;
    display: inline-flex;
    align-items: center;
    justify-content: center;
    border-radius: 4px;
    object-fit: cover;
    box-shadow: 0 3px 7px rgba(15,23,42,0.18);
}

.ko-score {
    border-radius: 12px;
    padding: 6px 7px;
    background:
        linear-gradient(180deg, rgba(15,23,42,0.08), rgba(15,23,42,0.045));
    color: #475569;
    border: 1px solid rgba(148,163,184,0.36);
    text-align: center;
    font-family: 'Montserrat', sans-serif;
    font-size: 13px;
    font-weight: 950;
}

.ko-user-result {
    display: grid;
    grid-template-columns: minmax(0, 1fr) auto minmax(0, 1fr);
    align-items: center;
    gap: 10px;
    margin-top: 8px;
    padding: 6px 9px;
    border-radius: 12px;
    background: rgba(255,255,255,0.70);
    border: 1px solid rgba(226,232,240,0.76);
    box-shadow: inset 0 1px 0 rgba(255,255,255,0.76);
}

.ko-user-label {
    color: #475569;
    font-size: 9px;
    font-weight: 950;
    letter-spacing: 0.055em;
    text-transform: uppercase;
    white-space: nowrap;
}

.ko-user-score {
    color: #0f172a;
    font-family: 'Montserrat', sans-serif;
    font-size: 11px;
    font-weight: 950;
    letter-spacing: 0.04em;
    white-space: nowrap;
}

.ko-user-points {
    justify-self: end;
    color: #94a3b8;
    font-size: 10px;
    font-weight: 950;
    white-space: nowrap;
}

.ko-user-points.positive {
    color: #16a34a;
}

.ko-user-points.zero {
    color: #64748b;
}

.ko-user-points.missing {
    color: #94a3b8;
}

.ko-impact-details {
    position: relative;
    z-index: 4;
    margin-top: 8px;
}

.ko-impact-details summary {
    list-style: none;
    cursor: pointer;
}

.ko-impact-details summary::-webkit-details-marker {
    display: none;
}

.ko-impact-details summary:hover .ko-user-result {
    border-color: rgba(244,197,66,0.58);
    box-shadow:
        inset 0 1px 0 rgba(255,255,255,0.86),
        0 8px 18px rgba(244,197,66,0.10);
}

.ko-impact-popover {
    width: min(360px, calc(100vw - 56px));
    margin-top: 8px;
    padding: 11px 12px;
    border-radius: 14px;
    background: rgba(255,255,255,0.98);
    border: 1px solid rgba(203,213,225,0.96);
    box-shadow:
        0 14px 30px rgba(15,23,42,0.14),
        inset 0 1px 0 rgba(255,255,255,0.88);
}

.ko-impact-popover h4 {
    margin: 0 0 7px;
    color: #07111F;
    font-family: 'Montserrat', sans-serif;
    font-size: 13px;
    font-weight: 950;
}

.ko-impact-summary {
    color: #64748b;
    font-size: 11px;
    font-weight: 850;
    margin-bottom: 8px;
}

.ko-impact-group-title {
    color: #334155;
    font-size: 11px;
    font-weight: 950;
    margin: 8px 0 4px;
}

.ko-impact-popover ul {
    margin: 0;
    padding-left: 17px;
}

.ko-impact-popover li {
    margin: 3px 0;
    color: #334155;
    font-size: 11px;
    font-weight: 750;
}

.ko-impact-popover li span {
    color: #64748b;
}

.ko-impact-popover li em {
    color: #0f172a;
    font-style: normal;
    font-weight: 950;
}

.ko-impact-empty {
    color: #94a3b8;
    font-size: 11px;
    font-weight: 850;
}

@media (max-width: 820px) {
    .inicio-v2-hero {
        min-height: unset;
        padding: 20px 14px;
        border-radius: 18px;
    }

    .inicio-v2-title {
        font-size: 28px;
        letter-spacing: 0.03em;
    }

    .inicio-v2-kicker {
        font-size: 10px;
        letter-spacing: 0.13em;
    }

    .inicio-v2-stage {
        grid-template-columns: 1fr;
        margin-top: 18px;
    }

    .ko-user-hero-card {
        min-height: unset;
        padding: 14px;
    }

    .ko-user-avatar,
    .ko-user-avatar-placeholder {
        width: 76px;
        height: 76px;
    }

    .ko-user-position {
        font-size: 34px;
    }

    .ko-ranking-panel {
        padding: 12px;
    }

    .ko-ranking-scroll {
        height: 300px;
    }

    .ko-ranking-row {
        grid-template-columns: 34px minmax(0, 1fr) 56px;
        gap: 8px;
        padding: 9px;
    }

    .ko-rank-pos {
        width: 30px;
        height: 30px;
        font-size: 12px;
    }

    .ko-player-name {
        font-size: 12px;
    }

    .ko-player-sub {
        font-size: 9px;
    }

    .ko-points-main {
        font-size: 17px;
    }

    .bracket-grid {
        grid-template-columns: 1fr;
    }

    .ko-body {
        grid-template-columns: minmax(0, 1fr) 62px minmax(0, 1fr);
        gap: 8px;
    }

    .ko-user-result {
        grid-template-columns: 1fr auto;
        gap: 6px 10px;
        padding: 7px 8px;
    }

    .ko-user-points {
        grid-column: 1 / -1;
        justify-self: end;
    }
}
</style>
""".replace("__HERO_BACKGROUND__", HEADER_BACKGROUND).replace(
            "__FONDO_CARD_INICIO__",
            FONDO_CARD_INICIO
        ).replace(
            "__FONDO_CARD_GOLD__",
            FONDO_CARD_GOLD
        ).replace(
            "__FONDO_CARD_SILVER__",
            FONDO_CARD_SILVER
        ).replace(
            "__FONDO_CARD_BRONCE__",
            FONDO_CARD_BRONCE
        ),
        unsafe_allow_html=True,
    )


def _normalizar_valor(valor, fallback=""):
    if valor is None:
        return fallback

    texto = str(valor).strip()
    if texto.lower() in ["", "nan", "none", "nat"]:
        return fallback

    return texto


def _formatear_gol(valor):
    numero = pd.to_numeric(valor, errors="coerce")

    if pd.isna(numero):
        return ""

    return str(int(numero))


def _estado_clase(estado):
    estado_norm = _normalizar_valor(estado, "Pendiente").lower()
    estado_norm = (
        estado_norm
        .replace(" ", "-")
        .replace("á", "a")
        .replace("é", "e")
        .replace("í", "i")
        .replace("ó", "o")
        .replace("ú", "u")
    )

    if estado_norm in ["en-vivo", "entretiempo", "finalizado", "pendiente"]:
        return f"estado-{estado_norm}"

    return "estado-pendiente"


def _calcular_ganador_perdedor(partido):
    r1 = _normalizar_valor(partido.get("r1"))
    r2 = _normalizar_valor(partido.get("r2"))

    if not r1 or not r2:
        return "", ""

    try:
        r1 = int(float(r1))
        r2 = int(float(r2))
    except ValueError:
        return "", ""

    if r1 == r2:
        return "", ""

    equipo_1 = _normalizar_valor(partido.get("equipo_1"))
    equipo_2 = _normalizar_valor(partido.get("equipo_2"))

    if r1 > r2:
        return equipo_1, equipo_2

    return equipo_2, equipo_1


def _resolver_referencia_equipo(nombre_equipo, partidos_resueltos):
    texto = _normalizar_valor(nombre_equipo)
    match = re.match(r"^(Ganador|Perdedor)\s+(\d+)$", texto, flags=re.IGNORECASE)

    if not match:
        return texto

    tipo = match.group(1).lower()
    numero_origen = int(match.group(2))
    partido_origen = partidos_resueltos.get(numero_origen)

    if not partido_origen:
        return texto

    columna = "ganador" if tipo == "ganador" else "perdedor"
    valor_explicito = _normalizar_valor(partido_origen.get(columna))

    if valor_explicito:
        return valor_explicito

    ganador_calculado, perdedor_calculado = _calcular_ganador_perdedor(partido_origen)
    valor_calculado = ganador_calculado if tipo == "ganador" else perdedor_calculado

    return valor_calculado or texto


def _resolver_equipos_desde_resultados(partidos):
    partidos_resueltos = {}
    salida = []

    for partido in sorted(partidos, key=lambda item: item.get("partido", 0)):
        partido_resuelto = dict(partido)
        numero = partido_resuelto.get("partido")

        partido_resuelto["equipo_1"] = _resolver_referencia_equipo(
            partido_resuelto.get("equipo_1"),
            partidos_resueltos
        )
        partido_resuelto["equipo_2"] = _resolver_referencia_equipo(
            partido_resuelto.get("equipo_2"),
            partidos_resueltos
        )

        if numero is not None:
            try:
                partidos_resueltos[int(numero)] = partido_resuelto
            except (TypeError, ValueError):
                pass

        salida.append(partido_resuelto)

    return salida


def _cargar_partidos_eliminatoria():
    df_eliminatoria = get_eliminatoria_app()

    if df_eliminatoria is None or df_eliminatoria.empty:
        return _resolver_equipos_desde_resultados(MOCK_ELIMINATORIA), False

    return _resolver_equipos_desde_resultados(
        df_eliminatoria.to_dict(orient="records")
    ), True


def _cargar_pronosticos_usuario(usuario):
    df_pronosticos = get_pronosticos_eliminatoria_app()

    if (
        not usuario
        or df_pronosticos is None
        or df_pronosticos.empty
        or not {"USUARIO", "N_PARTIDO", "P1", "P2"}.issubset(df_pronosticos.columns)
    ):
        return {}

    df_user = df_pronosticos[
        df_pronosticos["USUARIO"].astype(str).str.strip()
        == str(usuario).strip()
    ].copy()

    if df_user.empty:
        return {}

    df_user["N_PARTIDO"] = pd.to_numeric(df_user["N_PARTIDO"], errors="coerce")
    df_user = df_user.dropna(subset=["N_PARTIDO"])

    return {
        int(row["N_PARTIDO"]): row
        for _, row in df_user.iterrows()
    }


def _cargar_pronosticos_todos():
    df_pronosticos = get_pronosticos_eliminatoria_app()

    columnas = ["USUARIO", "N_PARTIDO", "P1", "P2", "CLASIFICADO_LADO"]

    if df_pronosticos is None or df_pronosticos.empty:
        return pd.DataFrame(columns=columnas)

    for col in columnas:
        if col not in df_pronosticos.columns:
            df_pronosticos[col] = ""

    df_pronosticos = df_pronosticos[columnas].copy()
    df_pronosticos["N_PARTIDO"] = pd.to_numeric(
        df_pronosticos["N_PARTIDO"],
        errors="coerce"
    )
    df_pronosticos["P1"] = pd.to_numeric(df_pronosticos["P1"], errors="coerce")
    df_pronosticos["P2"] = pd.to_numeric(df_pronosticos["P2"], errors="coerce")
    df_pronosticos = df_pronosticos.dropna(subset=["N_PARTIDO", "P1", "P2"])

    return df_pronosticos


def _fase_partidos(partidos_base, fase, llave=None):
    partidos = [p for p in partidos_base if p.get("fase") == fase]
    if llave:
        partidos = [p for p in partidos if p.get("llave") == llave]

    return sorted(
        partidos,
        key=lambda item: (
            item.get("slot") if item.get("slot") is not None else item.get("partido", 0),
            item.get("partido", 0)
        )
    )


def _marcador_partido(partido):
    estado = _normalizar_valor(partido.get("estado_partido"), "Pendiente")

    if estado in ["En Vivo", "Entretiempo"]:
        r1 = partido.get("live_r1")
        r2 = partido.get("live_r2")
    else:
        r1 = partido.get("r1")
        r2 = partido.get("r2")

    r1 = _formatear_gol(r1)
    r2 = _formatear_gol(r2)

    if r1 and r2:
        return f"{escape(r1)} : {escape(r2)}"

    return "VS"


def _resultado_para_puntos(partido):
    estado = _normalizar_valor(partido.get("estado_partido"), "Pendiente")

    if estado in ["En Vivo", "Entretiempo"]:
        r1 = partido.get("live_r1")
        r2 = partido.get("live_r2")
    else:
        r1 = partido.get("r1")
        r2 = partido.get("r2")

    r1_num = pd.to_numeric(r1, errors="coerce")
    r2_num = pd.to_numeric(r2, errors="coerce")

    if pd.isna(r1_num) or pd.isna(r2_num):
        return None

    return r1_num, r2_num


def _pronostico_partido(partido, pronosticos_usuario):
    try:
        numero = int(partido.get("partido"))
    except (TypeError, ValueError):
        numero = None

    pronostico = pronosticos_usuario.get(numero)

    if pronostico is None:
        return "Sin pronostico", "-", "missing"

    p1 = pd.to_numeric(pronostico.get("P1"), errors="coerce")
    p2 = pd.to_numeric(pronostico.get("P2"), errors="coerce")

    if pd.isna(p1) or pd.isna(p2):
        return "Sin pronostico", "-", "missing"

    resultado_texto = f"{int(p1)} - {int(p2)}"
    resultado_real = _resultado_para_puntos(partido)

    if resultado_real is None:
        return resultado_texto, "Pendiente", "missing"

    puntos, _, _, _ = calcular_detalle_eliminatoria(
        int(resultado_real[0]),
        int(resultado_real[1]),
        int(p1),
        int(p2),
        partido.get("clasificado_lado"),
        pronostico.get("CLASIFICADO_LADO")
    )

    return resultado_texto, f"+{puntos} Pts", "positive" if puntos > 0 else "zero"


def _lista_impacto_html(items, limite=9):
    if not items:
        return '<div class="ko-impact-empty">Nadie</div>'

    html_items = ""

    for item in items[:limite]:
        usuario = escape(str(item.get("usuario", "") or ""))
        resultado = escape(f'{item.get("p1", "-")} - {item.get("p2", "-")}')
        html_items += f'<li><em>{usuario}</em> <span>{resultado}</span></li>'

    restantes = len(items) - limite

    if restantes > 0:
        html_items += f'<li><span>+{restantes} mas</span></li>'

    return f"<ul>{html_items}</ul>"


def _impacto_partido(partido, df_pronosticos_todos):
    resultado_real = _resultado_para_puntos(partido)

    grupos = {
        4: [],
        3: [],
        2: [],
        1: [],
        0: [],
    }

    if resultado_real is None:
        return (
            "Todavia no hay resultado para calcular impacto.",
            grupos
        )

    if df_pronosticos_todos is None or df_pronosticos_todos.empty:
        return "No hay pronosticos cargados para este partido.", grupos

    try:
        numero = int(partido.get("partido"))
    except (TypeError, ValueError):
        return "No hay pronosticos cargados para este partido.", grupos

    pronos_partido = df_pronosticos_todos[
        df_pronosticos_todos["N_PARTIDO"].astype(int) == numero
    ].copy()

    for _, pron in pronos_partido.iterrows():
        p1 = pd.to_numeric(pron.get("P1"), errors="coerce")
        p2 = pd.to_numeric(pron.get("P2"), errors="coerce")

        if pd.isna(p1) or pd.isna(p2):
            continue

        puntos, _, _, _ = calcular_detalle_eliminatoria(
            int(resultado_real[0]),
            int(resultado_real[1]),
            int(p1),
            int(p2),
            partido.get("clasificado_lado"),
            pron.get("CLASIFICADO_LADO")
        )
        grupos[int(puntos)].append(
            {
                "usuario": str(pron.get("USUARIO", "") or "").strip(),
                "p1": int(p1),
                "p2": int(p2),
            }
        )

    total_suman = sum(len(grupos[puntos]) for puntos in [4, 3, 2, 1])
    impacto_summary = (
        f"{total_suman} jugadores suman "
        f"&middot; {len(grupos[4])} hacen +4 "
        f"&middot; {len(grupos[3])} hacen +3"
    )

    return impacto_summary, grupos


def _flag_html(valor):
    bandera = _normalizar_valor(valor, "⚽")

    if bandera.startswith("http") or bandera.startswith("data:image"):
        return f'<img class="ko-flag" src="{escape(bandera)}" alt="">'

    return f'<span class="ko-flag">{escape(bandera)}</span>'


def _card_html(
    partido,
    pronosticos_usuario,
    df_pronosticos_todos=None,
    mapa_banderas=None
):
    estado = _normalizar_valor(partido.get("estado_partido"), "Pendiente")
    estado_clase = _estado_clase(estado)
    fase = _normalizar_valor(partido.get("fase"))
    equipo_1 = _normalizar_valor(partido.get("equipo_1"), "Equipo 1")
    equipo_2 = _normalizar_valor(partido.get("equipo_2"), "Equipo 2")
    mapa_banderas = mapa_banderas or {}
    bandera_1 = mapa_banderas.get(equipo_1, "⚽")
    bandera_2 = mapa_banderas.get(equipo_2, "⚽")
    dia = _normalizar_valor(partido.get("dia"), "--/--/--")
    hora = _normalizar_valor(partido.get("hora"), "--:--")
    numero = _normalizar_valor(partido.get("partido"), "-")
    pronostico_texto, puntos_texto, puntos_clase = _pronostico_partido(
        partido,
        pronosticos_usuario
    )
    impacto_summary, grupos_impacto = _impacto_partido(
        partido,
        df_pronosticos_todos
    )
    clase_especial = ""

    if fase == "Final":
        clase_especial = " final-card"
    elif fase == "Semifinal":
        clase_especial = " semifinal-card"
    elif fase == "Tercer Puesto":
        clase_especial = " third-place-card"

    return f"""
<div class="ko-card{clase_especial}">
    <div class="ko-meta">
        <span>Partido #{escape(numero)}<span class="ko-badge {escape(estado_clase)}">{escape(estado)}</span></span>
        <span>{escape(dia)} | {escape(hora)}</span>
    </div>
    <div class="ko-body">
        <div class="ko-team left"><span class="ko-team-name">{escape(equipo_1)}</span>{_flag_html(bandera_1)}</div>
        <div class="ko-score">{_marcador_partido(partido)}</div>
        <div class="ko-team right">{_flag_html(bandera_2)}<span class="ko-team-name">{escape(equipo_2)}</span></div>
    </div>
    <details class="ko-impact-details">
        <summary>
            <div class="ko-user-result">
                <span class="ko-user-label">Tu resultado</span>
                <span class="ko-user-score">{escape(pronostico_texto)}</span>
                <span class="ko-user-points {escape(puntos_clase)}">{escape(puntos_texto)}</span>
            </div>
        </summary>
        <div class="ko-impact-popover">
            <h4>Impacto con este resultado</h4>
            <div class="ko-impact-summary">{impacto_summary}</div>
            <div class="ko-impact-group-title">+4 pts exacto + clasificado</div>
            {_lista_impacto_html(grupos_impacto[4])}
            <div class="ko-impact-group-title">+3 pts</div>
            {_lista_impacto_html(grupos_impacto[3])}
            <div class="ko-impact-group-title">+2 pts</div>
            {_lista_impacto_html(grupos_impacto[2])}
            <div class="ko-impact-group-title">+1 pt</div>
            {_lista_impacto_html(grupos_impacto[1])}
        </div>
    </details>
</div>
"""


def _render_panel(
    titulo,
    subtitulo,
    partidos,
    pronosticos_usuario,
    df_pronosticos_todos=None,
    mapa_banderas=None
):
    cards_html = "".join(
        _card_html(
            partido,
            pronosticos_usuario,
            df_pronosticos_todos,
            mapa_banderas
        )
        for partido in partidos
    )

    panel_html = (
        '<div class="bracket-panel">'
        '<div class="bracket-panel-header">'
        '<div class="bracket-panel-icon">&#9917;</div>'
        '<div>'
        f'<div class="bracket-panel-title">{escape(titulo)}</div>'
        f'<div class="bracket-panel-subtitle">{escape(subtitulo)}</div>'
        '</div>'
        '</div>'
        '<div class="bracket-scroll">'
        f'{cards_html}'
        '</div>'
        '</div>'
    )

    st.markdown(panel_html, unsafe_allow_html=True)


def _render_doble_columna(
    partidos_base,
    fase,
    pronosticos_usuario,
    df_pronosticos_todos=None,
    mapa_banderas=None
):
    st.markdown(
        f'<div class="bracket-stage-note">{escape(fase)} con dos caminos independientes hasta semifinales.</div>',
        unsafe_allow_html=True,
    )
    col_a, col_b = st.columns(2, gap="large")

    with col_a:
        partidos_a = _fase_partidos(partidos_base, fase, "A")
        _render_panel(
            "Llave A",
            f"{len(partidos_a)} partidos de {fase}",
            partidos_a,
            pronosticos_usuario,
            df_pronosticos_todos,
            mapa_banderas
        )

    with col_b:
        partidos_b = _fase_partidos(partidos_base, fase, "B")
        _render_panel(
            "Llave B",
            f"{len(partidos_b)} partidos de {fase}",
            partidos_b,
            pronosticos_usuario,
            df_pronosticos_todos,
            mapa_banderas
        )


def _render_simple(
    partidos_base,
    fase,
    titulo,
    subtitulo,
    pronosticos_usuario,
    df_pronosticos_todos=None,
    mapa_banderas=None
):
    st.markdown(
        f'<div class="bracket-stage-note">{escape(subtitulo)}</div>',
        unsafe_allow_html=True,
    )
    partidos = _fase_partidos(partidos_base, fase)
    _render_panel(
        titulo,
        f"{len(partidos)} partidos",
        partidos,
        pronosticos_usuario,
        df_pronosticos_todos,
        mapa_banderas
    )


def _safe_int(valor, default=0):
    try:
        if pd.isna(valor):
            return default

        return int(float(valor))
    except (TypeError, ValueError):
        return default


def _cargar_ranking_eliminatoria(partidos_base):
    try:
        df_usuarios = get_usuarios_app()
        df_pronosticos = get_pronosticos_eliminatoria_app()
        df_resultados = pd.DataFrame(partidos_base)

        return obtener_ranking_eliminatoria(
            df_usuarios,
            df_pronosticos,
            df_resultados,
            incluir_live=True
        )
    except Exception:
        return pd.DataFrame()


def _ranking_eliminatoria_html(df_ranking, usuario_actual=None):
    usuario_actual = str(usuario_actual or "").strip()

    ranking_html = (
        '<div class="ko-ranking-panel">'
        '<div class="ko-ranking-header">'
        '<div class="ko-ranking-icon">&#127942;</div>'
        '<div>'
        '<div class="ko-ranking-title">Ranking General</div>'
        '<div class="ko-ranking-subtitle">Fase eliminatoria con puntaje virtual en vivo</div>'
        '</div>'
        '</div>'
    )

    if df_ranking is None or df_ranking.empty:
        ranking_html += (
            '<div class="ko-ranking-empty">'
            'Todavia no hay ranking calculable para la fase eliminatoria.'
            '</div></div>'
        )
        return ranking_html

    ranking_html += '<div class="ko-ranking-scroll">'

    for idx, row in df_ranking.reset_index(drop=True).iterrows():
        posicion = idx + 1
        usuario = str(row.get("USUARIO", "") or "").strip()
        es_usuario_actual = usuario_actual and usuario == usuario_actual

        clases = ["ko-ranking-row"]

        if posicion <= 3:
            clases.append(f"top-{posicion}")

        if es_usuario_actual:
            clases.append("me")

        jugador = escape(str(row.get("JUGADOR", "Jugador") or "Jugador"))
        puntos = _safe_int(row.get("PUNTOS", 0))
        exactos = _safe_int(row.get("EXACTOS", 0))
        generales = _safe_int(row.get("GENERALES", 0))
        clasificados = _safe_int(row.get("CLASIFICADOS", 0))
        subtitulo = "Tu posicion actual" if es_usuario_actual else "Participante"

        ranking_html += f"""
<div class="{escape(' '.join(clases))}">
    <div class="ko-rank-pos">{posicion}</div>
    <div class="ko-player-info">
        <div class="ko-player-name">{jugador}</div>
        <div class="ko-player-sub">{escape(subtitulo)} &middot; 🎯 {exactos} &middot; ✅ {generales} &middot; 🏁 {clasificados}</div>
    </div>
    <div class="ko-rank-points">
        <div class="ko-points-main">{puntos}</div>
        <div class="ko-points-label">pts</div>
    </div>
</div>
"""

    ranking_html += '</div></div>'
    return ranking_html


def _usuario_hero_html(df_ranking, usuario_actual=None):
    usuario_actual = str(usuario_actual or "").strip()
    nombre = usuario_actual or "Jugador"
    avatar_url = ""
    posicion = "-"
    puntos = 0
    diferencia_lider = None

    if df_ranking is not None and not df_ranking.empty:
        lider = _safe_int(df_ranking.iloc[0].get("PUNTOS", 0))
        fila_usuario = df_ranking[
            df_ranking["USUARIO"].astype(str).str.strip() == usuario_actual
        ]

        if not fila_usuario.empty:
            fila = fila_usuario.iloc[0]
            nombre = str(fila.get("JUGADOR", nombre) or nombre)
            posicion = str(fila.get("Nº", "-") or "-")
            puntos = _safe_int(fila.get("PUNTOS", 0))
            diferencia_lider = max(lider - puntos, 0)

    try:
        df_usuarios = get_usuarios_app()
        if df_usuarios is not None and not df_usuarios.empty and usuario_actual:
            fila_usuario = df_usuarios[
                df_usuarios["USUARIO"].astype(str).str.strip() == usuario_actual
            ]

            if not fila_usuario.empty:
                usuario_row = fila_usuario.iloc[0]
                nombre = str(usuario_row.get("NOMBRE", nombre) or nombre)
                avatar_url = str(usuario_row.get("AVATAR_URL", "") or "").strip()
    except Exception:
        pass

    if avatar_url:
        avatar_html = (
            f'<img class="ko-user-avatar" src="{escape(avatar_url)}" '
            f'alt="{escape(nombre)}">'
        )
    else:
        inicial = escape((nombre[:1] or "J").upper())
        avatar_html = f'<div class="ko-user-avatar-placeholder">{inicial}</div>'

    if diferencia_lider is None:
        gap_texto = "Ranking en preparacion"
    elif diferencia_lider <= 0:
        gap_texto = "Lider de la eliminatoria"
    else:
        gap_texto = f"A {diferencia_lider} pts. del lider"

    return (
        '<div class="ko-user-hero-card">'
        f'{avatar_html}'
        f'<div class="ko-user-name">{escape(nombre)}</div>'
        f'<div class="ko-user-handle">@{escape(usuario_actual or "usuario")}</div>'
        '<div class="ko-user-position-label">Tu posicion</div>'
        f'<div class="ko-user-position">{escape(posicion)}&deg;</div>'
        f'<div class="ko-user-points-pill">{puntos} pts.</div>'
        f'<div class="ko-user-gap">{escape(gap_texto)}</div>'
        '</div>'
    )


def _render_hero_inicio_v2(df_ranking, usuario_actual, fuente_datos):
    _ = fuente_datos
    hero_html = (
        '<div class="inicio-v2-hero">'
        '<h1 class="inicio-v2-title">'
        '<span class="inicio-v2-title-icon">&#127942;</span>'
        'Prode Mundial 2026'
        '</h1>'
        '<div class="inicio-v2-kicker">La gloria esta en tus predicciones</div>'
        '<div class="inicio-v2-stage">'
        f'{_usuario_hero_html(df_ranking, usuario_actual)}'
        f'{_ranking_eliminatoria_html(df_ranking, usuario_actual)}'
        '</div>'
        '</div>'
    )
    st.markdown(hero_html, unsafe_allow_html=True)


def render_inicio_v2(usuario_actual=None, mapa_banderas=None):
    """
    Prototipo admin para disenar la portada de la fase eliminatoria.
    Lee Supabase si la tabla esta disponible y usa mock como respaldo.
    """

    _render_css()
    partidos_base, usa_supabase = _cargar_partidos_eliminatoria()
    pronosticos_usuario = _cargar_pronosticos_usuario(usuario_actual)
    df_pronosticos_todos = _cargar_pronosticos_todos()
    df_ranking_eliminatoria = _cargar_ranking_eliminatoria(partidos_base)
    fuente_datos = "Datos Supabase" if usa_supabase else "Mock local"

    _render_hero_inicio_v2(
        df_ranking_eliminatoria,
        usuario_actual,
        fuente_datos
    )

    st.markdown(
        """
<div class="inicio-v2-results-header">
    <div class="inicio-v2-results-icon">&#9917;</div>
    <div class="inicio-v2-results-title">Resultados Oficiales</div>
</div>
""",
        unsafe_allow_html=True,
    )

    tab_16, tab_8, tab_4, tab_semis, tab_final = st.tabs(
        ["16avos", "Octavos", "Cuartos", "Semifinales", "Final"]
    )

    with tab_16:
        _render_doble_columna(
            partidos_base,
            "16avos",
            pronosticos_usuario,
            df_pronosticos_todos,
            mapa_banderas
        )

    with tab_8:
        _render_doble_columna(
            partidos_base,
            "Octavos",
            pronosticos_usuario,
            df_pronosticos_todos,
            mapa_banderas
        )

    with tab_4:
        _render_doble_columna(
            partidos_base,
            "Cuartos",
            pronosticos_usuario,
            df_pronosticos_todos,
            mapa_banderas
        )

    with tab_semis:
        _render_simple(
            partidos_base,
            "Semifinal",
            "Semifinales",
            "Las dos llaves se reducen a sus mejores equipos antes de la final.",
            pronosticos_usuario,
            df_pronosticos_todos,
            mapa_banderas,
        )

    with tab_final:
        st.markdown(
            '<div class="bracket-stage-note">Final y tercer puesto cierran la etapa eliminatoria.</div>',
            unsafe_allow_html=True,
        )
        _render_panel(
            "Final / Tercer Puesto",
            "2 partidos decisivos",
            _fase_partidos(partidos_base, "Final") + _fase_partidos(partidos_base, "Tercer Puesto"),
            pronosticos_usuario,
            df_pronosticos_todos,
            mapa_banderas,
        )
