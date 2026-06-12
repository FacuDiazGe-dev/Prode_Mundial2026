import streamlit as st
import pandas as pd

from services.supabase_service import (
    get_resultados_supabase,
    get_usuarios_supabase,
    get_pronosticos_supabase,
    guardar_pronosticos_supabase,
    eliminar_usuario_supabase,
    actualizar_rol_usuario_supabase,
    actualizar_aporte_usuario_supabase,
    get_config_app,
    actualizar_config_supabase,
    guardar_resultados_supabase,
    guardar_estado_partido_supabase
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

    tab_estado, tab_resultados, tab_usuarios, tab_config, tab_tecnico = st.tabs(
        [
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
                "Pendiente no afecta el resultado. 1T, 2T y ET son visuales para Inicio. Finalizado copia el resultado "
                "a R1/R2 y entonces aplica al ranking."
            )

            df_estado_partidos = df_res_admin.sort_values("N_PARTIDO").copy()

            for col in ["LIVE", "LIVE_R1", "LIVE_R2", "ESTADO_PARTIDO"]:
                if col not in df_estado_partidos.columns:
                    if col == "LIVE":
                        df_estado_partidos[col] = False
                    else:
                        df_estado_partidos[col] = None

            opciones_partidos = df_estado_partidos["N_PARTIDO"].astype(int).tolist()

            if opciones_partidos:
                partidos_live_actuales = df_estado_partidos[
                    df_estado_partidos["ESTADO_PARTIDO"]
                    .fillna("")
                    .astype(str)
                    .str.strip()
                    .isin(["1T", "2T", "ET"])
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
                    estado_actual = "1T" if live_actual else "Pendiente"

                estados_partido = ["Pendiente", "1T", "2T", "ET", "Finalizado"]

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

                with st.form(f"form_estado_partido_live_{partido_sel}"):
                    col_r1_live, col_estado_live, col_r2_live = st.columns([1, 1.4, 1])

                    with col_r1_live:
                        live_r1 = st.number_input(
                            "Resultado equipo 1",
                            min_value=0,
                            max_value=20,
                            step=1,
                            value=(
                                int(valor_r1_actual)
                                if pd.notna(valor_r1_actual)
                                else 0
                            ),
                            key=f"admin_live_r1_input_{partido_sel}"
                        )

                    with col_estado_live:
                        estado_partido = st.selectbox(
                            "Estado",
                            options=estados_partido,
                            index=estados_partido.index(estado_actual),
                            key=f"admin_estado_partido_input_{partido_sel}"
                        )

                    with col_r2_live:
                        live_r2 = st.number_input(
                            "Resultado equipo 2",
                            min_value=0,
                            max_value=20,
                            step=1,
                            value=(
                                int(valor_r2_actual)
                                if pd.notna(valor_r2_actual)
                                else 0
                            ),
                            key=f"admin_live_r2_input_{partido_sel}"
                        )

                    guardar_estado = st.form_submit_button(
                        "Guardar estado en vivo",
                        use_container_width=True
                    )
                if guardar_estado:
                    if estado_partido in ["1T", "2T", "ET"]:
                        otros_live = df_estado_partidos[
                            (
                                df_estado_partidos["N_PARTIDO"] != partido_sel
                            )
                            & (
                                df_estado_partidos["ESTADO_PARTIDO"]
                                .fillna("")
                                .astype(str)
                                .str.strip()
                                .isin(["1T", "2T", "ET"])
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

            df_users_panel["APORTE_REALIZADO"] = (
                df_users_panel["APORTE_REALIZADO"]
                .fillna(False)
                .astype(str)
                .str.strip()
                .str.upper()
                .isin(["TRUE", "1", "1.0", "VERDADERO", "T", "SI", "SÍ"])
            )

            columnas_vista = [
                "APORTE_REALIZADO",
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
                df_users_panel[["USUARIO", "APORTE_REALIZADO"]]
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
                    "COMPLETADOS": st.column_config.NumberColumn(
                        "Pronósticos cargados"
                    )
                },
                key="admin_aportes_editor"
            )

            if st.button(
                "💾 Guardar aportes",
                use_container_width=True,
                key="admin_guardar_aportes"
            ):
                cambios_aporte = []

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

                if not cambios_aporte:
                    st.info("No hay cambios de aportes para guardar.")
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

                    if errores:
                        st.error("No se pudieron guardar algunos aportes.")
                        for error in errores:
                            st.caption(error)
                    else:
                        st.cache_data.clear()
                        st.success(
                            f"Aportes actualizados: {len(cambios_aporte)}."
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
