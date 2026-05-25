from pathlib import Path

import streamlit.components.v1 as components


_FRONTEND_DIR = Path(__file__).parent / "frontend"

_pronostico_cards = components.declare_component(
    "pronostico_cards_v2",
    path=str(_FRONTEND_DIR),
)


def pronostico_cards(pronosticos, key=None):
    return _pronostico_cards(
        pronosticos=pronosticos,
        default=pronosticos,
        key=key,
    )
