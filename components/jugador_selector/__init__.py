from pathlib import Path

import streamlit.components.v1 as components


_FRONTEND_DIR = Path(__file__).parent / "frontend"

_jugador_selector = components.declare_component(
    "jugador_selector",
    path=str(_FRONTEND_DIR),
)


def jugador_selector(jugadores, seleccionado=None, key=None):
    """
    Selector visual de jugadores.

    Parametros
    ----------
    jugadores : list[dict]
        Lista de jugadores. Cada jugador debe tener:
        {
            "id": "usuario",
            "nombre": "Nombre visible",
            "usuario": "usuario",
            "equipo": "Equipo favorito",
            "puntos": 0,
            "avatar": "https://..."
        }

    seleccionado : str | None
        ID del jugador seleccionado actualmente.

    key : str | None
        Key unica de Streamlit.

    Retorna
    -------
    str | None
        ID del jugador seleccionado.
    """

    return _jugador_selector(
        jugadores=jugadores,
        seleccionado=seleccionado,
        default=seleccionado,
        key=key,
    )
