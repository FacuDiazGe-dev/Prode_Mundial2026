import streamlit as st
import pandas as pd
import streamlit_antd_components as sac
from html import escape

from components.ui_button import ui_button
from styles_shared import css_panel_header, css_section_title, css_surface
from ranking_logic import calcular_detalle

try:
    from streamlit_elements import elements, mui, sync
    ELEMENTS_AVAILABLE = True
except Exception:
    elements = None
    mui = None
    sync = None
    ELEMENTS_AVAILABLE = False


def _render_lab_impacto_resultados(df_usuarios, df_res, df_pro, mapa_banderas):
    st.markdown("""
<div class="lab-panel">
<h3>Impacto en resultados oficiales</h3>
<div class="lab-note">
Prototipo visual: click en la franja "Tu resultado" para abrir el detalle de jugadores que suman.
</div>
</div>
""", unsafe_allow_html=True)

    if (
        df_res is None or df_res.empty
        or df_pro is None or df_pro.empty
        or not {"N_PARTIDO", "Equipo_1", "Equipo_2", "ESTADO_PARTIDO"}.issubset(df_res.columns)
        or not {"N_PARTIDO", "USUARIO", "P1", "P2"}.issubset(df_pro.columns)
    ):
        st.info("Faltan resultados o pronosticos para probar esta card.")
        return

    mapa_banderas = mapa_banderas or {}
    df_demo = df_res.copy()
    df_demo["N_PARTIDO_NUM"] = pd.to_numeric(df_demo["N_PARTIDO"], errors="coerce")
    estados_demo = df_demo["ESTADO_PARTIDO"].fillna("Pendiente").astype(str).str.strip()
    live_values = (
        df_demo["LIVE"].astype(bool)
        if "LIVE" in df_demo.columns
        else pd.Series(False, index=df_demo.index)
    )
    es_live = estados_demo.isin(["En Vivo", "Entretiempo"]) | live_values
    es_final = estados_demo.eq("Finalizado")
    df_demo = df_demo[es_live | es_final].sort_values("N_PARTIDO_NUM", ascending=False)

    if df_demo.empty:
        st.info("No hay partidos en vivo, entretiempo o finalizados para mostrar.")
        return

    opciones_partido = [
        f"#{int(row['N_PARTIDO_NUM'])} - {row.get('Equipo_1', '')} vs {row.get('Equipo_2', '')}"
        for _, row in df_demo.iterrows()
    ]
    elegido_label = st.selectbox(
        "Partido de prueba",
        options=opciones_partido,
        index=0,
        key="lab_impacto_partido"
    )

    partido_row = df_demo.iloc[opciones_partido.index(elegido_label)]
    n_partido = int(partido_row["N_PARTIDO_NUM"])
    estado = str(partido_row.get("ESTADO_PARTIDO", "Pendiente") or "Pendiente").strip()
    live_flag = bool(partido_row.get("LIVE", False))
    es_live_partido = estado in ["En Vivo", "Entretiempo"] or live_flag
    es_final_partido = estado == "Finalizado"

    def _to_int(value):
        try:
            if pd.isna(value):
                return None
            return int(value)
        except Exception:
            return None

    if es_live_partido:
        r1 = _to_int(partido_row.get("LIVE_R1"))
        r2 = _to_int(partido_row.get("LIVE_R2"))
        estado_label = "ENTRETIEMPO" if estado == "Entretiempo" else "EN VIVO"
        card_class = "live"
    elif es_final_partido:
        r1 = _to_int(partido_row.get("R1"))
        r2 = _to_int(partido_row.get("R2"))
        estado_label = "FINALIZADO"
        card_class = "finished"
    else:
        r1 = None
        r2 = None
        estado_label = "PROXIMAMENTE"
        card_class = "pending"

    usuario_actual = str(st.session_state.get("user_data", {}).get("USUARIO", "") or "")
    df_pro_demo = df_pro.copy()
    df_pro_demo["N_PARTIDO_NUM"] = pd.to_numeric(df_pro_demo["N_PARTIDO"], errors="coerce")
    pronos_partido = df_pro_demo[df_pro_demo["N_PARTIDO_NUM"] == n_partido].copy()
    grupos = {3: [], 1: [], 0: []}

    def _nombre_usuario(usuario):
        if df_usuarios is None or df_usuarios.empty or "USUARIO" not in df_usuarios.columns:
            return str(usuario)
        match = df_usuarios[df_usuarios["USUARIO"].astype(str).str.strip() == str(usuario).strip()]
        if match.empty:
            return str(usuario)
        nombre = str(match.iloc[0].get("NOMBRE", "") or "").strip()
        return nombre or str(usuario)

    for _, pron in pronos_partido.iterrows():
        p1 = _to_int(pron.get("P1"))
        p2 = _to_int(pron.get("P2"))
        puntos, _, _ = calcular_detalle(r1, r2, p1, p2)
        usuario = str(pron.get("USUARIO", "") or "").strip()
        grupos[int(puntos)].append({
            "nombre": _nombre_usuario(usuario),
            "usuario": usuario,
            "p1": p1,
            "p2": p2,
        })

    pron_usuario = pronos_partido[
        pronos_partido["USUARIO"].astype(str).str.strip() == usuario_actual
    ]
    if not pron_usuario.empty:
        p1_user = _to_int(pron_usuario.iloc[0].get("P1"))
        p2_user = _to_int(pron_usuario.iloc[0].get("P2"))
        pron_text = f"{p1_user} - {p2_user}"
        puntos_user, _, _ = calcular_detalle(r1, r2, p1_user, p2_user)
        puntos_text = f"+{puntos_user} Pts" if r1 is not None and r2 is not None else "Pendiente"
        points_class = "positive" if puntos_user > 0 else "zero"
    else:
        pron_text = "Sin pronostico"
        puntos_text = "-"
        points_class = "missing"

    def _flag_html(equipo):
        flag_value = str(mapa_banderas.get(equipo, "⚽"))
        if flag_value.startswith("data:image"):
            return f'<img src="{flag_value}" class="lab-impact-flag">'
        return f'<span class="lab-impact-flag-fallback">{escape(flag_value)}</span>'

    def _lista(items, limite=9):
        if not items:
            return '<div class="lab-impact-empty">Nadie</div>'

        html_items = ""
        for item in items[:limite]:
            html_items += (
                "<li>"
                f"<strong>{escape(item['nombre'])}</strong> "
                f"<span>@{escape(item['usuario'])}</span> "
                f"<em>{item['p1']}-{item['p2']}</em>"
                "</li>"
            )
        if len(items) > limite:
            html_items += f'<li class="more">y {len(items) - limite} mas...</li>'
        return f"<ul>{html_items}</ul>"

    equipo_1_raw = str(partido_row.get("Equipo_1", "") or "")
    equipo_2_raw = str(partido_row.get("Equipo_2", "") or "")
    score_text = f"{r1} : {r2}" if r1 is not None and r2 is not None else "VS"
    exactos = len(grupos[3])
    generales = len(grupos[1])
    dia = escape(str(partido_row.get("DIA", "") or ""))
    hora = escape(str(partido_row.get("HORA", "") or ""))

    st.markdown(
        f"""
<style>
.lab-impact-wrap {{
    max-width: 680px;
    margin: 12px auto 0;
}}
.lab-impact-match {{
    position: relative;
    overflow: visible;
    padding: 12px 13px;
    border-radius: 16px;
    background:
        linear-gradient(180deg, rgba(255,255,255,0.72), rgba(248,250,252,0.58)),
        url("https://storage.googleapis.com/foto-prode2026/Banners/FONDO_CARD_INICIO.png");
    background-size: cover;
    background-position: center;
    border: 1px solid rgba(148,163,184,0.38);
    box-shadow: 0 8px 18px rgba(15,23,42,0.055), inset 0 1px 0 rgba(255,255,255,0.75);
}}
.lab-impact-match.live {{
    border-color: rgba(22,163,74,0.55);
    box-shadow: 0 12px 26px rgba(15,23,42,0.09), 0 0 16px rgba(22,163,74,0.14), inset 0 1px 0 rgba(255,255,255,0.82);
}}
.lab-impact-match.live::after {{
    content: "";
    position: absolute;
    inset: 0 auto 0 0;
    width: 4px;
    border-radius: 16px 0 0 16px;
    background: linear-gradient(180deg, #22c55e, #f4c542);
}}
.lab-impact-meta {{
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 11px;
    font-size: 9.5px;
    font-weight: 900;
    color: #64748b;
    text-transform: uppercase;
    letter-spacing: 0.065em;
}}
.lab-impact-badge {{
    display: inline-flex;
    align-items: center;
    gap: 4px;
    padding: 4px 9px;
    margin-left: 6px;
    border-radius: 999px;
    font-size: 9px;
    font-weight: 950;
    letter-spacing: 0.08em;
}}
.lab-impact-badge.live {{
    background: linear-gradient(180deg, #34d399, #10b981);
    border: 1px solid rgba(5,150,105,0.88);
    color: #fff;
    box-shadow: 0 5px 11px rgba(5,150,105,0.18), 0 0 14px rgba(52,211,153,0.26);
}}
.lab-impact-badge.live::before {{
    content: "";
    width: 5px;
    height: 5px;
    border-radius: 999px;
    background: #ef4444;
    box-shadow: 0 0 7px rgba(239,68,68,0.78);
}}
.lab-impact-badge.finished {{
    background: rgba(100,116,139,0.12);
    border: 1px solid rgba(100,116,139,0.25);
    color: #475569;
}}
.lab-impact-body {{
    display: grid;
    grid-template-columns: minmax(0, 1fr) 74px minmax(0, 1fr);
    align-items: center;
    gap: 12px;
}}
.lab-impact-team {{
    display: flex;
    align-items: center;
    gap: 8px;
    min-width: 0;
    font-size: 13px;
    font-weight: 900;
    color: #0f172a;
}}
.lab-impact-team.left {{
    justify-content: flex-end;
    text-align: right;
}}
.lab-impact-team.right {{
    justify-content: flex-start;
    text-align: left;
}}
.lab-impact-team .name {{
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
}}
.lab-impact-flag {{
    width: 30px;
    height: 21px;
    object-fit: cover;
    border-radius: 5px;
    border: 1px solid rgba(255,255,255,0.85);
    box-shadow: 0 3px 7px rgba(15,23,42,0.18);
    flex-shrink: 0;
}}
.lab-impact-score {{
    background: radial-gradient(circle at 50% 0%, rgba(244,197,66,0.22), transparent 48%), linear-gradient(180deg, #0f172a, #07111F);
    color: #f8fafc;
    border-radius: 12px;
    padding: 8px 8px;
    text-align: center;
    font-family: 'Montserrat', sans-serif;
    font-size: 15px;
    font-weight: 900;
    letter-spacing: 0.06em;
    border: 1px solid rgba(244,197,66,0.30);
    box-shadow: 0 7px 16px rgba(7,17,31,0.20);
}}
.lab-impact-details {{
    position: relative;
    margin-top: 11px;
}}
.lab-impact-details summary {{
    list-style: none;
    cursor: pointer;
    display: grid;
    grid-template-columns: minmax(0, 1fr) auto minmax(0, 1fr);
    align-items: center;
    gap: 10px;
    padding: 8px 10px;
    border-radius: 12px;
    background: rgba(255,255,255,0.72);
    border: 1px solid rgba(226,232,240,0.82);
    box-shadow: inset 0 1px 0 rgba(255,255,255,0.76);
}}
.lab-impact-details summary::-webkit-details-marker {{
    display: none;
}}
.lab-impact-details summary:hover {{
    border-color: rgba(244,197,66,0.58);
    box-shadow: inset 0 1px 0 rgba(255,255,255,0.86), 0 8px 18px rgba(244,197,66,0.10);
}}
.lab-impact-label {{
    font-size: 9px;
    font-weight: 950;
    color: #475569;
    text-transform: uppercase;
    letter-spacing: 0.055em;
    white-space: nowrap;
}}
.lab-impact-user-score {{
    font-family: 'Montserrat', sans-serif;
    font-size: 11px;
    font-weight: 950;
    color: #0f172a;
    letter-spacing: 0.04em;
    white-space: nowrap;
}}
.lab-impact-points {{
    justify-self: end;
    font-size: 10px;
    font-weight: 950;
    white-space: nowrap;
}}
.lab-impact-points.positive {{
    color: #16a34a;
}}
.lab-impact-points.zero {{
    color: #64748b;
}}
.lab-impact-points.missing {{
    color: #94a3b8;
}}
.lab-impact-pop {{
    width: min(360px, calc(100vw - 56px));
    margin-top: 8px;
    padding: 11px 12px;
    border-radius: 14px;
    background: rgba(255,255,255,0.98);
    border: 1px solid rgba(203,213,225,0.96);
    box-shadow: 0 18px 34px rgba(15,23,42,0.16), inset 0 1px 0 rgba(255,255,255,0.88);
}}
.lab-impact-pop h4 {{
    margin: 0 0 7px;
    color: #07111F;
    font-family: 'Montserrat', sans-serif;
    font-size: 13px;
    font-weight: 950;
}}
.lab-impact-pop .summary {{
    color: #64748b;
    font-size: 11px;
    font-weight: 850;
    margin-bottom: 8px;
}}
.lab-impact-pop .group-title {{
    color: #334155;
    font-size: 11px;
    font-weight: 950;
    margin: 8px 0 4px;
}}
.lab-impact-pop ul {{
    margin: 0;
    padding-left: 17px;
}}
.lab-impact-pop li {{
    margin: 3px 0;
    color: #334155;
    font-size: 11px;
    font-weight: 750;
}}
.lab-impact-pop li span {{
    color: #64748b;
}}
.lab-impact-pop li em {{
    color: #0f172a;
    font-style: normal;
    font-weight: 950;
}}
.lab-impact-empty {{
    color: #94a3b8;
    font-size: 11px;
    font-weight: 800;
}}
@media (max-width: 768px) {{
    .lab-impact-body {{
        grid-template-columns: minmax(0, 1fr) 62px minmax(0, 1fr);
        gap: 8px;
    }}
    .lab-impact-team {{
        font-size: 12px;
    }}
    .lab-impact-score {{
        font-size: 13px;
        padding: 7px 6px;
    }}
    .lab-impact-details summary {{
        grid-template-columns: 1fr auto;
        gap: 6px 10px;
    }}
    .lab-impact-points {{
        grid-column: 1 / -1;
    }}
}}
</style>

<div class="lab-impact-wrap">
<div class="lab-impact-match {card_class}">
<div class="lab-impact-meta">
<span>Partido #{n_partido}<span class="lab-impact-badge {card_class}">{estado_label}</span></span>
<span>{dia} | {hora}</span>
</div>
<div class="lab-impact-body">
<div class="lab-impact-team left"><span class="name">{escape(equipo_1_raw)}</span>{_flag_html(equipo_1_raw)}</div>
<div class="lab-impact-score">{score_text}</div>
<div class="lab-impact-team right">{_flag_html(equipo_2_raw)}<span class="name">{escape(equipo_2_raw)}</span></div>
</div>
<details class="lab-impact-details">
<summary>
<span class="lab-impact-label">Tu resultado</span>
<span class="lab-impact-user-score">{escape(pron_text)}</span>
<span class="lab-impact-points {points_class}">{escape(puntos_text)}</span>
</summary>
<div class="lab-impact-pop">
<h4>Impacto con este resultado</h4>
<div class="summary">{exactos + generales} jugadores suman · {exactos} exactos · {generales} tendencia</div>
<div class="group-title">+3 pts exactos</div>
{_lista(grupos[3])}
<div class="group-title">+1 pt tendencia</div>
{_lista(grupos[1])}
</div>
</details>
</div>
</div>
""",
        unsafe_allow_html=True
    )


def render_laboratorio(
    df_usuarios=None,
    df_ranking=None,
    df_res=None,
    df_pro=None,
    mapa_banderas=None,
):
    css_laboratorio = (
        """
<style>
"""
        + css_section_title("lab-title")
        + """

"""
        + css_surface("lab-panel", "panel_light")
        + """

.lab-panel h3 {
    margin-top: 0;
    color: #07111F;
    font-family: 'Montserrat', sans-serif;
    font-weight: 900;
}

.lab-note {
    color: #64748b;
    font-size: 13px;
    font-weight: 700;
    margin-bottom: 12px;
}

.lab-preview-card {
    background:
        linear-gradient(
            135deg,
            rgba(7,17,31,0.98),
            rgba(15,23,42,0.94)
        );
    color: white;
    border-radius: 16px;
    padding: 16px;
    margin-top: 12px;
    border: 1px solid rgba(244,197,66,0.24);
}

.lab-preview-name {
    font-family: 'Montserrat', sans-serif;
    font-size: 20px;
    font-weight: 900;
}

.lab-preview-meta {
    color: rgba(255,255,255,0.68);
    font-size: 12px;
    font-weight: 800;
    margin-top: 4px;
}

.lab-player-row {
    display: flex;
    align-items: center;
    gap: 10px;
}

.lab-player-avatar {
    width: 36px;
    height: 36px;
    border-radius: 50%;
    object-fit: cover;
    border: 2px solid rgba(244,197,66,0.8);
}
"""
        + css_surface("lab-card", "panel_light")
        + css_panel_header("lab-card")
        + """

.lab-selector-box {
    background: rgba(248,250,252,0.78);
    border: 1px solid rgba(226,232,240,0.8);
    border-radius: 14px;
    padding: 12px;
    max-height: 360px;
    overflow-y: auto;
}

.lab-preview-row {
    display: flex;
    align-items: center;
    gap: 12px;
}

.lab-preview-avatar {
    width: 58px;
    height: 58px;
    border-radius: 50%;
    object-fit: cover;
    border: 3px solid #F4C542;
    box-shadow:
        0 10px 24px rgba(15,23,42,0.18),
        0 0 18px rgba(244,197,66,0.22);
}

.lab-return-box {
    margin-top: 14px;
    background: rgba(248,250,252,0.86);
    border: 1px solid rgba(226,232,240,0.85);
    border-radius: 14px;
    padding: 12px;
}

.lab-return-label {
    font-size: 10px;
    font-weight: 900;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    color: #64748b;
    margin-bottom: 6px;
}

.lab-return-value {
    font-family: 'Montserrat', sans-serif;
    font-size: 18px;
    font-weight: 900;
    color: #07111F;
}

@media (max-width: 768px) {
    .lab-selector-box {
        max-height: 300px;
    }
}
/* ============================================================
   LAB — PRUEBA BOTÓN + CARD DE JUGADOR
   ============================================================ */

.lab-player-select-row {
    margin-bottom: 8px;
}

.lab-player-card-mini {
    background: rgba(248,250,252,0.92);
    border: 1px solid rgba(226,232,240,0.9);
    border-radius: 14px;
    padding: 9px 10px;

    display: flex;
    align-items: center;
    gap: 10px;

    min-height: 54px;
}

.lab-player-card-mini.selected {
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

.lab-player-card-avatar {
    width: 38px;
    height: 38px;
    border-radius: 50%;
    object-fit: cover;
    border: 2px solid rgba(244,197,66,0.75);
    flex-shrink: 0;
}

.lab-player-card-info {
    flex: 1;
    min-width: 0;
}

.lab-player-card-name {
    color: #0f172a;
    font-size: 13px;
    font-weight: 900;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
}

.lab-player-card-team {
    color: #64748b;
    font-size: 11px;
    font-weight: 800;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
}

.lab-player-card-points {
    background: rgba(7,17,31,0.96);
    color: #F4C542;
    border-radius: 999px;
    padding: 5px 8px;
    font-size: 11px;
    font-weight: 900;
    white-space: nowrap;
}

.lab-select-button button {
    border-radius: 12px !important;
    min-height: 42px !important;
    font-size: 12px !important;
    font-weight: 900 !important;
    border: 1px solid rgba(244,197,66,0.38) !important;
    background: rgba(244,197,66,0.18) !important;
    color: #07111F !important;
}

.lab-select-button button:hover {
    background: rgba(244,197,66,0.30) !important;
    border-color: rgba(244,197,66,0.65) !important;
}

.lab-select-button button:disabled {
    background: rgba(7,17,31,0.92) !important;
    color: #F4C542 !important;
    border: 1px solid rgba(244,197,66,0.30) !important;
}
</style>
"""
    )

    st.markdown(css_laboratorio, unsafe_allow_html=True)

    st.markdown("""
<div class="lab-title">
<h1>🧪 Laboratorio</h1>
<p>Zona de pruebas para componentes antes de llevarlos a la app real.</p>
</div>
""", unsafe_allow_html=True)

    if df_usuarios is None or df_usuarios.empty:
        st.warning("No hay usuarios cargados para probar.")
        return

    df_lab = df_usuarios.copy()
    df_lab["NOMBRE"] = df_lab["NOMBRE"].fillna("Jugador").astype(str)
    df_lab["USUARIO"] = df_lab["USUARIO"].fillna("").astype(str)
    df_lab["EQUIPO FAVORITO"] = df_lab["EQUIPO FAVORITO"].fillna("-").astype(str)

    nombres = df_lab["NOMBRE"].tolist()
    # ============================================================
    # HELPERS — LAB FORO MUI
    # ============================================================

    if "lab_mui_like_count" not in st.session_state:
        st.session_state.lab_mui_like_count = 0

    if "lab_mui_dislike_count" not in st.session_state:
        st.session_state.lab_mui_dislike_count = 0

    if "lab_mui_total_actions" not in st.session_state:
        st.session_state.lab_mui_total_actions = 0

    if "lab_mui_action" not in st.session_state:
        st.session_state.lab_mui_action = ""

    # ============================================================
    # FUNCIONES CALLBACKS PARA BOTONES MUI
    # ✅ SOLUCIÓN: Usar callbacks Python directos en lugar de sync()
    # ============================================================

    def on_like_click(msg_id):
        """Callback cuando se clickea el botón de like"""
        st.session_state.lab_mui_like_count += 1
        st.session_state.lab_mui_total_actions += 1
        st.session_state.lab_mui_action = f"👍 Like en mensaje {msg_id}"

    def on_dislike_click(msg_id):
        """Callback cuando se clickea el botón de dislike"""
        st.session_state.lab_mui_dislike_count += 1
        st.session_state.lab_mui_total_actions += 1
        st.session_state.lab_mui_action = f"👎 Dislike en mensaje {msg_id}"

    def on_delete_click(msg_id):
        """Callback cuando se clickea el botón de delete"""
        st.session_state.lab_mui_total_actions += 1
        st.session_state.lab_mui_action = f"🗑️ Borrar mensaje {msg_id}"

    def render_preview_jugador(user, return_label, return_value):
        avatar = user.get("AVATAR_URL", "")
        avatar_html = ""

        if pd.notna(avatar) and str(avatar).strip() != "":
            avatar_html = f'<img src="{avatar}" class="lab-preview-avatar">'

        st.markdown(
            f"""
<div class="lab-card-header">
<div class="lab-card-icon">&#129534;</div>
<div>
<div class="lab-card-title">Vista previa</div>
<div class="lab-card-subtitle">Jugador seleccionado</div>
</div>
</div>

<div class="lab-preview-card">
<div class="lab-preview-row">
{avatar_html}
<div>
<div class="lab-preview-name">{user["NOMBRE"]}</div>
<div class="lab-preview-meta">@{user["USUARIO"]} &middot; {user["EQUIPO FAVORITO"]}</div>
</div>
</div>
</div>

<div class="lab-return-box">
<div class="lab-return-label">{return_label}</div>
<div class="lab-return-value">{return_value}</div>
</div>
""",
            unsafe_allow_html=True
        )

    tab = sac.tabs(
        [
            sac.TabsItem("Selector vertical", icon="people"),
            sac.TabsItem("Botón + Card", icon="layout-sidebar"),
            sac.TabsItem("Foro MUI", icon="chat-dots"),
            sac.TabsItem("Botones", icon="collection"),
            sac.TabsItem("UI Button", icon="cursor"),
            sac.TabsItem("Impacto resultados", icon="graph-up"),
            sac.TabsItem("Filtros", icon="funnel"),
            sac.TabsItem("Insignias", icon="award"),
        ],
        align="center",
        size="md",
        key="lab_tabs"
    )

    # ============================================================
    # TAB 1 — SELECTOR VERTICAL
    # ============================================================

    if tab == "Selector vertical":
        st.markdown("""
<div class="lab-panel">
<h3>Selector vertical de jugadores</h3>
<div class="lab-note">
Prueba para reemplazar el selectbox por un selector más visual. Evaluar mobile, scroll y nombres largos.
</div>
</div>
""", unsafe_allow_html=True)

        col1, col2 = st.columns([1, 1], gap="large")

        with col1:
            with st.container(border=True):
                st.markdown("""
<div class="lab-card-header">
<div class="lab-card-icon">👥</div>
<div>
<div class="lab-card-title">Jugadores</div>
<div class="lab-card-subtitle">Selector Ant Design dentro de contenedor nativo</div>
</div>
</div>
""", unsafe_allow_html=True)

                elegido = sac.buttons(
                    items=nombres,
                    index=0,
                    direction="vertical",
                    align="start",
                    size="middle",
                    radius="lg",
                    return_index=False,
                    key="lab_selector_vertical"
                )

        with col2:
            user = df_lab[df_lab["NOMBRE"] == elegido].iloc[0]

            with st.container(border=True):
                render_preview_jugador(
                    user,
                    "Valor devuelto por el componente",
                    elegido
                )

        # ============================================================
    # TAB 2 — BOTÓN + CARD
    # ============================================================

    elif tab == "Botón + Card":
        st.markdown("""
<div class="lab-panel">
<h3>Botón + Card de jugador</h3>
<div class="lab-note">
Prueba alternativa: el botón selecciona y la card contiene el diseño visual completo.
Esto evita depender de cards clickeables con HTML.
</div>
</div>
""", unsafe_allow_html=True)

        if "lab_jugador_card_sel" not in st.session_state:
            st.session_state.lab_jugador_card_sel = nombres[0] if nombres else None

        col1, col2 = st.columns([1.15, 1], gap="large")

        with col1:
            with st.container(border=True):
                st.markdown("""
<div class="lab-card-header">
<div class="lab-card-icon">👥</div>
<div>
<div class="lab-card-title">Listado selector</div>
<div class="lab-card-subtitle">Botón a la izquierda + card a la derecha</div>
</div>
</div>
""", unsafe_allow_html=True)

                with st.container(height=380):
                    for _, row in df_lab.iterrows():
                        nombre_raw = str(row["NOMBRE"])
                        usuario_raw = str(row["USUARIO"])
                        equipo = str(row["EQUIPO FAVORITO"])

                        avatar = row.get("AVATAR_URL", "")
                        avatar_html = ""

                        if pd.notna(avatar) and str(avatar).strip() != "":
                            avatar_html = f'<img src="{avatar}" class="lab-player-card-avatar">'
                        else:
                            avatar_html = '<div class="lab-player-card-avatar"></div>'

                        es_sel = st.session_state.lab_jugador_card_sel == nombre_raw
                        selected_class = "selected" if es_sel else ""

                        c_btn, c_card = st.columns([0.24, 0.76], gap="small")

                        with c_btn:
                            st.markdown(
                                '<div class="lab-select-button">',
                                unsafe_allow_html=True
                            )

                            if es_sel:
                                st.button(
                                    "Activo",
                                    key=f"lab_btn_activo_{usuario_raw}",
                                    use_container_width=True,
                                    disabled=True
                                )
                            else:
                                if st.button(
                                    "Ver",
                                    key=f"lab_btn_ver_{usuario_raw}",
                                    use_container_width=True
                                ):
                                    st.session_state.lab_jugador_card_sel = nombre_raw
                                    st.rerun()

                            st.markdown("</div>", unsafe_allow_html=True)

                        with c_card:
                            st.markdown(
                                f"""
<div class="lab-player-select-row">
<div class="lab-player-card-mini {selected_class}">
{avatar_html}
<div class="lab-player-card-info">
<div class="lab-player-card-name">{nombre_raw}</div>
<div class="lab-player-card-team">⚽ {equipo}</div>
</div>
<div class="lab-player-card-points">pts</div>
</div>
</div>
""",
                                unsafe_allow_html=True
                            )

        with col2:
            user = df_lab[
                df_lab["NOMBRE"] == st.session_state.lab_jugador_card_sel
            ].iloc[0]

            with st.container(border=True):
                render_preview_jugador(
                    user,
                    "Valor guardado en session_state",
                    st.session_state.lab_jugador_card_sel
                )

    # ============================================================
    # TAB 3 — FORO MUI / STREAMLIT-ELEMENTS
    # ============================================================

    elif tab == "Foro MUI":
        st.markdown("""
<div class="lab-panel">
<h3>Foro MUI con streamlit-elements ✅</h3>
<div class="lab-note">
✅ SOLUCIÓN ACTIVA: Usando callbacks Python directos en onClick (NO sync)
Clickea los botones de like, dislike y borrar. Los clicks se cuentan correctamente.
</div>
</div>
""", unsafe_allow_html=True)

        if not ELEMENTS_AVAILABLE:
            st.error(
                "streamlit-elements no está instalado. "
                "Agregá streamlit-elements==0.1.* en requirements.txt y reiniciá la app."
            )
            return

        # DEBUG info
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Total Clicks", st.session_state.lab_mui_total_actions)
        with col2:
            st.metric("Última acción", st.session_state.lab_mui_action or "Ninguna")

        if st.session_state.lab_mui_action:
            st.success(
                f"✅ {st.session_state.lab_mui_action} | "
                f"���� {st.session_state.lab_mui_like_count} · "
                f"👎 {st.session_state.lab_mui_dislike_count}"
            )
        else:
            st.info("🧪 Clickea cualquier botón en el Foro para comenzar...")

        mensajes_demo = [
            {
                "id": 1,
                "nombre": "Jorge Diaz",
                "usuario": "@Jorge",
                "fecha": "13/05 21:30",
                "texto": "Ma ver si se ponen la pila y empiezan a pronosticar",
                "avatar": "https://i.pravatar.cc/100?img=12",
                "imagen": "",
                "mio": False,
            },
            {
                "id": 2,
                "nombre": "Facu",
                "usuario": "@FacuAdmin",
                "fecha": "15/05 19:44",
                "texto": "Vamos a probar las cosas. Este mensaje tiene imagen adjunta y botones dentro de la card.",
                "avatar": "https://i.pravatar.cc/100?img=15",
                "imagen": "https://storage.googleapis.com/foto-prode2026/foro/demo/prode_demo.png",
                "mio": True,
            },
            {
                "id": 3,
                "nombre": "SANTIAGO CONTRERAS",
                "usuario": "@Santi",
                "fecha": "07/05 19:31",
                "texto": "El creador ya arranca con puntos?",
                "avatar": "",
                "imagen": "",
                "mio": False,
            },
            {
                "id": 4,
                "nombre": "Nahuel Diaz",
                "usuario": "@Nahuel",
                "fecha": "28/04 14:21",
                "texto": "Una vez registrado no te ingresa ni te redirecciona a la página inicial",
                "avatar": "",
                "imagen": "",
                "mio": False,
            },
        ]

        with elements("lab_foro_mui_frame"):

            with mui.Box(
                sx={
                    "width": "100%",
                    "boxSizing": "border-box",
                    "borderRadius": "22px",
                    "background": "rgba(255,255,255,0.96)",
                    "border": "1px solid rgba(226,232,240,0.95)",
                    "boxShadow": "0 14px 32px rgba(15,23,42,0.08)",
                    "p": 2,
                },
            ):

                # Header oscuro
                with mui.Box(
                    sx={
                        "background": "linear-gradient(135deg, #07111F, #111827)",
                        "borderRadius": "18px",
                        "p": 2,
                        "mb": 1.5,
                        "border": "1px solid rgba(244,197,66,0.24)",
                    }
                ):
                    mui.Typography(
                        "💬 Muro de la Comunidad",
                        variant="h5",
                        sx={
                            "fontWeight": 900,
                            "color": "#F8FAFC",
                            "fontFamily": "Montserrat, sans-serif",
                            "lineHeight": 1.05,
                        },
                    )
                    mui.Typography(
                        "Cards, imágenes, scroll y botones funcionales ✅",
                        variant="body2",
                        sx={
                            "color": "rgba(248,250,252,0.72)",
                            "fontWeight": 700,
                            "mt": 0.6,
                        },
                    )

                # Feed con scroll real
                with mui.Box(
                    sx={
                        "height": 520,
                        "overflowY": "auto",
                        "p": 1.2,
                        "borderRadius": "18px",
                        "background": "rgba(248,250,252,0.86)",
                        "border": "1px solid rgba(226,232,240,0.85)",
                    }
                ):
                    for msg in mensajes_demo:
                        avatar = msg["avatar"] or "https://ui-avatars.com/api/?name=Jugador&background=E2E8F0&color=0F172A"
                        is_mine = msg["mio"]

                        with mui.Card(
                            key=f"lab_mui_card_{msg['id']}",
                            sx={
                                "mb": 1.2,
                                "borderRadius": "18px",
                                "border": "1px solid rgba(226,232,240,0.95)"
                                if not is_mine
                                else "1px solid rgba(244,197,66,0.75)",
                                "boxShadow": "0 8px 18px rgba(15,23,42,0.05)",
                                "background": "linear-gradient(90deg, rgba(244,197,66,0.12), rgba(255,255,255,0.98))"
                                if is_mine
                                else "rgba(255,255,255,0.98)",
                            },
                        ):
                            with mui.CardContent(
                                sx={
                                    "p": 1.5,
                                    "&:last-child": {
                                        "pb": 1.5,
                                    },
                                }
                            ):

                                # Cabecera mensaje
                                with mui.Box(
                                    sx={
                                        "display": "flex",
                                        "alignItems": "center",
                                        "gap": 1.2,
                                        "mb": 1,
                                    }
                                ):
                                    mui.Avatar(
                                        src=avatar,
                                        sx={
                                            "width": 42,
                                            "height": 42,
                                            "border": "2px solid #F4C542",
                                        },
                                    )

                                    with mui.Box(
                                        sx={
                                            "minWidth": 0,
                                            "flex": 1,
                                        }
                                    ):
                                        with mui.Box(
                                            sx={
                                                "display": "flex",
                                                "alignItems": "center",
                                                "gap": 0.8,
                                            }
                                        ):
                                            mui.Typography(
                                                msg["nombre"],
                                                variant="body2",
                                                sx={
                                                    "fontWeight": 900,
                                                    "color": "#07111F",
                                                    "fontFamily": "Montserrat, sans-serif",
                                                },
                                            )

                                            if is_mine:
                                                mui.Box(
                                                    "TUYO",
                                                    sx={
                                                        "fontSize": "9px",
                                                        "fontWeight": 900,
                                                        "color": "#F4C542",
                                                        "background": "#07111F",
                                                        "borderRadius": "999px",
                                                        "px": 0.8,
                                                        "py": 0.2,
                                                    },
                                                )

                                        mui.Typography(
                                            msg["fecha"],
                                            variant="caption",
                                            sx={
                                                "color": "#94A3B8",
                                                "fontWeight": 800,
                                            },
                                        )

                                # Cuerpo texto + imagen
                                if msg["imagen"]:
                                    with mui.Box(
                                        sx={
                                            "display": "grid",
                                            "gridTemplateColumns": {
                                                "xs": "1fr",
                                                "sm": "1fr 180px",
                                            },
                                            "gap": 1.4,
                                            "alignItems": "start",
                                        }
                                    ):
                                        mui.Typography(
                                            msg["texto"],
                                            variant="body2",
                                            sx={
                                                "color": "#334155",
                                                "fontWeight": 700,
                                                "lineHeight": 1.35,
                                            },
                                        )

                                        mui.Box(
                                            component="img",
                                            src=msg["imagen"],
                                            sx={
                                                "width": "100%",
                                                "maxHeight": 150,
                                                "objectFit": "contain",
                                                "borderRadius": "14px",
                                                "border": "1px solid rgba(226,232,240,0.9)",
                                                "background": "#F8FAFC",
                                            },
                                        )
                                else:
                                    mui.Typography(
                                        msg["texto"],
                                        variant="body2",
                                        sx={
                                            "color": "#334155",
                                            "fontWeight": 700,
                                            "lineHeight": 1.35,
                                        },
                                    )

                                # ============================================================
                                # 🟢 BOTONES CON CALLBACKS PYTHON DIRECTOS
                                # onClick=lambda: on_like_click(msg["id"])
                                # NO USAR sync() — causa problemas con event.target.id
                                # ============================================================
                                with mui.Box(
                                    sx={
                                        "display": "flex",
                                        "gap": 1,
                                        "mt": 1.2,
                                        "flexWrap": "wrap",
                                    }
                                ):
                                    # BOTÓN LIKE
                                    mui.Button(
                                        f"👍 {st.session_state.lab_mui_like_count}",
                                        variant="outlined",
                                        size="small",
                                        onClick=lambda msg_id=msg["id"]: on_like_click(msg_id),
                                        sx={
                                            "textTransform": "none",
                                            "fontWeight": 900,
                                            "borderRadius": "10px",
                                            "minHeight": 30,
                                        },
                                    )

                                    # BOTÓN DISLIKE
                                    mui.Button(
                                        f"👎 {st.session_state.lab_mui_dislike_count}",
                                        variant="outlined",
                                        size="small",
                                        onClick=lambda msg_id=msg["id"]: on_dislike_click(msg_id),
                                        sx={
                                            "textTransform": "none",
                                            "fontWeight": 900,
                                            "borderRadius": "10px",
                                            "minHeight": 30,
                                        },
                                    )

                                    # BOTÓN DELETE
                                    mui.Button(
                                        "🗑️ Borrar",
                                        variant="outlined",
                                        color="warning",
                                        size="small",
                                        onClick=lambda msg_id=msg["id"]: on_delete_click(msg_id),
                                        sx={
                                            "textTransform": "none",
                                            "fontWeight": 900,
                                            "borderRadius": "10px",
                                            "minHeight": 30,
                                        },
                                    )
    
    # ============================================================
    # TAB 4 — BOTONES
    # ============================================================

    elif tab == "Botones":
        st.markdown("""
<div class="lab-panel">
<h3>Botones como selector</h3>
<div class="lab-note">
Sirve para pocos jugadores o para categorías. Si hay muchos, puede volverse largo.
</div>
</div>
""", unsafe_allow_html=True)

        max_items = st.slider(
            "Cantidad de jugadores a mostrar",
            min_value=3,
            max_value=min(20, len(nombres)),
            value=min(8, len(nombres))
        )

        elegido_btn = sac.buttons(
            items=nombres[:max_items],
            index=0,
            direction="vertical",
            align="start",
            size="large",
            radius="xl",
            return_index=False,
            key="lab_buttons_large"
        )

        st.success(f"Seleccionado: {elegido_btn}")

    # ============================================================
    # TAB 5 — FILTROS
    # ============================================================

    elif tab == "UI Button":
        st.markdown("""
<div class="lab-panel">
<h3>UI Button custom component</h3>
<div class="lab-note">
Prueba visual y funcional del boton reutilizable. El click devuelve True una sola vez por evento.
</div>
</div>
""", unsafe_allow_html=True)

        if "lab_ui_button_clicks" not in st.session_state:
            st.session_state.lab_ui_button_clicks = 0

        if "lab_ui_button_last" not in st.session_state:
            st.session_state.lab_ui_button_last = "Ninguno"

        col_a, col_b = st.columns(2)
        with col_a:
            st.metric("Clicks detectados", st.session_state.lab_ui_button_clicks)
        with col_b:
            st.metric("Ultimo boton", st.session_state.lab_ui_button_last)

        variants = [
            ("primary", "Principal", "✏️"),
            ("secondary", "Secundario", "📋"),
            ("dark", "Azul noche", "🌙"),
            ("ghost", "Fantasma", "👁️"),
            ("danger", "Eliminar", "🗑️"),
            ("locked", "Bloqueado", "🔒"),
            ("success", "Confirmar", "✅"),
        ]

        st.markdown("#### Variantes")
        for variant, label, icon in variants:
            clicked = ui_button(
                label=label,
                key=f"lab_ui_button_variant_{variant}",
                variant=variant,
                icon_left=icon,
                icon_right="›" if variant not in {"locked", "danger"} else None,
                disabled=variant == "locked",
                glow=variant in {"primary", "dark"},
                rounded="soft",
            )

            if clicked:
                st.session_state.lab_ui_button_clicks += 1
                st.session_state.lab_ui_button_last = variant
                st.rerun()

        st.markdown("#### Tamaños y formas")
        col_sm, col_md, col_lg = st.columns(3)
        with col_sm:
            if ui_button(
                "Small pill",
                key="lab_ui_button_sm",
                variant="secondary",
                size="sm",
                rounded="pill",
                compact=True,
                icon_left="•",
            ):
                st.session_state.lab_ui_button_clicks += 1
                st.session_state.lab_ui_button_last = "small"
                st.rerun()

        with col_md:
            if ui_button(
                "Medium soft",
                key="lab_ui_button_md",
                variant="primary",
                size="md",
                rounded="soft",
                icon_left="★",
            ):
                st.session_state.lab_ui_button_clicks += 1
                st.session_state.lab_ui_button_last = "medium"
                st.rerun()

        with col_lg:
            if ui_button(
                "Large card",
                key="lab_ui_button_lg",
                variant="dark",
                size="lg",
                rounded="card",
                icon_left="◆",
                glow=True,
            ):
                st.session_state.lab_ui_button_clicks += 1
                st.session_state.lab_ui_button_last = "large"
                st.rerun()

        st.markdown("#### Estados")
        col_loading, col_disabled = st.columns(2)
        with col_loading:
            ui_button(
                "Cargando",
                key="lab_ui_button_loading",
                variant="primary",
                loading=True,
            )

        with col_disabled:
            ui_button(
                "Deshabilitado",
                key="lab_ui_button_disabled",
                variant="secondary",
                disabled=True,
                icon_left="⛔",
            )

    # ============================================================
    # TAB 6 — IMPACTO RESULTADOS
    # ============================================================

    elif tab == "Impacto resultados":
        _render_lab_impacto_resultados(
            df_usuarios=df_usuarios,
            df_res=df_res,
            df_pro=df_pro,
            mapa_banderas=mapa_banderas,
        )

    # ============================================================
    # TAB 7 — FILTROS
    # ============================================================

    elif tab == "Filtros":
        st.markdown("""
<div class="lab-panel">
<h3>Filtros / segmentados</h3>
<div class="lab-note">
Esto puede servir para filtrar jugadores: Todos, Top 5, Fundadores, Con puntos.
</div>
</div>
""", unsafe_allow_html=True)

        filtro = sac.segmented(
            items=[
                sac.SegmentedItem("Todos", icon="people"),
                sac.SegmentedItem("Top 5", icon="trophy"),
                sac.SegmentedItem("Fundadores", icon="award"),
                sac.SegmentedItem("Con puntos", icon="graph-up"),
            ],
            index=0,
            size="md",
            radius="lg",
            return_index=False,
            key="lab_segmented_filters"
        )

        st.write("Filtro elegido:", filtro)

        st.markdown("""
<div class="lab-panel">
<h3>Vista previa de filtro</h3>
<div class="lab-note">
Acá después podríamos mostrar una lista filtrada de jugadores.
</div>
</div>
""", unsafe_allow_html=True)

    # ============================================================
    # TAB 6 — INSIGNIAS
    # ============================================================

    elif tab == "Insignias":
        st.markdown("""
<div class="lab-panel">
<h3>Tags / Insignias</h3>
<div class="lab-note">
Prueba para el futuro Muro de Insignias.
</div>
</div>
""", unsafe_allow_html=True)

        sac.tags(
            [
                sac.Tag("Puntero", icon="trophy", color="gold"),
                sac.Tag("On Fire", icon="fire", color="red"),
                sac.Tag("Master Exactos", icon="bullseye", color="blue"),
                sac.Tag("Fundador", icon="award", color="purple"),
                sac.Tag("Mentalista", icon="lightbulb", color="cyan"),
                sac.Tag("Bilardista", icon="shield", color="gray"),
            ],
            key="lab_tags_badges"
        )

        st.markdown("""
<div class="lab-preview-card">
<div class="lab-preview-name">Muro de Insignias</div>
<div class="lab-preview-meta">
Acá podemos probar estilos antes de pasarlos a Jugadores.
</div>
</div>
""", unsafe_allow_html=True)
