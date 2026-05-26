# Auditoria de estilos

Rama: `refactor-estilos-secciones`

Objetivo: ordenar CSS/HTML embebido por seccion sin cambiar logica de negocio ni comportamiento visual.

## Resumen por archivo

| Archivo | Bloques `<style>` | `unsafe_allow_html` | CSS de `stButton` | `border-radius` | `box-shadow` |
|---|---:|---:|---:|---:|---:|
| `sections/inicio.py` | 6 | 12 | 3 | 68 | 71 |
| `sections/mis_pronosticos.py` | 2 | 18 | 7 | 49 | 41 |
| `styles_config.py` | 2 | 3 | 0 | 13 | 4 |
| `sections/laboratorio.py` | 1 | 17 | 0 | 12 | 4 |
| `sections/foro.py` | 1 | 9 | 0 | 24 | 9 |
| `app.py` | 1 | 5 | 0 | 3 | 1 |
| `sections/reglas.py` | 1 | 4 | 0 | 5 | 2 |
| `sections/jugadores.py` | 1 | 4 | 0 | 24 | 16 |
| `sections/panel_control.py` | 0 | 0 | 0 | 0 | 0 |

## Hallazgos

- La mayor concentracion de CSS esta en `inicio.py`, especialmente ranking, noticias, resultados y comentarios.
- `mis_pronosticos.py` tiene estilos compartibles con `reglas.py`, `foro.py`, `jugadores.py` y `laboratorio.py`: titulos de seccion, paneles blancos, headers con icono dorado, sombras y radios.
- Todavia existen estilos directos sobre botones nativos de Streamlit en `mis_pronosticos.py` e `inicio.py`. Conviene migrarlos gradualmente a `ui_button` cuando sean acciones simples.
- `panel_control.py` casi no tiene CSS embebido. Conviene dejarlo para el final por riesgo funcional, no por complejidad visual.
- Los custom components tienen CSS encapsulado y no deberian mezclarse con la limpieza de CSS global.

## Tokens visuales repetidos

- Azul noche: `#07111F`, `#07111f`, `#0f172a`.
- Dorado: `#F4C542`, `#f4c542`, `rgba(244,197,66,...)`.
- Texto secundario: `#64748b`.
- Blanco frio: `#F8FAFC`, `#f8fafc`.
- Sombra suave: `0 12px 30px rgba(15,23,42,0.06)`.
- Radio panel: `18px`.
- Radio card: `14px` / `16px`.
- Radio pill: `999px`.

## Candidatos a estilos comunes

- `.page-section-title`, `.foro-title`, `.lab-title` y estructuras similares.
- Panel blanco con borde claro y sombra suave.
- Header de panel con icono dorado y titulo Montserrat.
- Chips/pills dorados.
- Estados de card seleccionada con borde dorado.
- Botones simples que hoy dependen de CSS sobre `stButton`.

## Orden recomendado

1. Crear un modulo comun de estilos con tokens y helpers, sin cambiar visual.
2. Migrar primero `sections/reglas.py` por ser pequeno y de bajo riesgo.
3. Migrar `sections/jugadores.py`, porque comparte patrones de panel/card y ya usa custom component.
4. Migrar partes acotadas de `sections/mis_pronosticos.py`, evitando tocar la logica de guardado.
5. Dividir `sections/inicio.py` por bloques: hero, ranking, noticias, resultados, comentarios.
6. Dejar `sections/foro.py` y `sections/panel_control.py` para el final.

## Regla de trabajo

Cada paso debe mantener la web visualmente igual. La primera etapa solo debe extraer CSS repetido o crear helpers sin alterar HTML ni logica.

## Prueba 1: `sections/reglas.py`

Se creo `styles_shared.py` con helpers para:

- Titulos de seccion.
- Panel base blanco.
- Header de panel con icono, titulo y subtitulo.

`sections/reglas.py` ahora usa esos helpers y conserva localmente solo el CSS especifico de FAQ y ajustes del decalogo.

## Sistema base

Se agrego `STYLE_GUIDE.md` como guia humana del sistema de estilos. La intencion es unificar jerarquias repetitivas:

- Titulos principales.
- Subtitulos principales.
- Titulos/subtitulos de paneles.
- Titulos/cuerpos de cards.
- Captions, pills y metadata.
- Superficies claras/oscuras.

Los bloques especiales, como el hero de Inicio o el ranking personal dentro del hero, deben conservar estilos propios.
