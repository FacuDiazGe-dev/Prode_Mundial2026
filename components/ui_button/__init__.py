from pathlib import Path

import streamlit as st
import streamlit.components.v1 as components


_FRONTEND_DIR = Path(__file__).parent / "frontend"
_DEV_SERVER_URL = "http://localhost:5173"
_RELEASE = True
_COMPONENT_ENABLED = True

if _RELEASE:
    _ui_button = components.declare_component(
        "ui_button",
        path=str(_FRONTEND_DIR),
    )
else:
    _ui_button = components.declare_component(
        "ui_button",
        url=_DEV_SERVER_URL,
    )


def ui_button(
    label,
    key=None,
    action=None,
    variant="primary",
    size="md",
    full_width=True,
    icon_left=None,
    icon_right=None,
    disabled=False,
    loading=False,
    align="center",
    compact=False,
    glow=False,
    rounded="soft",
    texture=True,
    texture_url=None,
):
    """Renderiza un boton visual custom y devuelve True solo al hacer click.

    Usar siempre una key unica. El componente vive dentro de un iframe, por eso
    su CSS queda encapsulado y no afecta botones nativos de Streamlit.

    Limitacion conocida: puede mostrarse cerca de formularios, pero no reemplaza
    a st.form_submit_button para enviar un st.form. Para guardar formularios
    nativos, mantener st.form_submit_button.
    """

    if key is None and action is not None:
        key = action

    if not key:
        raise ValueError("ui_button requiere una key unica.")

    if not _COMPONENT_ENABLED:
        return st.button(
            label,
            key=f"{key}_fallback",
            use_container_width=full_width,
            disabled=disabled or loading or variant == "locked",
        )

    event = _ui_button(
        label=label,
        action=action or key,
        variant=variant,
        size=size,
        full_width=full_width,
        icon_left=icon_left,
        icon_right=icon_right,
        disabled=disabled or loading or variant == "locked",
        loading=loading,
        align=align,
        compact=compact,
        glow=glow,
        rounded=rounded,
        texture=texture,
        texture_url=texture_url,
        default=None,
        key=key,
    )

    if not isinstance(event, dict):
        return False

    event_id = event.get("event_id")
    if not event_id:
        return False

    state_key = f"_ui_button_last_event_{key}"
    if st.session_state.get(state_key) == event_id:
        return False

    st.session_state[state_key] = event_id
    return True
