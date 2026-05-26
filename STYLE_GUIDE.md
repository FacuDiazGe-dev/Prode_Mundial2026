# Guia de estilos

Esta guia define una base visual comun para las secciones repetitivas del Prode.
No busca reemplazar disenos especiales como el hero de Inicio, ranking personal,
cards destacadas o componentes custom. Es una referencia para mantener coherencia
en textos, paneles y cards comunes.

## Principio

- Lo repetitivo usa estilos compartidos.
- Lo especial mantiene clase y diseno propio.
- Cada migracion debe verse igual antes y despues.
- No mezclar limpieza visual con cambios de logica.

## Tonos

| Tono | Uso |
|---|---|
| `night` | Titulos principales claros sobre fondos claros. |
| `dark` | Titulos de paneles/cards. |
| `muted` | Subtitulos, ayuda, texto secundario. |
| `light` | Texto sobre fondos oscuros. |
| `gold` | Enfasis premium, iconos, pills o estados destacados. |
| `danger` | Acciones o mensajes destructivos. |
| `success` | Confirmaciones o estados exitosos. |

## Familias de texto

| Estilo | Uso recomendado |
|---|---|
| `display_title` | Titulo principal de una seccion. |
| `section_subtitle` | Bajada debajo del titulo principal. |
| `panel_title` | Titulo dentro de paneles grandes. |
| `panel_subtitle` | Texto auxiliar debajo de un titulo de panel. |
| `card_title` | Titulo de cards o items repetidos. |
| `card_body` | Cuerpo de cards, listas y descripciones. |
| `caption` | Fechas, labels chicos, metadata. |
| `pill_label` | Texto dentro de chips/pills. |

## Superficies

| Superficie | Uso recomendado |
|---|---|
| `panel_light` | Contenedores principales blancos. |
| `card_light` | Cards internas o items repetidos. |
| `panel_dark` | Paneles destacados sobre azul noche. |

## Helpers disponibles

```python
from styles_shared import (
    css_text,
    css_section_title,
    css_surface,
    css_panel_base,
    css_panel_header,
)
```

### Texto suelto

```python
css_text("mi-clase", style="card_title", tone="dark")
```

### Titulo de seccion

```python
css_section_title("reglas-title")
```

Genera estilos para:

- `.reglas-title`
- `.reglas-title h1`
- `.reglas-title p`

### Panel comun

```python
css_panel_base("reglas-panel")
```

### Header de panel

```python
css_panel_header("reglas")
```

Genera estilos para:

- `.reglas-panel-header`
- `.reglas-panel-icon`
- `.reglas-panel-title`
- `.reglas-panel-subtitle`

## Casos especiales

Mantener con CSS propio:

- Hero de Inicio.
- Posicion/ranking personal dentro del hero.
- Ranking principal si necesita layout propio.
- Cards con fondos del bucket.
- Custom components (`ui_button`, `jugador_selector`, `pronostico_cards`).
- Panel de Control hasta que se migre de forma aislada.

## Orden de migracion recomendado

1. `reglas.py`
2. `jugadores.py`
3. `mis_pronosticos.py` por partes chicas.
4. `foro.py`
5. `inicio.py` por bloques.
6. `panel_control.py` al final.
