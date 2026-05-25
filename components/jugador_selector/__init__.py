from pathlib import Path

import streamlit.components.v1 as components


_FRONTEND_DIR = Path(__file__).parent / "frontend"

_jugador_selector = components.declare_component(
    "jugador_selector",
    path=str(_FRONTEND_DIR),
)


def jugador_selector(jugadores, seleccionado=None, key=None):
    return _jugador_selector(
        jugadores=jugadores,
        seleccionado=seleccionado,
        default=seleccionado,
        key=key,
    )
