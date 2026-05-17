import streamlit as st

# ============================================================
# CONSTANTES GLOBALES
# ============================================================

AVATAR_GENERICO = "https://storage.googleapis.com/foto-prode2026/perfiles/images.png"

ICONO_APP = "https://storage.googleapis.com/foto-prode2026/Banners/ICONOAPP.png"

FONDO_BASE = "https://storage.googleapis.com/foto-prode2026/Banners/FONDO%20BASE.jpg"

SIDEBAR_BANNER = "https://storage.googleapis.com/foto-prode2026/Banners/SIDEBAR_NEWV2.png"

HEADER_BACKGROUND = "https://storage.googleapis.com/foto-prode2026/Banners/headder-background.png"

EVOL_HEADER_BACKGROUND = "https://storage.googleapis.com/foto-prode2026/Banners/headder-background.png"

BANNERS_PAGINA = {
    "inicio": HEADER_BACKGROUND,
    "mis_pronosticos": HEADER_BACKGROUND,
    "jugadores": HEADER_BACKGROUND,
    "foro": HEADER_BACKGROUND,
    "panel_control": HEADER_BACKGROUND,
    "laboratorio": HEADER_BACKGROUND,
}


# ============================================================
# ESTILOS GLOBALES
# ============================================================

def aplicar_estilos_globales():
    """
    Aplica estilos globales:
    - fondo general de la app
    - sidebar oscuro premium
    - tipografías base
    - estilos reutilizables para banners
    """

    css = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&family=Montserrat:wght@700;800;900&display=swap');

/* ============================================================
   TIPOGRAFÍA GLOBAL
   ============================================================ */

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
}

/* ============================================================
   FONDO GENERAL DE LA APP
   ============================================================ */

.stApp {
    background-image:
        linear-gradient(rgba(255,255,255,0.40), rgba(255,255,255,0.40)),
        url("__FONDO_BASE__");
    background-attachment: fixed;
    background-size: cover;
    background-position: center;
}

/* ============================================================
   SIDEBAR OSCURO PREMIUM
   ============================================================ */

[data-testid="stSidebar"] {
    background-color: #07111F;
    background-image:
        linear-gradient(
            rgba(7,17,31,0.57),
            rgba(7,17,31,0.66)
        ),
        url("__SIDEBAR_BANNER__");
    background-size: cover;
    background-position: center;
    border-right: 1px solid rgba(255,255,255,0.08);
}

/* Contenedor interno del sidebar */
[data-testid="stSidebar"] > div:first-child {
    padding-top: 24px;
    padding-left: 18px;
    padding-right: 18px;
}

/* Textos generales del sidebar */
[data-testid="stSidebar"] .stMarkdown,
[data-testid="stSidebar"] label,
[data-testid="stSidebar"] p,
[data-testid="stSidebar"] span,
[data-testid="stSidebar"] div {
    color: #F8FAFC;
}

/* Labels y textos secundarios */
[data-testid="stSidebar"] label,
[data-testid="stSidebar"] .stCaptionContainer {
    color: #94A3B8 !important;
    font-weight: 700 !important;
}

/* Títulos dentro del sidebar */
[data-testid="stSidebar"] h1,
[data-testid="stSidebar"] h2,
[data-testid="stSidebar"] h3 {
    color: #F8FAFC !important;
    font-family: 'Montserrat', sans-serif !important;
    font-weight: 900 !important;
    letter-spacing: -0.03em;
}

/* ============================================================
   RADIO / MENÚ DEL SIDEBAR
   ============================================================ */

/* Contenedor de opciones */
[data-testid="stSidebar"] div[role="radiogroup"] {
    gap: 6px;
}

/* Cada item del radio */
[data-testid="stSidebar"] div[role="radiogroup"] label {
    background: rgba(255,255,255,0.035);
    border: 1px solid rgba(255,255,255,0.07);
    border-radius: 12px;
    padding: 9px 11px;
    margin-bottom: 6px;
    transition: all 0.18s ease;
}

/* Texto dentro del item */
[data-testid="stSidebar"] div[role="radiogroup"] label p {
    color: #CBD5E1 !important;
    font-size: 14px !important;
    font-weight: 700 !important;
}

/* Hover */
[data-testid="stSidebar"] div[role="radiogroup"] label:hover {
    background: rgba(255,255,255,0.075);
    border-color: rgba(255,255,255,0.14);
}

/* Item activo */
[data-testid="stSidebar"] div[role="radiogroup"] label[data-baseweb="radio"] {
    position: relative;
}

/* Círculo del radio: lo ocultamos visualmente */
[data-testid="stSidebar"] div[role="radiogroup"] label > div:first-child {
    display: none;
}

/* Opción seleccionada */
[data-testid="stSidebar"] div[role="radiogroup"] label:has(input:checked) {
    background: rgba(244,197,66,0.14);
    border: 1px solid rgba(244,197,66,0.34);
    border-left: 4px solid #F4C542;
    box-shadow: 0 8px 20px rgba(244,197,66,0.08);
}

/* Texto de opción seleccionada */
[data-testid="stSidebar"] div[role="radiogroup"] label:has(input:checked) p {
    color: #F8FAFC !important;
    font-weight: 900 !important;
}

/* ============================================================
   BOTONES DEL SIDEBAR
   ============================================================ */

[data-testid="stSidebar"] button {
    background: rgba(255,255,255,0.06) !important;
    border: 1px solid rgba(255,255,255,0.14) !important;
    border-radius: 12px !important;
    color: #F8FAFC !important;
    font-weight: 800 !important;
    transition: all 0.18s ease;
}

[data-testid="stSidebar"] button:hover {
    background: rgba(244,197,66,0.12) !important;
    border-color: rgba(244,197,66,0.34) !important;
    color: #F8FAFC !important;
}

/* ============================================================
   INPUTS / CAMPOS EN SIDEBAR
   ============================================================ */

[data-testid="stSidebar"] input,
[data-testid="stSidebar"] textarea,
[data-testid="stSidebar"] select {
    background: rgba(255,255,255,0.08) !important;
    color: #F8FAFC !important;
    border-radius: 10px !important;
    border: 1px solid rgba(255,255,255,0.14) !important;
}

[data-testid="stSidebar"] input::placeholder {
    color: #94A3B8 !important;
}

/* ============================================================
   COMPONENTES REUTILIZABLES PARA SIDEBAR
   Los usaremos luego desde app.py
   ============================================================ */

.sidebar-brand {
    margin-bottom: 26px;
    padding-bottom: 18px;
    border-bottom: 1px solid rgba(255,255,255,0.12);
}

.sidebar-brand-title {
    font-family: 'Montserrat', sans-serif;
    font-size: 19px;
    font-weight: 900;
    line-height: 1.05;
    letter-spacing: 0.02em;
    color: #F8FAFC;
    text-transform: uppercase;
}

.sidebar-brand-title span {
    color: #F4C542;
}

.sidebar-brand-subtitle {
    margin-top: 7px;
    font-size: 10px;
    font-weight: 700;
    color: #94A3B8;
    text-transform: uppercase;
    letter-spacing: 0.08em;
}

.sidebar-user-box {
    background: rgba(255,255,255,0.055);
    border: 1px solid rgba(255,255,255,0.10);
    border-radius: 14px;
    padding: 12px;
    margin-bottom: 22px;
}

.sidebar-user-label {
    font-size: 10px;
    font-weight: 800;
    color: #94A3B8;
    text-transform: uppercase;
    letter-spacing: 0.08em;
}

.sidebar-user-name {
    margin-top: 3px;
    font-size: 14px;
    font-weight: 900;
    color: #F8FAFC;
}

.sidebar-section-label {
    font-size: 11px;
    font-weight: 900;
    color: #F4C542;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    margin: 18px 0 10px 0;
}

.sidebar-footer {
    margin-top: 28px;
    padding-top: 18px;
    border-top: 1px solid rgba(255,255,255,0.12);
    font-size: 11px;
    line-height: 1.45;
    color: #94A3B8;
    opacity: 0.85;
}

.sidebar-footer strong {
    color: #F8FAFC;
    font-weight: 900;
}

/* ============================================================
   BANNERS REUTILIZABLES DE PÁGINA
   ============================================================ */

.app-section-banner {
    position: relative;
    border-radius: 18px;
    overflow: hidden;
    margin-bottom: 24px;
    padding: 34px 38px;
    min-height: 150px;

    display: flex;
    flex-direction: column;
    justify-content: center;

    color: white;
    background-size: cover;
    background-position: center;
    border: 1px solid rgba(255,255,255,0.10);
    box-shadow: 0 18px 45px rgba(15,23,42,0.22);
}

.app-section-banner::before {
    content: "";
    position: absolute;
    inset: 0;
    background:
        linear-gradient(90deg, rgba(0,0,0,0.86), rgba(0,0,0,0.38)),
        radial-gradient(circle at right, rgba(244,197,66,0.18), transparent 38%);
    z-index: 0;
}

.app-section-banner-content {
    position: relative;
    z-index: 1;
}

.app-section-title {
    font-family: 'Montserrat', sans-serif;
    font-size: 28px;
    font-weight: 900;
    line-height: 1.05;
    margin: 0;
    letter-spacing: -0.04em;
    text-transform: uppercase;
}

.app-section-subtitle {
    margin-top: 8px;
    font-size: 14px;
    font-weight: 600;
    color: rgba(255,255,255,0.72);
}

/* ============================================================
   RESPONSIVE
   ============================================================ */

@media (max-width: 768px) {
    .app-section-banner {
        padding: 26px 22px;
        min-height: 120px;
        border-radius: 16px;
    }

    .app-section-title {
        font-size: 22px;
    }

    .app-section-subtitle {
        font-size: 12px;
    }
}
</style>
"""

    css = css.replace("__FONDO_BASE__", FONDO_BASE)
    css = css.replace("__SIDEBAR_BANNER__", SIDEBAR_BANNER)

    st.markdown(css, unsafe_allow_html=True)


# ============================================================
# BANNER REUTILIZABLE POR PÁGINA
# ============================================================

def dibujar_banner_pagina(
    titulo="PRODE MUNDIAL 2026",
    subtitulo="La gloria está en tus predicciones",
    banner_key="inicio"
):
    """
    Renderiza un banner horizontal reutilizable por pestaña.
    """

    imagen = BANNERS_PAGINA.get(
        banner_key,
        BANNERS_PAGINA["inicio"]
    )

    st.markdown(f"""
<div class="app-section-banner" style="background-image: url('{imagen}');">
    <div class="app-section-banner-content">
        <h1 class="app-section-title">{titulo}</h1>
        <div class="app-section-subtitle">{subtitulo}</div>
    </div>
</div>
""", unsafe_allow_html=True)


# ============================================================
# BANNER ANTIGUO - COMPATIBILIDAD
# ============================================================

def dibujar_banner():
    """
    Banner antiguo.
    Se conserva para no romper imports viejos, pero idealmente no usarlo.
    """

    dibujar_banner_pagina(
        titulo="🏆 PRODE MUNDIAL 2026",
        subtitulo="¡La gloria está en tus predicciones!",
        banner_key="inicio"
    )

def mostrar_decalogo():
    st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@500;600;700;800;900&family=Oswald:wght@500;600;700&display=swap');

:root {
    --bg-main: #0C1624;
    --bg-card: #162334;
    --bg-card-soft: #1B2A3D;
    --title: #F4F7FB;
    --subtitle: #F2F6FA;
    --text: #FFFFFF;
    --muted: #8FA3B8;
    --accent-soft: #B8C7D9;
    --champagne: #D7C6A0;
    --border: rgba(255,255,255,0.08);
    --border-strong: rgba(255,255,255,0.12);
    --shadow: 0 18px 40px rgba(3, 10, 20, 0.34);
}

.decalogo-card {
    position: relative;
    overflow: hidden;
    width: 100%;
    max-width: 860px;
    margin: 0 auto;
    background:
        radial-gradient(
            circle at 50% 0%,
            rgba(215,198,160,0.05),
            rgba(215,198,160,0.00) 26%
        ),
        linear-gradient(
            180deg,
            #162334 0%,
            #0C1624 100%
        );
    border: 1px solid rgba(215,198,160,0.12);
    border-radius: 22px;
    padding: 26px 22px 22px 22px;
    box-shadow: var(--shadow);
}

.decalogo-card::before {
    content: "";
    position: absolute;
    top: 0;
    left: 24px;
    right: 24px;
    height: 1px;
    background: linear-gradient(
        90deg,
        rgba(215,198,160,0.00),
        rgba(215,198,160,0.85),
        rgba(215,198,160,0.00)
    );
}

.decalogo-header {
    text-align: center;
    margin-bottom: 15px;
}

.decalogo-title {
    margin: 0;
    color: var(--title);
    font-family: 'Oswald', 'Barlow Condensed', sans-serif;
    font-size: 31px;
    font-weight: 600;
    line-height: 1.02;
    letter-spacing: 0.04em;
    text-transform: uppercase;
}

.decalogo-lead {
    max-width: 560px;
    margin: 10px auto 0 auto;
    color: var(--muted);
    font-family: 'Inter', sans-serif;
    font-size: 13px;
    font-weight: 600;
    line-height: 1.45;
}

.decalogo-divider {
    width: 74px;
    height: 2px;
    margin: 16px auto 0 auto;
    border-radius: 999px;
    background: linear-gradient(
        90deg,
        rgba(215,198,160,0.00),
        rgba(215,198,160,0.95),
        rgba(215,198,160,0.00)
    );
}

.decalogo-list {
    list-style: none;
    margin: 0;
    padding: 0;
    display: flex;
    flex-direction: column;
    gap: 10px;
}

.decalogo-item {
    display: grid;
    grid-template-columns: 44px minmax(0, 1fr);
    gap: 12px;
    align-items: start;
    padding: 14px 14px;
    border-radius: 16px;
    border: 1px solid var(--border);
    background: linear-gradient(
        180deg,
        rgba(255,255,255,0.035),
        rgba(255,255,255,0.025)
    );
    box-shadow:
        inset 0 1px 0 rgba(255,255,255,0.03),
        0 8px 18px rgba(0,0,0,0.10);
}

.decalogo-number {
    width: 34px;
    height: 34px;
    display: flex;
    align-items: center;
    justify-content: center;
    border-radius: 11px;
    border: 1px solid rgba(215,198,160,0.16);
    background: rgba(255,255,255,0.035);
    color: var(--accent-soft);
    font-family: 'Oswald', sans-serif;
    font-size: 14px;
    font-weight: 600;
    line-height: 1;
    letter-spacing: 0.04em;
}

.decalogo-content {
    min-width: 0;
}

.decalogo-rule-title {
    margin: 0 0 5px 0;

    color: #F4F7FB;
    font-family: 'Inter', sans-serif;
    font-size: 14.5px;
    font-weight: 900;
    line-height: 1.24;
    letter-spacing: 0.01em;
}

.decalogo-rule-text {
    margin: 0;

    color: #ffffff;
    font-family: 'Inter', sans-serif;
    font-size: 13px;
    font-weight: 150;
    line-height: 1.56;
}

.decalogo-item:hover {
    background: linear-gradient(
        180deg,
        rgba(255,255,255,0.048),
        rgba(255,255,255,0.032)
    );
    border-color: var(--border-strong);
}

@media (max-width: 768px) {
    .decalogo-card {
        border-radius: 18px;
        padding: 20px 22px 22px 22px;
    }

    .decalogo-title {
        font-size: 24px;
        line-height: 1.06;
    }

    .decalogo-lead {
        font-size: 12px;
        max-width: 100%;
    }

    .decalogo-list {
        gap: 8px;
    }

    .decalogo-item {
        grid-template-columns: 38px minmax(0, 1fr);
        gap: 10px;
        padding: 12px 11px;
        border-radius: 14px;
    }

    .decalogo-number {
        width: 30px;
        height: 30px;
        border-radius: 10px;
        font-size: 12px;
    }

    .decalogo-rule-title {
        font-size: 13px;
    }

    .decalogo-rule-text {
        font-size: 12px;
        line-height: 1.48;
    }
}
</style>

<section class="decalogo-card">
<header class="decalogo-header">
<h2 class="decalogo-title">El Decálogo del Prode</h2>
<p class="decalogo-lead">Las reglas sagradas para jugar, cargar y sobrevivir al VAR emocional.</p>
<div class="decalogo-divider"></div>
</header>

<ol class="decalogo-list">
<li class="decalogo-item">
<span class="decalogo-number">01</span>
<div class="decalogo-content">
<h3 class="decalogo-rule-title">Respetar al rival</h3>
<p class="decalogo-rule-text">La chicana es parte del juego, la falta de respeto no.</p>
</div>
</li>

<li class="decalogo-item">
<span class="decalogo-number">02</span>
<div class="decalogo-content">
<h3 class="decalogo-rule-title">Ley del VAR</h3>
<p class="decalogo-rule-text">¡Prohibido llorar por el VAR!, a Pe-la-se!.</p>
</div>
</li>

<li class="decalogo-item">
<span class="decalogo-number">03</span>
<div class="decalogo-content">
<h3 class="decalogo-rule-title">Fair Play</h3>
<p class="decalogo-rule-text">No tontié, no pidas que te editen un resultado después del 8/6.</p>
</div>
</li>

<li class="decalogo-item">
<span class="decalogo-number">04</span>
<div class="decalogo-content">
<h3 class="decalogo-rule-title">El Puntero</h3>
<p class="decalogo-rule-text">Al que va primero en el ranking se le respeta... o se le envidia.</p>
</div>
</li>

<li class="decalogo-item">
<span class="decalogo-number">05</span>
<div class="decalogo-content">
<h3 class="decalogo-rule-title">Grito de Gol</h3>
<p class="decalogo-rule-text">Se permite escribir "¡GOOOOL!" en mayúsculas.</p>
</div>
</li>

<li class="decalogo-item">
<span class="decalogo-number">06</span>
<div class="decalogo-content">
<h3 class="decalogo-rule-title">La Cábala</h3>
<p class="decalogo-rule-text">No se revelan las cábalas personales.</p>
</div>
</li>

<li class="decalogo-item">
<span class="decalogo-number">07</span>
<div class="decalogo-content">
<h3 class="decalogo-rule-title">Oliver Atom</h3>
<p class="decalogo-rule-text">Recuerda que: "¡El balón está vivo!" y que "El partido no se termina hasta que se termina".</p>
</div>
</li>

<li class="decalogo-item">
<span class="decalogo-number">08</span>
<div class="decalogo-content">
<h3 class="decalogo-rule-title">Sabiduría</h3>
<p class="decalogo-rule-text">Si no sabes de fútbol, fingí que sí; los puntos no mienten wachx.</p>
</div>
</li>

<li class="decalogo-item">
<span class="decalogo-number">09</span>
<div class="decalogo-content">
<h3 class="decalogo-rule-title">Puntualidad</h3>
<p class="decalogo-rule-text">No dejes para mañana el pronóstico que puedes cargar hoy, amen.</p>
</div>
</li>

<li class="decalogo-item">
<span class="decalogo-number">10</span>
<div class="decalogo-content">
<h3 class="decalogo-rule-title">La Gloria</h3>
<p class="decalogo-rule-text">¡Disfrutar el mundial! ⚽</p>
</div>
</li>
</ol>
</section>
""", unsafe_allow_html=True)
