import streamlit as st
import pandas as pd
from html import escape

from styles_config import AVATAR_GENERICO
from ranking_logic import calcular_detalle
from tools import get_flag_img_cached


def render_jugadores(
    df_usuarios,
    df_ranking,
    df_pro,
    df_res
):
    # ============================================================
    # ESTILOS — JUGADORES
    # ============================================================

    st.markdown("""
<style>

/* ============================================================
   1. TÍTULO GENERAL DE LA SECCIÓN
   ============================================================ */

.players-title {
    margin-bottom: 22px;
}

.players-title h1 {
    font-family: 'Montserrat', sans-serif;
    font-size: 34px;
    font-weight: 900;
    color: #07111F;
    margin: 0;
    letter-spacing: -0.04em;
}

.players-title p {
    margin: 6px 0 0 0;
    color: #64748b;
    font-size: 15px;
    font-weight: 600;
}


/* ============================================================
   2. PANELES BASE Y ENCABEZADOS
   Usados en ficha, muro de insignias y pronósticos.
   ============================================================ */

/* ============================================================
   2. PANELES BASE Y ENCABEZADOS
   Usados en ficha, muro de insignias y pronósticos.
   ============================================================ */

.players-panel,
.player-profile-panel,
.badges-wall-panel,
.player-preds-panel {
    background: rgba(255,255,255,0.94);
    border: 1px solid rgba(226,232,240,0.9);
    border-radius: 18px;
    padding: 16px;
    box-shadow: 0 12px 30px rgba(15,23,42,0.06);
}

.players-panel-header {
    display: flex;
    align-items: center;
    gap: 10px;
    padding: 4px 4px 14px 4px;
    margin-bottom: 12px;
    border-bottom: 1px solid rgba(226,232,240,0.75);
}

.players-panel-icon {
    width: 32px;
    height: 32px;
    border-radius: 10px;
    display: flex;
    align-items: center;
    justify-content: center;
    background: rgba(244,197,66,0.16);
    color: #0f172a;
    font-size: 16px;
    flex-shrink: 0;
}

.players-panel-title {
    font-family: 'Montserrat', sans-serif;
    font-size: 18px;
    font-weight: 900;
    color: #0f172a;
}

.players-panel-subtitle {
    color: #64748b;
    font-size: 12px;
    font-weight: 700;
    margin-top: 2px;
}

/* ============================================================
   3. LISTADO SELECTOR DE JUGADORES
   Estructura: botón pequeño + card visual del jugador.
   ============================================================ */

.player-select-row {
    margin-bottom: 8px;
}

.player-list-card {
    background: rgba(248,250,252,0.92);
    border: 1px solid rgba(226,232,240,0.9);
    border-radius: 14px;
    padding: 9px 10px;

    display: flex;
    align-items: center;
    gap: 10px;

    min-height: 54px;
    transition: all 0.16s ease;
}

.player-list-card.selected {
    border: 1px solid rgba(244,197,66,0.85);
    background:
        linear-gradient(
            90deg,
            rgba(244,197,66,0.20),
            rgba(248,250,252,0.96)
        );
    box-shadow:
        inset 0 1px 0 rgba(255,255,255,0.6),
        0 8px 18px rgba(244,197,66,0.10);
}

.player-list-avatar {
    width: 38px;
    height: 38px;
    border-radius: 50%;
    object-fit: cover;
    border: 2px solid rgba(244,197,66,0.75);
    flex-shrink: 0;
}

.player-list-main {
    flex: 1;
    min-width: 0;
}

.player-list-name {
    color: #0f172a;
    font-size: 13px;
    font-weight: 900;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
}

.player-list-team {
    color: #64748b;
    font-size: 11px;
    font-weight: 800;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
}

.player-list-points {
    background: rgba(7,17,31,0.96);
    color: #F4C542;
    border-radius: 999px;
    padding: 5px 8px;
    font-size: 11px;
    font-weight: 900;
    white-space: nowrap;
}


/* ============================================================
   4. BOTÓN SELECTOR DEL LISTADO
   Botón pequeño de acción: ver / activo.
   ============================================================ */

.player-select-btn button {
    border-radius: 12px !important;
    min-height: 42px !important;
    font-size: 15px !important;
    font-weight: 900 !important;

    border: 1px solid rgba(244,197,66,0.38) !important;
    background: rgba(255,255,255,0.88) !important;
    color: #07111F !important;

    box-shadow: 0 6px 14px rgba(15,23,42,0.05) !important;
}

.player-select-btn button:hover {
    background: rgba(244,197,66,0.14) !important;
    border-color: rgba(244,197,66,0.45) !important;
    color: #07111F !important;
}

.player-select-btn button:disabled {
    background: rgba(255,255,255,0.88) !important;
    color: #64748b !important;
    border: 1px solid rgba(226,232,240,0.95) !important;
    opacity: 1 !important;
    box-shadow: 0 6px 14px rgba(15,23,42,0.04) !important;
}


/* ============================================================
   5. FICHA DEL JUGADOR SELECCIONADO
   Card principal de perfil.
   ============================================================ */

.player-hero {
    background:
        radial-gradient(
            circle at 50% 0%,
            rgba(244,197,66,0.22),
            rgba(255,255,255,0.00) 42%
        ),
        linear-gradient(
            180deg,
            rgba(248,250,252,0.96),
            rgba(255,255,255,0.96)
        );
    border: 1px solid rgba(226,232,240,0.85);
    border-radius: 16px;
    padding: 18px 14px 14px 14px;
    text-align: center;
}

.player-avatar {
    width: 118px;
    height: 118px;
    object-fit: cover;
    border-radius: 50%;
    border: 5px solid #F4C542;
    box-shadow:
        0 14px 34px rgba(15,23,42,0.18),
        0 0 26px rgba(244,197,66,0.30);
}

.player-name {
    font-family: 'Montserrat', sans-serif;
    font-size: 24px;
    font-weight: 900;
    color: #0f172a;
    margin-top: 13px;
    line-height: 1.05;
}

.player-team {
    color: #64748b;
    font-size: 13px;
    font-weight: 900;
    margin-top: 4px;
}

.player-rank-pill {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    gap: 6px;

    margin-top: 12px;
    padding: 7px 12px;

    background: rgba(7,17,31,0.96);
    border: 1px solid rgba(244,197,66,0.24);
    border-radius: 999px;

    color: #F8FAFC;
    font-size: 12px;
    font-weight: 900;
}

.player-rank-pill strong {
    color: #F4C542;
}


/* ============================================================
   6. ESTADÍSTICAS DEL JUGADOR
   Puntos, exactos y generales.
   ============================================================ */

.player-stats {
    display: grid;
    grid-template-columns: repeat(3, minmax(0, 1fr));
    gap: 8px;
    margin: 14px 0;
}

.player-stat {
    border: 1px solid rgba(226,232,240,0.9);
    border-radius: 14px;
    padding: 10px 6px;
    background: rgba(248,250,252,0.78);
    text-align: center;
    min-width: 0;
}

.player-stat-icon {
    font-size: 17px;
    line-height: 1;
    margin-bottom: 4px;
}

.player-stat-number {
    font-family: 'Montserrat', sans-serif;
    font-size: 17px;
    font-weight: 900;
    color: #0f172a;
    line-height: 1;
}

.player-stat-label {
    margin-top: 4px;
    font-size: 9px;
    color: #64748b;
    font-weight: 900;
    text-transform: uppercase;
}


/* ============================================================
   7. BIO DEL JUGADOR
   Texto breve dentro de la ficha.
   ============================================================ */

.player-bio {
    margin-top: 12px;
    padding: 12px;
    border-radius: 14px;
    background: rgba(248,250,252,0.82);
    border: 1px solid rgba(226,232,240,0.85);
    color: #334155;
    font-size: 13px;
    font-weight: 700;
    line-height: 1.35;
}


/* ============================================================
   8. MURO DE INSIGNIAS / LOGROS
   Logros globales alternativos al ranking.
   ============================================================ */
.badges-desktop {
    display: block;
    margin-top: 18px;
}

.badges-mobile {
    display: none;
}

.badges-grid {
    display: grid;
    grid-template-columns: repeat(3, minmax(0, 1fr));
    gap: 9px;
}

.badge-card {
    background: rgba(248,250,252,0.88);
    border: 1px solid rgba(226,232,240,0.9);
    border-radius: 14px;
    padding: 10px 7px;
    min-height: 104px;

    text-align: center;

    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
    
    transition: all 0.16s ease;
}

.badge-card:hover {
    transform: translateY(-1px);
    border-color: rgba(244,197,66,0.55);
    box-shadow: 0 8px 18px rgba(244,197,66,0.10);
}

.badge-icon {
    width: 34px;
    height: 34px;
    border-radius: 12px;
    background: rgba(244,197,66,0.16);
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 19px;
    margin-bottom: 7px;
}

.badge-title {
    color: #0f172a;
    font-size: 10px;
    font-weight: 900;
    line-height: 1.1;
    text-transform: uppercase;
    letter-spacing: 0.02em;
    margin-bottom: 5px;
}

.badge-winner {
    color: #07111F;
    font-size: 12px;
    font-weight: 900;
    line-height: 1.1;
    max-width: 100%;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
}

.badge-detail {
    color: #64748b;
    font-size: 9px;
    font-weight: 800;
    margin-top: 3px;
    line-height: 1.15;
}

@media (max-width: 768px) {
    .badges-grid {
        grid-template-columns: repeat(3, minmax(0, 1fr));
        gap: 6px;
    }

    .badges-desktop {
        display: none;
    }

    .badges-mobile {
        display: block;
        margin-top: 18px;
    }

    .badge-card {
        min-height: 92px;
        padding: 8px 5px;
    }

    .badge-icon {
        width: 30px;
        height: 30px;
        font-size: 17px;
        margin-bottom: 5px;
    }

    .badge-title {
        font-size: 8px;
    }

    .badge-winner {
        font-size: 10px;
    }

    .badge-detail {
        font-size: 8px;
    }
}

/* ============================================================
   9. PRONÓSTICOS DEL JUGADOR
   Listado compacto de partidos pronosticados.
   ============================================================ */

.player-preds-scroll {
    max-height: 360px;
    overflow-y: auto;
    padding-right: 4px;
}

.player-pred-row {
    display: grid;
    grid-template-columns: 32px 1fr 58px 1fr;
    align-items: center;
    gap: 6px;

    padding: 7px 6px;
    border-bottom: 1px solid rgba(226,232,240,0.75);
    font-size: 11px;
}
.player-pred-row {
    display: grid;
    grid-template-columns: 32px 1fr 58px 1fr;
    align-items: center;
    gap: 6px;

    padding: 7px 6px;
    border-bottom: 1px solid rgba(226,232,240,0.75);
    font-size: 11px;
}

.player-pred-num {
    color: #94a3b8;
    font-weight: 900;
}

.player-pred-team-left {
    text-align: right;
    color: #334155;
    font-weight: 800;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
}

.player-pred-team-right {
    text-align: left;
    color: #334155;
    font-weight: 800;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
}

.player-pred-score {
    text-align: center;
    background: rgba(7,17,31,0.96);
    color: #F4C542;
    border-radius: 8px;
    padding: 4px 6px;
    font-weight: 900;
}


/* ============================================================
   10. MOBILE
   Ajustes compactos para celulares.
   ============================================================ */

@media (max-width: 768px) {
    .players-title h1 {
        font-size: 28px;
    }

    .players-title p {
        font-size: 12px;
    }

    .players-panel,
    .player-profile-panel,
    .badges-wall-panel,
    .player-preds-panel {
        padding: 13px;
        border-radius: 16px;
    }

    .players-panel-title {
        font-size: 16px;
    }

    .players-panel-subtitle {
        font-size: 11px;
    }

    .player-list-card {
        padding: 8px;
        min-height: 50px;
    }

    .player-list-avatar {
        width: 34px;
        height: 34px;
    }

    .player-list-name {
        font-size: 12px;
    }

    .player-list-team {
        font-size: 10px;
    }

    .player-list-points {
        font-size: 10px;
        padding: 4px 7px;
    }

    .player-select-btn button {
        min-height: 38px !important;
        font-size: 13px !important;
    }

    .player-avatar {
        width: 104px;
        height: 104px;
    }

    .player-name {
        font-size: 21px;
    }

    .badges-grid {
        grid-template-columns: 1fr;
    }
    
    .player-pred-row {
        grid-template-columns: 28px 1fr 52px 1fr;
        font-size: 10px;
    }
}

</style>
""", unsafe_allow_html=True)
    # ============================================================
    # HELPERS
    # ============================================================

    def safe_int(value, default=0):
        try:
            return int(value)
        except Exception:
            return default

    def flag_html(flag_value):
        """
        Devuelve una bandera como HTML si viene como imagen/base64,
        o como texto/emoji si viene en otro formato.
        """
        flag_value = str(flag_value)

        if flag_value.startswith("http") or flag_value.startswith("data:image"):
            return f'<img src="{flag_value}" width="18" style="vertical-align:middle;">'

        return escape(flag_value)

    def get_avatar(row):
        avatar = row.get("AVATAR_URL", "")
        if pd.notna(avatar) and str(avatar).strip() != "":
            return avatar
        return AVATAR_GENERICO
        
    def get_ranking_row(user_row):
        usuario = str(user_row.get("USUARIO", ""))
        nombre = str(user_row.get("NOMBRE", ""))

        if "USUARIO" in df_ranking.columns:
            match = df_ranking[df_ranking["USUARIO"] == usuario]
            if not match.empty:
                return match.iloc[0], match.index[0]

        if "JUGADOR" in df_ranking.columns:
            match = df_ranking[
                df_ranking["JUGADOR"]
                .astype(str)
                .str.contains(nombre, na=False, regex=False)
            ]
            if not match.empty:
                return match.iloc[0], match.index[0]

        return None, None

    def get_nombre_desde_ranking(rank_row):
        if rank_row is None:
            return "-"

        if "JUGADOR" in rank_row:
            return str(rank_row.get("JUGADOR", "-"))

        if "USUARIO" in rank_row:
            usuario = str(rank_row.get("USUARIO", ""))
            match = df_usuarios[df_usuarios["USUARIO"] == usuario]
            if not match.empty:
                return str(match.iloc[0].get("NOMBRE", usuario))

        return "-"

    def calcular_racha_exactos(user_row):
        r_act = 0
        r_max = 0

        u_pro_sorted = (
            df_pro[df_pro["USUARIO"] == user_row["USUARIO"]]
            .sort_values("N_PARTIDO")
        )

        for _, p in u_pro_sorted.iterrows():
            p_ref = df_res[df_res["N_PARTIDO"] == p["N_PARTIDO"]]

            if not p_ref.empty and pd.notna(p_ref.iloc[0].get("R1")):
                pts, exa, gen = calcular_detalle(
                    p_ref.iloc[0]["R1"],
                    p_ref.iloc[0]["R2"],
                    p["P1"],
                    p["P2"]
                )

                if exa == 1:
                    r_act += 1
                    r_max = max(r_max, r_act)
                else:
                    r_act = 0

        return r_max

    def calcular_logros_globales():
        logros = []

        if df_ranking.empty:
            return logros

        # ------------------------------------------------------------
        # Helpers internos
        # ------------------------------------------------------------

        def nombre_usuario_por_usuario(usuario):
            match = df_usuarios[df_usuarios["USUARIO"].astype(str) == str(usuario)]
            if not match.empty:
                return str(match.iloc[0].get("NOMBRE", usuario))
            return str(usuario)

        def nombre_desde_rank(row):
            if row is None:
                return "-"

            if "JUGADOR" in row:
                return str(row.get("JUGADOR", "-"))

            if "USUARIO" in row:
                return nombre_usuario_por_usuario(row.get("USUARIO", "-"))

            return "-"

        def get_bio_len(row):
            bio = str(row.get("DESCRIPCION", "")).strip()

            if bio.lower() == "nan":
                bio = ""

            return len(bio)

        # ------------------------------------------------------------
        # 1. PUNTERO
        # ------------------------------------------------------------

        top_row = df_ranking.iloc[0]
        logros.append({
            "icon": "🏆",
            "title": "Puntero",
            "winner": nombre_desde_rank(top_row),
            "detail": f'{safe_int(top_row.get("PUNTOS", 0))} pts'
        })

        # ------------------------------------------------------------
        # 2. FRANCOTIRADOR — más exactos
        # ------------------------------------------------------------

        if "EXACTOS" in df_ranking.columns:
            exactos_num = pd.to_numeric(df_ranking["EXACTOS"], errors="coerce").fillna(0)
            idx_exactos = exactos_num.idxmax()
            row_exactos = df_ranking.loc[idx_exactos]

            logros.append({
                "icon": "🎯",
                "title": "Francotirador",
                "winner": nombre_desde_rank(row_exactos),
                "detail": f'{safe_int(row_exactos.get("EXACTOS", 0))} exactos'
            })
        else:
            logros.append({
                "icon": "🎯",
                "title": "Francotirador",
                "winner": "-",
                "detail": "Sin datos"
            })

        # ------------------------------------------------------------
        # 3. REGULARIDAD PURA — más generales
        # ------------------------------------------------------------

        if "GENERALES" in df_ranking.columns:
            generales_num = pd.to_numeric(df_ranking["GENERALES"], errors="coerce").fillna(0)
            idx_generales = generales_num.idxmax()
            row_generales = df_ranking.loc[idx_generales]

            logros.append({
                "icon": "✅",
                "title": "Regularidad",
                "winner": nombre_desde_rank(row_generales),
                "detail": f'{safe_int(row_generales.get("GENERALES", 0))} generales'
            })
        else:
            logros.append({
                "icon": "✅",
                "title": "Regularidad",
                "winner": "-",
                "detail": "Sin datos"
            })

        # ------------------------------------------------------------
        # DATOS DE PRONÓSTICOS POR USUARIO
        # ------------------------------------------------------------

        stats_pronosticos = []

        for _, u in df_usuarios.iterrows():
            usuario = str(u.get("USUARIO", ""))
            nombre = str(u.get("NOMBRE", usuario))

            pro_user = df_pro[df_pro["USUARIO"].astype(str) == usuario]

            if pro_user.empty:
                continue

            p1 = pd.to_numeric(pro_user["P1"], errors="coerce").fillna(0)
            p2 = pd.to_numeric(pro_user["P2"], errors="coerce").fillna(0)

            total_partidos = len(pro_user)
            goles_totales = int((p1 + p2).sum())
            promedio_goles = goles_totales / total_partidos if total_partidos > 0 else 0
            empates = int((p1 == p2).sum())

            stats_pronosticos.append({
                "usuario": usuario,
                "nombre": nombre,
                "total_partidos": total_partidos,
                "goles_totales": goles_totales,
                "promedio_goles": promedio_goles,
                "empates": empates
            })

        # ------------------------------------------------------------
        # 4. OPTIMISTA DEL GOL — mayor promedio de goles
        # ------------------------------------------------------------

        if stats_pronosticos:
            optimista = max(
                stats_pronosticos,
                key=lambda x: x["promedio_goles"]
            )

            logros.append({
                "icon": "⚽",
                "title": "Optimista",
                "winner": optimista["nombre"],
                "detail": f'{round(optimista["promedio_goles"], 1)} goles/prom.'
            })
        else:
            logros.append({
                "icon": "⚽",
                "title": "Optimista",
                "winner": "-",
                "detail": "Sin datos"
            })

        # ------------------------------------------------------------
        # 5. BILARDISTA — menor promedio de goles
        # ------------------------------------------------------------

        if stats_pronosticos:
            bilardista = min(
                stats_pronosticos,
                key=lambda x: x["promedio_goles"]
            )

            logros.append({
                "icon": "🧱",
                "title": "Bilardista",
                "winner": bilardista["nombre"],
                "detail": f'{round(bilardista["promedio_goles"], 1)} goles/prom.'
            })
        else:
            logros.append({
                "icon": "🧱",
                "title": "Bilardista",
                "winner": "-",
                "detail": "Sin datos"
            })

        # ------------------------------------------------------------
        # 6. REY DEL EMPATE — más empates pronosticados
        # ------------------------------------------------------------

        if stats_pronosticos:
            rey_empate = max(
                stats_pronosticos,
                key=lambda x: x["empates"]
            )

            logros.append({
                "icon": "🤝",
                "title": "Rey empate",
                "winner": rey_empate["nombre"],
                "detail": f'{rey_empate["empates"]} empates'
            })
        else:
            logros.append({
                "icon": "🤝",
                "title": "Rey empate",
                "winner": "-",
                "detail": "Sin datos"
            })

        # ------------------------------------------------------------
        # 7. EL POETA — bio más larga
        # ------------------------------------------------------------

        df_bios = df_usuarios.copy()
        df_bios["BIO_LEN"] = df_bios.apply(get_bio_len, axis=1)

        if not df_bios.empty and df_bios["BIO_LEN"].max() > 0:
            poeta_row = df_bios.loc[df_bios["BIO_LEN"].idxmax()]

            logros.append({
                "icon": "📝",
                "title": "El poeta",
                "winner": str(poeta_row.get("NOMBRE", "-")),
                "detail": f'{int(poeta_row.get("BIO_LEN", 0))} caracteres'
            })
        else:
            logros.append({
                "icon": "📝",
                "title": "El poeta",
                "winner": "-",
                "detail": "Sin bios"
            })

        # ------------------------------------------------------------
        # 8. EL MISTERIOSO — bio vacía o más corta
        # ------------------------------------------------------------

        if not df_bios.empty:
            misteriosos = df_bios[df_bios["BIO_LEN"] == 0]

            if not misteriosos.empty:
                misterioso_row = misteriosos.iloc[0]
                detalle_misterioso = "Sin bio"
            else:
                misterioso_row = df_bios.loc[df_bios["BIO_LEN"].idxmin()]
                detalle_misterioso = f'{int(misterioso_row.get("BIO_LEN", 0))} caracteres'

            logros.append({
                "icon": "🕵️",
                "title": "Misterioso",
                "winner": str(misterioso_row.get("NOMBRE", "-")),
                "detail": detalle_misterioso
            })
        else:
            logros.append({
                "icon": "🕵️",
                "title": "Misterioso",
                "winner": "-",
                "detail": "Sin datos"
            })

        # ------------------------------------------------------------
        # 9. CALCULADORA — más cercano al promedio general del grupo
        # ------------------------------------------------------------

        if stats_pronosticos:
            promedio_grupo = sum(
                x["promedio_goles"] for x in stats_pronosticos
            ) / len(stats_pronosticos)

            calculadora = min(
                stats_pronosticos,
                key=lambda x: abs(x["promedio_goles"] - promedio_grupo)
            )

            logros.append({
                "icon": "📊",
                "title": "Calculadora",
                "winner": calculadora["nombre"],
                "detail": f'{round(calculadora["promedio_goles"], 1)} vs {round(promedio_grupo, 1)}'
            })
        else:
            logros.append({
                "icon": "📊",
                "title": "Calculadora",
                "winner": "-",
                "detail": "Sin datos"
            })

        return logros

    # ============================================================
    # TÍTULO
    # ============================================================

    st.markdown("""
<div class="players-title">
<h1>👥 Jugadores</h1>
<p>Plantel, logros y pronósticos de la banda del Prode.</p>
</div>
""", unsafe_allow_html=True)

    nombres_usuarios = df_usuarios["NOMBRE"].fillna("Jugador").tolist()

    if "jugador_seleccionado" not in st.session_state:
        st.session_state.jugador_seleccionado = nombres_usuarios[0] if nombres_usuarios else None

    # ============================================================
    # ESTRUCTURA PRINCIPAL
    # Desktop:
    # - Izquierda: lista de jugadores
    # - Derecha: ficha + pronósticos
    #
    # Mobile:
    # - Lista
    # - Ficha
    # - Pronósticos
    # - Insignias
    # ============================================================

    c_lista, c_detalle = st.columns([1.05, 1.15], gap="large")

    # ============================================================
    # COLUMNA IZQUIERDA — LISTA DE JUGADORES
    # ============================================================

    with c_lista:
        with st.container(border=True):

            st.markdown("""
<div class="players-panel-header">
<div class="players-panel-icon">👥</div>
<div>
<div class="players-panel-title">Jugadores</div>
<div class="players-panel-subtitle">Seleccioná a quién querés espiar</div>
</div>
</div>
""", unsafe_allow_html=True)

            nombres_usuarios = df_usuarios["NOMBRE"].fillna("Jugador").tolist()

            if "jugador_seleccionado" not in st.session_state:
                st.session_state.jugador_seleccionado = (
                    nombres_usuarios[0] if nombres_usuarios else None
                )

            with st.container(height=430):
                for _, u in df_usuarios.iterrows():
                    foto_mini = get_avatar(u)

                    rank_row, idx_rank = get_ranking_row(u)
                    pts = safe_int(rank_row.get("PUNTOS", 0)) if rank_row is not None else 0

                    nombre_raw = str(u.get("NOMBRE", "Jugador"))
                    usuario_raw = str(u.get("USUARIO", nombre_raw))
                    nombre = escape(nombre_raw)
                    equipo = escape(str(u.get("EQUIPO FAVORITO", "-")))

                    es_seleccionado = (
                        st.session_state.jugador_seleccionado == nombre_raw
                    )

                    selected_class = "selected" if es_seleccionado else ""

                    c_btn, c_card = st.columns([0.16, 0.84], gap="small")

                    with c_btn:
                        st.markdown(
                            '<div class="player-select-btn">',
                            unsafe_allow_html=True
                        )

                        if es_seleccionado:
                            st.button(
                                "🔍",
                                key=f"jugador_activo_{usuario_raw}",
                                use_container_width=True,
                                disabled=True
                            )
                        else:
                            if st.button(
                                "🔍",
                                key=f"ver_jugador_{usuario_raw}",
                                use_container_width=True
                            ):
                                st.session_state.jugador_seleccionado = nombre_raw
                                st.rerun()

                        st.markdown("</div>", unsafe_allow_html=True)

                    with c_card:
                        st.markdown(
                            f"""
<div class="player-select-row">
<div class="player-list-card {selected_class}">
<img src="{foto_mini}" class="player-list-avatar">
<div class="player-list-main">
<div class="player-list-name">{nombre}</div>
<div class="player-list-team">⚽ {equipo}</div>
</div>
<div class="player-list-points">{pts} pts</div>
</div>
</div>
""",
                            unsafe_allow_html=True
                        )

            user_sel_query = df_usuarios[
                df_usuarios["NOMBRE"] == st.session_state.jugador_seleccionado
            ]

            user_sel = user_sel_query.iloc[0] if not user_sel_query.empty else None

    # ============================================================
    # COLUMNA DERECHA — PERFIL + PRONÓSTICOS DEL JUGADOR
    # ============================================================

    with c_detalle:
        if user_sel is None:
            st.warning("Seleccioná un jugador para ver su perfil.")
            return

        datos_vivos, idx_real = get_ranking_row(user_sel)

        foto_perfil = get_avatar(user_sel)
        nombre = escape(str(user_sel.get("NOMBRE", "Jugador")))
        usuario = escape(str(user_sel.get("USUARIO", "")))
        equipo = escape(str(user_sel.get("EQUIPO FAVORITO", "-")))
        bio = escape(str(user_sel.get("DESCRIPCION", "")))

        if bio.strip() == "" or bio.strip().lower() == "nan":
            bio = "Sin bio cargada todavía."

        pts = safe_int(datos_vivos.get("PUNTOS", 0)) if datos_vivos is not None else 0
        exactos = safe_int(datos_vivos.get("EXACTOS", 0)) if datos_vivos is not None else 0
        generales = safe_int(datos_vivos.get("GENERALES", 0)) if datos_vivos is not None else 0

        try:
            posicion = int(idx_real)
        except Exception:
            posicion = "-"

        # ------------------------------------------------------------
        # FICHA DEL JUGADOR
        # ------------------------------------------------------------

        st.markdown(
            f"""
<div class="player-profile-panel">

<div class="players-panel-header">
<div class="players-panel-icon">👤</div>
<div>
<div class="players-panel-title">Ficha del jugador</div>
<div class="players-panel-subtitle">Resumen del seleccionado</div>
</div>
</div>

<div class="player-hero">
<img src="{foto_perfil}" class="player-avatar">
<div class="player-name">{nombre}</div>
<div class="player-team">@{usuario} · {equipo}</div>

<div class="player-rank-pill">
<span>📊 Posición actual</span>
<strong>{posicion}°</strong>
</div>
</div>

<div class="player-stats">
<div class="player-stat">
<div class="player-stat-icon">🏆</div>
<div class="player-stat-number">{pts}</div>
<div class="player-stat-label">Puntos</div>
</div>

<div class="player-stat">
<div class="player-stat-icon">🎯</div>
<div class="player-stat-number">{exactos}</div>
<div class="player-stat-label">Exactos</div>
</div>

<div class="player-stat">
<div class="player-stat-icon">✅</div>
<div class="player-stat-number">{generales}</div>
<div class="player-stat-label">Generales</div>
</div>
</div>

<div class="player-bio">
<strong>Bio:</strong> {bio}
</div>
</div>
""",
            unsafe_allow_html=True
        )

        # ------------------------------------------------------------
        # PRONÓSTICOS DEL JUGADOR
        # ------------------------------------------------------------

        pro_user_sel = df_pro[df_pro["USUARIO"] == user_sel["USUARIO"]]

        if pro_user_sel.empty:
            rows_html = """
<div class="player-bio">
Sin pronósticos cargados todavía.
</div>
"""
        else:
            rows = []

            for _, p in pro_user_sel.sort_values("N_PARTIDO").iterrows():
                p_match = df_res[df_res["N_PARTIDO"] == p["N_PARTIDO"]]

                if not p_match.empty:
                    p_inf = p_match.iloc[0]

                    f1 = get_flag_img_cached(p_inf["Equipo_1"])
                    f2 = get_flag_img_cached(p_inf["Equipo_2"])

                    i1 = flag_html(f1)
                    i2 = flag_html(f2)

                    rows.append(
                        f"""
<div class="player-pred-row">
<div class="player-pred-num">{int(p["N_PARTIDO"])}</div>
<div class="player-pred-team-left">{escape(str(p_inf["Equipo_1"]))} {i1}</div>
<div class="player-pred-score">{int(p["P1"])} - {int(p["P2"])}</div>
<div class="player-pred-team-right">{i2} {escape(str(p_inf["Equipo_2"]))}</div>
</div>
"""
                    )

            rows_html = "\n".join(rows)

        st.markdown(
            f"""
<div class="player-preds-panel">

<div class="players-panel-header">
<div class="players-panel-icon">🗳️</div>
<div>
<div class="players-panel-title">Pronósticos</div>
<div class="players-panel-subtitle">Predicciones de {nombre}</div>
</div>
</div>

<div class="player-preds-scroll">
{rows_html}
</div>

</div>
""",
            unsafe_allow_html=True
        )

    # ============================================================
    # BLOQUE INFERIOR — MURO DE INSIGNIAS
    # En desktop queda debajo de la lista, a la izquierda.
    # En mobile queda después de perfil y pronósticos.
    # ============================================================

    c_badges, c_empty = st.columns([1.05, 1.15], gap="large")

    with c_badges:
        logros = calcular_logros_globales()

        badges_html = ""

        for logro in logros:
            badges_html += f"""
<div class="badge-card">
<div class="badge-icon">{logro["icon"]}</div>
<div class="badge-title">{escape(str(logro["title"]))}</div>
<div class="badge-winner">{escape(str(logro["winner"]))}</div>
<div class="badge-detail">{escape(str(logro["detail"]))}</div>
</div>
"""

        st.markdown(
            f"""
<div class="badges-wall-panel">

<div class="players-panel-header">
<div class="players-panel-icon">🏅</div>
<div>
<div class="players-panel-title">Muro de Insignias</div>
<div class="players-panel-subtitle">Logros alternativos del Prode</div>
</div>
</div>

<div class="badges-grid">
{badges_html}
</div>

</div>
""",
            unsafe_allow_html=True
        )

    with c_empty:
        st.empty()
