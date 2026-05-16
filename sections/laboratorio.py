import streamlit as st
import pandas as pd
import streamlit_antd_components as sac

try:
    from streamlit_elements import elements, mui
    ELEMENTS_AVAILABLE = True
except Exception:
    elements = None
    mui = None
    ELEMENTS_AVAILABLE = False

def render_laboratorio(df_usuarios=None, df_ranking=None):
    st.markdown("""
<style>
.lab-title {
    margin-bottom: 22px;
}

.lab-title h1 {
    font-family: 'Montserrat', sans-serif;
    font-size: 34px;
    font-weight: 900;
    color: #07111F;
    margin: 0;
    letter-spacing: -0.04em;
}

.lab-title p {
    margin: 6px 0 0 0;
    color: #64748b;
    font-size: 15px;
    font-weight: 600;
}

.lab-panel {
    background: rgba(255,255,255,0.94);
    border: 1px solid rgba(226,232,240,0.9);
    border-radius: 18px;
    padding: 16px;
    box-shadow: 0 12px 30px rgba(15,23,42,0.06);
    margin-bottom: 18px;
}

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
.lab-card {
    background: rgba(255,255,255,0.94);
    border: 1px solid rgba(226,232,240,0.9);
    border-radius: 18px;
    padding: 16px;
    box-shadow: 0 12px 30px rgba(15,23,42,0.06);
    margin-bottom: 18px;
}

.lab-card-header {
    display: flex;
    align-items: center;
    gap: 10px;
    padding-bottom: 14px;
    margin-bottom: 12px;
    border-bottom: 1px solid rgba(226,232,240,0.75);
}

.lab-card-icon {
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

.lab-card-title {
    font-family: 'Montserrat', sans-serif;
    font-size: 18px;
    font-weight: 900;
    color: #0f172a;
}

.lab-card-subtitle {
    color: #64748b;
    font-size: 12px;
    font-weight: 700;
    margin-top: 2px;
}

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
    .lab-card {
        padding: 13px;
    }

    .lab-selector-box {
        max-height: 300px;
    }

    .lab-card-title {
        font-size: 16px;
    }

    .lab-card-subtitle {
        font-size: 11px;
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
""", unsafe_allow_html=True)

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

    if "lab_mui_click_event" not in st.session_state:
        st.session_state.lab_mui_click_event = None

    if "lab_mui_last_event_id" not in st.session_state:
        st.session_state.lab_mui_last_event_id = None

    if "lab_mui_action" not in st.session_state:
        st.session_state.lab_mui_action = ""

    if "lab_mui_like_count" not in st.session_state:
        st.session_state.lab_mui_like_count = 0

    if "lab_mui_dislike_count" not in st.session_state:
        st.session_state.lab_mui_dislike_count = 0

    if "lab_mui_total_actions" not in st.session_state:
        st.session_state.lab_mui_total_actions = 0

    def extraer_id_evento(event):
        """
        Intenta extraer el id del evento MUI.
        Primero por atributos tipo objeto, después por diccionario.
        """

        if event is None:
            return None

        # Caso tipo objeto: event.target.id
        try:
            target = event.target
            event_id = getattr(target, "id", None)
            if event_id:
                return event_id
        except Exception:
            pass

        # Caso tipo objeto: event.currentTarget.id
        try:
            current_target = event.currentTarget
            event_id = getattr(current_target, "id", None)
            if event_id:
                return event_id
        except Exception:
            pass

        # Caso diccionario
        try:
            event_id = event.get("target", {}).get("id", None)
            if event_id:
                return event_id
        except Exception:
            pass

        try:
            event_id = event.get("currentTarget", {}).get("id", None)
            if event_id:
                return event_id
        except Exception:
            pass

        return None

    def procesar_evento_mui():
        event = st.session_state.get("lab_mui_click_event")
        action_id = extraer_id_evento(event)

        if not action_id:
            return

        if action_id == st.session_state.lab_mui_last_event_id:
            return

        st.session_state.lab_mui_last_event_id = action_id

        if str(action_id).startswith("like_"):
            msg_id = str(action_id).replace("like_", "")
            st.session_state.lab_mui_like_count += 1
            st.session_state.lab_mui_total_actions += 1
            st.session_state.lab_mui_action = f"👍 Like en mensaje {msg_id}"

        elif str(action_id).startswith("dislike_"):
            msg_id = str(action_id).replace("dislike_", "")
            st.session_state.lab_mui_dislike_count += 1
            st.session_state.lab_mui_total_actions += 1
            st.session_state.lab_mui_action = f"👎 Dislike en mensaje {msg_id}"

        elif str(action_id).startswith("delete_"):
            msg_id = str(action_id).replace("delete_", "")
            st.session_state.lab_mui_total_actions += 1
            st.session_state.lab_mui_action = f"🗑️ Borrar mensaje {msg_id}"

    procesar_evento_mui()
    tab = sac.tabs(
        [
            sac.TabsItem("Selector vertical", icon="people"),
            sac.TabsItem("Botón + Card", icon="layout-sidebar"),
            sac.TabsItem("Foro MUI", icon="chat-dots"),
            sac.TabsItem("Botones", icon="collection"),
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

            avatar = user.get("AVATAR_URL", "")
            avatar_html = ""

            if pd.notna(avatar) and str(avatar).strip() != "":
                avatar_html = f'<img src="{avatar}" class="lab-preview-avatar">'

            with st.container(border=True):
                st.markdown(
                    f"""
<div class="lab-card-header">
<div class="lab-card-icon">🧾</div>
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
<div class="lab-preview-meta">@{user["USUARIO"]} · {user["EQUIPO FAVORITO"]}</div>
</div>
</div>
</div>

<div class="lab-return-box">
<div class="lab-return-label">Valor devuelto por el componente</div>
<div class="lab-return-value">{elegido}</div>
</div>
""",
                    unsafe_allow_html=True
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

            avatar = user.get("AVATAR_URL", "")
            avatar_html = ""

            if pd.notna(avatar) and str(avatar).strip() != "":
                avatar_html = f'<img src="{avatar}" class="lab-preview-avatar">'

            with st.container(border=True):
                st.markdown(
                    f"""
<div class="lab-card-header">
<div class="lab-card-icon">🧾</div>
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
<div class="lab-preview-meta">@{user["USUARIO"]} · {user["EQUIPO FAVORITO"]}</div>
</div>
</div>
</div>

<div class="lab-return-box">
<div class="lab-return-label">Valor guardado en session_state</div>
<div class="lab-return-value">{st.session_state.lab_jugador_card_sel}</div>
</div>
""",
                    unsafe_allow_html=True
                )

    # ============================================================
    # TAB 3 — FORO MUI / STREAMLIT-ELEMENTS
    # ============================================================

    elif tab == "Foro MUI":
        st.write("DEBUG click event:", st.session_state.get("lab_mui_click_event"))
        st.write("DEBUG last event id:", st.session_state.get("lab_mui_last_event_id"))
        st.write("DEBUG action:", st.session_state.get("lab_mui_action"))
        st.write("DEBUG total actions:", st.session_state.get("lab_mui_total_actions"))

        st.markdown("""
<div class="lab-panel">
<h3>Foro MUI con streamlit-elements</h3>
<div class="lab-note">
Prueba para resolver el problema real del Foro: cards, scroll interno y botones dentro del mismo árbol visual React / Material UI.
</div>
</div>
""", unsafe_allow_html=True)

        if not ELEMENTS_AVAILABLE:
            st.error(
                "streamlit-elements no está instalado. "
                "Agregá streamlit-elements==0.1.* en requirements.txt y reiniciá la app."
            )
            return

        if st.session_state.lab_mui_action:
            st.success(
                f"✅ Botón MUI funcionando · {st.session_state.lab_mui_action} · "
                f"Acciones totales: {st.session_state.lab_mui_total_actions} · "
                f"👍 {st.session_state.lab_mui_like_count} · "
                f"👎 {st.session_state.lab_mui_dislike_count} · "
                f"Recibido: {st.session_state.lab_mui_selected_action}"
            )
        else:
            st.info("🧪 Todavía no se presionó ningún botón MUI.")

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

                # Indicador visual dentro del panel MUI
                with mui.Box(
                    sx={
                        "display": "flex",
                        "alignItems": "center",
                        "justifyContent": "space-between",
                        "gap": 1,
                        "mb": 1.5,
                        "p": 1.2,
                        "borderRadius": "14px",
                        "background": "rgba(248,250,252,0.92)",
                        "border": "1px solid rgba(226,232,240,0.9)",
                    }
                ):
                    mui.Typography(
                        st.session_state.lab_mui_action
                        if st.session_state.lab_mui_action
                        else "Esperando acción MUI...",
                        variant="body2",
                        sx={
                            "fontWeight": 800,
                            "color": "#334155",
                        },
                    )

                    mui.Box(
                        f"Clicks: {st.session_state.lab_mui_total_actions}",
                        sx={
                            "px": 1.2,
                            "py": 0.45,
                            "borderRadius": "999px",
                            "background": "#07111F",
                            "color": "#F4C542",
                            "fontSize": "12px",
                            "fontWeight": 900,
                            "whiteSpace": "nowrap",
                        },
                    )
                
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
                        "Cards, imágenes, scroll y botones MUI integrados",
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

                                # Botones dentro de la card
                                with mui.Box(
                                    sx={
                                        "display": "flex",
                                        "gap": 1,
                                        "mt": 1.2,
                                        "flexWrap": "wrap",
                                    }
                                ):
                                    mui.Button(
                                        f"👍 {st.session_state.lab_mui_like_count}",
                                        variant="outlined",
                                        size="small",
                                        id=f"like_{msg['id']}",
                                        key=f"lab_like_{msg['id']}",
                                        onClick=sync("lab_mui_click_event"),
                                        sx={
                                            "textTransform": "none",
                                            "fontWeight": 900,
                                            "borderRadius": "10px",
                                            "minHeight": 30,
                                        },
                                    )

                                    mui.Button(
                                        f"👎 {st.session_state.lab_mui_dislike_count}",
                                        variant="outlined",
                                        size="small",
                                        id=f"dislike_{msg['id']}",
                                        key=f"lab_dislike_{msg['id']}",
                                        onClick=sync("lab_mui_click_event"),
                                        sx={
                                            "textTransform": "none",
                                            "fontWeight": 900,
                                            "borderRadius": "10px",
                                            "minHeight": 30,
                                        },
                                    )
                                    mui.Button(
                                        "🗑️ Borrar",
                                        variant="outlined",
                                        color="warning",
                                        size="small",
                                        id=f"delete_{msg['id']}",
                                        key=f"lab_delete_{msg['id']}",
                                        onClick=sync("lab_mui_click_event"),
                                        sx={
                                            "textTransform": "none",
                                            "fontWeight": 900,
                                            "borderRadius": "10px",
                                            "minHeight": 30,
                                        },
                                    )
    
    # ============================================================
    # TAB 2 — BOTONES
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
    # TAB 3 — FILTROS
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
    # TAB 4 — INSIGNIAS
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
