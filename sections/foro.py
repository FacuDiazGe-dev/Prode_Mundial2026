import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from html import escape

from styles_config import (
    AVATAR_GENERICO,
)
from tools import upload_foro_image


def render_foro(conn, df_usuarios, df_ranking, df_foro):

    # ============================================================
    # ESTILOS — FORO
    # ============================================================

    st.markdown("""
<style>

/* ============================================================
   1. TÍTULO GENERAL
   ============================================================ */

.foro-title {
    margin-bottom: 22px;
}

.foro-title h1 {
    font-family: 'Montserrat', sans-serif;
    font-size: 34px;
    font-weight: 900;
    color: #07111F;
    margin: 0;
    letter-spacing: -0.04em;
}

.foro-title p {
    margin: 6px 0 0 0;
    color: #64748b;
    font-size: 15px;
    font-weight: 600;
}


/* ============================================================
   2. PANELES BASE
   ============================================================ */

.foro-panel,
.foro-community-panel {
    background: rgba(255,255,255,0.94);
    border: 1px solid rgba(226,232,240,0.9);
    border-radius: 18px;
    padding: 16px;
    box-shadow: 0 12px 30px rgba(15,23,42,0.06);
}

.foro-panel-header {
    display: flex;
    align-items: center;
    gap: 10px;
    padding: 4px 4px 14px 4px;
    margin-bottom: 12px;
    border-bottom: 1px solid rgba(226,232,240,0.75);
}

.foro-panel-icon {
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

.foro-panel-title {
    font-family: 'Montserrat', sans-serif;
    font-size: 18px;
    font-weight: 900;
    color: #0f172a;
}

.foro-panel-subtitle {
    color: #64748b;
    font-size: 12px;
    font-weight: 700;
    margin-top: 2px;
}

/* ============================================================
   2B. AJUSTE VISUAL PREMIUM — FORO
   Más contraste, acento dorado y lectura más clara.
   ============================================================ */

.foro-panel {
    background:
        radial-gradient(
            circle at 0% 0%,
            rgba(244,197,66,0.14),
            rgba(255,255,255,0.96) 34%
        ),
        rgba(255,255,255,0.96);
}

.foro-community-panel {
    background:
        radial-gradient(
            circle at 100% 0%,
            rgba(244,197,66,0.10),
            rgba(255,255,255,0.96) 36%
        ),
        rgba(255,255,255,0.96);
}

.foro-panel-title {
    letter-spacing: -0.02em;
}

.foro-panel-subtitle {
    color: #475569;
}

.foro-message-card {
    border-left: 4px solid rgba(148,163,184,0.35);
}

.foro-message-card.mine {
    border-left: 4px solid #F4C542;
}

.foro-message-name {
    color: #07111F;
}

.foro-message-text {
    color: #1f2937;
}

.foro-feed-shell {
    margin-top: 8px;
    padding: 8px;
    border-radius: 18px;
    background: rgba(248,250,252,0.72);
    border: 1px solid rgba(226,232,240,0.75);
}

/* ============================================================
   2C. PANEL INTEGRADO — MURO DEL FORO
   Contiene header + publicar + feed.
   ============================================================ */

.foro-hero-header {
    position: relative;
    overflow: hidden;

    background:
        linear-gradient(
            180deg,
            rgba(255,255,255,0.08),
            rgba(255,255,255,0.01)
        ),
        linear-gradient(
            135deg,
            rgba(7,17,31,0.82),
            rgba(15,23,42,0.72)
        ),
        var(--foro-header-bg);

    background-size: cover;
    background-position: center;
    background-repeat: no-repeat;

    border: 1px solid rgba(244,197,66,0.28);
    border-radius: 18px;
    padding: 16px;
    margin-bottom: 10px;

    box-shadow:
        inset 0 1px 0 rgba(255,255,255,0.08),
        0 0 18px rgba(244,197,66,0.16),
        0 10px 22px rgba(15,23,42,0.16);
}
.foro-hero-row {
    display: flex;
    align-items: center;
    gap: 12px;
}

.foro-hero-icon {
    width: 38px;
    height: 38px;
    border-radius: 13px;
    background: rgba(244,197,66,0.18);
    color: #F4C542;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 19px;
    flex-shrink: 0;
}

.foro-hero-title {
    font-family: 'Montserrat', sans-serif;
    font-size: 20px;
    font-weight: 900;
    color: #F8FAFC;
    line-height: 1.05;
}

.foro-hero-subtitle {
    color: rgba(248,250,252,0.70);
    font-size: 12px;
    font-weight: 800;
    margin-top: 4px;
}


@media (max-width: 768px) {
    .foro-main-shell {
        padding: 10px;
        border-radius: 18px;
    }

    .foro-hero-header {
        padding: 13px;
        border-radius: 16px;
        margin-bottom: 8px;
    }

    .foro-hero-title {
        font-size: 18px;
    }

    .foro-hero-subtitle {
        font-size: 11px;
    }
}

/* ============================================================
   3. FORMULARIO
   ============================================================ */

.foro-form-note {
    background: rgba(248,250,252,0.82);
    border: 1px solid rgba(226,232,240,0.85);
    border-radius: 14px;
    padding: 11px 12px;
    color: #64748b;
    font-size: 12px;
    font-weight: 800;
    margin-bottom: 12px;
}


/* ============================================================
   4. MENSAJES DEL FORO
   Feed compacto tipo muro social.
   ============================================================ */

.foro-feed {
    margin-top: 4px;
}

/* Card general de cada mensaje */
.foro-message-card {
    background: rgba(255,255,255,0.96);
    border: 1px solid rgba(226,232,240,0.9);
    border-radius: 16px;

    padding: 11px 12px;
    margin-bottom: 4px;

    box-shadow: 0 8px 18px rgba(15,23,42,0.04);
}

/* Card de mensaje propio */
.foro-message-card.mine {
    background:
        linear-gradient(
            90deg,
            rgba(244,197,66,0.13),
            rgba(255,255,255,0.96)
        );
    border-color: rgba(244,197,66,0.42);
}

/* Cabecera: avatar + nombre + fecha */
.foro-message-head {
    display: flex;
    align-items: center;
    gap: 9px;
    margin-bottom: 7px;
}

.foro-avatar {
    width: 38px;
    height: 38px;
    border-radius: 50%;
    object-fit: cover;
    border: 2px solid rgba(244,197,66,0.75);
    flex-shrink: 0;
}

.foro-message-meta {
    flex: 1;
    min-width: 0;
}

.foro-message-name {
    color: #0f172a;
    font-size: 13px;
    font-weight: 900;
    line-height: 1.05;
}

.foro-message-date {
    color: #94a3b8;
    font-size: 10px;
    font-weight: 800;
    margin-top: 2px;
}

.foro-own-pill {
    display: inline-block;
    margin-left: 6px;
    padding: 2px 6px;

    border-radius: 999px;
    background: rgba(7,17,31,0.95);

    color: #F4C542;
    font-size: 9px;
    font-weight: 900;
}

/* Texto del mensaje */
.foro-message-text {
    color: #334155;
    font-size: 13px;
    font-weight: 700;
    line-height: 1.35;
    white-space: pre-wrap;
}

/* Si el mensaje no tiene texto, evita altura visual innecesaria */
.foro-message-text:empty {
    display: none;
}

/* Cuerpo del mensaje.
   En desktop permite texto + imagen en dos columnas. */
.foro-message-body {
    display: block;
}

.foro-message-body.has-image {
    display: grid;
    grid-template-columns: minmax(0, 1fr) 220px;
    gap: 12px;
    align-items: start;
}

.foro-message-body.has-image .foro-message-text {
    min-width: 0;
}

/* ============================================================
   4B. IMÁGENES PUBLICADAS EN EL FORO
   Imagen como adjunto, no como banner gigante.
   ============================================================ */

.foro-image-wrap {
    margin-top: 0;
    display: flex;
    justify-content: center;
}

.foro-message-img {
    width: 100%;
    max-width: 220px;
    max-height: 180px;

    object-fit: contain;
    display: block;

    border-radius: 13px;
    border: 1px solid rgba(226,232,240,0.9);
    background: rgba(248,250,252,0.78);
}


/* ============================================================
   4C. ACCIONES DEL FORO — SEGMENTED CONTROL
   Barra compacta debajo de cada card.
   ============================================================ */

div[data-testid="stSegmentedControl"] {
    margin: 0 0 12px 0 !important;
}

div[data-testid="stSegmentedControl"] button {
    min-height: 32px !important;
    padding: 3px 9px !important;

    border-radius: 10px !important;
    border: 1px solid rgba(226,232,240,0.95) !important;

    background: rgba(255,255,255,0.92) !important;
    color: #334155 !important;

    font-size: 12px !important;
    font-weight: 900 !important;
}

div[data-testid="stSegmentedControl"] button:hover {
    background: rgba(244,197,66,0.14) !important;
    border-color: rgba(244,197,66,0.45) !important;
    color: #07111F !important;
}

/* Reduce la separación entre card y barra de acciones */
.foro-message-card + div[data-testid="stSegmentedControl"] {
    margin-top: -2px !important;
}


/* ============================================================
   4D. MOBILE — FEED DEL FORO
   ============================================================ */

@media (max-width: 768px) {
    .foro-feed {
        margin-top: 12px;
    }

    .foro-message-card {
        padding: 10px;
        border-radius: 15px;
        margin-bottom: 3px;
    }

    .foro-avatar {
        width: 36px;
        height: 36px;
    }

    .foro-message-name {
        font-size: 12px;
    }

    .foro-message-date {
        font-size: 9px;
    }

    .foro-message-text {
        font-size: 12px;
        line-height: 1.32;
    }

    .foro-message-img {
        width: 100%;
        max-width: 100%;
        max-height: 230px;
    }

    div[data-testid="stSegmentedControl"] {
        margin: 0 0 12px 0 !important;
    }

    div[data-testid="stSegmentedControl"] button {
        min-height: 30px !important;
        padding: 3px 7px !important;
        font-size: 11px !important;
    }
}

/* ============================================================
   5. COMUNIDAD / STATS 
   ============================================================ */
/* ============================================================
   5A. CENTRAL DEL PRODE / NOTICIAS
   ============================================================ */

.community-side-panel {
    background:
        linear-gradient(
            180deg,
            rgba(255,255,255,0.94),
            rgba(248,250,252,0.90)
        );
    border: 1px solid rgba(226,232,240,0.9);
    border-radius: 18px;
    padding: 14px;
    margin-bottom: 12px;

    box-shadow:
        0 10px 24px rgba(15,23,42,0.06),
        inset 0 1px 0 rgba(255,255,255,0.65);
}

.community-side-header {
    display: flex;
    align-items: center;
    gap: 10px;

    padding-bottom: 10px;
    margin-bottom: 10px;

    border-bottom: 1px solid rgba(226,232,240,0.75);
}

.community-side-icon {
    width: 31px;
    height: 31px;
    border-radius: 10px;

    display: flex;
    align-items: center;
    justify-content: center;

    background: rgba(244,197,66,0.16);
    color: #0f172a;
    font-size: 16px;
    flex-shrink: 0;
}

.community-side-title {
    font-family: 'Montserrat', sans-serif;
    font-size: 16px;
    font-weight: 900;
    color: #07111F;
    line-height: 1.05;
}

.community-side-subtitle {
    color: #64748b;
    font-size: 11px;
    font-weight: 750;
    margin-top: 2px;
}

.news-scroll {
    max-height: 178px;
    overflow-y: auto;
    padding-right: 4px;
}

.news-card {
    background: rgba(255,255,255,0.84);
    border: 1px solid rgba(226,232,240,0.90);
    border-radius: 14px;
    padding: 10px 11px;
    margin-bottom: 8px;

    box-shadow: 0 6px 14px rgba(15,23,42,0.035);
}

.news-card:last-child {
    margin-bottom: 0;
}

.news-tag {
    display: inline-block;

    margin-bottom: 5px;
    padding: 3px 7px;

    border-radius: 999px;
    background: rgba(7,17,31,0.95);
    color: #F4C542;

    font-size: 9px;
    font-weight: 900;
    text-transform: uppercase;
    letter-spacing: 0.04em;
}

.news-title {
    color: #07111F;
    font-family: 'Montserrat', sans-serif;
    font-size: 12.5px;
    font-weight: 900;
    line-height: 1.15;
    margin-bottom: 4px;
}

.news-text {
    color: #475569;
    font-size: 11.5px;
    font-weight: 650;
    line-height: 1.35;
}
.news-date {
    margin-top: 6px;
    color: #94a3b8;
    font-size: 9.5px;
    font-weight: 800;
}
/* ============================================================
   5B. MEDALLERO COMPACTO
   ============================================================ */

.medallero-grid {
    display: grid;
    grid-template-columns: repeat(3, minmax(0, 1fr));
    gap: 8px;
}

.medallero-card {
    min-width: 0;
    min-height: 124px;

    background:
        linear-gradient(
            180deg,
            rgba(255,255,255,0.66),
            rgba(248,250,252,0.46)
        );

    border: 1px solid rgba(226,232,240,0.95);
    border-radius: 15px;

    padding: 7px 5px 8px 5px;
    text-align: center;

    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;

    box-shadow:
        0 8px 18px rgba(15,23,42,0.04),
        inset 0 1px 0 rgba(255,255,255,0.65);
}

.medallero-img {
    width: 76px;
    height: 76px;
    object-fit: contain;
    display: block;
    margin-bottom: 2px;

    filter: drop-shadow(0 8px 10px rgba(0,0,0,0.18));
}

.medallero-title {
    color: #07111F;
    font-family: 'Montserrat', sans-serif;
    font-size: 8px;
    font-weight: 900;
    line-height: 1.02;
    text-transform: uppercase;
    letter-spacing: 0.015em;

    margin-bottom: 2px;

    max-width: 100%;
    overflow: hidden;
    text-overflow: ellipsis;
}

.medallero-winner {
    color: #0f172a;
    font-size: 8.8px;
    font-weight: 900;
    line-height: 1.05;

    max-width: 100%;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
}

.medallero-detail {
    display: inline-block;

    margin-top: 4px;
    padding: 3px 7px;

    border-radius: 999px;

    background: rgba(7,17,31,0.96);
    border: 1px solid rgba(244,197,66,0.18);

    color: #F4C542;

    font-size: 7.3px;
    font-weight: 900;
    line-height: 1.05;

    max-width: 100%;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
}
.medallero-card.earned {
    border-color: rgba(244,197,66,0.38);
    background:
        linear-gradient(
            180deg,
            rgba(255,255,255,0.78),
            rgba(255,251,235,0.58)
        );
}

.medallero-card.locked {
    opacity: 0.92;
}
.medallero-side-panel {
    position: relative;
    overflow: hidden;

    background:
        linear-gradient(
            180deg,
            rgba(255,255,255,0.72),
            rgba(248,250,252,0.62)
        ),
        var(--medallero-bg);

    background-size: cover;
    background-position: center;
    background-repeat: no-repeat;

    border: 1px solid rgba(244,197,66,0.22);
}

.medallero-side-panel .community-side-header {
    position: relative;
    z-index: 2;
}

.medallero-side-panel .medallero-grid {
    position: relative;
    z-index: 2;
}

/* ============================================================
   5C. PULSO DE COMUNIDAD
   ============================================================ */

.community-stats-grid {
    display: grid;
    grid-template-columns: repeat(2, minmax(0, 1fr));
    gap: 8px;
}

.community-stat-mini {
    background: rgba(248,250,252,0.86);
    border: 1px solid rgba(226,232,240,0.88);
    border-radius: 14px;
    padding: 10px 8px;
    min-width: 0;
}

.community-stat-label {
    color: #64748b;
    font-size: 9px;
    font-weight: 900;
    text-transform: uppercase;
    letter-spacing: 0.04em;
    margin-bottom: 4px;
}

.community-stat-value {
    color: #07111F;
    font-family: 'Montserrat', sans-serif;
    font-size: 13px;
    font-weight: 900;
    line-height: 1.1;

    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
}

.foro-stat-box {
    background: rgba(248,250,252,0.82);
    border: 1px solid rgba(226,232,240,0.85);
    border-radius: 14px;
    padding: 12px;
    margin-bottom: 12px;
}

.foro-stat-title {
    font-size: 11px;
    color: #64748b;
    font-weight: 900;
    text-transform: uppercase;
    letter-spacing: 0.06em;
    margin-bottom: 8px;
}

.foro-stat-line {
    color: #0f172a;
    font-size: 13px;
    font-weight: 800;
    margin-bottom: 5px;
}

.foro-rule-list {
    color: #334155;
    font-size: 13px;
    font-weight: 700;
    line-height: 1.45;
}

/* ============================================================
   6. MOBILE
   ============================================================ */

@media (max-width: 768px) {
    .foro-title h1 {
        font-size: 28px;
    }

    .foro-title p {
        font-size: 12px;
    }

    .foro-panel,
    .foro-community-panel {
        padding: 13px;
        border-radius: 16px;
    }

    .foro-message-text {
        font-size: 13px;
    }

    .foro-message-body.has-image {
        display: block;
    }

    .foro-image-wrap {
        margin-top: 9px;
    }

    .foro-message-img {
        width: 100%;
        max-width: 100%;
        max-height: 230px;
    }
    .news-scroll {
        max-height: 160px;
    }

    .medallero-grid {
        grid-template-columns: repeat(3, minmax(0, 1fr));
        gap: 7px;
    }

    .medallero-card {
        min-height: 112px;
        padding: 6px 4px;
    }

    .medallero-img {
        width: 66px;
        height: 66px;
    }

    .medallero-title {
        font-size: 7.2px;
    }

    .medallero-winner {
        font-size: 8px;
    }

    .medallero-detail {
        font-size: 6.8px;
        padding: 3px 6px;
    }
    
}

    
</style>
""", unsafe_allow_html=True)

    # ============================================================
    # DATOS BASE
    # ============================================================

    if df_foro is None or df_foro.empty:
        df_foro = pd.DataFrame(
            columns=[
                "FECHA",
                "USUARIO",
                "NOMBRE",
                "MENSAJE",
                "PARTIDO_ID",
                "LIKES",
                "DISLIKES",
                "FORO_IMG_URL"
            ]
        )

    for col in ["FECHA", "USUARIO", "NOMBRE", "MENSAJE", "PARTIDO_ID", "LIKES", "DISLIKES", "FORO_IMG_URL"]:
        if col not in df_foro.columns:
            if col in ["LIKES", "DISLIKES"]:
                df_foro[col] = 0
            elif col == "PARTIDO_ID":
                df_foro[col] = 0
            else:
                df_foro[col] = ""

    user_data = st.session_state["user_data"]
    user_actual = user_data["USUARIO"]
    nombre_actual = user_data["NOMBRE"]
    rol_actual = str(user_data.get("ROL", "")).strip().lower()
    puede_cargar_noticias = rol_actual in ["admin", "colaborador"]
    
    if "foro_uploader_key" not in st.session_state:
        st.session_state.foro_uploader_key = 0
        
    try:
        df_noticias = conn.read(
            worksheet="NOTICIAS",
            ttl=60
        )
    except Exception:
        df_noticias = pd.DataFrame()

    if df_noticias is None or df_noticias.empty:
        df_noticias = pd.DataFrame(
            columns=[
                "FECHA",
                "TIPO",
                "TITULO",
                "TEXTO",
                "AUTOR",
                "VISIBLE",
                "PRIORIDAD"
            ]
        )

    for col in ["FECHA", "TIPO", "TITULO", "TEXTO", "AUTOR", "VISIBLE", "PRIORIDAD"]:
        if col not in df_noticias.columns:
            if col == "PRIORIDAD":
                df_noticias[col] = 99
            elif col == "VISIBLE":
                df_noticias[col] = "TRUE"
            else:
                df_noticias[col] = ""        

    # ============================================================
    # HELPERS
    # ============================================================

    def safe_int(value, default=0):
        try:
            return int(value)
        except Exception:
            return default

    def get_avatar(usuario):
        match = df_usuarios[
            df_usuarios["USUARIO"].astype(str) == str(usuario)
        ]

        if not match.empty:
            avatar = match.iloc[0].get("AVATAR_URL", "")
            if pd.notna(avatar) and str(avatar).strip() != "":
                return avatar

        return AVATAR_GENERICO

    def save_foro(df_new):
        conn.update(
            worksheet="FORO",
            data=df_new
        )
        st.cache_data.clear()
        st.rerun()

    def save_noticias(df_new):
        conn.update(
            worksheet="NOTICIAS",
            data=df_new
        )
        st.cache_data.clear()
        st.rerun()

    def normalizar_badges(valor):
        if valor is None:
            return []

        if isinstance(valor, list):
            return valor

        if isinstance(valor, str):
            limpio = (
                valor
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

    def buscar_ganador_badge(nombre_badge):
        if df_ranking is None or df_ranking.empty:
            return None

        if "BADGES" not in df_ranking.columns:
            return None

        for _, row in df_ranking.iterrows():
            badges_usuario = normalizar_badges(
                row.get("BADGES", [])
            )

            if nombre_badge in badges_usuario:
                return row

        return None

    def detalle_badge(nombre_badge, row):
        if row is None:
            return "Desde partido 5"

        puntos = int(row.get("PUNTOS", 0))
        exactos = int(row.get("EXACTOS", 0))
        generales = int(row.get("GENERALES", 0))

        if nombre_badge == "Puntero":
            return f"{puntos} pts"

        if nombre_badge == "Sr. Prode":
            return f"{exactos} exactos"

        if nombre_badge == "Siempre Suma":
            return f"{generales} generales"

        if nombre_badge == "Optimista del Gol":
            return "Mucho gol"

        if nombre_badge == "El Cholo":
            return "Modo bilardista"

        if nombre_badge == "Rey del Empate":
            return "Empató todo"

        if nombre_badge == "El Macaya":
            return "Analista del grupo"

        if nombre_badge == "El Misterioso":
            return "Perfil bajo"

        if nombre_badge == "El Distinto":
            return "Contra la corriente"

        return "Logro desbloqueado"
    
    # ============================================================
    # TÍTULO
    # ============================================================

    FORO_MURO_BG_URL = "https://storage.googleapis.com/foto-prode2026/Banners/CABEZA%20SECCION%20FINA.png"
    BADGES_WALL_BG_URL = "https://storage.googleapis.com/foto-prode2026/Banners/INSIGNIAS%20FONDO.png"
    
    st.markdown("""
<div class="foro-title">
<h1>💬 Comunidad</h1>
<p>El vestuario, el bar y el VAR emocional del grupo.</p>
</div>
""", unsafe_allow_html=True)

    col_main, col_side = st.columns([1.6, 1], gap="large")

    # ============================================================
    # COLUMNA PRINCIPAL — MURO
    # ============================================================

    with col_main:

        # ------------------------------------------------------------
        # HEADER DEL MURO
        # ------------------------------------------------------------

        st.markdown(
            f"""
<div class="foro-hero-header" style="--foro-header-bg: url('{FORO_MURO_BG_URL}');">
<div class="foro-hero-row">
<div class="foro-hero-icon">💬</div>
<div>
<div class="foro-hero-title">Muro de la Comunidad</div>
<div class="foro-hero-subtitle">Chascarrillos, fotos y comentarios mundialistas</div>
</div>
</div>
</div>
""",
            unsafe_allow_html=True
        )

        # ------------------------------------------------------------
        # FORMULARIO DE PUBLICACIÓN
        # ------------------------------------------------------------

        with st.expander("🔥 Publicar en el muro", expanded=False):
            with st.form("nuevo_post_full", clear_on_submit=True):

                texto = st.text_area(
                    "¿Qué tenés en mente?",
                    max_chars=250
                )

                img_file = st.file_uploader(
                    "Foto opcional",
                    type=["jpg", "jpeg", "png", "webp"],
                    help="Opcional. Ideal para fotos de juntadas, asados o cábalas.",
                    key=f"foro_img_uploader_{st.session_state.foro_uploader_key}"
                )

                if img_file is not None:
                    st.image(
                        img_file,
                        caption="Vista previa",
                        width=240
                    )

                submit = st.form_submit_button(
                    "🚀 Publicar",
                    use_container_width=True
                )

                if submit:
                    texto_limpio = texto.strip()

                    if not texto_limpio and img_file is None:
                        st.warning("Escribí un mensaje o subí una imagen.")
                        st.stop()

                    img_url = ""

                    if img_file is not None:
                        try:
                            img_url = upload_foro_image(
                                archivo=img_file,
                                usuario=user_actual
                            )

                            if str(img_url).startswith("Error:"):
                                st.error(img_url)
                                st.stop()

                        except Exception as e:
                            st.error(f"No se pudo subir la imagen: {e}")
                            st.stop()

                    nuevo_msg = {
                        "FECHA": (datetime.now() - timedelta(hours=3)).strftime("%d/%m %H:%M"),
                        "USUARIO": user_actual,
                        "NOMBRE": nombre_actual,
                        "MENSAJE": texto_limpio,
                        "PARTIDO_ID": 0,
                        "LIKES": 0,
                        "DISLIKES": 0,
                        "FORO_IMG_URL": img_url
                    }

                    df_update = pd.concat(
                        [df_foro, pd.DataFrame([nuevo_msg])],
                        ignore_index=True
                    )

                    st.session_state.foro_uploader_key += 1

                    save_foro(df_update)

        # ------------------------------------------------------------
        # FEED CON SCROLL
        # ------------------------------------------------------------

        with st.container(height=620):
            st.markdown('<div class="foro-feed">', unsafe_allow_html=True)

            if df_foro.empty:
                st.info("Todavía no hay mensajes en el foro.")

            else:
                for idx, m in df_foro.iloc[::-1].iterrows():
                    usuario_msg = str(m.get("USUARIO", ""))
                    es_mio = usuario_msg == str(user_actual)

                    foto_msg = get_avatar(usuario_msg)

                    nombre_msg = escape(str(m.get("NOMBRE", "Jugador")))
                    fecha_msg = escape(str(m.get("FECHA", "")))
                    mensaje_msg = escape(str(m.get("MENSAJE", "")))

                    img_url = str(m.get("FORO_IMG_URL", "")).strip()
                    img_html = ""

                    if img_url and img_url.lower() != "nan":
                        img_html = f"""
<div class="foro-image-wrap">
<img src="{escape(img_url, quote=True)}" class="foro-message-img">
</div>
"""

                    body_class = (
                        "foro-message-body has-image"
                        if img_html
                        else "foro-message-body"
                    )

                    own_pill = '<span class="foro-own-pill">TUYO</span>' if es_mio else ""
                    card_class = "foro-message-card mine" if es_mio else "foro-message-card"

                    st.markdown(
                        f"""
<div class="{card_class}">
<div class="foro-message-head">
<img src="{foto_msg}" class="foro-avatar">
<div class="foro-message-meta">
<div class="foro-message-name">{nombre_msg}{own_pill}</div>
<div class="foro-message-date">{fecha_msg}</div>
</div>
</div>

<div class="{body_class}">
<div class="foro-message-text">{mensaje_msg}</div>
{img_html}
</div>
</div>
""",
                        unsafe_allow_html=True
                    )

                    l_count = safe_int(m.get("LIKES", 0))
                    d_count = safe_int(m.get("DISLIKES", 0))

                    if es_mio:
                        opciones_accion = ["🗑️ Borrar"]
                    else:
                        opciones_accion = [
                            f"👍 {l_count}",
                            f"👎 {d_count}"
                        ]

                        if rol_actual == "admin":
                            opciones_accion.append("🗑️ Borrar")

                    accion = st.segmented_control(
                        "Acciones del mensaje",
                        options=opciones_accion,
                        selection_mode="single",
                        default=None,
                        key=f"foro_accion_{idx}",
                        label_visibility="collapsed",
                        width="stretch"
                    )

                    if accion is not None:
                        if accion.startswith("👍"):
                            df_foro.at[idx, "LIKES"] = l_count + 1
                            save_foro(df_foro)

                        elif accion.startswith("👎"):
                            df_foro.at[idx, "DISLIKES"] = d_count + 1
                            save_foro(df_foro)

                        elif accion.startswith("🗑️"):
                            df_new = df_foro.drop(idx).reset_index(drop=True)
                            save_foro(df_new)

            st.markdown("</div>", unsafe_allow_html=True)  # cierra foro-feed

    # ============================================================
    # COLUMNA DERECHA — NOTICIAS / MEDALLERO / STATS
    # ============================================================

    with col_side:
    
        # ------------------------------------------------------------
        # NOTICIAS
        # ------------------------------------------------------------

        noticias_visibles = df_noticias.copy()

        if "VISIBLE" in noticias_visibles.columns:
            noticias_visibles["VISIBLE_CHECK"] = (
                noticias_visibles["VISIBLE"]
                .astype(str)
                .str.strip()
                .str.upper()
            )

            noticias_visibles = noticias_visibles[
                noticias_visibles["VISIBLE_CHECK"].isin(
                    ["TRUE", "1", "1.0", "VERDADERO", "T"]
                )
            ]

        noticias_visibles["PRIORIDAD_NUM"] = pd.to_numeric(
            noticias_visibles["PRIORIDAD"],
            errors="coerce"
        ).fillna(99)

        noticias_visibles = noticias_visibles.sort_values(
            by=["PRIORIDAD_NUM", "FECHA"],
            ascending=[True, False]
        )

        noticias_html = ""

        if noticias_visibles.empty:
            noticias_html = """
<div class="news-card">
<div class="news-tag">Info</div>
<div class="news-title">Sin noticias por ahora</div>
<div class="news-text">Cuando haya novedades del Mundial o del Prode van a aparecer acá.</div>
</div>
"""
        else:
            for _, n in noticias_visibles.head(8).iterrows():
                tipo = escape(str(n.get("TIPO", "Info")))
                titulo = escape(str(n.get("TITULO", "")))
                texto = escape(str(n.get("TEXTO", "")))
                fecha = escape(str(n.get("FECHA", "")))

                noticias_html += f"""
<div class="news-card">
<div class="news-tag">{tipo}</div>
<div class="news-title">{titulo}</div>
<div class="news-text">{texto}</div>
<div class="news-date">{fecha}</div>
</div>
"""

        st.markdown(
            f"""
<div class="community-side-panel">
<div class="community-side-header">
<div class="community-side-icon">📰</div>
<div>
<div class="community-side-title">Noticias</div>
<div class="community-side-subtitle">Avisos, novedades y perlitas del Mundial</div>
</div>
</div>

<div class="news-scroll">
{noticias_html}
</div>
</div>
""",
            unsafe_allow_html=True
        )
        
        #-----CARGA DE NOTICIAS (SOLO ADMIN Y COLAB) ----------------
        if puede_cargar_noticias:
            with st.expander("➕ Cargar noticia", expanded=False):
                with st.form("form_nueva_noticia", clear_on_submit=True):

                    tipo_noticia = st.selectbox(
                        "Tipo",
                        [
                            "Noticia",
                            "Aviso",
                            "Prode",
                            "Comunidad",
                            "Partido"
                        ]
                    )

                    titulo_noticia = st.text_input(
                        "Título",
                        max_chars=80
                    )

                    texto_noticia = st.text_area(
                        "Texto",
                        max_chars=240
                    )

                    visible_noticia = st.toggle(
                        "Visible",
                        value=True
                    )

                    prioridad_noticia = st.number_input(
                        "Prioridad",
                        min_value=1,
                        max_value=99,
                        value=5,
                        step=1,
                        help="1 aparece más arriba. 99 aparece más abajo."
                    )

                    submit_noticia = st.form_submit_button(
                        "📰 Publicar noticia",
                        use_container_width=True
                    )

                    if submit_noticia:
                        if not titulo_noticia.strip() or not texto_noticia.strip():
                            st.warning("Completá título y texto.")
                            st.stop()

                        nueva_noticia = {
                            "FECHA": (datetime.now() - timedelta(hours=3)).strftime("%d/%m %H:%M"),
                            "TIPO": tipo_noticia,
                            "TITULO": titulo_noticia.strip(),
                            "TEXTO": texto_noticia.strip(),
                            "AUTOR": nombre_actual,
                            "VISIBLE": "TRUE" if visible_noticia else "FALSE",
                            "PRIORIDAD": prioridad_noticia
                        }

                        df_noticias_update = pd.concat(
                            [
                                df_noticias,
                                pd.DataFrame([nueva_noticia])
                            ],
                            ignore_index=True
                        )

                        save_noticias(df_noticias_update)
                        
            with st.expander("🛠️ Gestionar noticias", expanded=False):

                if df_noticias.empty:
                    st.info("Todavía no hay noticias cargadas.")

                else:
                    df_editor_noticias = df_noticias.copy()

                    columnas_editor = [
                        "FECHA",
                        "TIPO",
                        "TITULO",
                        "TEXTO",
                        "AUTOR",
                        "VISIBLE",
                        "PRIORIDAD"
                    ]

                    for col in columnas_editor:
                        if col not in df_editor_noticias.columns:
                            if col == "PRIORIDAD":
                                df_editor_noticias[col] = 99
                            elif col == "VISIBLE":
                                df_editor_noticias[col] = "TRUE"
                            else:
                                df_editor_noticias[col] = ""

                    df_editor_noticias = df_editor_noticias[columnas_editor]

                    edited_noticias = st.data_editor(
                        df_editor_noticias,
                        use_container_width=True,
                        hide_index=True,
                        num_rows="fixed",
                        key="editor_gestion_noticias",
                        disabled=[
                            "FECHA",
                            "AUTOR"
                        ],
                        column_config={
                            "FECHA": st.column_config.TextColumn(
                                "Fecha",
                                disabled=True,
                                width="small"
                            ),
                            "TIPO": st.column_config.SelectboxColumn(
                                "Tipo",
                                options=[
                                    "Noticia",
                                    "Aviso",
                                    "Prode",
                                    "Comunidad",
                                    "Partido"
                                ],
                                width="small"
                            ),
                            "TITULO": st.column_config.TextColumn(
                                "Título",
                                max_chars=80,
                                width="medium"
                            ),
                            "TEXTO": st.column_config.TextColumn(
                                "Texto",
                                max_chars=240,
                                width="large"
                            ),
                            "AUTOR": st.column_config.TextColumn(
                                "Autor",
                                disabled=True,
                                width="small"
                            ),
                            "VISIBLE": st.column_config.SelectboxColumn(
                                "Visible",
                                options=[
                                    "TRUE",
                                    "FALSE"
                                ],
                                width="small"
                            ),
                            "PRIORIDAD": st.column_config.NumberColumn(
                                "Prioridad",
                                min_value=1,
                                max_value=99,
                                step=1,
                                width="small"
                            ),
                        }
                    )

                    if st.button(
                        "💾 Guardar cambios en noticias",
                        use_container_width=True
                    ):
                        conn.update(
                            worksheet="NOTICIAS",
                            data=edited_noticias
                        )

                        st.cache_data.clear()
                        st.success("✅ Noticias actualizadas correctamente.")
                        st.rerun()
        # ------------------------------------------------------------
        # MEDALLERO DEL PRODE — PROVISORIO
        # ------------------------------------------------------------

        BADGE_ASSET_BASE_URL = "https://storage.googleapis.com/foto-prode2026/badges"

        badge_asset_map = {
            "Puntero": {
                "large": f"{BADGE_ASSET_BASE_URL}/puntero/PUNTERO_LARGE_512.png",
                "gray_large": f"{BADGE_ASSET_BASE_URL}/puntero/PUNTERO_LARGE_GRAY_512.png",
            },
            "Sr. Prode": {
                "large": f"{BADGE_ASSET_BASE_URL}/srprode/SRPRODE_LARGE_512.png",
                "gray_large": f"{BADGE_ASSET_BASE_URL}/srprode/SRPRODE_LARGE_GRAY_512.png",
            },
            "Siempre Suma": {
                "large": f"{BADGE_ASSET_BASE_URL}/suma/SUMA_LARGE_512.png",
                "gray_large": f"{BADGE_ASSET_BASE_URL}/suma/SUMA_LARGE_GRAY_512.png",
            },
            "Optimista del Gol": {
                "large": f"{BADGE_ASSET_BASE_URL}/optimista/OPTIMISTA_LARGE_512.png",
                "gray_large": f"{BADGE_ASSET_BASE_URL}/optimista/OPTIMISTA_LARGE_GRAY_512.png",
            },
            "El Cholo": {
                "large": f"{BADGE_ASSET_BASE_URL}/elcholo/ELCHOLO_LARGE_512.png",
                "gray_large": f"{BADGE_ASSET_BASE_URL}/elcholo/ELCHOLO_LARGE_GRAY_512.png",
            },
            "Rey del Empate": {
                "large": f"{BADGE_ASSET_BASE_URL}/empate/EMPATE_LARGE_512.png",
                "gray_large": f"{BADGE_ASSET_BASE_URL}/empate/EMPATE_LARGE_GRAY_512.png",
            },
            "El Macaya": {
                "large": f"{BADGE_ASSET_BASE_URL}/macaya/MACAYA_LARGE_512.png",
                "gray_large": f"{BADGE_ASSET_BASE_URL}/macaya/MACAYA_LARGE_GRAY_512.png",
            },
            "El Misterioso": {
                "large": f"{BADGE_ASSET_BASE_URL}/misterioso/MISTERIOSO_LARGE_512.png",
                "gray_large": f"{BADGE_ASSET_BASE_URL}/misterioso/MISTERIOSO_LARGE_GRAY_512.png",
            },
            "El Distinto": {
                "large": f"{BADGE_ASSET_BASE_URL}/distinto/DISTINTO_LARGE_512.png",
                "gray_large": f"{BADGE_ASSET_BASE_URL}/distinto/DISTINTO_LARGE_GRAY_512.png",
            },
        }

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

        medallero_html = ""

        for title in badge_order:
            ganador_row = buscar_ganador_badge(title)
            assets = badge_asset_map.get(title, {})

            if ganador_row is None:
                badge_img = assets.get("gray_large", "")
                winner_txt = "🔒 Sin dueño"
                detail_txt = "Desde partido 5"
                state_class = "locked"
            else:
                badge_img = assets.get("large", "") or assets.get("gray_large", "")
                winner_txt = f"👤 {str(ganador_row.get('JUGADOR', '-'))}"
                detail_txt = detalle_badge(title, ganador_row)
                state_class = "earned"

            medallero_html += f"""
<div class="medallero-card {state_class}">
<img src="{escape(badge_img, quote=True)}" class="medallero-img" loading="lazy" alt="{escape(title)}">
<div class="medallero-title">{escape(title)}</div>
<div class="medallero-winner">{escape(winner_txt)}</div>
<div class="medallero-detail">{escape(detail_txt)}</div>
</div>
"""

        st.markdown(
            f"""
<div class="community-side-panel">
<div class="community-side-header">
<div class="community-side-icon">🏅</div>
<div>
<div class="community-side-title">Medallero del Prode</div>
<div class="community-side-subtitle">Reconocimientos y gloria comunitaria</div>
</div>
</div>

<div class="medallero-grid">
{medallero_html}
</div>
</div>
""",
            unsafe_allow_html=True
        )
        # ------------------------------------------------------------
        # DATOS DE COMUNIDAD
        # ------------------------------------------------------------

        if df_foro.empty:
            top_com = pd.Series(dtype=int)
            top_likes = pd.Series(dtype=int)
            top_dis = pd.Series(dtype=int)
        else:
            top_com = df_foro["NOMBRE"].value_counts().head(3)

            df_foro["LIKES"] = pd.to_numeric(
                df_foro["LIKES"],
                errors="coerce"
            ).fillna(0)

            df_foro["DISLIKES"] = pd.to_numeric(
                df_foro["DISLIKES"],
                errors="coerce"
            ).fillna(0)

            top_likes = (
                df_foro.groupby("NOMBRE")["LIKES"]
                .sum()
                .sort_values(ascending=False)
                .head(1)
            )

            top_dis = (
                df_foro.groupby("NOMBRE")["DISLIKES"]
                .sum()
                .sort_values(ascending=False)
                .head(1)
            )

        agitadores_html = ""

        if top_com.empty:
            agitadores_html = '<div class="foro-stat-line">Sin mensajes todavía</div>'
        else:
            for nombre, cant in top_com.items():
                agitadores_html += (
                    f'<div class="foro-stat-line">💬 {escape(str(nombre))} ({cant})</div>'
                )

        popularidad_html = ""

        if top_likes.empty:
            popularidad_html += '<div class="foro-stat-line">🌟 Sin likes todavía</div>'
        else:
            for n, t in top_likes.items():
                if t > 0:
                    popularidad_html += (
                        f'<div class="foro-stat-line">🌟 Más bancado: {escape(str(n))}</div>'
                    )
                else:
                    popularidad_html += '<div class="foro-stat-line">🌟 Sin likes todavía</div>'

        if top_dis.empty:
            popularidad_html += '<div class="foro-stat-line">🍋 Sin polémicas</div>'
        else:
            for n, t in top_dis.items():
                if t > 0:
                    popularidad_html += (
                        f'<div class="foro-stat-line">🍋 Más polémico: {escape(str(n))}</div>'
                    )
                else:
                    popularidad_html += '<div class="foro-stat-line">🍋 Sin polémicas</div>'

        total_mensajes = len(df_foro)
        if top_com.empty:
            top_agitador_txt = "Sin mensajes"
        else:
            top_nombre = str(top_com.index[0])
            top_cant = int(top_com.iloc[0])
            top_agitador_txt = f"💬 {top_nombre} ({top_cant})"

        if top_likes.empty or int(top_likes.iloc[0]) <= 0:
            mas_bancado_txt = "🌟 Sin likes"
        else:
            mas_bancado_txt = f"🌟 {str(top_likes.index[0])}"

        if top_dis.empty or int(top_dis.iloc[0]) <= 0:
            mas_polemico_txt = "🍋 Sin polémicas"
        else:
            mas_polemico_txt = f"🍋 {str(top_dis.index[0])}"

        # ------------------------------------------------------------
        # COMUNIDAD — cerrado por defecto
        # ------------------------------------------------------------
   
        st.markdown(
            f"""
<div class="community-side-panel">
<div class="community-side-header">
<div class="community-side-icon">📊</div>
<div>
<div class="community-side-title">Pulso de Comunidad</div>
<div class="community-side-subtitle">Actividad, banca y polémica del grupo</div>
</div>
</div>

<div class="community-stats-grid">
<div class="community-stat-mini">
<div class="community-stat-label">Mensajes</div>
<div class="community-stat-value">💬 {total_mensajes}</div>
</div>

<div class="community-stat-mini">
<div class="community-stat-label">Top agitador</div>
<div class="community-stat-value">{escape(top_agitador_txt)}</div>
</div>

<div class="community-stat-mini">
<div class="community-stat-label">Más bancado</div>
<div class="community-stat-value">{escape(mas_bancado_txt)}</div>
</div>

<div class="community-stat-mini">
<div class="community-stat-label">Polémica</div>
<div class="community-stat-value">{escape(mas_polemico_txt)}</div>
</div>
</div>
</div>
""",
            unsafe_allow_html=True
        )
