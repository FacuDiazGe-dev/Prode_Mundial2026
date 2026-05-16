import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from html import escape

from styles_config import (
    AVATAR_GENERICO,
    mostrar_decalogo
)
from tools import upload_foro_image


def render_foro(conn, df_usuarios):

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
    margin-top: 14px;
    padding: 10px;
    border-radius: 18px;
    background: rgba(255,255,255,0.42);
    border: 1px solid rgba(226,232,240,0.62);
}

/* ============================================================
   2C. PANEL INTEGRADO — MURO DEL FORO
   Contiene header + publicar + feed.
   ============================================================ */

.foro-main-shell {
    background: rgba(255,255,255,0.94);
    border: 1px solid rgba(226,232,240,0.9);
    border-radius: 20px;
    padding: 14px;
    box-shadow: 0 12px 30px rgba(15,23,42,0.06);
}

.foro-hero-header {
    background:
        radial-gradient(
            circle at 0% 0%,
            rgba(244,197,66,0.22),
            rgba(7,17,31,0.98) 38%
        ),
        linear-gradient(
            135deg,
            rgba(7,17,31,0.98),
            rgba(15,23,42,0.96)
        );

    border: 1px solid rgba(244,197,66,0.22);
    border-radius: 18px;
    padding: 16px;
    margin-bottom: 10px;

    box-shadow:
        inset 0 1px 0 rgba(255,255,255,0.06),
        0 10px 22px rgba(15,23,42,0.10);
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

.foro-publish-wrap {
    margin-bottom: 10px;
}

/* Feed integrado al mismo módulo */
.foro-feed-shell {
    padding: 10px;
    border-radius: 18px;
    background: rgba(248,250,252,0.72);
    border: 1px solid rgba(226,232,240,0.75);
}

/* Ajuste fino para que el expander no quede tan separado */
.foro-publish-wrap div[data-testid="stExpander"] {
    margin-bottom: 0 !important;
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

    .foro-feed-shell {
        padding: 8px;
        border-radius: 16px;
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
    margin-top: 14px;
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
   5. COMUNIDAD / STATS / REGLAS
   ============================================================ */

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

    .foro-message-img {
        max-height: 260px;
    }
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
</style>
""", unsafe_allow_html=True)

    # ============================================================
    # DATOS BASE
    # ============================================================

    df_foro = conn.read(
        worksheet="FORO",
        ttl=60
    )

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
    rol_actual = user_data.get("ROL", "")

    if "foro_uploader_key" not in st.session_state:
        st.session_state.foro_uploader_key = 0

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

    # ============================================================
    # TÍTULO
    # ============================================================

    st.markdown("""
<div class="foro-title">
<h1>💬 Foro del Prode</h1>
<p>El vestuario, el bar y el VAR emocional del grupo.</p>
</div>
""", unsafe_allow_html=True)

    col_main, col_side = st.columns([1, 1], gap="large")

    # ============================================================
    # COLUMNA PRINCIPAL — MURO
    # ============================================================
    with col_main:
        st.markdown("""
<div class="foro-hero-header">
<div class="foro-hero-row">
<div class="foro-hero-icon">💬</div>
<div>
<div class="foro-hero-title">Muro de la Comunidad</div>
<div class="foro-hero-subtitle">Chascarrillos, fotos y comentarios mundialistas</div>
</div>
</div>
</div>
""", unsafe_allow_html=True))

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
                    
            st.markdown("</div>", unsafe_allow_html=True)  # cierra foro-feed

        st.markdown("</div>", unsafe_allow_html=True)      # cierra foro-feed-shell

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

        st.markdown("</div>", unsafe_allow_html=True)      # cierra foro-feed-shell

        st.markdown("</div>", unsafe_allow_html=True)      # cierra foro-main-shell
    # ============================================================
    # COLUMNA DERECHA — DECÁLOGO / COMUNIDAD / REGLAS
    # ============================================================

    with col_side:

        # ------------------------------------------------------------
        # DECÁLOGO — abierto por defecto
        # ------------------------------------------------------------

        with st.expander("📜 Decálogo del Foro", expanded=True):
            mostrar_decalogo()

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

        # ------------------------------------------------------------
        # COMUNIDAD — cerrado por defecto
        # ------------------------------------------------------------

        with st.expander("📢 Comunidad", expanded=False):
            st.markdown(
                f"""
<div class="foro-stat-box">
<div class="foro-stat-title">Resumen</div>
<div class="foro-stat-line">💬 Mensajes totales: {total_mensajes}</div>
</div>

<div class="foro-stat-box">
<div class="foro-stat-title">Top agitadores</div>
{agitadores_html}
</div>

<div class="foro-stat-box">
<div class="foro-stat-title">Popularidad</div>
{popularidad_html}
</div>
""",
                unsafe_allow_html=True
            )

        # ------------------------------------------------------------
        # REGLAS Y FAQ — cerrado por defecto
        # ------------------------------------------------------------

        with st.expander("📘 Reglas y preguntas frecuentes", expanded=False):
            st.markdown("""
<div class="foro-rule-list">

**¿Cómo se suman puntos?**  
- Resultado exacto: se suma el puntaje definido por el grupo.  
- Ganador o empate correcto: suma puntaje parcial.  
- Sin acierto: 0 puntos.

**¿Hasta cuándo puedo cargar mis pronósticos?**  
- Hasta la fecha límite indicada en “Mis Pronósticos”.  
- Después de ese momento, la edición queda bloqueada.

**¿Cómo se determina el ganador?**  
- Gana quien tenga más puntos al final de la fase definida.  
- En caso de empate, se puede desempatar por exactos, generales u otro criterio que defina el grupo.

**¿Cuánto hay que poner?**  
- El monto lo define el grupo.  
- Este dato después puede editarse desde el Panel de Control.

**¿Puedo modificar mis pronósticos?**  
- Sí, mientras la edición esté abierta.  
- Una vez bloqueados, ya no se pueden editar.

**¿Qué pasa si no cargo un partido?**  
- Queda sin pronóstico o con el valor por defecto que defina el grupo.

</div>
""", unsafe_allow_html=True)
