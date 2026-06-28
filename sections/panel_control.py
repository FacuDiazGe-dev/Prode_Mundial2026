import streamlit as st
import pandas as pd

from ranking_logic import obtener_ranking_eliminatoria
from services.football_data_service import sugerir_estados_partidos_api
from services.supabase_service import (
    get_resultados_supabase,
    get_usuarios_supabase,
    get_pronosticos_supabase,
    guardar_pronosticos_supabase,
    eliminar_usuario_supabase,
    actualizar_rol_usuario_supabase,
    actualizar_aporte_usuario_supabase,
    actualizar_eliminatoria_usuario_supabase,
    get_config_app,
    actualizar_config_supabase,
    get_eliminatoria_app,
    get_pronosticos_eliminatoria_app,
    actualizar_equipos_eliminatoria_supabase,
    guardar_resultado_eliminatoria_supabase,
    guardar_resultados_supabase,
    guardar_estado_partido_supabase
)


def _render_editor_equipos_eliminatoria_16avos(df_res=None):
    """Editor manual de equipos base para la fase eliminatoria."""

    with st.expander("Equipos iniciales de 16avos", expanded=False):
        st.caption(
            "Carga manual de los cruces base. Solo modifica Equipo 1 y Equipo 2 "
            "de los partidos 1 al 16; no toca resultados, estados ni avances."
        )

        df_eliminatoria_admin = get_eliminatoria_app()

        if df_eliminatoria_admin is None or df_eliminatoria_admin.empty:
            st.warning("No se pudo cargar la tabla de eliminatoria.")
            return

        df_16avos_admin = df_eliminatoria_admin[
            df_eliminatoria_admin["fase"].astype(str).str.strip() == "16avos"
        ].copy()

        df_16avos_admin["partido"] = pd.to_numeric(
            df_16avos_admin["partido"],
            errors="coerce"
        )

        df_16avos_admin["slot"] = pd.to_numeric(
            df_16avos_admin["slot"],
            errors="coerce"
        )

        df_16avos_admin = df_16avos_admin[
            df_16avos_admin["partido"].between(1, 16)
        ].copy()

        df_16avos_admin = df_16avos_admin.sort_values(
            ["llave", "slot", "partido"],
            na_position="last"
        )

        df_editor_equipos = df_16avos_admin[
            ["partido", "llave", "slot", "dia", "hora", "equipo_1", "equipo_2"]
        ].rename(
            columns={
                "partido": "N_PARTIDO",
                "llave": "LLAVE",
                "slot": "SLOT",
                "dia": "DIA",
                "hora": "HORA",
                "equipo_1": "EQUIPO_1",
                "equipo_2": "EQUIPO_2",
            }
        )

        df_editor_equipos["N_PARTIDO"] = df_editor_equipos["N_PARTIDO"].astype(int)
        df_editor_equipos["SLOT"] = df_editor_equipos["SLOT"].fillna(0).astype(int)

        df_equipos_editado = st.data_editor(
            df_editor_equipos,
            use_container_width=True,
            hide_index=True,
            key="editor_equipos_eliminatoria_16avos",
            disabled=["N_PARTIDO", "LLAVE", "SLOT", "DIA", "HORA"],
            column_config={
                "N_PARTIDO": st.column_config.NumberColumn("Partido", width="small"),
                "LLAVE": st.column_config.TextColumn("Llave", width="small"),
                "SLOT": st.column_config.NumberColumn("Slot", width="small"),
                "DIA": st.column_config.TextColumn("Dia", width="medium"),
                "HORA": st.column_config.TextColumn("Hora", width="small"),
                "EQUIPO_1": st.column_config.TextColumn("Equipo 1", width="medium"),
                "EQUIPO_2": st.column_config.TextColumn("Equipo 2", width="medium"),
            }
        )

        if st.button(
            "Guardar equipos de 16avos",
            use_container_width=True
        ):
            ok, msg = actualizar_equipos_eliminatoria_supabase(
                df_equipos_editado
            )

            if ok:
                st.cache_data.clear()
                st.success(msg)
                st.rerun()
            else:
                st.error(msg)

        st.markdown("---")
        st.caption("Asistente: elegí partido y equipos desde la lista oficial.")

        equipos_disponibles = [
            "Alemania", "Arabia Saudita", "Argelia", "Argentina",
            "Australia", "Austria", "Bélgica", "Bosnia y Herzegovina",
            "Brasil", "Cabo Verde", "Canadá", "Catar", "Colombia",
            "Corea del Sur", "Costa de Marfil", "Croacia", "Curazao",
            "Ecuador", "Egipto", "Escocia", "España", "Estados Unidos",
            "Francia", "Ghana", "Haití", "Inglaterra", "Irak", "Irán",
            "Japón", "Jordania", "Marruecos", "México", "Noruega",
            "Nueva Zelanda", "Países Bajos", "Panamá", "Paraguay",
            "Portugal", "República Checa", "República Democrática del Congo",
            "Senegal", "Sudáfrica", "Suecia", "Suiza", "Túnez",
            "Turquía", "Uruguay", "Uzbekistán"
        ]

        if df_res is not None and not df_res.empty:
            for col in ["Equipo_1", "Equipo_2"]:
                if col in df_res.columns:
                    equipos_disponibles.extend(
                        df_res[col]
                        .dropna()
                        .astype(str)
                        .str.strip()
                        .tolist()
                    )

        equipos_disponibles = sorted(
            {
                equipo
                for equipo in equipos_disponibles
                if equipo and equipo.lower() not in ["equipo 1", "equipo 2"]
            }
        )

        if not equipos_disponibles:
            st.warning("No se pudo armar la lista de equipos desde la fase de grupos.")
            return

        partido_options = df_editor_equipos["N_PARTIDO"].astype(int).tolist()
        col_partido, col_equipo_1, col_equipo_2, col_guardar = st.columns(
            [0.9, 1.7, 1.7, 1.1],
            vertical_alignment="bottom"
        )

        with col_partido:
            partido_sel = st.selectbox(
                "Partido",
                partido_options,
                format_func=lambda n: f"#{n}",
                key="asistente_eliminatoria_partido"
            )

        fila_partido = df_editor_equipos[
            df_editor_equipos["N_PARTIDO"].astype(int) == int(partido_sel)
        ].iloc[0]

        equipo_1_actual = str(fila_partido.get("EQUIPO_1", "")).strip()
        equipo_2_actual = str(fila_partido.get("EQUIPO_2", "")).strip()

        idx_equipo_1 = (
            equipos_disponibles.index(equipo_1_actual)
            if equipo_1_actual in equipos_disponibles
            else 0
        )
        idx_equipo_2 = (
            equipos_disponibles.index(equipo_2_actual)
            if equipo_2_actual in equipos_disponibles
            else min(1, len(equipos_disponibles) - 1)
        )

        with col_equipo_1:
            equipo_1_sel = st.selectbox(
                "Equipo 1",
                equipos_disponibles,
                index=idx_equipo_1,
                key="asistente_eliminatoria_equipo_1"
            )

        with col_equipo_2:
            equipo_2_sel = st.selectbox(
                "Equipo 2",
                equipos_disponibles,
                index=idx_equipo_2,
                key="asistente_eliminatoria_equipo_2"
            )

        with col_guardar:
            guardar_partido = st.button(
                "Cargar",
                use_container_width=True
            )

        st.caption(
            f"Llave {fila_partido.get('LLAVE', '')} · Slot {fila_partido.get('SLOT', '')} · "
            f"{fila_partido.get('DIA', '')} {fila_partido.get('HORA', '')}"
        )

        if equipo_1_sel == equipo_2_sel:
            st.warning("Elegiste el mismo equipo en ambos lados.")

        if guardar_partido:
            if equipo_1_sel == equipo_2_sel:
                st.error("No se puede guardar el mismo equipo en ambos lados.")
            else:
                df_partido = pd.DataFrame(
                    [
                        {
                            "N_PARTIDO": int(partido_sel),
                            "EQUIPO_1": equipo_1_sel,
                            "EQUIPO_2": equipo_2_sel,
                        }
                    ]
                )

                ok, msg = actualizar_equipos_eliminatoria_supabase(df_partido)

                if ok:
                    st.cache_data.clear()
                    st.success(msg)
                    st.rerun()
                else:
                    st.error(msg)


def _render_tabla_partidos_eliminatoria():
    """Tabla editable de control rapido de partidos eliminatorios."""

    st.markdown("### Partidos eliminatoria")
    st.caption(
        "Editor rapido para pruebas. En Vivo y Entretiempo usan Live R1/Live R2; "
        "Finalizado usa R1/R2 y Clasifica."
    )

    df_eliminatoria = get_eliminatoria_app()

    if df_eliminatoria is None or df_eliminatoria.empty:
        st.warning("No se pudieron cargar los partidos de eliminatoria.")
        return

    df_tabla = df_eliminatoria.copy()

    for col in ["partido", "slot", "r1", "r2", "live_r1", "live_r2"]:
        if col in df_tabla.columns:
            df_tabla[col] = pd.to_numeric(df_tabla[col], errors="coerce")

    columnas = [
        "partido",
        "fase",
        "llave",
        "slot",
        "equipo_1",
        "r1",
        "r2",
        "equipo_2",
        "estado_partido",
        "live_r1",
        "live_r2",
        "clasificado_lado",
        "dia",
        "hora",
    ]

    columnas_presentes = [
        col
        for col in columnas
        if col in df_tabla.columns
    ]

    df_tabla = df_tabla[columnas_presentes].rename(
        columns={
            "partido": "Partido",
            "fase": "Fase",
            "llave": "Llave",
            "slot": "Slot",
            "equipo_1": "Equipo 1",
            "r1": "R1",
            "r2": "R2",
            "equipo_2": "Equipo 2",
            "estado_partido": "Estado",
            "live_r1": "Live R1",
            "live_r2": "Live R2",
            "clasificado_lado": "Clasifica",
            "dia": "Dia",
            "hora": "Hora",
        }
    )

    if "Estado" in df_tabla.columns:
        df_tabla["Estado"] = (
            df_tabla["Estado"]
            .fillna("Pendiente")
            .astype(str)
            .str.strip()
            .replace({"": "Pendiente"})
        )

    if "Clasifica" in df_tabla.columns:
        df_tabla["Clasifica"] = (
            df_tabla["Clasifica"]
            .fillna("")
            .astype(str)
            .str.strip()
        )

    def normalizar_numero(value):
        if pd.isna(value) or str(value).strip() == "":
            return None

        try:
            return int(float(value))
        except (TypeError, ValueError):
            return None

    def normalizar_texto(value):
        if pd.isna(value):
            return ""

        return str(value).strip()

    columnas_editables = [
        col
        for col in ["R1", "R2", "Estado", "Live R1", "Live R2", "Clasifica"]
        if col in df_tabla.columns
    ]
    df_original = df_tabla.copy()

    df_editado = st.data_editor(
        df_tabla,
        use_container_width=True,
        hide_index=True,
        height=420,
        key="tabla_resultados_eliminatoria_editable",
        disabled=[
            col
            for col in [
                "Partido",
                "Fase",
                "Llave",
                "Slot",
                "Equipo 1",
                "Equipo 2",
                "Dia",
                "Hora",
            ]
            if col in df_tabla.columns
        ],
        column_config={
            "Partido": st.column_config.NumberColumn("Partido", width="small"),
            "Slot": st.column_config.NumberColumn("Slot", width="small"),
            "R1": st.column_config.NumberColumn(
                "R1",
                min_value=0,
                max_value=20,
                step=1,
                width="small"
            ),
            "R2": st.column_config.NumberColumn(
                "R2",
                min_value=0,
                max_value=20,
                step=1,
                width="small"
            ),
            "Estado": st.column_config.SelectboxColumn(
                "Estado",
                options=["Pendiente", "En Vivo", "Entretiempo", "Finalizado"],
                width="medium"
            ),
            "Live R1": st.column_config.NumberColumn(
                "Live R1",
                min_value=0,
                max_value=20,
                step=1,
                width="small"
            ),
            "Live R2": st.column_config.NumberColumn(
                "Live R2",
                min_value=0,
                max_value=20,
                step=1,
                width="small"
            ),
            "Clasifica": st.column_config.SelectboxColumn(
                "Clasifica",
                options=["", "equipo_1", "equipo_2"],
                help="Dejar vacio si todavia no esta definido.",
                width="small"
            ),
        }
    )

    if st.button(
        "Guardar tabla eliminatoria",
        key="guardar_tabla_resultados_eliminatoria",
        use_container_width=True,
        type="primary"
    ):
        cambios = []

        for idx, fila in df_editado.iterrows():
            original = df_original.loc[idx]

            cambio = False
            for col in columnas_editables:
                if col in ["R1", "R2", "Live R1", "Live R2"]:
                    cambio = (
                        normalizar_numero(fila.get(col))
                        != normalizar_numero(original.get(col))
                    )
                else:
                    cambio = (
                        normalizar_texto(fila.get(col))
                        != normalizar_texto(original.get(col))
                    )

                if cambio:
                    break

            if cambio:
                cambios.append(fila)

        if not cambios:
            st.info("No hay cambios para guardar.")
            return

        errores = []
        guardados = 0

        for fila in cambios:
            partido = normalizar_numero(fila.get("Partido"))
            estado = normalizar_texto(fila.get("Estado")) or "Pendiente"
            clasificado_lado = normalizar_texto(fila.get("Clasifica"))

            if not partido:
                errores.append("Hay una fila sin numero de partido.")
                continue

            if estado in ["En Vivo", "Entretiempo"]:
                r1 = normalizar_numero(fila.get("Live R1"))
                r2 = normalizar_numero(fila.get("Live R2"))
                if r1 is None:
                    r1 = normalizar_numero(fila.get("R1")) or 0
                if r2 is None:
                    r2 = normalizar_numero(fila.get("R2")) or 0
            elif estado == "Finalizado":
                r1 = normalizar_numero(fila.get("R1"))
                r2 = normalizar_numero(fila.get("R2"))
                if r1 is None or r2 is None:
                    errores.append(
                        f"Partido {partido}: para Finalizado completa R1 y R2."
                    )
                    continue
            else:
                r1 = 0
                r2 = 0
                clasificado_lado = ""

            ok, msg = guardar_resultado_eliminatoria_supabase(
                partido,
                r1,
                r2,
                clasificado_lado=clasificado_lado,
                estado_partido=estado
            )

            if ok:
                guardados += 1
            else:
                errores.append(f"Partido {partido}: {msg}")

        if errores:
            st.error("No se pudieron guardar todos los cambios.")
            for error in errores:
                st.caption(error)

        if guardados:
            st.cache_data.clear()
            st.success(f"Partidos actualizados: {guardados}.")
            st.rerun()


def _render_carga_manual_resultado_eliminatoria():
    """Formulario compacto para cargar resultado oficial eliminatorio."""

    st.markdown("### Carga manual de estado y resultado")
    st.caption(
        "En Vivo y Entretiempo guardan marcador live. Finalizado guarda R1/R2 "
        "como resultado oficial y resuelve el clasificado."
    )

    df_eliminatoria = get_eliminatoria_app()

    if df_eliminatoria is None or df_eliminatoria.empty:
        st.warning("No se pudieron cargar los partidos de eliminatoria.")
        return

    df_partidos = df_eliminatoria.copy()
    df_partidos["partido"] = pd.to_numeric(df_partidos["partido"], errors="coerce")
    df_partidos = df_partidos.dropna(subset=["partido"]).copy()
    df_partidos["partido"] = df_partidos["partido"].astype(int)
    fase_orden = {
        "16avos": 1,
        "Octavos": 2,
        "Cuartos": 3,
        "Semifinal": 4,
        "Tercer Puesto": 5,
        "Final": 6,
    }
    df_partidos["_fase_orden_admin"] = (
        df_partidos["fase"].map(fase_orden).fillna(99).astype(int)
    )
    df_partidos = df_partidos.sort_values(
        ["_fase_orden_admin", "llave", "slot", "partido"],
        na_position="last"
    )

    opciones = df_partidos["partido"].tolist()

    if not opciones:
        st.info("No hay partidos disponibles para cargar.")
        return

    def formato_partido(n_partido):
        fila = df_partidos[df_partidos["partido"] == int(n_partido)].iloc[0]
        fase = str(fila.get("fase", "") or "").strip()
        equipo_1 = str(fila.get("equipo_1", "") or "").strip()
        equipo_2 = str(fila.get("equipo_2", "") or "").strip()
        return f"#{int(n_partido)} - {fase} - {equipo_1} vs {equipo_2}"

    partido_sel = st.selectbox(
        "Partido",
        opciones,
        format_func=formato_partido,
        key="admin_eliminatoria_resultado_partido"
    )

    partido_row = df_partidos[
        df_partidos["partido"] == int(partido_sel)
    ].iloc[0]

    equipo_1 = str(partido_row.get("equipo_1", "") or "").strip() or "Equipo 1"
    equipo_2 = str(partido_row.get("equipo_2", "") or "").strip() or "Equipo 2"

    estado_actual = str(partido_row.get("estado_partido", "") or "").strip()
    estados_partido = ["Pendiente", "En Vivo", "Entretiempo", "Finalizado"]

    if estado_actual not in estados_partido:
        estado_actual = "Pendiente"

    r1_base = (
        partido_row.get("live_r1")
        if estado_actual in ["En Vivo", "Entretiempo"]
        else partido_row.get("r1")
    )
    r2_base = (
        partido_row.get("live_r2")
        if estado_actual in ["En Vivo", "Entretiempo"]
        else partido_row.get("r2")
    )

    r1_actual = pd.to_numeric(r1_base, errors="coerce")
    r2_actual = pd.to_numeric(r2_base, errors="coerce")
    lado_actual = str(partido_row.get("clasificado_lado", "") or "").strip()

    with st.form(f"form_resultado_eliminatoria_{partido_sel}"):
        col_info, col_estado, col_r1, col_r2, col_clasifica = st.columns(
            [2.1, 1.2, 0.7, 0.7, 1.4],
            vertical_alignment="bottom"
        )

        with col_info:
            st.write(f"**{equipo_1} vs {equipo_2}**")
            st.caption(
                f"{partido_row.get('fase', '')} · "
                f"{partido_row.get('dia', '')} {partido_row.get('hora', '')}"
            )

        with col_estado:
            estado_partido = st.selectbox(
                "Estado",
                estados_partido,
                index=estados_partido.index(estado_actual),
                key=f"admin_eliminatoria_estado_{partido_sel}"
            )

        with col_r1:
            r1 = st.number_input(
                "R1",
                min_value=0,
                max_value=20,
                step=1,
                value=int(r1_actual) if pd.notna(r1_actual) else 0,
                key=f"admin_eliminatoria_r1_{partido_sel}"
            )

        with col_r2:
            r2 = st.number_input(
                "R2",
                min_value=0,
                max_value=20,
                step=1,
                value=int(r2_actual) if pd.notna(r2_actual) else 0,
                key=f"admin_eliminatoria_r2_{partido_sel}"
            )

        with col_clasifica:
            opciones_clasifica = [
                ("", "Sin definir"),
                ("equipo_1", equipo_1),
                ("equipo_2", equipo_2),
            ]
            valores_clasifica = [item[0] for item in opciones_clasifica]
            index_default = (
                valores_clasifica.index(lado_actual)
                if lado_actual in valores_clasifica
                else 0
            )
            clasificado_lado = st.selectbox(
                "Clasifica",
                options=valores_clasifica,
                index=index_default,
                format_func=lambda lado: (
                    equipo_1
                    if lado == "equipo_1"
                    else equipo_2
                    if lado == "equipo_2"
                    else "Sin definir"
                ),
                key=f"admin_eliminatoria_clasifica_{partido_sel}"
            )

        guardar = st.form_submit_button(
            "Guardar estado / resultado",
            use_container_width=True,
            type="primary"
        )

    if guardar:
        ok, msg = guardar_resultado_eliminatoria_supabase(
            n_partido=partido_sel,
            r1=r1,
            r2=r2,
            clasificado_lado=clasificado_lado,
            estado_partido=estado_partido
        )

        if ok:
            st.cache_data.clear()
            st.success(msg)
            st.rerun()

        st.error(msg)


def _render_ranking_eliminatoria_preview(df_usuarios):
    """Ranking tecnico de eliminatoria para validar puntajes antes de Inicio V2."""

    st.markdown("### Ranking eliminatoria preview")
    st.caption(
        "Vista tecnica para validar la nueva regla. Incluye partidos En Vivo y "
        "Entretiempo como puntaje virtual."
    )

    df_eliminatoria = get_eliminatoria_app()
    df_pronosticos_eliminatoria = get_pronosticos_eliminatoria_app()

    if df_eliminatoria is None or df_eliminatoria.empty:
        st.info("No hay partidos de eliminatoria cargados.")
        return

    if df_pronosticos_eliminatoria is None or df_pronosticos_eliminatoria.empty:
        st.info("Todavia no hay pronosticos de eliminatoria cargados.")
        return

    incluir_live = st.toggle(
        "Incluir resultados live como preview",
        value=True,
        key="admin_ranking_eliminatoria_incluir_live"
    )

    df_rank_eliminatoria = obtener_ranking_eliminatoria(
        df_usuarios,
        df_pronosticos_eliminatoria,
        df_eliminatoria,
        incluir_live=incluir_live
    )

    if df_rank_eliminatoria.empty:
        st.info("No hay puntos calculables todavia.")
        return

    partidos_computables = 0
    df_partidos = df_eliminatoria.copy()

    if "estado_partido" in df_partidos.columns:
        estados_validos = ["Finalizado"]

        if incluir_live:
            estados_validos.extend(["En Vivo", "Entretiempo"])

        partidos_computables = (
            df_partidos["estado_partido"]
            .fillna("")
            .astype(str)
            .str.strip()
            .isin(estados_validos)
            .sum()
        )

    col_rank_1, col_rank_2, col_rank_3 = st.columns(3)

    with col_rank_1:
        st.metric("Partidos computables", int(partidos_computables))

    with col_rank_2:
        st.metric("Jugadores", len(df_rank_eliminatoria))

    with col_rank_3:
        st.metric("Puntaje lider", int(df_rank_eliminatoria["PUNTOS"].max()))

    columnas_preview = [
        "Nº",
        "JUGADOR",
        "USUARIO",
        "PUNTOS",
        "EXACTOS",
        "GENERALES",
        "CLASIFICADOS",
    ]

    columnas_preview = [
        col
        for col in columnas_preview
        if col in df_rank_eliminatoria.columns
    ]

    st.dataframe(
        df_rank_eliminatoria[columnas_preview],
        use_container_width=True,
        hide_index=True,
        height=360
    )


def render_panel_control(
    df_res,
    df_usuarios,
    df_pro,
    df_foro,
    df_noticias,
    df_ranking,
    registro_permitido_fecha,
    estado_mantenimiento
):
    
    # ============================================================
    # VALIDACIÓN DE SEGURIDAD
    # ============================================================

    if st.session_state["user_data"]["ROL"] != "admin":
        st.error("⛔ No tienes permisos para acceder a esta sección.")
        return

    # ============================================================
    # HEADER
    # ============================================================

    st.markdown("## ⚙️ Centro de Administración")
    st.caption("Gestión general del Prode Mundial 2026")

    if st.button(
        "Actualizar datos desde Supabase",
        use_container_width=True,
        key="admin_refrescar_datos_supabase"
    ):
        st.cache_data.clear()
        st.rerun()

    usuarios_count = len(df_usuarios) if df_usuarios is not None else 0
    pronosticos_count = len(df_pro) if df_pro is not None else 0
    foro_count = len(df_foro) if df_foro is not None else 0

    resultados_visibles = 0

    if df_res is not None and not df_res.empty and "VIZ" in df_res.columns:
        resultados_visibles = (
            df_res["VIZ"]
            .astype(str)
            .str.strip()
            .str.upper()
            .isin(["TRUE", "1", "1.0", "VERDADERO", "T"])
            .sum()
        )

    c1, c2, c3, c4 = st.columns(4)

    with c1:
        st.metric("👥 Usuarios", usuarios_count)

    with c2:
        st.metric("📝 Pronósticos", pronosticos_count)

    with c3:
        st.metric("💬 Mensajes", foro_count)

    with c4:
        st.metric("⚽ Resultados visibles", resultados_visibles)

    st.markdown("---")

    tab_eliminatoria, tab_estado, tab_resultados, tab_usuarios, tab_config, tab_tecnico = st.tabs(
        [
            "Eliminatoria",
            "📊 Estado",
            "⚽ Resultados",
            "👥 Usuarios",
            "🚦 Configuración",
            "🧪 Técnico"
        ]
    )

    # ============================================================
    # TAB 1 — ESTADO / AUDITORÍA
    # ============================================================

    with tab_estado:
        st.subheader("📊 Estado general")

        st.markdown("### 🕵️ Auditoría de Cargas")

        if df_pro is None or df_pro.empty:
            st.info("Todavía no hay pronósticos cargados.")
        else:
            conteo_pro = (
                df_pro["USUARIO"]
                .value_counts()
                .reset_index()
            )

            conteo_pro.columns = [
                "USUARIO",
                "COMPLETADOS"
            ]

            df_auditoria = pd.merge(
                df_usuarios[["USUARIO", "NOMBRE"]],
                conteo_pro,
                on="USUARIO",
                how="left"
            ).fillna(0)

            def estado_carga(cant):
                if cant >= 72:
                    return "✅ Completo"

                if cant >= 24:
                    return f"🟡 Parcial ({int(cant)})"

                if cant > 0:
                    return f"⚠️ Incompleto ({int(cant)})"

                return "❌ No empezó"

            df_auditoria["ESTADO"] = (
                df_auditoria["COMPLETADOS"]
                .apply(estado_carga)
            )

            st.dataframe(
                df_auditoria[["NOMBRE", "USUARIO", "COMPLETADOS", "ESTADO"]],
                use_container_width=True,
                hide_index=True
            )

            if st.button("📢 Generar mensaje para colgados"):
                faltantes = (
                    df_auditoria[
                        df_auditoria["COMPLETADOS"] < 72
                    ]["NOMBRE"]
                    .tolist()
                )

                if faltantes:
                    msg_escrache = (
                        "🚨 ATENCIÓN: Faltan completar pronósticos: "
                        f"{', '.join(faltantes)}. ¡No se duerman!"
                    )

                    st.warning("Copia esto al foro:")
                    st.code(msg_escrache)

                else:
                    st.success("¡Todos los jugadores completaron sus pronósticos! 👏")

    # ============================================================
    # TAB 2 — RESULTADOS
    # ============================================================

    with tab_eliminatoria:
        st.subheader("Fase Eliminatoria")
        st.caption(
            "Herramientas separadas para preparar y administrar la etapa eliminatoria."
        )

        _render_editor_equipos_eliminatoria_16avos(df_res=df_res)

        st.markdown("---")
        _render_carga_manual_resultado_eliminatoria()

        st.markdown("---")
        _render_ranking_eliminatoria_preview(df_usuarios)

        st.markdown("---")
        _render_tabla_partidos_eliminatoria()

    with tab_resultados:
        st.subheader("⚽ Gestión de Resultados Oficiales")

        df_res_admin = df_res.copy()

        if df_res_admin is None or df_res_admin.empty:
            st.error("No se pudieron cargar los resultados desde Supabase.")
        else:
            df_res_admin["N_PARTIDO"] = pd.to_numeric(
                df_res_admin["N_PARTIDO"],
                errors="coerce"
            )

            df_res_admin = df_res_admin.dropna(
                subset=["N_PARTIDO"]
            ).copy()

            df_res_admin["N_PARTIDO"] = df_res_admin["N_PARTIDO"].astype(int)

            if "FECHA" not in df_res_admin.columns:
                df_res_admin["FECHA"] = 1

            df_res_admin["FECHA_NUM"] = pd.to_numeric(
                df_res_admin["FECHA"],
                errors="coerce"
            ).fillna(1).astype(int)

            tabs_fechas = st.tabs(
                [
                    "Fecha 1",
                    "Fecha 2",
                    "Fecha 3"
                ]
            )

            df_editado_total = []

            for fecha_num, tab in zip([1, 2, 3], tabs_fechas):
                with tab:
                    df_fecha = (
                        df_res_admin[
                            df_res_admin["FECHA_NUM"] == fecha_num
                        ]
                        .sort_values("N_PARTIDO")
                        .copy()
                    )

                    if df_fecha.empty:
                        st.info(f"No hay partidos cargados para Fecha {fecha_num}.")
                        continue

                    columnas_editor = [
                        "N_PARTIDO",
                        "Equipo_1",
                        "R1",
                        "R2",
                        "Equipo_2",
                        "DIA",
                        "HORA",
                        "VIZ"
                    ]

                    for col in columnas_editor:
                        if col not in df_fecha.columns:
                            if col in ["R1", "R2"]:
                                df_fecha[col] = None
                            elif col == "VIZ":
                                df_fecha[col] = False
                            else:
                                df_fecha[col] = ""

                    for col in ["LIVE", "LIVE_R1", "LIVE_R2", "ESTADO_PARTIDO"]:
                        if col not in df_fecha.columns:
                            if col == "LIVE":
                                df_fecha[col] = False
                            else:
                                df_fecha[col] = None

                    df_fecha_editor = df_fecha[columnas_editor].copy()
                    df_fecha_editor["LIVE"] = df_fecha["LIVE"].values

                    df_fecha_editor["R1"] = pd.to_numeric(
                        df_fecha_editor["R1"],
                        errors="coerce"
                    )

                    df_fecha_editor["R2"] = pd.to_numeric(
                        df_fecha_editor["R2"],
                        errors="coerce"
                    )

                    df_fecha_editor["VIZ"] = (
                        df_fecha_editor["VIZ"]
                        .astype(str)
                        .str.strip()
                        .str.upper()
                        .isin(["TRUE", "1", "1.0", "VERDADERO", "T", "SI", "SÍ"])
                    )

                    df_fecha_editor["LIVE"] = (
                        df_fecha_editor["LIVE"]
                        .astype(str)
                        .str.strip()
                        .str.upper()
                        .isin(["TRUE", "1", "1.0", "VERDADERO", "T", "SI", "SÍ"])
                    )

                    edited_fecha = st.data_editor(
                        df_fecha_editor,
                        use_container_width=True,
                        hide_index=True,
                        key=f"editor_resultados_fecha_{fecha_num}",
                        disabled=[
                            "N_PARTIDO",
                            "Equipo_1",
                            "Equipo_2",
                            "DIA",
                            "HORA"
                        ],
                        column_config={
                            "N_PARTIDO": st.column_config.NumberColumn(
                                "N°",
                                width="small"
                            ),
                            "Equipo_1": st.column_config.TextColumn(
                                "Equipo 1",
                                width="medium"
                            ),
                            "R1": st.column_config.NumberColumn(
                                "R1",
                                min_value=0,
                                max_value=20,
                                step=1,
                                width="small"
                            ),
                            "R2": st.column_config.NumberColumn(
                                "R2",
                                min_value=0,
                                max_value=20,
                                step=1,
                                width="small"
                            ),
                            "Equipo_2": st.column_config.TextColumn(
                                "Equipo 2",
                                width="medium"
                            ),
                            "DIA": st.column_config.TextColumn(
                                "Día",
                                width="small"
                            ),
                            "HORA": st.column_config.TextColumn(
                                "Hora",
                                width="small"
                            ),
                            "VIZ": st.column_config.CheckboxColumn(
                                "Visible",
                                width="small"
                            ),
                            "LIVE": None,
                        }
                    )

                    edited_fecha["FECHA"] = fecha_num
                    live_scores_base = (
                        df_fecha[["N_PARTIDO", "LIVE_R1", "LIVE_R2", "ESTADO_PARTIDO"]]
                        .drop_duplicates("N_PARTIDO")
                        .set_index("N_PARTIDO")
                    )
                    edited_fecha["LIVE_R1"] = (
                        edited_fecha["N_PARTIDO"]
                        .map(live_scores_base["LIVE_R1"])
                    )
                    edited_fecha["LIVE_R2"] = (
                        edited_fecha["N_PARTIDO"]
                        .map(live_scores_base["LIVE_R2"])
                    )
                    edited_fecha["ESTADO_PARTIDO"] = (
                        edited_fecha["N_PARTIDO"]
                        .map(live_scores_base["ESTADO_PARTIDO"])
                    )
                    df_editado_total.append(edited_fecha)

            st.markdown("---")

            if st.button(
                "Guardar tabla oficial",
                help="Guarda R1, R2 y Visible de la tabla superior.",
                use_container_width=True,
                type="primary"
            ):
                try:
                    if not df_editado_total:
                        st.warning("No hay resultados para guardar.")
                        st.stop()

                    df_final_resultados = pd.concat(
                        df_editado_total,
                        ignore_index=True
                    )

                    ok, msg = guardar_resultados_supabase(df_final_resultados)

                    if ok:
                        st.cache_data.clear()
                        st.success("Tabla oficial actualizada.")
                        st.balloons()
                        st.rerun()
                    else:
                        st.error(msg)

                except Exception as e:
                    st.error(f"Error al guardar resultados: {e}")

            st.markdown("---")

            st.markdown("### Estado en vivo del partido")
            st.caption(
                "Pendiente no afecta el resultado. En Vivo y Entretiempo son visuales para Inicio. Finalizado copia el resultado "
                "a R1/R2 y entonces aplica al ranking."
            )

            df_estado_partidos = df_res_admin.sort_values("N_PARTIDO").copy()

            for col in ["LIVE", "LIVE_R1", "LIVE_R2", "ESTADO_PARTIDO"]:
                if col not in df_estado_partidos.columns:
                    if col == "LIVE":
                        df_estado_partidos[col] = False
                    else:
                        df_estado_partidos[col] = None

            estado_no_finalizado_api = (
                df_estado_partidos["ESTADO_PARTIDO"]
                .fillna("Pendiente")
                .astype(str)
                .str.strip()
                .ne("Finalizado")
            )

            def _es_visible_api(value):
                return (
                    str(value)
                    .strip()
                    .upper()
                    in ["TRUE", "1", "1.0", "VERDADERO", "T", "SI", "SÍ"]
                )

            if "VIZ" in df_estado_partidos.columns:
                viz_mask_api = df_estado_partidos["VIZ"].apply(_es_visible_api)
            else:
                viz_mask_api = pd.Series(False, index=df_estado_partidos.index)

            df_partidos_visibles_api = df_estado_partidos[
                viz_mask_api & estado_no_finalizado_api
            ].copy()

            with st.expander("Prototipo API externa", expanded=False):
                st.caption(
                    "Consulta football-data.org para partidos visibles. "
                    "Muestra sugerencias de estado y resultado para validar manualmente. "
                    "No aplica cambios automaticamente."
                )

                if df_partidos_visibles_api.empty:
                    st.info("No hay partidos visibles no finalizados para consultar.")
                else:
                    st.write(
                        f"Partidos visibles no finalizados a consultar: {len(df_partidos_visibles_api)}"
                    )

                    if st.button(
                        "Consultar API partidos visibles",
                        key="admin_api_live_consultar_visibles",
                        use_container_width=True
                    ):
                        st.session_state["admin_api_live_resultado"] = (
                            sugerir_estados_partidos_api(df_partidos_visibles_api)
                        )
                        st.rerun()

                    resultado_api_live = st.session_state.get(
                        "admin_api_live_resultado"
                    )

                    if resultado_api_live:
                        if not resultado_api_live.get("ok"):
                            st.warning(resultado_api_live.get("mensaje"))
                        else:
                            sugerencias = resultado_api_live.get("sugerencias", [])
                            st.success(resultado_api_live.get("mensaje"))

                            resumen_rows = []
                            for sugerencia in sugerencias:
                                resumen_rows.append(
                                    {
                                        "Partido": sugerencia.get("n_partido"),
                                        "Prode": (
                                            f"{sugerencia.get('equipo_1')} vs "
                                            f"{sugerencia.get('equipo_2')}"
                                        ),
                                        "Encontrado": "Si" if sugerencia.get("ok") else "No",
                                        "Estado API": sugerencia.get("status_api", ""),
                                        "Estado visual API": sugerencia.get(
                                            "estado_visual",
                                            sugerencia.get("estado", "")
                                        ),
                                        "Resultado": (
                                            f"{sugerencia.get('r1')} - {sugerencia.get('r2')}"
                                            if sugerencia.get("r1") is not None
                                            and sugerencia.get("r2") is not None
                                            else ""
                                        ),
                                        "Partido API": (
                                            f"{sugerencia.get('home', '')} vs "
                                            f"{sugerencia.get('away', '')}"
                                        ),
                                    }
                                )

                            st.dataframe(
                                pd.DataFrame(resumen_rows),
                                hide_index=True,
                                use_container_width=True
                            )

                            st.info(
                                "La API solo informa sugerencias. Revisalas y, si corresponde, "
                                "cargalas manualmente en el formulario de estado en vivo."
                            )

                            finalizados_detectados = [
                                s for s in sugerencias
                                if s.get("ok") and s.get("estado") == "Finalizado"
                            ]

                            if finalizados_detectados:
                                st.warning(
                                    "Hay partidos finalizados detectados. No se aplican desde la API: "
                                    "validalos manualmente antes de guardar."
                                )

            opciones_partidos = df_estado_partidos["N_PARTIDO"].astype(int).tolist()

            if opciones_partidos:
                partidos_live_actuales = df_estado_partidos[
                    df_estado_partidos["ESTADO_PARTIDO"]
                    .fillna("")
                    .astype(str)
                    .str.strip()
                    .isin(["En Vivo", "Entretiempo"])
                ]

                partido_default = opciones_partidos[0]

                if not partidos_live_actuales.empty:
                    partido_default = int(
                        partidos_live_actuales
                        .sort_values("N_PARTIDO")
                        .iloc[0]["N_PARTIDO"]
                    )

                partido_sel = st.selectbox(
                    "Numero de partido",
                    options=opciones_partidos,
                    index=opciones_partidos.index(partido_default),
                    format_func=lambda n: f"Partido #{n}",
                    key="admin_estado_partido_select"
                )

                partido_row = df_estado_partidos[
                    df_estado_partidos["N_PARTIDO"] == partido_sel
                ].iloc[0]

                st.info(
                    f"{partido_row.get('Equipo_1', '')} vs {partido_row.get('Equipo_2', '')} "
                    f"- {partido_row.get('DIA', '')} {partido_row.get('HORA', '')}"
                )

                estado_actual = str(partido_row.get("ESTADO_PARTIDO") or "").strip()

                if estado_actual == "Sin live":
                    estado_actual = "Pendiente"

                if not estado_actual:
                    live_actual = (
                        str(partido_row.get("LIVE", ""))
                        .strip()
                        .upper()
                        in ["TRUE", "1", "1.0", "VERDADERO", "T", "SI", "SÃƒÂ"]
                    )
                    estado_actual = "En Vivo" if live_actual else "Pendiente"

                estados_partido = ["Pendiente", "En Vivo", "Entretiempo", "Finalizado"]

                if estado_actual not in estados_partido:
                    estado_actual = "Pendiente"

                valor_r1_actual = (
                    partido_row["LIVE_R1"]
                    if pd.notna(partido_row.get("LIVE_R1"))
                    else partido_row.get("R1")
                )
                valor_r2_actual = (
                    partido_row["LIVE_R2"]
                    if pd.notna(partido_row.get("LIVE_R2"))
                    else partido_row.get("R2")
                )

                r1_key = f"admin_live_r1_input_{partido_sel}"
                r2_key = f"admin_live_r2_input_{partido_sel}"
                estado_key = f"admin_estado_partido_input_{partido_sel}"

                if r1_key not in st.session_state:
                    st.session_state[r1_key] = (
                        int(valor_r1_actual)
                        if pd.notna(valor_r1_actual)
                        else 0
                    )

                if r2_key not in st.session_state:
                    st.session_state[r2_key] = (
                        int(valor_r2_actual)
                        if pd.notna(valor_r2_actual)
                        else 0
                    )

                if estado_key not in st.session_state:
                    st.session_state[estado_key] = estado_actual

                with st.form(f"form_estado_partido_live_{partido_sel}"):
                    col_r1_live, col_estado_live, col_r2_live = st.columns([1, 1.4, 1])

                    with col_r1_live:
                        live_r1 = st.number_input(
                            "Resultado equipo 1",
                            min_value=0,
                            max_value=20,
                            step=1,
                            key=r1_key
                        )

                    with col_estado_live:
                        estado_partido = st.selectbox(
                            "Estado",
                            options=estados_partido,
                            key=estado_key
                        )

                    with col_r2_live:
                        live_r2 = st.number_input(
                            "Resultado equipo 2",
                            min_value=0,
                            max_value=20,
                            step=1,
                            key=r2_key
                        )

                    guardar_estado = st.form_submit_button(
                        "Guardar estado en vivo",
                        use_container_width=True
                    )
                if guardar_estado:
                    if estado_partido in ["En Vivo", "Entretiempo"]:
                        otros_live = df_estado_partidos[
                            (
                                df_estado_partidos["N_PARTIDO"] != partido_sel
                            )
                            & (
                                df_estado_partidos["ESTADO_PARTIDO"]
                                .fillna("")
                                .astype(str)
                                .str.strip()
                                .isin(["En Vivo", "Entretiempo"])
                            )
                        ]

                        if not otros_live.empty:
                            st.error(
                                "Ya hay otro partido en vivo. "
                                "Primero pasalo a 'Pendiente' o 'Finalizado'."
                            )
                            st.stop()

                    ok_estado, msg_estado = guardar_estado_partido_supabase(
                        n_partido=partido_sel,
                        estado_partido=estado_partido,
                        live_r1=live_r1,
                        live_r2=live_r2
                    )

                    if ok_estado:
                        st.cache_data.clear()
                        st.success(msg_estado)
                        st.rerun()

                    st.error(msg_estado)
            else:
                st.info("No hay partidos disponibles para cargar estado live.")
    # ============================================================
    # TAB 3 — USUARIOS
    # ============================================================

    with tab_usuarios:
        st.subheader("👥 Gestión de Usuarios")

        if df_usuarios is None or df_usuarios.empty:
            st.info("No hay usuarios registrados.")
        else:
            df_users_panel = df_usuarios.copy()

            if "ROL" not in df_users_panel.columns:
                df_users_panel["ROL"] = "jugador"

            conteo_pro = (
                df_pro["USUARIO"]
                .value_counts()
                .reset_index()
                if df_pro is not None and not df_pro.empty
                else pd.DataFrame(columns=["USUARIO", "COMPLETADOS"])
            )

            if not conteo_pro.empty:
                conteo_pro.columns = ["USUARIO", "COMPLETADOS"]

            df_users_panel = pd.merge(
                df_users_panel,
                conteo_pro,
                on="USUARIO",
                how="left"
            )

            df_users_panel["COMPLETADOS"] = (
                df_users_panel["COMPLETADOS"]
                .fillna(0)
                .astype(int)
            )

            if "APORTE_REALIZADO" not in df_users_panel.columns:
                df_users_panel["APORTE_REALIZADO"] = False

            if "ELIMINATORIA" not in df_users_panel.columns:
                df_users_panel["ELIMINATORIA"] = True

            df_users_panel["APORTE_REALIZADO"] = (
                df_users_panel["APORTE_REALIZADO"]
                .fillna(False)
                .astype(str)
                .str.strip()
                .str.upper()
                .isin(["TRUE", "1", "1.0", "VERDADERO", "T", "SI", "SÍ"])
            )

            df_users_panel["ELIMINATORIA"] = (
                df_users_panel["ELIMINATORIA"]
                .fillna(True)
                .astype(str)
                .str.strip()
                .str.upper()
                .isin(["TRUE", "1", "1.0", "VERDADERO", "T", "SI", "SÃ"])
            )

            columnas_vista = [
                "APORTE_REALIZADO",
                "ELIMINATORIA",
                "USUARIO",
                "NOMBRE",
                "ROL",
                "EQUIPO FAVORITO",
                "COMPLETADOS"
            ]

            for col in columnas_vista:
                if col not in df_users_panel.columns:
                    df_users_panel[col] = ""

            df_aportes_original = (
                df_users_panel[["USUARIO", "APORTE_REALIZADO", "ELIMINATORIA"]]
                .copy()
                .set_index("USUARIO")
            )

            df_aportes_editado = st.data_editor(
                df_users_panel[columnas_vista],
                use_container_width=True,
                hide_index=True,
                disabled=[
                    "USUARIO",
                    "NOMBRE",
                    "ROL",
                    "EQUIPO FAVORITO",
                    "COMPLETADOS"
                ],
                column_config={
                    "APORTE_REALIZADO": st.column_config.CheckboxColumn(
                        "Aporte realizado",
                        help="Marcá los usuarios que ya realizaron el aporte."
                    ),
                    "ELIMINATORIA": st.column_config.CheckboxColumn(
                        "Eliminatoria",
                        help="Marca los usuarios que participan en eliminatoria."
                    ),
                    "COMPLETADOS": st.column_config.NumberColumn(
                        "Pronósticos cargados"
                    )
                },
                key="admin_aportes_editor"
            )

            if st.button(
                "💾 Guardar usuarios",
                use_container_width=True,
                key="admin_guardar_aportes"
            ):
                cambios_aporte = []
                cambios_eliminatoria = []

                for _, row in df_aportes_editado.iterrows():
                    usuario_aporte = str(row.get("USUARIO", "")).strip()

                    if not usuario_aporte:
                        continue

                    aporte_nuevo = bool(row.get("APORTE_REALIZADO", False))

                    if usuario_aporte not in df_aportes_original.index:
                        continue

                    aporte_original = bool(
                        df_aportes_original.loc[
                            usuario_aporte,
                            "APORTE_REALIZADO"
                        ]
                    )

                    if aporte_nuevo != aporte_original:
                        cambios_aporte.append(
                            (usuario_aporte, aporte_nuevo)
                        )

                    eliminatoria_nuevo = bool(row.get("ELIMINATORIA", True))
                    eliminatoria_original = bool(
                        df_aportes_original.loc[
                            usuario_aporte,
                            "ELIMINATORIA"
                        ]
                    )

                    if eliminatoria_nuevo != eliminatoria_original:
                        cambios_eliminatoria.append(
                            (usuario_aporte, eliminatoria_nuevo)
                        )

                if not cambios_aporte and not cambios_eliminatoria:
                    st.info("No hay cambios de usuarios para guardar.")
                else:
                    errores = []

                    for usuario_aporte, aporte_nuevo in cambios_aporte:
                        ok, msg = actualizar_aporte_usuario_supabase(
                            usuario=usuario_aporte,
                            aporte_realizado=aporte_nuevo
                        )

                        if not ok:
                            errores.append(
                                f"{usuario_aporte}: {msg}"
                            )

                    for usuario_elim, eliminatoria_nuevo in cambios_eliminatoria:
                        ok, msg = actualizar_eliminatoria_usuario_supabase(
                            usuario=usuario_elim,
                            eliminatoria=eliminatoria_nuevo
                        )

                        if not ok:
                            errores.append(
                                f"{usuario_elim}: {msg}"
                            )

                    if errores:
                        st.error("No se pudieron guardar algunos usuarios.")
                        for error in errores:
                            st.caption(error)
                    else:
                        st.cache_data.clear()
                        st.success(
                            "Usuarios actualizados: "
                            f"{len(cambios_aporte) + len(cambios_eliminatoria)}."
                        )
                        st.rerun()

            st.markdown("---")
            st.markdown("### 🛡️ Cambiar rol")

            usuarios_roles = df_users_panel["USUARIO"].astype(str).tolist()

            usuario_rol = st.selectbox(
                "Usuario",
                usuarios_roles,
                index=None,
                placeholder="Elegir usuario...",
                key="admin_usuario_rol"
            )

            nuevo_rol = st.selectbox(
                "Nuevo rol",
                ["jugador", "colaborador", "admin"],
                key="admin_nuevo_rol"
            )

            if st.button(
                "💾 Actualizar rol",
                use_container_width=True,
                disabled=not usuario_rol
            ):
                ok, msg = actualizar_rol_usuario_supabase(
                    usuario=usuario_rol,
                    nuevo_rol=nuevo_rol
                )

                if ok:
                    st.cache_data.clear()

                    if (
                        usuario_rol
                        == st.session_state["user_data"]["USUARIO"]
                    ):
                        st.session_state["user_data"]["ROL"] = nuevo_rol

                    st.success(msg)
                    st.rerun()
                else:
                    st.error(msg)

            st.markdown("---")
            st.markdown("### 🗑️ Eliminar usuario")

            usuarios_borrables = df_users_panel[
                df_users_panel["USUARIO"]
                != st.session_state["user_data"]["USUARIO"]
            ]

            if usuarios_borrables.empty:
                st.info("No hay otros usuarios para eliminar.")
            else:
                user_a_eliminar = st.selectbox(
                    "Selecciona un jugador para eliminar:",
                    usuarios_borrables["USUARIO"].astype(str).tolist(),
                    index=None,
                    placeholder="Elegir usuario...",
                    key="admin_user_eliminar"
                )

                if user_a_eliminar:
                    nombre_eliminar = usuarios_borrables[
                        usuarios_borrables["USUARIO"] == user_a_eliminar
                    ]["NOMBRE"].iloc[0]

                    st.warning(
                        f"⚠️ Estás por borrar a **{nombre_eliminar}** "
                        f"(@{user_a_eliminar}) y todos sus pronósticos."
                    )

                    confirmado = st.checkbox(
                        "Confirmo borrar usuario y sus pronósticos",
                        key="conf_borrar_supabase"
                    )

                    if st.button(
                        "❌ BORRAR PERMANENTEMENTE",
                        type="primary",
                        use_container_width=True,
                        disabled=not confirmado
                    ):
                        ok, msg = eliminar_usuario_supabase(user_a_eliminar)

                        if ok:
                            st.cache_data.clear()
                            st.success(msg)
                            st.rerun()
                        else:
                            st.error(msg)

    # ============================================================
    # TAB 4 — CONFIGURACIÓN
    # ============================================================

    with tab_config:
        st.subheader("🚦 Configuración del Prode")

        try:
            df_config = get_config_app()
            estado_manual = (
                str(df_config.iloc[0]["REGISTRO"])
                .strip()
                .upper()
            )
            estado_mant = (
                str(df_config.iloc[0]["MANTENIMIENTO"])
                .strip()
                .upper()
            )

        except Exception as e:
            st.error(f"No se pudo cargar CONFIG desde Supabase: {e}")
            estado_manual = "OFF"
            estado_mant = "OFF"

        st.markdown("### 🚫 Control de Inscripciones")
        
        if estado_manual == "ON":
            st.success("✅ Inscripciones ABIERTAS")
        
            if st.button(
                "🔴 CERRAR REGISTRO MANUALMENTE",
                use_container_width=True
            ):
                ok, msg = actualizar_config_supabase(
                    campo="registro",
                    valor="OFF"
                )
        
                if ok:
                    st.cache_data.clear()
                    st.success("Registro cerrado con éxito")
                    st.rerun()
                else:
                    st.error(msg)
        
        else:
            st.error("⛔ Inscripciones CERRADAS")
        
            if st.button(
                "🟢 ABRIR REGISTRO MANUALMENTE",
                use_container_width=True
            ):
                ok, msg = actualizar_config_supabase(
                    campo="registro",
                    valor="ON"
                )
        
                if ok:
                    st.cache_data.clear()
                    st.success("Registro abierto con éxito")
                    st.rerun()
                else:
                    st.error(msg)


        st.markdown("---")
        st.markdown("### 📝 Control de Pronósticos")
        
        try:
            estado_pronosticos = (
                str(df_config.iloc[0].get("PRONOSTICOS_ESTADO", "ON"))
                .strip()
                .upper()
            )
        
            cierre_pronosticos_actual = (
                str(df_config.iloc[0].get("CIERRE_PRONOSTICOS", "2026-06-11 15:00"))
                .strip()
            )
        
        except Exception:
            estado_pronosticos = "ON"
            cierre_pronosticos_actual = "2026-06-11 15:00"
        
        if estado_pronosticos == "ON":
            st.success("✅ Carga de pronósticos ABIERTA")
        else:
            st.error("⛔ Carga de pronósticos CERRADA")
        
        nueva_fecha_cierre = st.text_input(
            "Fecha y hora de cierre de pronósticos",
            value=cierre_pronosticos_actual,
            help="Formato recomendado: 2026-06-11 15:00",
            key="admin_cierre_pronosticos"
        )
        
        col_prono_1, col_prono_2 = st.columns(2)
        
        with col_prono_1:
            if st.button(
                "💾 Guardar fecha de cierre",
                use_container_width=True
            ):
                ok, msg = actualizar_config_supabase(
                    campo="cierre_pronosticos",
                    valor=nueva_fecha_cierre
                )
        
                if ok:
                    st.cache_data.clear()
                    st.success("Fecha de cierre de pronósticos actualizada.")
                    st.rerun()
                else:
                    st.error(msg)
        
        with col_prono_2:
            nuevo_estado_pronosticos = (
                "OFF"
                if estado_pronosticos == "ON"
                else "ON"
            )
        
            texto_boton_pronosticos = (
                "🔴 CERRAR PRONÓSTICOS"
                if estado_pronosticos == "ON"
                else "🟢 ABRIR PRONÓSTICOS"
            )
        
            if st.button(
                texto_boton_pronosticos,
                use_container_width=True
            ):
                ok, msg = actualizar_config_supabase(
                    campo="pronosticos_estado",
                    valor=nuevo_estado_pronosticos
                )
        
                if ok:
                    st.cache_data.clear()
                    st.success("Estado de pronósticos actualizado.")
                    st.rerun()
                else:
                    st.error(msg)
                    
        st.markdown("---")
        st.markdown("### Fase Eliminatoria")
        st.caption(
            "Estos valores se guardan en la tabla config como filas clave/valor. "
            "Si una clave no existe, el boton Guardar cierres eliminatoria la crea."
        )

        try:
            estado_eliminatoria = (
                str(df_config.iloc[0].get("PRONOSTICOS_ELIMINATORIA_ESTADO", "ON"))
                .strip()
                .upper()
            )

            cierres_eliminatoria = {
                "16avos": str(df_config.iloc[0].get("CIERRE_ELIMINATORIA_16AVOS", "2026-06-28 15:00")).strip(),
                "Octavos": str(df_config.iloc[0].get("CIERRE_ELIMINATORIA_OCTAVOS", "2026-07-03 23:59")).strip(),
                "Cuartos": str(df_config.iloc[0].get("CIERRE_ELIMINATORIA_CUARTOS", "2026-07-08 23:59")).strip(),
                "Semifinal": str(df_config.iloc[0].get("CIERRE_ELIMINATORIA_SEMIFINAL", "2026-07-13 23:59")).strip(),
                "Final": str(df_config.iloc[0].get("CIERRE_ELIMINATORIA_FINAL", "2026-07-17 23:59")).strip(),
            }
        except Exception:
            estado_eliminatoria = "ON"
            cierres_eliminatoria = {
                "16avos": "2026-06-28 15:00",
                "Octavos": "2026-07-03 23:59",
                "Cuartos": "2026-07-08 23:59",
                "Semifinal": "2026-07-13 23:59",
                "Final": "2026-07-17 23:59",
            }

        if estado_eliminatoria == "ON":
            st.success("Carga de eliminatoria ABIERTA")
        else:
            st.error("Carga de eliminatoria CERRADA")

        campos_cierre_eliminatoria = {
            "16avos": "cierre_eliminatoria_16avos",
            "Octavos": "cierre_eliminatoria_octavos",
            "Cuartos": "cierre_eliminatoria_cuartos",
            "Semifinal": "cierre_eliminatoria_semifinal",
            "Final": "cierre_eliminatoria_final",
        }

        valores_cierre_eliminatoria = {}

        for fase, campo_config in campos_cierre_eliminatoria.items():
            valores_cierre_eliminatoria[fase] = st.text_input(
                f"Cierre {fase}",
                value=cierres_eliminatoria[fase],
                help="Formato recomendado: YYYY-MM-DD HH:MM",
                key=f"admin_{campo_config}"
            )

        col_elim_1, col_elim_2 = st.columns(2)

        with col_elim_1:
            if st.button(
                "Guardar / crear cierres eliminatoria",
                use_container_width=True
            ):
                errores = []

                for fase, campo_config in campos_cierre_eliminatoria.items():
                    ok, msg = actualizar_config_supabase(
                        campo=campo_config,
                        valor=valores_cierre_eliminatoria[fase]
                    )

                    if not ok:
                        errores.append(f"{fase}: {msg}")

                if errores:
                    st.error("No se pudieron guardar todos los cierres.")
                    st.write(errores)
                else:
                    st.cache_data.clear()
                    st.success("Cierres de eliminatoria actualizados.")
                    st.rerun()

        with col_elim_2:
            nuevo_estado_eliminatoria = (
                "OFF"
                if estado_eliminatoria == "ON"
                else "ON"
            )

            texto_boton_eliminatoria = (
                "CERRAR ELIMINATORIA"
                if estado_eliminatoria == "ON"
                else "ABRIR ELIMINATORIA"
            )

            if st.button(
                texto_boton_eliminatoria,
                use_container_width=True
            ):
                ok, msg = actualizar_config_supabase(
                    campo="pronosticos_eliminatoria_estado",
                    valor=nuevo_estado_eliminatoria
                )

                if ok:
                    st.cache_data.clear()
                    st.success("Estado de eliminatoria actualizado.")
                    st.rerun()
                else:
                    st.error(msg)

        st.markdown("---")
        st.markdown("### 🚧 Mantenimiento")

        if estado_mant == "ON":
            st.error("WEB BLOQUEADA")

            if st.button("✅ ABRIR WEB"):
                ok, msg = actualizar_config_supabase(
                    campo="mantenimiento",
                    valor="OFF"
                )

                if ok:
                    st.cache_data.clear()
                    st.success("Web abierta correctamente")
                    st.rerun()
                else:
                    st.error(msg)

        else:
            st.success("WEB ACTIVA")

            if st.button("🚫 CERRAR WEB"):
                ok, msg = actualizar_config_supabase(
                    campo="mantenimiento",
                    valor="ON"
                )

                if ok:
                    st.cache_data.clear()
                    st.success("Web cerrada por mantenimiento")
                    st.rerun()
                else:
                    st.error(msg)

    # ============================================================
    # TAB 5 — TÉCNICO
    # ============================================================

    with tab_tecnico:
        st.subheader("🧪 Diagnóstico técnico")

        with st.expander("🧪 Test Supabase", expanded=False):
            try:
                df_resultados_sb = get_resultados_supabase()
                df_usuarios_sb = get_usuarios_supabase()
                df_pronosticos_sb = get_pronosticos_supabase()

                st.success("✅ Conexión con Supabase funcionando.")

                st.write("Filas en resultados Supabase:", len(df_resultados_sb))
                st.write("Filas en usuarios Supabase:", len(df_usuarios_sb))
                st.write("Filas en pronósticos Supabase:", len(df_pronosticos_sb))

                st.markdown("#### Resultados")
                st.dataframe(
                    df_resultados_sb.head(),
                    use_container_width=True,
                    hide_index=True
                )

                st.markdown("#### Usuarios")
                st.dataframe(
                    df_usuarios_sb.head(),
                    use_container_width=True,
                    hide_index=True
                )

                st.markdown("#### Pronósticos")
                st.dataframe(
                    df_pronosticos_sb.head(),
                    use_container_width=True,
                    hide_index=True
                )

                st.markdown("---")
                st.markdown("#### Test de escritura controlado")

                usuario_test = st.text_input(
                    "Usuario test",
                    value=st.session_state["user_data"]["USUARIO"],
                    key="sb_usuario_test"
                )

                partido_test = st.number_input(
                    "Partido test",
                    min_value=1,
                    max_value=72,
                    value=1,
                    step=1,
                    key="sb_partido_test"
                )

                p1_test = st.number_input(
                    "P1 test",
                    min_value=0,
                    max_value=20,
                    value=0,
                    step=1,
                    key="sb_p1_test"
                )

                p2_test = st.number_input(
                    "P2 test",
                    min_value=0,
                    max_value=20,
                    value=0,
                    step=1,
                    key="sb_p2_test"
                )

                if st.button(
                    "🧪 Probar guardado en Supabase",
                    use_container_width=True
                ):
                    df_test_guardado = pd.DataFrame(
                        [
                            {
                                "USUARIO": usuario_test,
                                "N_PARTIDO": partido_test,
                                "P1": p1_test,
                                "P2": p2_test
                            }
                        ]
                    )

                    ok, msg = guardar_pronosticos_supabase(df_test_guardado)

                    if ok:
                        st.success(msg)
                    else:
                        st.error(msg)

            except Exception as e:
                st.error(f"❌ Error conectando con Supabase: {e}")
