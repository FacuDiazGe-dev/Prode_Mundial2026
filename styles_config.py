import streamlit as st

# ============================================================
# CONSTANTES GLOBALES
# ============================================================

AVATAR_GENERICO = "https://storage.googleapis.com/foto-prode2026/perfiles/images.png"

ICONO_APP = "https://storage.googleapis.com/foto-prode2026/Banners/ICONOAPP.png"

FONDO_BASE = "https://storage.googleapis.com/foto-prode2026/Banners/FONDO%20BASE.jpg"

SIDEBAR_BANNER = "https://storage.googleapis.com/foto-prode2026/Banners/BANNER%20VERTICAL_V3.jpg"

HEADER_BACKGROUND = "https://storage.googleapis.com/foto-prode2026/Banners/headder-background.png"

HEADER_BACKGROUND = "https://storage.googleapis.com/foto-prode2026/Banners/headder-background.png"

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
    - fondo del sidebar
    - tipografías base
    - estilos reutilizables para banners
    """

    css = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;700;800;900&family=Montserrat:wght@700;800;900&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
}

.stApp {
    background-image:
        linear-gradient(rgba(255,255,255,0.80), rgba(255,255,255,0.80)),
        url("__FONDO_BASE__");
    background-attachment: fixed;
    background-size: cover;
    background-position: center;
}

[data-testid="stSidebar"] {
    background-image:
        linear-gradient(rgba(0,0,0,0.70), rgba(0,0,0,0.82)),
        url("__SIDEBAR_BANNER__");
    background-size: cover;
    background-position: center;
}

[data-testid="stSidebar"] .stMarkdown,
[data-testid="stSidebar"] label,
[data-testid="stSidebar"] .stRadio p,
[data-testid="stSidebar"] h1,
[data-testid="stSidebar"] h2,
[data-testid="stSidebar"] h3,
[data-testid="stSidebar"] p {
    color: #FFFFFF !important;
    font-weight: 800 !important;
    text-shadow: 2px 2px 8px rgba(0,0,0,0.85) !important;
}

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
    """Renderiza el decálogo azul profundo con tus frases personalizadas."""
    st.markdown("""
        <div style="background: rgba(240, 242, 246, 0.85); padding: 25px; border-radius: 15px; border: 1px solid rgba(3, 41, 73, 0.2); backdrop-filter: blur(10px); box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.15);">
            <h4 style="text-align: center; color: rgb(3, 41, 73); margin-top: 0; margin-bottom: 25px; font-family: sans-serif; letter-spacing: 2px; font-weight: 800; text-transform: uppercase;">📜 EL DECÁLOGO DEL PRODE</h4>
            <ol style="font-size: 0.95em; color: #333333; padding-left: 25px; font-family: sans-serif;">
                <li style="margin-bottom: 15px; line-height: 1.6; font-weight: bold; color: rgb(3, 41, 73);">
                    <span style="font-weight: normal; color: #333333;"><b style="color: rgb(3, 41, 73);">Respetar al rival:</b> La chicana es parte del juego, la falta de respeto no.</span>
                </li>
                <li style="margin-bottom: 15px; line-height: 1.6; font-weight: bold; color: rgb(3, 41, 73);">
                    <span style="font-weight: normal; color: #333333;"><b style="color: rgb(3, 41, 73);">Ley del VAR:</b> ¡Prohibido llorar por el VAR!, a Pe-la-se!.</span>
                </li>
                <li style="margin-bottom: 15px; line-height: 1.6; font-weight: bold; color: rgb(3, 41, 73);">
                    <span style="font-weight: normal; color: #333333;"><b style="color: rgb(3, 41, 73);">Fair Play:</b> No tontié, no pidas que te editen un resultado después del 8/6.</span>
                </li>
                <li style="margin-bottom: 15px; line-height: 1.6; font-weight: bold; color: rgb(3, 41, 73);">
                    <span style="font-weight: normal; color: #333333;"><b style="color: rgb(3, 41, 73);">El Puntero:</b> Al que va primero en el ranking se le respeta... o se le envidia.</span>
                </li>
                <li style="margin-bottom: 15px; line-height: 1.6; font-weight: bold; color: rgb(3, 41, 73);">
                    <span style="font-weight: normal; color: #333333;"><b style="color: rgb(3, 41, 73);">Grito de Gol:</b> Se permite escribir "¡GOOOOL!" en mayúsculas.</span>
                </li>
                <li style="margin-bottom: 15px; line-height: 1.6; font-weight: bold; color: rgb(3, 41, 73);">
                    <span style="font-weight: normal; color: #333333;"><b style="color: rgb(3, 41, 73);">La Cábala:</b> No se revelan las cábalas personales.</span>
                </li>
                <li style="margin-bottom: 15px; line-height: 1.6; font-weight: bold; color: rgb(3, 41, 73);">
                    <span style="font-weight: normal; color: #333333;"><b style="color: rgb(3, 41, 73);">Oliver Atom:</b> Recuerda que: "¡El balón está vivo!" y que "El partido no se termina hasta que se termina".</span>
                </li>
                <li style="margin-bottom: 15px; line-height: 1.6; font-weight: bold; color: rgb(3, 41, 73);">
                    <span style="font-weight: normal; color: #333333;"><b style="color: rgb(3, 41, 73);">Sabiduría:</b> Si no sabes de fútbol, fingí que sí; los puntos no mienten wachx.</span>
                </li>
                <li style="margin-bottom: 15px; line-height: 1.6; font-weight: bold; color: rgb(3, 41, 73);">
                    <span style="font-weight: normal; color: #333333;"><b style="color: rgb(3, 41, 73);">Puntualidad:</b> No dejes para mañana el pronóstico que puedes cargar hoy, amen.</span>
                </li>
                <li style="margin-bottom: 15px; line-height: 1.6; font-weight: bold; color: rgb(3, 41, 73);">
                    <span style="font-weight: normal; color: #333333;"><b style="color: rgb(3, 41, 73);">La Gloria:</b> ¡Disfrutar el mundial! ⚽</span>
                </li>
            </ol>
        </div>
    """, unsafe_allow_html=True)
