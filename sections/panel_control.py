import streamlit as st
import pandas as pd

from services.supabase_service import (
    get_resultados_supabase,
    get_usuarios_supabase,
    get_pronosticos_supabase,
    guardar_pronosticos_supabase,
    eliminar_usuario_supabase,
    actualizar_rol_usuario_supabase
)

def render_panel_control(
    conn,
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
        st.subheader("⚽ Gestión de Resultados")

        st.info(
            "Esta sección todavía conserva la lógica anterior de Google Sheets. "
            "El próximo paso será migrar la escritura de resultados a Supabase."
        )

        df_res_admin = conn.read(
            worksheet="RESULTADOS",
            ttl=5
        )

        with st.form("form_admin_master_72"):

            df_to_update = df_res_admin.copy()
            df_to_update["VIZ"] = df_to_update["VIZ"].astype(object)

            t1, t2, t3 = st.tabs(
                [
                    "Fecha 1",
                    "Fecha 2",
                    "Fecha 3"
                ]
            )

            def renderizar_bloque(df_grupo, contenedor):
                with contenedor:
                    for idx_df, row in df_grupo.iterrows():
                        id_p = int(row["N_PARTIDO"])

                        r1_curr = (
                            int(row["R1"])
                            if pd.notna(row["R1"])
                            else 0
                        )

                        r2_curr = (
                            int(row["R2"])
                            if pd.notna(row["R2"])
                            else 0
                        )

                        viz_act = (
                            str(row["VIZ"])
                            .strip()
                            .upper()
                            in [
                                "TRUE",
                                "1",
                                "1.0",
                                "VERDADERO"
                            ]
                        )

                        st.markdown(
                            f"**P{id_p}:** {row['Equipo_1']} vs {row['Equipo_2']}"
                        )

                        c1, c_vs, c2, c_viz = st.columns(
                            [1, 0.2, 1, 1.2]
                        )

                        with c1:
                            r1_val = st.number_input(
                                f"G1_{id_p}",
                                0,
                                20,
                                r1_curr,
                                key=f"r1_{id_p}",
                                label_visibility="collapsed"
                            )

                        with c_vs:
                            st.write(
                                "<div style='text-align:center; padding-top:5px;'>:</div>",
                                unsafe_allow_html=True
                            )

                        with c2:
                            r2_val = st.number_input(
                                f"G2_{id_p}",
                                0,
                                20,
                                r2_curr,
                                key=f"r2_{id_p}",
                                label_visibility="collapsed"
                            )

                        with c_viz:
                            viz_val = st.toggle(
                                "Visible",
                                value=viz_act,
                                key=f"viz_{id_p}"
                            )

                            finalizado = st.checkbox(
                                "Fin",
                                value=pd.notna(row["R1"]),
                                key=f"fin_{id_p}"
                            )

                        df_to_update.at[idx_df, "R1"] = (
                            r1_val
                            if finalizado
                            else None
                        )

                        df_to_update.at[idx_df, "R2"] = (
                            r2_val
                            if finalizado
                            else None
                        )

                        df_to_update.at[idx_df, "VIZ"] = (
                            "TRUE"
                            if viz_val
                            else "FALSE"
                        )

                        st.markdown("---")

            renderizar_bloque(
                df_to_update.iloc[0:24],
                t1
            )

            renderizar_bloque(
                df_to_update.iloc[24:48],
                t2
            )

            renderizar_bloque(
                df_to_update.iloc[48:72],
                t3
            )

            submit = st.form_submit_button(
                "💾 GUARDAR LOS 72 PARTIDOS",
                use_container_width=True
            )

            if submit:
                try:
                    conn.update(
                        worksheet="RESULTADOS",
                        data=df_to_update
                    )

                    st.cache_data.clear()
                    st.success("✅ ¡Los 72 partidos han sido actualizados!")
                    st.balloons()
                    st.rerun()

                except Exception as e:
                    st.error(f"❌ Error al conectar: {e}")

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

            columnas_vista = [
                "USUARIO",
                "NOMBRE",
                "ROL",
                "EQUIPO FAVORITO",
                "COMPLETADOS"
            ]

            for col in columnas_vista:
                if col not in df_users_panel.columns:
                    df_users_panel[col] = ""

            st.dataframe(
                df_users_panel[columnas_vista],
                use_container_width=True,
                hide_index=True
            )

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

        df_config = conn.read(
            worksheet="CONFIG",
            ttl=10
        )

        estado_manual = str(
            df_config.iloc[0]["REGISTRO"]
        ).strip().upper()

        st.markdown("### 🚫 Control de Inscripciones")

        if registro_permitido_fecha and estado_manual == "ON":
            st.success("✅ Inscripciones ABIERTAS")

            if st.button(
                "🔴 CERRAR REGISTRO MANUALMENTE",
                use_container_width=True
            ):
                df_config.at[0, "REGISTRO"] = "OFF"

                conn.update(
                    worksheet="CONFIG",
                    data=df_config
                )

                st.cache_data.clear()
                st.success("Registro cerrado con éxito")
                st.rerun()

        else:
            st.error("⛔ Inscripciones CERRADAS")

            if registro_permitido_fecha:
                if st.button(
                    "🟢 ABRIR REGISTRO MANUALMENTE",
                    use_container_width=True
                ):
                    df_config.at[0, "REGISTRO"] = "ON"

                    conn.update(
                        worksheet="CONFIG",
                        data=df_config
                    )

                    st.cache_data.clear()
                    st.success("Registro abierto con éxito")
                    st.rerun()

            else:
                st.warning(
                    "No se puede abrir manualmente: ya pasó la fecha límite (07/06)."
                )

        st.markdown("---")
        st.markdown("### 🚧 Mantenimiento")

        if estado_mantenimiento == "ON":
            st.error("WEB BLOQUEADA")

            if st.button("✅ ABRIR WEB"):
                df_config = conn.read(
                    worksheet="CONFIG",
                    ttl=0
                )

                df_config.at[0, "MANTENIMIENTO"] = "OFF"

                conn.update(
                    worksheet="CONFIG",
                    data=df_config
                )

                st.cache_data.clear()
                st.rerun()

        else:
            st.success("WEB ACTIVA")

            if st.button("🚫 CERRAR WEB"):
                df_config = conn.read(
                    worksheet="CONFIG",
                    ttl=0
                )

                df_config.at[0, "MANTENIMIENTO"] = "ON"

                conn.update(
                    worksheet="CONFIG",
                    data=df_config
                )

                st.cache_data.clear()
                st.rerun()

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
