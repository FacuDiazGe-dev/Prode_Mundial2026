import streamlit as st

# --- CONSTANTES ---
AVATAR_GENERICO = "https://storage.googleapis.com/foto-prode2026/perfiles/images.png"

def aplicar_estilos_globales():
    """Inyecta el CSS para fondos, sidebar y banners."""
    st.markdown(f"""
        <style>
        /* 1. Fondo base del sitio */
        .stApp {{
            background-image: url("https://storage.googleapis.com/foto-prode2026/Banners/FONDO%20BASE.jpg");
            background-attachment: fixed;
            background-size: cover;
        }}

        /* 2. Banner Vertical en el Sidebar y contraste de letras */
        [data-testid="stSidebar"] {{
            background-image: url("https://storage.googleapis.com/foto-prode2026/Banners/BANNER%20VERTICAL_V3.jpg");
            background-size: cover;
            background-position: center;
        }}

        /* Estilo de letras en Sidebar para fondo oscuro */
        [data-testid="stSidebar"] .stMarkdown, 
        [data-testid="stSidebar"] label, 
        [data-testid="stSidebar"] .stRadio p,
        [data-testid="stSidebar"] h3 {{
            color: #FFFFFF !important;
            font-weight: 800 !important;
            text-shadow: 2px 2px 8px #000000, 0px 0px 10px #000000 !important;
        }}

        /* 3. Banner Superior Horizontal */
        .banner-superior {{
            background-image: linear-gradient(rgba(0,0,0,0.3), rgba(0,0,0,0.3)), 
                              url("https://storage.googleapis.com/foto-prode2026/Banners/BANNER%20HORIZONTAL.jpg");
            background-size: cover;
            background-position: center 10%;
            padding: 50px;
            border-radius: 15px;
            text-align: center;
            color: white;
            margin-bottom: 25px;
            box-shadow: 0px 4px 15px rgba(0,0,0,0.5);
        }}
        </style>
    """, unsafe_allow_html=True)

def dibujar_banner():
    """Renderiza el banner superior horizontal."""
    st.markdown("""
        <div class="banner-superior">
            <h1 style="font-size: 2.8em; text-shadow: 3px 3px 6px black; margin: 0;">🏆 PRODE MUNDIAL 2026 - Fase de Grupos</h1>
            <p style="font-size: 1.2em; text-shadow: 2px 2px 4px black; margin: 0;">¡La gloria está en tus predicciones!</p>
        </div>
    """, unsafe_allow_html=True)

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
