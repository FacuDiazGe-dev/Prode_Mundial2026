# ui_button

Componente visual reutilizable para botones con HTML/CSS/JS encapsulado en iframe.
No modifica estilos globales de Streamlit.

## Uso basico

```python
from components.ui_button import ui_button

clicked = ui_button(
    label="Editar Perfil",
    key="btn_editar_perfil",
    icon_left="✏️",
    variant="primary",
)

if clicked:
    st.session_state.editando_perfil = True
    st.rerun()
```

La funcion devuelve `True` solo en el rerun inmediato al click. En cualquier
otro render devuelve `False`.

## Props

- `label`: texto visible.
- `key`: obligatoria y unica por boton.
- `variant`: `primary`, `secondary`, `dark`, `ghost`, `danger`, `locked`, `success`.
- `size`: `sm`, `md`, `lg`.
- `full_width`: ocupa todo el ancho disponible.
- `icon_left` / `icon_right`: iconos o texto corto a los lados.
- `disabled`: desactiva el click.
- `loading`: muestra spinner y desactiva el click.
- `align`: `left`, `center`, `right`.
- `compact`: reduce altura y espaciado.
- `glow`: agrega brillo suave.
- `rounded`: `pill`, `card`, `soft`.
- `texture`: activa textura interna.
- `texture_url`: imagen opcional para textura.

## Formularios

El componente puede mostrarse cerca de formularios, pero no reemplaza a
`st.form_submit_button` para enviar un `st.form`. Si el formulario usa inputs
nativos de Streamlit, mantener el submit nativo para guardar.

## Desarrollo local del componente

Este componente actualmente usa un frontend HTML estatico en `frontend/index.html`.
Por defecto debe quedar:

```python
_RELEASE = True
```

Con esa configuracion Streamlit carga el componente desde `path`, sin depender
de ningun puerto local ni de `npm`.

Si en el futuro se migra a React/Vite:

```python
_RELEASE = False
_DEV_SERVER_URL = "http://localhost:5173"
```

En ese modo hay que correr dos terminales:

```powershell
streamlit run app.py
cd components/ui_button/frontend
npm run dev
```

Si el frontend dev no esta levantado o el puerto no coincide, volver a
`_RELEASE = True`.

Para desactivar temporalmente el custom component sin romper la app:

```python
_COMPONENT_ENABLED = False
```

Esto usa un `st.button` nativo como fallback funcional.

## Recomendaciones

- Usar `primary` para acciones principales.
- Usar `secondary` o `ghost` para acciones neutras.
- Usar `success` para confirmaciones.
- Usar `danger` para acciones destructivas.
- Usar `locked` o `disabled=True` para acciones bloqueadas.
- Migrar botones por grupos y probar mobile antes de pasar a produccion.
