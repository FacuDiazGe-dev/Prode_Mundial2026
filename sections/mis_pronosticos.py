import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from html import escape

from styles_config import AVATAR_GENERICO
from tools import upload_profile_picture


def render_mis_pronosticos(
    df_res,
    df_usuarios,
    df_pro,
    df_ranking,
    mapa_banderas,
    conn
):
    # ============================================================
    # ESTILOS — MIS PRONÓSTICOS / MI PERFIL
    # ============================================================

    st.markdown("""
<style>
.page-section-title {
    margin-bottom: 22px;
}

.page-section-title h1 {
    font-family: 'Montserrat', sans-serif;
    font-size: 34px;
    font-weight: 900;
    color: #07111F;
    margin: 0;
    letter-spacing: -0.04em;
}

.page-section-title p {
    margin: 6px 0 0 0;
    color: #64748b;
    font-size: 15px;
    font-weight: 600;
}

.pred-panel,
.profile-panel {
    background: rgba(255,255,255,0.94);
    border: 1px solid rgba(226,232,240,0.9);
    border-radius: 18px;
    padding: 16px;
    box-shadow: 0 12px 30px rgba(15,23,42,0.06);
}

.panel-header {
    display: flex;
    align-items: center;
    gap: 10px;
    padding: 4px 4px 14px 4px;
    margin-bottom: 12px;
    border-bottom: 1px solid rgba(226,232,240,0.75);
}

.panel-icon {
    width: 32px;
    height: 32px;
    border-radius: 10px;
    display: flex;
    align-items: center;
    justify-content: center;
    background: rgba(244,197,66,0.16);
    color: #0f172a;
    font-size: 16px;
}

.panel-title {
    font-family: 'Montserrat', sans-serif;
    font-size: 18px;
    font-weight: 900;
    color: #0f172a;
}

.pred-status {
    background: linear-gradient(90deg, rgba(244,197,66,0.18), rgba(255,255,255,0.95));
    border: 1px solid rgba(244,197,66,0.45);
    color: #92400e;
    border-radius: 14px;
    padding: 12px 14px;
    margin-bottom: 14px;
    font-size: 13px;
    font-weight: 800;
}

.pred-status.locked {
    background: rgba(248,250,252,0.95);
    border: 1px solid rgba(148,163,184,0.35);
    color: #64748b;
}

/* ============================================================
   CARDS HORIZONTALES DE PRONÓSTICOS
   Desktop + Mobile compacto
   ============================================================ */

.pred-match-card,
.pred-match-card-v2 {
    background: rgba(248,250,252,0.94);
    border: 1px solid rgba(226,232,240,0.9);
    border-radius: 15px;
    padding: 10px 12px 8px 12px;
    margin-bottom: 4px;
    overflow: hidden;
}

.pred-match-meta {
    display: flex;
    justify-content: space-between;
    align-items: center;
    color: #94a3b8;
    font-size: 10px;
    font-weight: 900;
    text-transform: uppercase;
    letter-spacing: 0.06em;
    margin-bottom: 0;
}

.pred-team {
    display: flex;
    align-items: center;
    min-height: 38px;
    color: #0f172a;
    font-size: 13px;
    font-weight: 900;
    overflow: hidden;
    white-space: nowrap;
}

.pred-team-left {
    justify-content: flex-end;
    text-align: right;
}

.pred-team-right {
    justify-content: flex-start;
    text-align: left;
}

.pred-team span {
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
}

.pred-flag-wrap {
    min-height: 38px;
    display: flex;
    align-items: center;
    justify-content: center;
}

.pred-flag {
    width: 28px;
    height: 20px;
    object-fit: cover;
    border-radius: 4px;
    box-shadow: 0 2px 5px rgba(15,23,42,0.16);
    flex-shrink: 0;
}

.pred-vs {
    min-height: 38px;
    display: flex;
    align-items: center;
    justify-content: center;
    color: #0f172a;
    font-family: 'Montserrat', sans-serif;
    font-weight: 900;
    padding: 0;
}

.pred-match-gap {
    height: 10px;
    border-bottom: 1px solid rgba(226,232,240,0.65);
    margin-bottom: 8px;
}

/* Inputs como casilleros de marcador */
div[data-testid="stNumberInput"] input {
    text-align: center;
    font-family: 'Montserrat', sans-serif;
    font-weight: 900;
    border-radius: 10px !important;
    border: 1px solid rgba(244,197,66,0.42) !important;
    background: rgba(255,255,255,0.96) !important;
}

/* Botones de edición / guardado */
div[data-testid="stFormSubmitButton"] button {
    border-radius: 13px !important;
    min-height: 44px !important;
    font-family: 'Inter', sans-serif !important;
    font-size: 14px !important;
    font-weight: 900 !important;

    background: linear-gradient(
        135deg,
        rgba(244,197,66,0.95),
        rgba(255,220,105,0.95)
    ) !important;

    color: #07111F !important;
    border: 1px solid rgba(180,130,20,0.28) !important;

    box-shadow:
        0 8px 18px rgba(244,197,66,0.18),
        inset 0 1px 0 rgba(255,255,255,0.38) !important;

    transition: all 0.18s ease !important;
}

div[data-testid="stFormSubmitButton"] button:hover {
    transform: translateY(-1px);
    background: linear-gradient(
        135deg,
        rgba(255,214,80,1),
        rgba(255,230,135,1)
    ) !important;

    border-color: rgba(180,130,20,0.45) !important;
    box-shadow:
        0 10px 22px rgba(244,197,66,0.24),
        inset 0 1px 0 rgba(255,255,255,0.45) !important;
}

div[data-testid="stFormSubmitButton"] button:disabled {
    background: rgba(248,250,252,0.95) !important;
    color: #94a3b8 !important;
    border: 1px solid rgba(226,232,240,0.95) !important;
    box-shadow: none !important;
}

/* ============================================================
   RESUMEN OSCURO — ESTADÍSTICAS DE PRONÓSTICOS
   ============================================================ */

.pred-summary-footer {
    background:
        linear-gradient(
            135deg,
            rgba(7,17,31,0.98),
            rgba(15,23,42,0.94)
        );
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 16px;
    padding: 15px 16px;
    margin: 12px 10px 4px 10px;
    box-shadow:
        inset 0 1px 0 rgba(255,255,255,0.05),
        0 10px 24px rgba(15,23,42,0.08);
}

.pred-summary-kicker {
    font-size: 10px;
    font-weight: 900;
    color: rgba(255,255,255,0.55);
    text-transform: uppercase;
    letter-spacing: 0.08em;
    margin-bottom: 9px;
}

.pred-summary-grid {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 8px;
}

.pred-summary-item {
    background: rgba(255,255,255,0.06);
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 12px;
    padding: 9px 6px;
    text-align: center;
}

.pred-summary-icon {
    font-size: 16px;
    line-height: 1;
    margin-bottom: 4px;
}

.pred-summary-number {
    font-family: 'Montserrat', sans-serif;
    font-size: 17px;
    font-weight: 900;
    color: #F8FAFC;
    line-height: 1;
}

.pred-summary-label {
    margin-top: 4px;
    font-size: 9px;
    font-weight: 800;
    color: rgba(255,255,255,0.55);
    text-transform: uppercase;
}

.pred-summary-style {
    margin-top: 10px;
    color: rgba(255,255,255,0.72);
    font-size: 11px;
    font-weight: 800;
}

.pred-summary-style strong {
    color: #F4C542;
}

/* ============================================================
   MOBILE — UNA SOLA LÍNEA POR PARTIDO
   ============================================================ */

@media (max-width: 768px) {

    html, body {
        overflow-x: hidden !important;
    }

    div[data-testid="stForm"] {
        overflow-x: hidden !important;
        padding: 12px !important;
    }

    .page-section-title h1 {
        font-size: 27px;
        line-height: 1.05;
    }

    .page-section-title p {
        font-size: 12px;
    }

    .pred-panel-header-v2 {
        padding: 2px 2px 12px 2px;
        margin-bottom: 10px;
    }

    .panel-title {
        font-size: 17px;
    }

    .pred-panel-subtitle {
        font-size: 10px;
    }

    .pred-match-card-v2 {
        padding: 8px 8px 7px 8px !important;
        margin-bottom: 3px !important;
        border-radius: 13px !important;
    }

    .pred-match-meta {
        font-size: 8px !important;
        letter-spacing: 0.03em !important;
    }

    .pred-team {
        min-height: 32px !important;
        font-size: 9px !important;
        line-height: 1 !important;
    }

    .pred-team span {
        max-width: 54px !important;
    }

    .pred-flag-wrap {
        min-height: 32px !important;
    }

    .pred-flag {
        width: 18px !important;
        height: 13px !important;
        border-radius: 3px !important;
    }

    .pred-vs {
        min-height: 32px !important;
        font-size: 13px !important;
        padding: 0 !important;
    }

    div[data-testid="stNumberInput"] {
        min-width: 30px !important;
        max-width: 34px !important;
    }

    div[data-testid="stNumberInput"] input {
        height: 32px !important;
        min-height: 32px !important;
        max-height: 32px !important;
        width: 32px !important;
        min-width: 32px !important;
        max-width: 32px !important;
        padding: 0 !important;
        font-size: 14px !important;
        border-radius: 8px !important;
    }

    /* Oculta + / - en celular para conservar la fila horizontal */
    div[data-testid="stNumberInput"] button {
        display: none !important;
    }

    .pred-match-gap {
        height: 6px !important;
        margin-bottom: 6px !important;
    }

    .pred-summary-footer {
        margin: 10px 6px 4px 6px !important;
        padding: 12px !important;
        border-radius: 14px !important;
    }

    .pred-summary-grid {
        grid-template-columns: repeat(2, 1fr);
        gap: 7px;
    }

    .pred-summary-item {
        padding: 8px 6px;
    }

    .pred-summary-number {
        font-size: 16px;
    }

    .pred-summary-label {
        font-size: 8px;
    }

    .pred-summary-style {
        margin-top: 8px;
        font-size: 10px;
        text-align: center;
    }
}
    text-align: center;
}

.profile-avatar {
    width: 128px;
    height: 128px;
    object-fit: cover;
    border-radius: 50%;
    border: 5px solid #F4C542;
    box-shadow:
        0 12px 34px rgba(0,0,0,0.18),
        0 0 22px rgba(244,197,66,0.28);
}

.profile-name {
    font-family: 'Montserrat', sans-serif;
    font-size: 26px;
    font-weight: 900;
    color: #0f172a;
    margin-top: 14px;
}

.profile-user {
    color: #64748b;
    font-size: 14px;
    font-weight: 700;
    margin-bottom: 18px;
}

.profile-info {
    text-align: left;
    border-top: 1px solid rgba(226,232,240,0.85);
    margin-top: 18px;
    padding-top: 12px;
}

.profile-info-row {
    display: grid;
    grid-template-columns: 120px 1fr;
    gap: 12px;
    padding: 9px 0;
    border-bottom: 1px solid rgba(226,232,240,0.65);
    font-size: 13px;
}

.profile-info-label {
    color: #64748b;
    font-weight: 800;
}

.profile-info-value {
    color: #0f172a;
    font-weight: 800;
}

.profile-stats {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 8px;
    margin: 18px 0;
}

.profile-stat {
    border: 1px solid rgba(226,232,240,0.9);
    border-radius: 14px;
    padding: 10px 6px;
    background: rgba(248,250,252,0.75);
}

.profile-stat-icon {
    font-size: 18px;
}

.profile-stat-number {
    font-family: 'Montserrat', sans-serif;
    font-size: 18px;
    font-weight: 900;
    color: #0f172a;
    line-height: 1.1;
}

.profile-stat-label {
    font-size: 10px;
    color: #64748b;
    font-weight: 800;
}

.profile-edit-box {
    background: rgba(248,250,252,0.72);
    border: 1px solid rgba(226,232,240,0.85);
    border-radius: 15px;
    padding: 14px;
}
.pred-summary-footer {
    background:
        linear-gradient(
            135deg,
            rgba(7,17,31,0.98),
            rgba(15,23,42,0.94)
        );
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 16px;

    padding: 14px 14px;
    margin: 10px 10px 2px 10px;

    box-shadow:
        inset 0 1px 0 rgba(255,255,255,0.05),
        0 10px 24px rgba(15,23,42,0.08);
}

.pred-summary-kicker {
    font-size: 10px;
    font-weight: 900;
    color: rgba(255,255,255,0.55);
    text-transform: uppercase;
    letter-spacing: 0.08em;
    margin-bottom: 9px;
}

.pred-summary-grid {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 8px;
}

.pred-summary-item {
    background: rgba(255,255,255,0.06);
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 12px;
    padding: 9px 6px;
    text-align: center;
}

.pred-summary-icon {
    font-size: 16px;
    line-height: 1;
    margin-bottom: 4px;
}

.pred-summary-number {
    font-family: 'Montserrat', sans-serif;
    font-size: 17px;
    font-weight: 900;
    color: #F8FAFC;
    line-height: 1;
}

.pred-summary-label {
    margin-top: 4px;
    font-size: 9px;
    font-weight: 800;
    color: rgba(255,255,255,0.55);
    text-transform: uppercase;
}

.pred-summary-style {
    margin-top: 10px;
    color: rgba(255,255,255,0.72);
    font-size: 11px;
    font-weight: 800;
}

.pred-summary-style strong {
    color: #F4C542;
}


    # ============================================================
    # HELPERS
    # ============================================================

    def flag_html(flag_value):
        flag_value = str(flag_value)

        if flag_value.startswith("http") or flag_value.startswith("data:image"):
            return f'<img src="{flag_value}" class="pred-flag">'

        return f'<span>{escape(flag_value)}</span>'

    def get_user_rank_stats(usuario):
        row_rank = df_ranking[df_ranking["USUARIO"] == usuario]

        if row_rank.empty:
            return {
                "pos": "-",
                "pts": 0,
                "exactos": 0,
                "generales": 0
            }

        row = row_rank.iloc[0]

        try:
            pos = int(row_rank.index[0])
        except:
            pos = "-"

        return {
            "pos": pos,
            "pts": int(row.get("PUNTOS", 0)),
            "exactos": int(row.get("EXACTOS", 0)),
            "generales": int(row.get("GENERALES", 0))
        }

    def calcular_stats_pronosticos(lista_pronosticos):
        total_partidos = len(lista_pronosticos)

        if total_partidos == 0:
            return {
                "con_ganador": 0,
                "empates": 0,
                "goles": 0,
                "promedio_goles": 0,
                "estilo": "Sin datos"
            }

        con_ganador = 0
        empates = 0
        goles = 0
    
        for p in lista_pronosticos:
            p1 = int(p.get("P1", 0))
            p2 = int(p.get("P2", 0))
    
            goles += p1 + p2
    
            if p1 == p2:
                empates += 1
            else:
                con_ganador += 1
    
        promedio_goles = goles / total_partidos
    
        if promedio_goles >= 3:
            estilo = "Optimista del gol"
        elif promedio_goles <= 1.8:
            estilo = "Bilardista táctico"
        else:
            estilo = "Equilibrado"
    
        return {
            "con_ganador": con_ganador,
            "empates": empates,
            "goles": goles,
            "promedio_goles": round(promedio_goles, 1),
            "estilo": estilo
        }
    # ============================================================
    # DATOS BASE
    # ============================================================

    if "permitir_edicion" not in st.session_state:
        st.session_state.permitir_edicion = False

    if "editando_perfil" not in st.session_state:
        st.session_state.editando_perfil = False

    user_actual = st.session_state["user_data"]["USUARIO"]
    u_data = st.session_state["user_data"]

    df_user_pro = df_pro[df_pro["USUARIO"] == user_actual]

    ahora_arg = datetime.utcnow() - timedelta(hours=3)
    fecha_limite = datetime(2026, 6, 8, 23, 59, 59)
    es_tiempo_valido = ahora_arg < fecha_limite

    # ============================================================
    # TÍTULO DE PÁGINA
    # ============================================================

    st.markdown("""
<div class="page-section-title">
    <h1>Mis Pronósticos / Mi Perfil</h1>
    <p>Gestioná tus predicciones y tu información personal.</p>
</div>
""", unsafe_allow_html=True)

    c_pron, c_perfil = st.columns([1.35, 1], gap="large")

    # ============================================================
    # COLUMNA IZQUIERDA — MIS PRONÓSTICOS
    # ============================================================

    with c_pron:

        modo_edicion = st.session_state.permitir_edicion
        esta_bloqueado = not (es_tiempo_valido and modo_edicion)

        if es_tiempo_valido:
            estado_txt = "Edición abierta hasta el 08/06/2026"
            estado_class = "open"
        else:
            estado_txt = "Plazo finalizado · modo lectura"
            estado_class = "locked"
            modo_edicion = False
            st.session_state.permitir_edicion = False
            esta_bloqueado = True

        with st.form("form_pronosticos_v5"):

            # ------------------------------------------------------------
            # HEADER INTEGRADO DEL PANEL
            # ------------------------------------------------------------

            st.markdown(f"""
<div class="pred-panel-header-v2">
<div class="pred-panel-title-row">
<div class="panel-icon">📝</div>
<div>
<div class="panel-title">Mis Pronósticos</div>
<div class="pred-panel-subtitle {estado_class}">{estado_txt}</div>
</div>
</div>
</div>
""", unsafe_allow_html=True)

            lista_nuevos_pro = []
            # ------------------------------------------------------------
            # LISTADO DE PARTIDOS — CARD HORIZONTAL COMPACTA
            # ------------------------------------------------------------

            lista_nuevos_pro = []

            with st.container(height=520):

                for _, row in df_res.sort_values("N_PARTIDO").iterrows():
                    id_p = int(row["N_PARTIDO"])
                    match = df_user_pro[df_user_pro["N_PARTIDO"] == id_p]

                    v1 = (
                        int(match.iloc[0]["P1"])
                        if not match.empty and pd.notna(match.iloc[0]["P1"])
                        else 0
                    )

                    v2 = (
                        int(match.iloc[0]["P2"])
                        if not match.empty and pd.notna(match.iloc[0]["P2"])
                        else 0
                    )

                    equipo_1 = str(row.get("Equipo_1", ""))
                    equipo_2 = str(row.get("Equipo_2", ""))

                    bandera1 = mapa_banderas.get(equipo_1, "⚽")
                    bandera2 = mapa_banderas.get(equipo_2, "⚽")

                    dia = str(row.get("DIA", ""))
                    hora = str(row.get("HORA", ""))

                    # Header de la card
                    st.markdown(f"""
<div class="pred-match-card-v2">
<div class="pred-match-meta">
<span>Partido #{id_p}</span>
<span>{escape(dia)} | {escape(hora)}</span>
</div>
</div>
""", unsafe_allow_html=True)

                    # Fila horizontal compacta:
                    # Eq1 - Flag1 - R1 - : - R2 - Flag2 - Eq2
                    c_eq1, c_flag1, c_g1, c_vs, c_g2, c_flag2, c_eq2 = st.columns(
                        [1.05, 0.22, 0.28, 0.08, 0.28, 0.22, 1.05],
                        gap="small"
                    )

                    with c_eq1:
                        st.markdown(f"""
<div class="pred-team pred-team-left">
<span>{escape(equipo_1)}</span>
</div>
""", unsafe_allow_html=True)

                    with c_flag1:
                        st.markdown(f"""
<div class="pred-flag-wrap">
{flag_html(bandera1)}
</div>
""", unsafe_allow_html=True)

                    with c_g1:
                        p1_val = st.number_input(
                            f"G1_{id_p}",
                            min_value=0,
                            max_value=15,
                            value=v1,
                            key=f"mispron_f1_{id_p}",
                            label_visibility="collapsed",
                            disabled=esta_bloqueado
                        )

                    with c_vs:
                        st.markdown(
                            '<div class="pred-vs">:</div>',
                            unsafe_allow_html=True
                        )

                    with c_g2:
                        p2_val = st.number_input(
                            f"G2_{id_p}",
                            min_value=0,
                            max_value=15,
                            value=v2,
                            key=f"mispron_f2_{id_p}",
                            label_visibility="collapsed",
                            disabled=esta_bloqueado
                        )

                    with c_flag2:
                        st.markdown(f"""
<div class="pred-flag-wrap">
{flag_html(bandera2)}
</div>
""", unsafe_allow_html=True)

                    with c_eq2:
                        st.markdown(f"""
<div class="pred-team pred-team-right">
<span>{escape(equipo_2)}</span>
</div>
""", unsafe_allow_html=True)

                    lista_nuevos_pro.append(
                        {
                            "N_PARTIDO": id_p,
                            "USUARIO": user_actual,
                            "P1": p1_val,
                            "P2": p2_val
                        }
                    )

                    st.markdown(
                        "<div class='pred-match-gap'></div>",
                        unsafe_allow_html=True
                    )

            stats_pronosticos = calcular_stats_pronosticos(lista_nuevos_pro)
            # ------------------------------------------------------------
            # ACCIONES
            # ------------------------------------------------------------
            
            if not es_tiempo_valido:
                submit = st.form_submit_button(
                    "Lectura — edición deshabilitada",
                    use_container_width=True,
                    disabled=True
                )
                cancelar = False
                editar = False
            
            elif not modo_edicion:
                editar = st.form_submit_button(
                    "✏️ Editar pronósticos",
                    use_container_width=True
                )
                submit = False
                cancelar = False
            
            else:
                c_cancelar, c_guardar = st.columns([0.35, 0.65])
            
                cancelar = c_cancelar.form_submit_button(
                    "❌ Cancelar",
                    use_container_width=True
                )
            
                submit = c_guardar.form_submit_button(
                    "💾 Guardar pronósticos",
                    use_container_width=True
                )
            
                editar = False
            
            # ------------------------------------------------------------
            # RESUMEN OSCURO
            # ------------------------------------------------------------
            
            st.markdown(
                f"""
            <div class="pred-summary-footer">
            <div class="pred-summary-kicker">Tus pronósticos</div>
            
            <div class="pred-summary-grid">
            <div class="pred-summary-item">
                <div class="pred-summary-icon">🏆</div>
                <div class="pred-summary-number">{stats_pronosticos["con_ganador"]}</div>
                <div class="pred-summary-label">Con ganador</div>
            </div>
            
            <div class="pred-summary-item">
                <div class="pred-summary-icon">🤝</div>
                <div class="pred-summary-number">{stats_pronosticos["empates"]}</div>
                <div class="pred-summary-label">Empates</div>
            </div>
            
            <div class="pred-summary-item">
                <div class="pred-summary-icon">⚽</div>
                <div class="pred-summary-number">{stats_pronosticos["goles"]}</div>
                <div class="pred-summary-label">Goles</div>
            </div>
            
            <div class="pred-summary-item">
                <div class="pred-summary-icon">📊</div>
                <div class="pred-summary-number">{stats_pronosticos["promedio_goles"]}</div>
                <div class="pred-summary-label">Promedio</div>
            </div>
            </div>
            
            <div class="pred-summary-style">
            Estilo de predicción: <strong>{stats_pronosticos["estilo"]}</strong>
            </div>
            </div>
            """,
                unsafe_allow_html=True
            )
            
            # ------------------------------------------------------------
            # EVENTOS
            # ------------------------------------------------------------
            
            if editar:
                st.session_state.permitir_edicion = True
                st.rerun()
            
            if cancelar:
                st.session_state.permitir_edicion = False
                st.rerun()
            
            if submit:
                try:
                    df_pro_full = conn.read(
                        worksheet="PRONOSTICOS",
                        ttl=5
                    )
            
                    df_otros = df_pro_full[
                        df_pro_full["USUARIO"] != user_actual
                    ]
            
                    df_final = pd.concat(
                        [df_otros, pd.DataFrame(lista_nuevos_pro)],
                        ignore_index=True
                    )
            
                    conn.update(
                        worksheet="PRONOSTICOS",
                        data=df_final
                    )
            
                    st.cache_data.clear()
                    st.session_state.permitir_edicion = False
            
                    st.success("✅ ¡Pronósticos guardados correctamente!")
                    st.balloons()
                    st.rerun()
            
                except Exception as e:
                    st.error(f"Error al guardar: {e}")

    # ============================================================
    # COLUMNA DERECHA — MI PERFIL
    # ============================================================

    with c_perfil:
        stats = get_user_rank_stats(user_actual)

        foto_actual = u_data.get("AVATAR_URL")

        if not foto_actual or pd.isna(foto_actual):
            foto = AVATAR_GENERICO
        else:
            foto = foto_actual

        if not st.session_state.editando_perfil:
            nombre = escape(str(u_data.get("NOMBRE", "Jugador")))
            usuario = escape(str(u_data.get("USUARIO", "")))
            equipo = escape(str(u_data.get("EQUIPO FAVORITO", "-")))
            edad = escape(str(u_data.get("EDAD", "-")))
            bio = escape(str(u_data.get("DESCRIPCION", "")))

            st.markdown(
                f"""
<div class="profile-panel">
<div class="panel-header">
    <div class="panel-icon">👤</div>
    <div class="panel-title">Mi Perfil</div>
</div>

<div class="profile-card">
    <img src="{foto}" class="profile-avatar">
    <div class="profile-name">{nombre}</div>
    <div class="profile-user">@{usuario}</div>
</div>

<div class="profile-info">
<div class="profile-info-row">
    <div class="profile-info-label">⚽ Equipo</div>
    <div class="profile-info-value">{equipo}</div>
</div>
<div class="profile-info-row">
    <div class="profile-info-label">🎂 Edad</div>
    <div class="profile-info-value">{edad} años</div>
</div>
<div class="profile-info-row">
    <div class="profile-info-label">📝 Bio</div>
    <div class="profile-info-value">{bio}</div>
</div>
</div>

<div class="profile-stats">
<div class="profile-stat">
    <div class="profile-stat-icon">🏆</div>
    <div class="profile-stat-number">{stats["pts"]}</div>
    <div class="profile-stat-label">Puntos</div>
</div>
<div class="profile-stat">
    <div class="profile-stat-icon">🎯</div>
    <div class="profile-stat-number">{stats["exactos"]}</div>
    <div class="profile-stat-label">Exactos</div>
</div>
<div class="profile-stat">
    <div class="profile-stat-icon">✅</div>
    <div class="profile-stat-number">{stats["generales"]}</div>
    <div class="profile-stat-label">Generales</div>
</div>
<div class="profile-stat">
    <div class="profile-stat-icon">📊</div>
    <div class="profile-stat-number">{stats["pos"]}°</div>
    <div class="profile-stat-label">Posición</div>
</div>
</div>
</div>
""",
                unsafe_allow_html=True
            )

            if st.button("✏️ Editar Perfil", use_container_width=True):
                st.session_state.editando_perfil = True
                st.rerun()

        else:
            st.markdown("""
<div class="profile-panel">
    <div class="panel-header">
        <div class="panel-icon">✏️</div>
        <div class="panel-title">Editar Perfil</div>
    </div>
    <div class="profile-edit-box">
""", unsafe_allow_html=True)

            with st.form("form_edit_perfil_v4"):
                archivo_perfil = st.file_uploader(
                    "Actualizar foto de perfil",
                    type=["jpg", "jpeg", "png"]
                )

                n_nom = st.text_input(
                    "Nombre Real",
                    value=str(u_data.get("NOMBRE", ""))
                )

                equipos = [
                    "Argentina",
                    "México",
                    "España",
                    "Brasil",
                    "Uruguay",
                    "Colombia",
                    "Otro"
                ]

                equipo_actual = u_data.get("EQUIPO FAVORITO", "Argentina")
                idx_equipo = equipos.index(equipo_actual) if equipo_actual in equipos else 0

                n_equ = st.selectbox(
                    "Hincha de",
                    equipos,
                    index=idx_equipo
                )

                n_bio = st.text_area(
                    "Bio",
                    value=str(u_data.get("DESCRIPCION", "")),
                    max_chars=100
                )

                c_b1, c_b2 = st.columns(2)

                guardar = c_b1.form_submit_button("✅ Guardar")
                cancelar = c_b2.form_submit_button("❌ Cancelar")

                if guardar:
                    nueva_url = u_data.get("AVATAR_URL", AVATAR_GENERICO)

                    if archivo_perfil:
                        with st.spinner("Subiendo foto al servidor..."):
                            ts = datetime.now().strftime("%H%M%S")
                            nombre_archivo = f"perfil_{u_data['USUARIO']}_{ts}.jpg"
                            res_url = upload_profile_picture(
                                archivo_perfil,
                                nombre_archivo
                            )

                            if res_url and "Error" not in res_url:
                                nueva_url = res_url
                            else:
                                st.error(f"Error al subir: {res_url}")

                    try:
                        df_u = conn.read(worksheet="USUARIOS", ttl=10)

                        df_u.loc[
                            df_u["USUARIO"] == u_data["USUARIO"],
                            ["NOMBRE", "AVATAR_URL", "EQUIPO FAVORITO", "DESCRIPCION"]
                        ] = [n_nom, nueva_url, n_equ, n_bio]

                        conn.update(
                            worksheet="USUARIOS",
                            data=df_u
                        )

                        st.session_state["user_data"].update(
                            {
                                "NOMBRE": n_nom,
                                "AVATAR_URL": nueva_url,
                                "EQUIPO FAVORITO": n_equ,
                                "DESCRIPCION": n_bio
                            }
                        )

                        st.session_state.editando_perfil = False
                        st.cache_data.clear()

                        st.success("¡Perfil actualizado!")
                        st.rerun()

                    except Exception as e:
                        st.error(f"Error: {e}")

                if cancelar:
                    st.session_state.editando_perfil = False
                    st.rerun()

            st.markdown("</div></div>", unsafe_allow_html=True)
