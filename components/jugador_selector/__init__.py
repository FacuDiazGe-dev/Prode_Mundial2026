import os
import streamlit.components.v1 as components


_COMPONENT_DIR = os.path.dirname(os.path.abspath(__file__))
_FRONTEND_DIR = os.path.join(_COMPONENT_DIR, "frontend")


_jugador_selector = components.declare_component(
    "jugador_selector",
    path=_FRONTEND_DIR,
)


def jugador_selector(jugadores, seleccionado=None, key=None):
    """
    Selector visual de jugadores.

    Parámetros
    ----------
    jugadores : list[dict]
        Lista de jugadores. Cada jugador debe tener:
        {
            "id": "messi",
            "nombre": "Lionel Messi",
            "equipo": "Argentina",
            "avatar": "https://..."
        }

    seleccionado : str | None
        ID del jugador seleccionado actualmente.

    key : str | None
        Key única de Streamlit.

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
