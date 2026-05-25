# Guia rapida del codigo

Este archivo es un mapa para orientarte cuando revises el proyecto. La idea es saber donde mirar primero sin tener que entender todo Streamlit de golpe.

## Flujo principal

- `app.py`: entrada principal. Configura Streamlit, carga datos desde Supabase, maneja login/registro, arma el menu lateral y llama a cada pantalla.
- `services/supabase_service.py`: capa de datos. Lee y escribe tablas de Supabase, y adapta nombres de columnas para que el resto de la app use un formato estable.
- `ranking_logic.py`: reglas de puntos, ranking general e insignias.
- `tools.py`: utilidades compartidas, principalmente banderas y subida de imagenes al bucket de Google Cloud Storage.
- `styles_config.py`: constantes visuales, estilos globales, sidebar y banners reutilizables.
- `sections/`: pantallas de la aplicacion. Cada archivo tiene una funcion `render_*`.

## Pantallas

- `sections/inicio.py`: portada, podio, ranking, noticias, resultados y chat rapido.
- `sections/mis_pronosticos.py`: pronosticos del usuario, evolucion de puntos y perfil personal.
- `sections/jugadores.py`: plantel, ficha de jugador, pronosticos e insignias.
- `sections/foro.py`: comunidad, mensajes, noticias, reacciones e insignias.
- `sections/reglas.py`: reglas y preguntas frecuentes.
- `sections/panel_control.py`: administracion de resultados, usuarios, roles, inscripciones y mantenimiento.
- `sections/laboratorio.py`: pruebas visuales o prototipos.

## Datos importantes

- Resultados: tabla `resultados`.
- Usuarios: tabla `usuarios`.
- Pronosticos: tabla `pronosticos`.
- Comunidad: tabla `foro`.
- Noticias: tabla `noticias`.
- Configuracion: tabla usada por `get_config_app()` para mantenimiento, registro y cierre de pronosticos.

## Secretos locales

El archivo real de secretos es:

```text
.streamlit/secrets.toml
```

Ese archivo no debe subirse a GitHub. Debe contener:

- `SUPABASE_URL`
- `SUPABASE_SERVICE_ROLE_KEY`
- `[connections.gsheets]` con la service account de Google Cloud usada para subir imagenes.

## Zonas para limpiar de a poco

- CSS repetido en `inicio.py`, `mis_pronosticos.py`, `foro.py` y `jugadores.py`.
- Helpers repetidos como `flag_html`, normalizadores de badges y constructores de insignias.
- URLs de assets repetidas que conviene centralizar en `styles_config.py`.
- HTML largo embebido en `st.markdown(..., unsafe_allow_html=True)`.

## Regla de trabajo segura

Como la web productiva usa Supabase real, probar navegacion local no modifica datos. Pero editar perfil, foro, noticias, resultados, roles o pronosticos desde local si puede escribir en la base real si usas los mismos secretos.
