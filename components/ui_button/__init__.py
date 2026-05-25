from pathlib import Path

import streamlit as st
import streamlit.components.v1 as components


_FRONTEND_DIR = Path(__file__).parent / "frontend"

_ui_button = components.declare_component(
    "ui_button",
    path=str(_FRONTEND_DIR),
)


def ui_button(
    label,
    action,
    icon=None,
    variant="primary",
    full_width=True,
    disabled=False,
    key=None,
):
    event = _ui_button(
        label=label,
        action=action,
        icon=icon,
        variant=variant,
        full_width=full_width,
        disabled=disabled,
        default=None,
        key=key,
    )

    if not isinstance(event, dict):
        return None

    event_id = event.get("event_id")
    if not event_id:
        return None

    state_key = f"_ui_button_last_event_{key or action}"
    if st.session_state.get(state_key) == event_id:
        return None

    st.session_state[state_key] = event_id
    return event.get("action")
