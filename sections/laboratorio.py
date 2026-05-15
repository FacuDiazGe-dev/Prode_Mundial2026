import streamlit as st
import streamlit_antd_components as sac


def render_laboratorio(df_usuarios=None, df_ranking=None):
    st.markdown("""
    <div style="margin-bottom: 22px;">
        <h1 style="
            font-family: Montserrat, sans-serif;
            font-size: 34px;
            font-weight: 900;
            color: #07111F;
            margin: 0;
            letter-spacing: -0.04em;
        ">
            🧪 Laboratorio
        </h1>
        <p style="
            margin: 6px 0 0 0;
            color: #64748b;
            font-size: 15px;
            font-weight: 600;
        ">
            Zona de pruebas para componentes nuevos antes de llevarlos a la app.
        </p>
    </div>
    """, unsafe_allow_html=True)

    st.divider()

    st.subheader("Selector de jugadores — Ant Design Buttons")

    if df_usuarios is None or df_usuarios.empty:
        st.warning("No hay usuarios cargados para probar.")
        return

    nombres = df_usuarios["NOMBRE"].fillna("Jugador").astype(str).tolist()

    elegido = sac.buttons(
        items=nombres,
        label="Seleccioná un jugador",
        index=0,
        direction="vertical",
        align="start",
        size="middle",
        radius="lg",
        return_index=False,
        key="lab_selector_jugadores"
    )

    st.write("Jugador seleccionado:", elegido)

    st.divider()

    st.subheader("Selector horizontal")

    elegido_horizontal = sac.segmented(
        items=nombres[:5],
        label="Prueba segmentada",
        index=0,
        size="middle",
        return_index=False,
        key="lab_segmented_jugadores"
    )

    st.write("Segmentado seleccionado:", elegido_horizontal)

    st.divider()

    st.subheader("Badges / Tags")

    sac.tags(
        [
            sac.Tag("Puntero", icon="trophy", color="gold"),
            sac.Tag("On Fire", icon="fire", color="red"),
            sac.Tag("Fundador", icon="star", color="blue"),
            sac.Tag("Mentalista", icon="bulb", color="purple"),
        ],
        key="lab_tags"
    )
