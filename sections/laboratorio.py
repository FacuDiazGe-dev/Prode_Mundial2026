import streamlit as st
import pandas as pd
import streamlit_antd_components as sac


def render_laboratorio(df_usuarios=None, df_ranking=None):
    st.markdown("""
<style>
.lab-title {
    margin-bottom: 22px;
}

.lab-title h1 {
    font-family: 'Montserrat', sans-serif;
    font-size: 34px;
    font-weight: 900;
    color: #07111F;
    margin: 0;
    letter-spacing: -0.04em;
}

.lab-title p {
    margin: 6px 0 0 0;
    color: #64748b;
    font-size: 15px;
    font-weight: 600;
}

.lab-panel {
    background: rgba(255,255,255,0.94);
    border: 1px solid rgba(226,232,240,0.9);
    border-radius: 18px;
    padding: 16px;
    box-shadow: 0 12px 30px rgba(15,23,42,0.06);
    margin-bottom: 18px;
}

.lab-panel h3 {
    margin-top: 0;
    color: #07111F;
    font-family: 'Montserrat', sans-serif;
    font-weight: 900;
}

.lab-note {
    color: #64748b;
    font-size: 13px;
    font-weight: 700;
    margin-bottom: 12px;
}

.lab-preview-card {
    background:
        linear-gradient(
            135deg,
            rgba(7,17,31,0.98),
            rgba(15,23,42,0.94)
        );
    color: white;
    border-radius: 16px;
    padding: 16px;
    margin-top: 12px;
    border: 1px solid rgba(244,197,66,0.24);
}

.lab-preview-name {
    font-family: 'Montserrat', sans-serif;
    font-size: 20px;
    font-weight: 900;
}

.lab-preview-meta {
    color: rgba(255,255,255,0.68);
    font-size: 12px;
    font-weight: 800;
    margin-top: 4px;
}

.lab-player-row {
    display: flex;
    align-items: center;
    gap: 10px;
}

.lab-player-avatar {
    width: 36px;
    height: 36px;
    border-radius: 50%;
    object-fit: cover;
    border: 2px solid rgba(244,197,66,0.8);
}
</style>
""", unsafe_allow_html=True)

    st.markdown("""
<div class="lab-title">
<h1>🧪 Laboratorio</h1>
<p>Zona de pruebas para componentes antes de llevarlos a la app real.</p>
</div>
""", unsafe_allow_html=True)

    if df_usuarios is None or df_usuarios.empty:
        st.warning("No hay usuarios cargados para probar.")
        return

    df_lab = df_usuarios.copy()
    df_lab["NOMBRE"] = df_lab["NOMBRE"].fillna("Jugador").astype(str)
    df_lab["USUARIO"] = df_lab["USUARIO"].fillna("").astype(str)
    df_lab["EQUIPO FAVORITO"] = df_lab["EQUIPO FAVORITO"].fillna("-").astype(str)

    nombres = df_lab["NOMBRE"].tolist()

    tab = sac.tabs(
        [
            sac.TabsItem("Selector vertical", icon="people"),
            sac.TabsItem("Botones", icon="collection"),
            sac.TabsItem("Filtros", icon="funnel"),
            sac.TabsItem("Insignias", icon="award"),
        ],
        align="center",
        size="md",
        key="lab_tabs"
    )

    # ============================================================
    # TAB 1 — SELECTOR VERTICAL
    # ============================================================

    if tab == "Selector vertical":
        st.markdown("""
<div class="lab-panel">
<h3>Selector vertical de jugadores</h3>
<div class="lab-note">
Prueba para reemplazar el selectbox por un selector más visual. Evaluar mobile, scroll y nombres largos.
</div>
</div>
""", unsafe_allow_html=True)

        col1, col2 = st.columns([1, 1], gap="large")

        with col1:
            elegido = sac.buttons(
                items=nombres,
                index=0,
                direction="vertical",
                align="start",
                size="middle",
                radius="lg",
                return_index=False,
                key="lab_selector_vertical"
            )

        with col2:
            user = df_lab[df_lab["NOMBRE"] == elegido].iloc[0]
            st.markdown(
                f"""
<div class="lab-preview-card">
<div class="lab-preview-name">{user["NOMBRE"]}</div>
<div class="lab-preview-meta">@{user["USUARIO"]} · {user["EQUIPO FAVORITO"]}</div>
</div>
""",
                unsafe_allow_html=True
            )

            st.write("Valor devuelto por el componente:")
            st.code(str(elegido))

    # ============================================================
    # TAB 2 — BOTONES
    # ============================================================

    elif tab == "Botones":
        st.markdown("""
<div class="lab-panel">
<h3>Botones como selector</h3>
<div class="lab-note">
Sirve para pocos jugadores o para categorías. Si hay muchos, puede volverse largo.
</div>
</div>
""", unsafe_allow_html=True)

        max_items = st.slider(
            "Cantidad de jugadores a mostrar",
            min_value=3,
            max_value=min(20, len(nombres)),
            value=min(8, len(nombres))
        )

        elegido_btn = sac.buttons(
            items=nombres[:max_items],
            index=0,
            direction="vertical",
            align="start",
            size="large",
            radius="xl",
            return_index=False,
            key="lab_buttons_large"
        )

        st.success(f"Seleccionado: {elegido_btn}")

    # ============================================================
    # TAB 3 — FILTROS
    # ============================================================

    elif tab == "Filtros":
        st.markdown("""
<div class="lab-panel">
<h3>Filtros / segmentados</h3>
<div class="lab-note">
Esto puede servir para filtrar jugadores: Todos, Top 5, Fundadores, Con puntos.
</div>
</div>
""", unsafe_allow_html=True)

        filtro = sac.segmented(
            items=[
                sac.SegmentedItem("Todos", icon="people"),
                sac.SegmentedItem("Top 5", icon="trophy"),
                sac.SegmentedItem("Fundadores", icon="award"),
                sac.SegmentedItem("Con puntos", icon="graph-up"),
            ],
            index=0,
            size="md",
            radius="lg",
            return_index=False,
            key="lab_segmented_filters"
        )

        st.write("Filtro elegido:", filtro)

        st.markdown("""
<div class="lab-panel">
<h3>Vista previa de filtro</h3>
<div class="lab-note">
Acá después podríamos mostrar una lista filtrada de jugadores.
</div>
</div>
""", unsafe_allow_html=True)

    # ============================================================
    # TAB 4 — INSIGNIAS
    # ============================================================

    elif tab == "Insignias":
        st.markdown("""
<div class="lab-panel">
<h3>Tags / Insignias</h3>
<div class="lab-note">
Prueba para el futuro Muro de Insignias.
</div>
</div>
""", unsafe_allow_html=True)

        sac.tags(
            [
                sac.Tag("Puntero", icon="trophy", color="gold"),
                sac.Tag("On Fire", icon="fire", color="red"),
                sac.Tag("Master Exactos", icon="bullseye", color="blue"),
                sac.Tag("Fundador", icon="award", color="purple"),
                sac.Tag("Mentalista", icon="lightbulb", color="cyan"),
                sac.Tag("Bilardista", icon="shield", color="gray"),
            ],
            key="lab_tags_badges"
        )

        st.markdown("""
<div class="lab-preview-card">
<div class="lab-preview-name">Muro de Insignias</div>
<div class="lab-preview-meta">
Acá podemos probar estilos antes de pasarlos a Jugadores.
</div>
</div>
""", unsafe_allow_html=True)
