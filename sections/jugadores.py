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

.players-panel,
.player-profile-panel {
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
}

.players-panel-title {
    font-family: 'Montserrat', sans-serif;
    font-size: 18px;
    font-weight: 900;
    color: #0f172a;
}

.player-list-card {
    background: rgba(248,250,252,0.92);
    border: 1px solid rgba(226,232,240,0.9);
    border-radius: 14px;
    padding: 10px;
    margin-bottom: 8px;

    display: flex;
    align-items: center;
    gap: 10px;
}

.player-list-avatar {
    width: 42px;
    height: 42px;
    border-radius: 50%;
    object-fit: cover;
    border: 2px solid rgba(244,197,66,0.75);
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

.player-badges-box {
    background: rgba(248,250,252,0.82);
    border: 1px solid rgba(226,232,240,0.85);
    border-radius: 15px;
    padding: 12px;
    margin-top: 12px;
}

.player-badges-title {
    color: #64748b;
    font-size: 10px;
    font-weight: 900;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    margin-bottom: 8px;
}

.player-badges-grid {
    display: flex;
    justify-content: center;
    flex-wrap: wrap;
    gap: 10px;
}

.player-badge {
    font-size: 24px;
}

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

.player-pred-title {
    margin-top: 18px;
    margin-bottom: 10px;
    color: #0f172a;
    font-size: 14px;
    font-weight: 900;
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

@media (max-width: 768px) {
    .players-title h1 {
        font-size: 28px;
    }

    .player-stats {
        grid-template-columns: repeat(3, minmax(0, 1fr));
    }

    .player-avatar {
        width: 104px;
        height: 104px;
    }

    .player-name {
        font-size: 21px;
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
                df_ranking["JUGADOR"].astype(str).str.contains(nombre, na=False, regex=False)
            ]
            if not match.empty:
                return match.iloc[0], match.index[0]

        return None, None

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

    def calcular_badges(user_row, datos_vivos, idx_real):
        css = {
            k: "filter: grayscale(100%); opacity: 0.18;"
            for k in ["puntero", "master", "mentalista", "lento", "onfire", "fundador"]
        }

        if datos_vivos is None:
            return css

        if "Nº" in datos_vivos and "👑" in str(datos_vivos["Nº"]):
            css["puntero"] = ""

        if int(datos_vivos.get("EXACTOS", 0)) >= 5:
            css["master"] = ""

        if (
            "GENERALES" in df_ranking.columns
            and int(datos_vivos.get("GENERALES", 0)) == int(df_ranking["GENERALES"].max())
            and int(df_ranking["GENERALES"].max()) > 0
        ):
            css["mentalista"] = ""

        if len(df_ranking) > 2 and idx_real == (len(df_ranking) - 1):
            css["lento"] = ""

        try:
            if int(user_row.get("ID", 999)) <= 3:
                css["fundador"] = ""
        except:
            pass

        r_max = calcular_racha_exactos(user_row)
        if r_max >= 3:
            css["onfire"] = ""

        return css

    def safe_int(value, default=0):
        try:
            return int(value)
        except:
            return default

    # ============================================================
    # TÍTULO
    # ============================================================

    st.markdown("""
<div class="players-title">
<h1>👥 Jugadores</h1>
<p>Conocé a la banda que compite por la gloria del Prode.</p>
</div>
""", unsafe_allow_html=True)

    c_lista, c_perfil = st.columns([1.1, 1], gap="large")

    # ============================================================
    # COLUMNA IZQUIERDA — LISTA
    # ============================================================

    with c_lista:
        st.markdown("""
<div class="players-panel">
<div class="players-panel-header">
<div class="players-panel-icon">👥</div>
<div class="players-panel-title">Lista de Participantes</div>
</div>
</div>
""", unsafe_allow_html=True)

        nombres_usuarios = df_usuarios["NOMBRE"].fillna("Jugador").tolist()

        nombre_elegido = st.selectbox(
            "Seleccioná un jugador:",
            nombres_usuarios,
            label_visibility="collapsed"
        )

        user_sel_query = df_usuarios[df_usuarios["NOMBRE"] == nombre_elegido]
        user_sel = user_sel_query.iloc[0] if not user_sel_query.empty else None

        with st.container(height=520):
            for _, u in df_usuarios.iterrows():
                foto_mini = get_avatar(u)

                rank_row, idx_rank = get_ranking_row(u)
                pts = safe_int(rank_row.get("PUNTOS", 0)) if rank_row is not None else 0

                nombre = escape(str(u.get("NOMBRE", "Jugador")))
                equipo = escape(str(u.get("EQUIPO FAVORITO", "-")))

                st.markdown(
                    f"""
<div class="player-list-card">
<img src="{foto_mini}" class="player-list-avatar">
<div class="player-list-main">
<div class="player-list-name">{nombre}</div>
<div class="player-list-team">⚽ {equipo}</div>
</div>
<div class="player-list-points">{pts} pts</div>
</div>
""",
                    unsafe_allow_html=True
                )

    # ============================================================
    # COLUMNA DERECHA — PERFIL SELECCIONADO
    # ============================================================

    with c_perfil:
        st.markdown("""
<div class="player-profile-panel">
<div class="players-panel-header">
<div class="players-panel-icon">👤</div>
<div class="players-panel-title">Perfil Seleccionado</div>
</div>
</div>
""", unsafe_allow_html=True)

        if user_sel is None:
            st.warning("Seleccioná un jugador para ver su perfil.")
            return

        datos_vivos, idx_real = get_ranking_row(user_sel)

        if datos_vivos is None:
            st.warning("El jugador no tiene puntos suficientes para mostrar rendimiento.")
            return

        css_badges = calcular_badges(user_sel, datos_vivos, idx_real)

        foto_perfil = get_avatar(user_sel)
        nombre = escape(str(user_sel.get("NOMBRE", "Jugador")))
        usuario = escape(str(user_sel.get("USUARIO", "")))
        equipo = escape(str(user_sel.get("EQUIPO FAVORITO", "-")))
        bio = escape(str(user_sel.get("DESCRIPCION", "")))

        if bio.strip() == "" or bio.strip().lower() == "nan":
            bio = "Sin bio cargada todavía."

        pts = safe_int(datos_vivos.get("PUNTOS", 0))
        exactos = safe_int(datos_vivos.get("EXACTOS", 0))
        generales = safe_int(datos_vivos.get("GENERALES", 0))

        try:
            posicion = int(idx_real)
        except:
            posicion = "-"

        st.markdown(
            f"""
<div class="player-profile-panel">
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

<div class="player-badges-box">
<div class="player-badges-title">Insignias</div>
<div class="player-badges-grid">
<span title="Puntero" class="player-badge" style="{css_badges['puntero']}">🏆</span>
<span title="Master Exactos" class="player-badge" style="{css_badges['master']}">🎯</span>
<span title="Mentalista" class="player-badge" style="{css_badges['mentalista']}">🧙‍♂️</span>
<span title="Fundador" class="player-badge" style="{css_badges['fundador']}">🏅</span>
<span title="On Fire" class="player-badge" style="{css_badges['onfire']}">🔥</span>
<span title="El más lento" class="player-badge" style="{css_badges['lento']}">🐌</span>
</div>
</div>

<div class="player-bio">
<strong>Bio:</strong> {bio}
</div>
</div>
""",
            unsafe_allow_html=True
        )

        # ============================================================
        # PREDICCIONES DEL USUARIO
        # ============================================================

        st.markdown(
            f'<div class="player-pred-title">🗳️ Pronósticos de {nombre}</div>',
            unsafe_allow_html=True
        )

        pro_user_sel = df_pro[df_pro["USUARIO"] == user_sel["USUARIO"]]

        if pro_user_sel.empty:
            st.warning("Sin pronósticos.")
        else:
            with st.container(height=360):
                for _, p in pro_user_sel.sort_values("N_PARTIDO").iterrows():
                    p_match = df_res[df_res["N_PARTIDO"] == p["N_PARTIDO"]]

                    if not p_match.empty:
                        p_inf = p_match.iloc[0]

                        f1 = get_flag_img_cached(p_inf["Equipo_1"])
                        f2 = get_flag_img_cached(p_inf["Equipo_2"])

                        i1 = f'<img src="{f1}" width="18">' if "data" in str(f1) else str(f1)
                        i2 = f'<img src="{f2}" width="18">' if "data" in str(f2) else str(f2)

                        st.markdown(
                            f"""
<div class="player-pred-row">
<div class="player-pred-num">{int(p["N_PARTIDO"])}</div>
<div class="player-pred-team-left">{escape(str(p_inf["Equipo_1"]))} {i1}</div>
<div class="player-pred-score">{int(p["P1"])} - {int(p["P2"])}</div>
<div class="player-pred-team-right">{i2} {escape(str(p_inf["Equipo_2"]))}</div>
</div>
""",
                            unsafe_allow_html=True
                        )
