#------------------------------------------------MENU INICIO-----------------------------------------------
import streamlit as st
import pandas as pd
import textwrap

from html import escape

from styles_config import (
    AVATAR_GENERICO,
    HEADER_BACKGROUND
)

def render_inicio(
    df_ranking,
    df_usuarios,
    df_pro,
    df_res,
    mapa_banderas,
    df_foro=None,
    df_noticias=None
):
    """
    Renderiza la pantalla principal de Inicio.
    Incluye:
    - Hero principal
    - Ranking general
    - Resultados de la fecha
    - Evolución de puntos
    - Foro / chat
    """

    top_3 = df_ranking.head(3)
    
    def get_pod_data(index):
        if len(top_3) > index:
            row = top_3.iloc[index]
            u_info = df_usuarios[df_usuarios['USUARIO'] == row['USUARIO']]
            foto = u_info['AVATAR_URL'].values[0] if not u_info.empty and pd.notna(u_info['AVATAR_URL'].values[0]) else AVATAR_GENERICO
            nombre = str(row['JUGADOR']).split(' ')[0]
            return nombre, int(row['PUNTOS']), foto
        return "-", 0, AVATAR_GENERICO

    n1, p1, f1 = get_pod_data(0)
    n2, p2, f2 = get_pod_data(1)
    n3, p3, f3 = get_pod_data(2)

    try:
        row_user = df_ranking[df_ranking['USUARIO'] == st.session_state['user_data']['USUARIO']]
        pos_display = row_user.index[0]
        pts_usr = int(row_user['PUNTOS'].values[0])
        dif = int(p1 - pts_usr)
        dif_ref = "¡Eres el Líder! 🏆" if dif <= 0 else f"↑ a {dif} Pts. del Líder"
    except:
        pos_display, pts_usr, dif_ref = "-", 0, "..."
      
    # --- 2. HTML Y CSS COMPACTO ---
    
    html_hero = textwrap.dedent("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;700&family=Montserrat:wght@800;900&display=swap');
    
    .hero-container {
        font-family: 'Inter', sans-serif;
        background-image:
            linear-gradient(
                90deg,
                rgba(0,0,0,0.92) 0%,
                rgba(0,0,0,0.72) 46%,
                rgba(0,0,0,0.36) 100%
            ),
            url('__HEADER_BACKGROUND__');
        background-size: cover;
        background-position: center;
        border-radius: 18px;
        color: white;
        overflow: hidden;
        border: 1px solid rgba(255,255,255,0.10);
        box-shadow: 0 18px 45px rgba(15,23,42,0.22);
        margin-bottom: 20px;
    }
    
    .header-top {
        text-align: center;
        padding: 18px 20px 10px 20px;
    }
    
    .title-main {
        font-family: 'Montserrat', sans-serif;
        font-size: 34px;
        font-weight: 900;
        text-transform: uppercase;
        margin: 0;
        line-height: 1.05;
        letter-spacing: 1.5px;
        color: #F8FAFC;
        text-shadow:
            0 3px 12px rgba(0,0,0,0.65),
            0 0 18px rgba(255,255,255,0.08);
    }
    
    .title-sub {
        font-size: 11px;
        opacity: 0.48;
        letter-spacing: 2px;
        margin-top: 8px;
        text-transform: uppercase;
        font-weight: 700;
    }
    
    .divider-h {
        height: 1px;
        background: linear-gradient(
            90deg,
            transparent,
            rgba(255,255,255,0.18),
            transparent
        );
        margin: 12px 60px 0 60px;
    }
    
    .content-bottom {
        display: grid;
        grid-template-columns: 22% 78%;
        align-items: center;
        min-height: 190px;
        padding: 8px 24px 24px 24px;
    }
    
    .pos-section {
        min-height: 138px;
        display: flex;
        flex-direction: column;
        justify-content: center;
    
        background: linear-gradient(
            135deg,
            rgba(7, 17, 31, 0.78),
            rgba(7, 17, 31, 0.38)
        );
    
        border: 1px solid rgba(255,255,255,0.14);
        border-radius: 18px;
        padding: 20px 22px;
    
        box-shadow:
            0 0 28px rgba(255,255,255,0.08),
            0 12px 26px rgba(0,0,0,0.28),
            inset 0 1px 0 rgba(255,255,255,0.08);
    
        backdrop-filter: blur(4px);
    }
    
    .label-pos {
        font-size: 10px;
        opacity: 0.58;
        font-weight: 800;
        text-transform: uppercase;
        letter-spacing: 0.04em;
        margin-bottom: 5px;
    }
    
    .val-pos {
        font-family: 'Montserrat', sans-serif;
        font-size: 56px;
        font-weight: 900;
        line-height: 0.9;
        margin: 4px 0 10px 0;
        color: #F8FAFC;
        letter-spacing: -2px;
        text-shadow:
            0 0 18px rgba(255,255,255,0.34),
            0 0 32px rgba(244,197,66,0.22),
            0 4px 12px rgba(0,0,0,0.55);
    }
    
    .pts-box {
        font-family: 'Montserrat', sans-serif;
        font-size: 20px;
        font-weight: 900;
        line-height: 1;
    }
    
    .pts-box span {
        font-size: 12px;
        opacity: 0.52;
        font-weight: 800;
    }
    
    .msg-status {
        font-size: 11px;
        margin-top: 8px;
        opacity: 0.78;
        font-weight: 700;
    }
    
    .podium-section {
        display: flex;
        justify-content: center;
        align-items: flex-end;
        gap: 30px;
        padding: 12px 10px 4px 10px;
    }
    
    .pod-item {
        text-align: center;
        position: relative;
        width: 128px;
        display: flex;
        flex-direction: column;
        align-items: center;
    }
    
    .pod-first {
        transform: translateY(-20px);
    }
    
    .av-wrap {
        position: relative;
        display: inline-block;
    }
    
    .av-img {
        border-radius: 50%;
        object-fit: cover;
        box-sizing: border-box;
        background: #07111F;
    
        border: 4px solid rgba(255,255,255,0.35);
    
        box-shadow:
            0 10px 28px rgba(0,0,0,0.55),
            0 0 0 1px rgba(255,255,255,0.08);
    }
    
    .av-first {
        border: 5px solid #F4C542 !important;
        box-shadow:
            0 12px 34px rgba(0,0,0,0.62),
            0 0 22px rgba(244,197,66,0.40),
            0 0 0 1px rgba(255,255,255,0.18);
    }
    
    .av-second {
        border: 4px solid #C0C0C0 !important;
        box-shadow:
            0 10px 28px rgba(0,0,0,0.55),
            0 0 12px rgba(192,192,192,0.25);
    }
    
    .av-third {
        border: 4px solid #CD7F32 !important;
        box-shadow:
            0 10px 28px rgba(0,0,0,0.55),
            0 0 12px rgba(205,127,50,0.25);
    }
    
    .b-rank {
        position: absolute;
        top: 2px;
        right: 2px;
    
        width: 22px;
        height: 22px;
        border-radius: 50%;
    
        display: flex;
        align-items: center;
        justify-content: center;
    
        font-size: 10px;
        font-weight: 900;
        z-index: 10;
    
        box-shadow:
            0 4px 10px rgba(0,0,0,0.35),
            inset 0 1px 0 rgba(255,255,255,0.25);
    }
    
    .b-gold {
        background: linear-gradient(135deg, #FFD700, #F4A900);
        color: #111827;
    }
    
    .b-silver {
        background: linear-gradient(135deg, #E5E7EB, #9CA3AF);
        color: #111827;
    }
    
    .b-bronze {
        background: linear-gradient(135deg, #CD7F32, #9A5A22);
        color: white;
    }
    
    .pod-name {
        font-weight: 900;
        font-size: 13px;
        margin-top: 9px;
        text-transform: uppercase;
        color: #F8FAFC;
        text-shadow: 0 2px 8px rgba(0,0,0,0.65);
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
        max-width: 120px;
    }
    
    .pod-pts {
        font-size: 11px;
        opacity: 0.66;
        font-weight: 800;
        margin-top: 2px;
    }
    
    .pod-first .pod-name {
        color: #F4C542;
    }
    
    .pod-first .pod-pts {
        color: #F4C542;
        opacity: 0.9;
    }
    
    @media (max-width: 768px) {
        .hero-container {
            border-radius: 16px;
        }
    
        .header-top {
            padding: 18px 14px 8px 14px;
        }
    
        .title-main {
            font-size: 26px;
            line-height: 1.1;
        }
    
        .title-sub {
            font-size: 9px;
            letter-spacing: 1.2px;
        }
    
        .divider-h {
            margin: 10px 28px 0 28px;
        }
    
        .content-bottom {
            display: flex;
            flex-direction: column;
            padding: 12px 14px 20px 14px;
            gap: 18px;
        }
    
        .pos-section {
            width: 100%;
            min-height: auto;
            padding: 18px;
            text-align: center;
            box-sizing: border-box;
        }
    
        .val-pos {
            font-size: 48px;
        }
    
        .podium-section {
            width: 100%;
            gap: 8px;
            padding: 6px 0 0 0;
            justify-content: space-between;
        }
    
        .pod-item {
            width: 33%;
        }
    
        .pod-first {
            transform: translateY(-10px);
        }
    
        .pod-name {
            font-size: 11px;
            max-width: 100%;
        }
    
        .pod-pts {
            font-size: 10px;
        }
    }
    </style>

<div class="hero-container">

<div class="header-top">
    <h1 class="title-main">🏆 PRODE MUNDIAL 2026</h1>
    <div class="title-sub">La gloria está en tus predicciones</div>
    <div class="divider-h"></div>
</div>

<div class="content-bottom">

<div class="pos-section">
    <div class="label-pos">Tu posición</div>
    <div class="val-pos">__POS_DISPLAY__°</div>
    <div class="pts-box">__PTS_USR__ <span>PTS.</span></div>
    <div class="msg-status">__DIF_REF__</div>
</div>

<div class="podium-section">

<div class="pod-item">
    <div class="av-wrap">
        <div class="b-rank b-silver">2</div>
        <img src="__F2__" class="av-img av-second" style="width:82px; height:82px;">
    </div>
    <div class="pod-name">__N2__</div>
    <div class="pod-pts">__P2__ PTS.</div>
</div>

<div class="pod-item pod-first">
<div class="av-wrap">
    <div class="b-rank b-gold">1</div>
    <img src="__F1__" class="av-img av-first" style="width:112px; height:112px;">
</div>
<div class="pod-name">__N1__</div>
<div class="pod-pts">__P1__ PTS.</div>
</div>

<div class="pod-item">
<div class="av-wrap">
    <div class="b-rank b-bronze">3</div>
    <img src="__F3__" class="av-img av-third" style="width:82px; height:82px;">
</div>
<div class="pod-name">__N3__</div>
<div class="pod-pts">__P3__ PTS.</div>
</div>

</div>

</div>

</div>
    """).strip()
    
    html_hero = (
        html_hero
        .replace("__HEADER_BACKGROUND__", str(HEADER_BACKGROUND))
        .replace("__POS_DISPLAY__", str(pos_display))
        .replace("__PTS_USR__", str(pts_usr))
        .replace("__DIF_REF__", str(dif_ref))
        .replace("__F1__", str(f1))
        .replace("__F2__", str(f2))
        .replace("__F3__", str(f3))
        .replace("__N1__", str(n1))
        .replace("__N2__", str(n2))
        .replace("__N3__", str(n3))
        .replace("__P1__", str(p1))
        .replace("__P2__", str(p2))
        .replace("__P3__", str(p3))
    )
    
    st.markdown(html_hero, unsafe_allow_html=True)
    
    # =============================================================================
    # REFUERZO VISUAL: COHERENCIA CON EL HEADER (Basado en image_58b775.png)
    # =============================================================================

    st.markdown(f"""
<style>
    /* Títulos de sección: Menos 'estridencia', más elegancia */
    .dash-title {{
        font-family: 'Inter', -apple-system, sans-serif;
        font-size: 1.35rem; /* Aumentamos tamaño para jerarquía */
        font-weight: 800;
        color: #0f172a; /* Azul noche casi negro, muy profesional */
        letter-spacing: -0.025em;
        margin-bottom: 28px; /* Más aire entre el título y el contenido */
        display: flex;
        align-items: center;
        gap: 15px;
        padding: 12px 20px;
        
        /* Solución a las "manchas": fondo sólido sutil o glassmorphism real */
        background: #ffffff; 
        border-radius: 14px;
        
        /* Cambiamos el azul brillante por el azul marino del Prode */
        border-left: 6px solid #1e3a8a; 
        
        /* Sombra muy suave para que "flote" sobre el dibujo de fondo sin ensuciar */
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
    }}


    /* Unificar las tarjetas de score con el mismo radio de borde */
    .score-card {{
        border-radius: 14px !important;
        border: 1px solid #e2e8f0 !important;
    }}
</style>
    """, unsafe_allow_html=True)

    c_izq, c_der = st.columns([1, 1.1], gap="large")

# ------------------ COLUMNA IZQUIERDA: LÍDERES Y TENDENCIAS ------------------
    with c_izq:
        st.markdown("""
        <style>
        .ranking-panel {
            background: rgba(255, 255, 255, 0.94);
            border: 1px solid rgba(226, 232, 240, 0.9);
            border-radius: 18px;
            padding: 14px;
            box-shadow: 0 12px 30px rgba(15, 23, 42, 0.06);
        
            width: 100%;
            box-sizing: border-box;
            overflow: hidden;
        }
        
        .ranking-panel-header {
            display: flex;
            align-items: center;
            gap: 10px;
            padding: 4px 4px 14px 4px;
            margin-bottom: 8px;
            border-bottom: 1px solid rgba(226, 232, 240, 0.75);
        }
        
        .ranking-panel-icon {
            width: 30px;
            height: 30px;
            border-radius: 10px;
        
            display: flex;
            align-items: center;
            justify-content: center;
        
            background: rgba(244, 197, 66, 0.16);
            color: #0f172a;
            font-size: 16px;
        
            flex-shrink: 0;
        }
        
        .ranking-panel-title {
            font-family: 'Montserrat', sans-serif;
            font-size: 17px;
            font-weight: 900;
            color: #0f172a;
            text-transform: uppercase;
            letter-spacing: 0.01em;
        }
        
        /* ============================================================
           SCROLL VERTICAL REAL
           ============================================================ */
        
        .ranking-scroll {
            display: block !important;
        
            width: 100% !important;
            height: 315px;
        
            overflow-y: auto !important;
            overflow-x: hidden !important;
        
            padding-right: 6px;
            box-sizing: border-box;
        
            white-space: normal !important;
        }
        
        .ranking-scroll::-webkit-scrollbar {
            width: 6px;
        }
        
        .ranking-scroll::-webkit-scrollbar-track {
            background: rgba(226, 232, 240, 0.55);
            border-radius: 999px;
        }
        
        .ranking-scroll::-webkit-scrollbar-thumb {
            background: rgba(15, 23, 42, 0.22);
            border-radius: 999px;
        }
        
        /* ============================================================
           FILAS DEL RANKING
           ============================================================ */
        
        .ranking-row {
            width: 100% !important;
            box-sizing: border-box !important;
        
            display: grid !important;
            grid-template-columns: 42px minmax(0, 1fr) 72px !important;
            align-items: center !important;
            gap: 12px !important;
        
            padding: 11px 12px;
            margin-bottom: 8px;
        
            border-radius: 14px;
            background: rgba(248, 250, 252, 0.92);
            border: 1px solid rgba(226, 232, 240, 0.85);
        
            transition: all 0.18s ease;
        }
        
        .ranking-row:last-child {
            margin-bottom: 0;
        }
        
        .ranking-row:hover {
            transform: translateY(-1px);
            box-shadow: 0 8px 18px rgba(15, 23, 42, 0.08);
        }
        
        .ranking-row.me {
            background:
                linear-gradient(
                    90deg,
                    rgba(244, 197, 66, 0.20),
                    rgba(255,255,255,0.96)
                );
        
            border: 1px solid rgba(244, 197, 66, 0.68);
            box-shadow: 0 10px 25px rgba(244, 197, 66, 0.13);
        }
        
        /* ============================================================
           POSICIÓN
           ============================================================ */
        
        .rank-pos {
            width: 32px;
            height: 32px;
            border-radius: 50%;
        
            display: flex;
            align-items: center;
            justify-content: center;
        
            font-family: 'Montserrat', sans-serif;
            font-size: 13px;
            font-weight: 900;
        
            color: #0f172a;
            background: #e5e7eb;
        
            flex-shrink: 0;
        }
        
        .rank-pos.gold {
            background: linear-gradient(135deg, #FFD700, #F4A900);
            color: #111827;
        }
        
        .rank-pos.silver {
            background: linear-gradient(135deg, #d1d5db, #9ca3af);
            color: #111827;
        }
        
        .rank-pos.bronze {
            background: linear-gradient(135deg, #CD7F32, #9A5A22);
            color: white;
        }
        
        /* ============================================================
           INFO DEL JUGADOR
           ============================================================ */
        
        .player-info {
            min-width: 0 !important;
            width: 100% !important;
            box-sizing: border-box;
        }
        
        .player-name {
            font-family: 'Inter', sans-serif;
            font-size: 13px;
            font-weight: 900;
            color: #0f172a;
        
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
        }
        
        .player-sub {
            margin-top: 3px;
        
            font-size: 10px;
            font-weight: 700;
            color: #64748b;
        
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
        }
        
        .player-sub strong {
            color: #0f172a;
            font-weight: 900;
        }
        
        /* ============================================================
           INSIGNIAS MINI
           ============================================================ */
        
        .ranking-badges-mini {
            display: flex !important;
            flex-direction: row !important;
            flex-wrap: wrap !important;
            align-items: center !important;
        
            gap: 4px !important;
            margin-top: 5px !important;
            min-height: 20px;
        
            width: 100%;
            overflow: hidden;
        }
        
        .ranking-badge-mini {
            width: 19px !important;
            height: 19px !important;
        
            object-fit: contain !important;
            display: block !important;
            flex: 0 0 auto !important;
        
            filter: drop-shadow(0 2px 4px rgba(15,23,42,0.16));
        }
        
        .ranking-row.me .ranking-badge-mini {
            width: 21px !important;
            height: 21px !important;
        }
        
        /* ============================================================
           PUNTOS
           ============================================================ */
        
        .rank-points {
            text-align: right;
            min-width: 0;
        }
        
        .points-main {
            font-family: 'Montserrat', sans-serif;
            font-size: 19px;
            font-weight: 900;
            color: #0f172a;
            line-height: 1;
        }
        
        .points-label {
            font-size: 9px;
            font-weight: 800;
            color: #94a3b8;
            text-transform: uppercase;
            margin-top: 2px;
        }
        
        .ranking-row.me .points-main {
            color: #0f172a;
        }
        
        /* ============================================================
           MOBILE
           ============================================================ */
        
        @media (max-width: 768px) {
            .ranking-panel {
                padding: 12px;
                border-radius: 16px;
            }
        
            .ranking-panel-title {
                font-size: 15px;
            }
        
            .ranking-scroll {
                height: 315px;
                overflow-y: auto !important;
                overflow-x: hidden !important;
            }
        
            .ranking-row {
                grid-template-columns: 38px minmax(0, 1fr) 56px !important;
                gap: 8px !important;
                padding: 10px;
                border-radius: 13px;
            }
        
            .rank-pos {
                width: 30px;
                height: 30px;
                font-size: 12px;
            }
        
            .player-name {
                font-size: 12px;
            }
        
            .player-sub {
                font-size: 9px;
            }
        
            .ranking-badge-mini {
                width: 17px !important;
                height: 17px !important;
            }
        
            .ranking-row.me .ranking-badge-mini {
                width: 18px !important;
                height: 18px !important;
            }
        
            .points-main {
                font-size: 16px;
            }
        }
        </style>
        """, unsafe_allow_html=True)
        
        from html import escape
        
        def clase_medalla(posicion_num):
            if posicion_num == 1:
                return "gold"
            elif posicion_num == 2:
                return "silver"
            elif posicion_num == 3:
                return "bronze"
            return ""
        
        usuario_actual = st.session_state["user_data"]["USUARIO"]

        BADGE_ASSET_BASE_URL = "https://storage.googleapis.com/foto-prode2026/badges"

        ranking_badge_asset_map = {
            "Puntero": f"{BADGE_ASSET_BASE_URL}/puntero/PUNTERO_MINI_128.png",
            "Sr. Prode": f"{BADGE_ASSET_BASE_URL}/srprode/SRPRODE_MINI_128.png",
            "Siempre Suma": f"{BADGE_ASSET_BASE_URL}/suma/SUMA_MINI_128.png",
            "Optimista del Gol": f"{BADGE_ASSET_BASE_URL}/optimista/OPTIMISTA_MINI_128.png",
            "El Cholo": f"{BADGE_ASSET_BASE_URL}/elcholo/ELCHOLO_MINI_128.png",
            "Rey del Empate": f"{BADGE_ASSET_BASE_URL}/empate/EMPATE_MINI_128.png",
            "El Macaya": f"{BADGE_ASSET_BASE_URL}/macaya/MACAYA_MINI_128.png",
            "El Misterioso": f"{BADGE_ASSET_BASE_URL}/misterioso/MISTERIOSO_MINI_128.png",
            "El Distinto": f"{BADGE_ASSET_BASE_URL}/distinto/DISTINTO_MINI_128.png",
        }
        def build_ranking_badges_html(badges):
            if badges is None:
                return ""
        
            if isinstance(badges, str):
                badges = [badges]
        
            if not isinstance(badges, list):
                return ""
        
            html = ""
        
            for badge in badges:
                badge_name = str(badge).strip()
                badge_url = ranking_badge_asset_map.get(badge_name, "")
        
                if badge_url:
                    html += (
                        f'<img src="{escape(badge_url)}" '
                        f'class="ranking-badge-mini" '
                        f'title="{escape(badge_name)}" '
                        f'alt="{escape(badge_name)}">'
                    )
        
            if html == "":
                return ""
        
            return f'<div class="ranking-badges-mini">{html}</div>'
        
        ranking_html = '<div class="ranking-panel">'
        ranking_html += '<div class="ranking-panel-header">'
        ranking_html += '<div class="ranking-panel-icon">🏆</div>'
        ranking_html += '<div class="ranking-panel-title">Ranking General</div>'
        ranking_html += '</div>'
        ranking_html += '<div class="ranking-scroll">'
        
        for i, row in df_ranking.reset_index(drop=True).iterrows():
            posicion_num = i + 1
        
            pos_label = escape(str(row.get("Nº", posicion_num)))
            jugador = escape(str(row.get("JUGADOR", "Jugador")))
            usuario = str(row.get("USUARIO", ""))
        
            puntos = int(row.get("PUNTOS", 0))
            exactos = int(row.get("EXACTOS", 0))
            generales = int(row.get("GENERALES", 0))
        
            es_usuario_actual = usuario == usuario_actual
        
            clase_usuario = "me" if es_usuario_actual else ""
            medalla = clase_medalla(posicion_num)
        
            subtitulo = "Tu posición actual" if es_usuario_actual else "Participante"
        
            badges_html = build_ranking_badges_html(
                row.get("BADGES", [])
            )
        
            ranking_html += f"""
<div class="ranking-row {clase_usuario}">
<div class="rank-pos {medalla}">{pos_label}</div>

<div class="player-info">
<div class="player-name">{jugador}</div>
<div class="player-sub">{subtitulo} · 🎯 {exactos} · ✅ {generales}</div>
{badges_html}
</div>

<div class="rank-points">
<div class="points-main">{puntos}</div>
<div class="points-label">pts</div>
</div>
</div>
"""

        ranking_html += '</div>'
        ranking_html += '</div>'
        
        st.markdown(ranking_html, unsafe_allow_html=True)
         # ============================================================
        # NOTICIAS Y AVISOS — CARD EDITORIAL
        # Reemplaza Evolución de Puntos en Inicio
        # ============================================================

        st.markdown("""
<style>
.news-home-panel {
    background: rgba(255, 255, 255, 0.94);
    border: 1px solid rgba(226, 232, 240, 0.9);
    border-radius: 18px;
    padding: 14px;
    box-shadow: 0 12px 30px rgba(15, 23, 42, 0.06);
    overflow: hidden;
}

.news-home-header {
    display: flex;
    align-items: center;
    gap: 10px;
    padding: 4px 4px 14px 4px;
    margin-bottom: 8px;
    border-bottom: 1px solid rgba(226, 232, 240, 0.75);
}

.news-home-icon {
    width: 30px;
    height: 30px;
    border-radius: 10px;

    display: flex;
    align-items: center;
    justify-content: center;

    background: rgba(244, 197, 66, 0.16);
    color: #0f172a;
    font-size: 16px;
    flex-shrink: 0;
}

.news-home-title {
    font-family: 'Montserrat', sans-serif;
    font-size: 17px;
    font-weight: 900;
    color: #0f172a;
    text-transform: uppercase;
    letter-spacing: 0.01em;
}

.news-featured-card {
    position: relative;
    overflow: hidden;

    min-height: 150px;

    border-radius: 15px;
    margin-bottom: 10px;

    background:
        linear-gradient(
            90deg,
            rgba(7,17,31,0.92) 0%,
            rgba(7,17,31,0.72) 48%,
            rgba(7,17,31,0.22) 100%
        ),
        var(--news-featured-img);

    background-size: cover;
    background-position: center right;

    border: 1px solid rgba(255,255,255,0.10);

    box-shadow:
        inset 0 1px 0 rgba(255,255,255,0.08),
        0 8px 18px rgba(15,23,42,0.12);
}

.news-featured-content {
    padding: 14px 15px;
    max-width: 72%;
}

.news-tag {
    display: inline-flex;
    align-items: center;
    justify-content: center;

    padding: 4px 8px;
    margin-bottom: 9px;

    border-radius: 999px;

    font-size: 9px;
    font-weight: 900;
    text-transform: uppercase;
    letter-spacing: 0.04em;
}

.news-tag.aviso {
    background: rgba(244,197,66,0.18);
    color: #F4C542;
    border: 1px solid rgba(244,197,66,0.38);
}

.news-tag.mundial {
    background: rgba(34,197,94,0.16);
    color: #86efac;
    border: 1px solid rgba(34,197,94,0.34);
}

.news-tag.prode {
    background: rgba(59,130,246,0.16);
    color: #93c5fd;
    border: 1px solid rgba(59,130,246,0.34);
}

.news-tag.comunidad {
    background: rgba(168,85,247,0.16);
    color: #d8b4fe;
    border: 1px solid rgba(168,85,247,0.34);
}

.news-tag.partido {
    background: rgba(249,115,22,0.16);
    color: #fdba74;
    border: 1px solid rgba(249,115,22,0.34);
}

.news-featured-title {
    font-family: 'Montserrat', sans-serif;
    font-size: 18px;
    font-weight: 900;
    color: #F8FAFC;
    line-height: 1.12;
    margin-bottom: 7px;
    text-shadow: 0 2px 8px rgba(0,0,0,0.65);
}

.news-featured-text {
    color: rgba(248,250,252,0.78);
    font-size: 12px;
    font-weight: 650;
    line-height: 1.32;
    margin-bottom: 9px;
}

.news-date {
    color: rgba(226,232,240,0.52);
    font-size: 10px;
    font-weight: 800;
}

.news-secondary-card {
    display: grid;
    grid-template-columns: minmax(0, 1fr) 78px;
    gap: 10px;
    align-items: center;

    background: rgba(248,250,252,0.92);
    border: 1px solid rgba(226,232,240,0.88);
    border-radius: 14px;

    padding: 10px;
    margin-bottom: 9px;

    box-shadow: 0 6px 14px rgba(15,23,42,0.035);
}

.news-secondary-title {
    font-family: 'Montserrat', sans-serif;
    font-size: 12.5px;
    font-weight: 900;
    color: #0f172a;
    line-height: 1.14;
    margin-bottom: 4px;
}

.news-secondary-text {
    color: #64748b;
    font-size: 10.5px;
    font-weight: 700;
    line-height: 1.28;

    display: -webkit-box;
    -webkit-line-clamp: 2;
    -webkit-box-orient: vertical;
    overflow: hidden;
}



.news-secondary-img {
    width: 78px;
    height: 58px;
    border-radius: 10px;
    object-fit: cover;

    border: 1px solid rgba(226,232,240,0.9);
    box-shadow: 0 4px 10px rgba(15,23,42,0.12);
}

.news-home-footer {
    margin-top: 4px;

    display: flex;
    align-items: center;
    justify-content: space-between;

    border-radius: 13px;
    border: 1px solid rgba(226,232,240,0.88);
    background: rgba(248,250,252,0.86);

    padding: 10px 12px;

    color: #334155;
    font-size: 12px;
    font-weight: 900;
}

.news-empty {
    height: 315px;

    display: flex;
    align-items: center;
    justify-content: center;

    text-align: center;
    color: #94a3b8;

    font-family: 'Inter', sans-serif;
    font-size: 13px;
    font-weight: 800;

    background: rgba(248,250,252,0.74);
    border: 1px solid rgba(226,232,240,0.85);
    border-radius: 15px;
}

@media (max-width: 768px) {
    .news-home-panel {
        padding: 12px;
        border-radius: 16px;
    }

    .news-home-title {
        font-size: 15px;
    }

    .news-featured-card {
        min-height: 145px;
    }

    .news-featured-content {
        max-width: 82%;
    }

    .news-featured-title {
        font-size: 16px;
    }

    .news-featured-text {
        font-size: 11px;
    }

    .news-secondary-card {
        grid-template-columns: minmax(0, 1fr) 66px;
    }

    .news-secondary-img {
        width: 66px;
        height: 50px;
    }
}
</style>
""", unsafe_allow_html=True)

        NEWS_FALLBACK_IMG = "https://storage.googleapis.com/foto-prode2026/Banners/CABEZA%20SECCION%20FINA.png"

        if df_noticias is None or df_noticias.empty:
            noticias_visibles = pd.DataFrame()
        else:
            noticias_visibles = df_noticias.copy()

            columnas_noticias = [
                "ID",
                "FECHA",
                "TIPO",
                "TITULO",
                "TEXTO",
                "AUTOR",
                "VISIBLE",
                "PRIORIDAD",
                "LINK",
                "IMAGEN_URL",
                "FUENTE"
            ]

            for col in columnas_noticias:
                if col not in noticias_visibles.columns:
                    if col == "ID":
                        noticias_visibles[col] = 0
                    elif col == "VISIBLE":
                        noticias_visibles[col] = "TRUE"
                    elif col == "PRIORIDAD":
                        noticias_visibles[col] = 99
                    else:
                        noticias_visibles[col] = ""

            # ------------------------------------------------------------
            # FILTRO DE VISIBILIDAD
            # ------------------------------------------------------------

            noticias_visibles["VISIBLE_CHECK"] = (
                noticias_visibles["VISIBLE"]
                .astype(str)
                .str.strip()
                .str.upper()
            )

            noticias_visibles = noticias_visibles[
                noticias_visibles["VISIBLE_CHECK"].isin(
                    ["TRUE", "1", "1.0", "VERDADERO", "T"]
                )
            ].copy()

            # ------------------------------------------------------------
            # ORDENAMIENTO
            # Prioridad menor arriba.
            # Dentro de la misma prioridad, última publicada primero.
            # ------------------------------------------------------------

            noticias_visibles["PRIORIDAD_NUM"] = pd.to_numeric(
                noticias_visibles["PRIORIDAD"],
                errors="coerce"
            ).fillna(99)

            noticias_visibles["ID_NUM"] = pd.to_numeric(
                noticias_visibles["ID"],
                errors="coerce"
            ).fillna(0)

            noticias_visibles = noticias_visibles.sort_values(
                by=["PRIORIDAD_NUM", "ID_NUM"],
                ascending=[True, False]
            )
        
        news_html = """
<div class="news-home-panel">
<div class="news-home-header">
<div class="news-home-icon">📣</div>
<div class="news-home-title">Noticias y Avisos</div>
</div>
"""

        if noticias_visibles.empty:
            news_html += """
<div class="news-empty">
Todavía no hay noticias visibles.<br>
Cuando haya novedades del Prode o del Mundial aparecerán acá.
</div>
</div>
"""
        else:
            noticias_home = noticias_visibles.head(3).copy()

            noticia_principal = noticias_home.iloc[0]

            tipo_raw = str(noticia_principal.get("TIPO", "Aviso")).strip()
            tipo_class = tipo_raw.lower()
            tipo_class = (
                tipo_class
                .replace("á", "a")
                .replace("é", "e")
                .replace("í", "i")
                .replace("ó", "o")
                .replace("ú", "u")
                .replace(" ", "-")
            )

            titulo = escape(str(noticia_principal.get("TITULO", "")))
            texto = escape(str(noticia_principal.get("TEXTO", "")))
            fecha = escape(str(noticia_principal.get("FECHA", "")))
            link = str(noticia_principal.get("LINK", "")).strip()

            img = str(noticia_principal.get("IMAGEN_URL", "")).strip()
            if img == "" or img.lower() == "nan":
                img = NEWS_FALLBACK_IMG

            card_open = ""
            card_close = ""

            if link and link.lower() != "nan":
                card_open = f'<a href="{escape(link, quote=True)}" target="_blank" style="text-decoration:none;">'
                card_close = "</a>"

            news_html += f"""
{card_open}
<div class="news-featured-card" style="--news-featured-img: url('{escape(img, quote=True)}');">
<div class="news-featured-content">
<div class="news-tag {escape(tipo_class)}">{escape(tipo_raw)}</div>
<div class="news-featured-title">{titulo}</div>
<div class="news-featured-text">{texto}</div>
<div class="news-date">{fecha}</div>
</div>
</div>
{card_close}
"""

            for _, n in noticias_home.iloc[1:3].iterrows():
                tipo_raw = str(n.get("TIPO", "Prode")).strip()
                tipo_class = tipo_raw.lower()
                tipo_class = (
                    tipo_class
                    .replace("á", "a")
                    .replace("é", "e")
                    .replace("í", "i")
                    .replace("ó", "o")
                    .replace("ú", "u")
                    .replace(" ", "-")
                )

                titulo = escape(str(n.get("TITULO", "")))
                texto = escape(str(n.get("TEXTO", "")))
                fecha = escape(str(n.get("FECHA", "")))
                link = str(n.get("LINK", "")).strip()

                img = str(n.get("IMAGEN_URL", "")).strip()
                if img == "" or img.lower() == "nan":
                    img = NEWS_FALLBACK_IMG

                card_open = ""
                card_close = ""

                if link and link.lower() != "nan":
                    card_open = f'<a href="{escape(link, quote=True)}" target="_blank" style="text-decoration:none;">'
                    card_close = "</a>"

                news_html += f"""
{card_open}
<div class="news-secondary-card">
<div>
<div class="news-tag {escape(tipo_class)}">{escape(tipo_raw)}</div>
<div class="news-secondary-title">{titulo}</div>
<div class="news-secondary-text">{texto}</div>
<div class="news-date">{fecha}</div>
</div>
<img src="{escape(img, quote=True)}" class="news-secondary-img">
</div>
{card_close}
"""

            news_html += """
<div class="news-home-footer">
<span>Ver más en Comunidad</span>
<span>›</span>
</div>
</div>
"""

        st.markdown(news_html, unsafe_allow_html=True)       

# ------------------ COLUMNA DERECHA: ACCIÓN Y COMUNIDAD ------------------
    with c_der:
# ============================================================
# RESULTADOS / PARTIDOS VISUALES CON SCROLL
# Reemplaza el bloque actual de Resultados de la Fecha
# ============================================================

# ============================================================
# RESULTADOS DE LA FECHA — CARD INTEGRADA
# ============================================================

        st.markdown("""
        <style>
        .matches-panel {
            background: rgba(255, 255, 255, 0.94);
            border: 1px solid rgba(226, 232, 240, 0.9);
            border-radius: 18px;
            padding: 14px;
            box-shadow: 0 12px 30px rgba(15, 23, 42, 0.06);
        }
        
        .matches-panel-header {
            display: flex;
            align-items: center;
            gap: 10px;
            padding: 4px 4px 14px 4px;
            margin-bottom: 8px;
            border-bottom: 1px solid rgba(226, 232, 240, 0.75);
        }
        
        .matches-panel-icon {
            width: 30px;
            height: 30px;
            border-radius: 10px;
            display: flex;
            align-items: center;
            justify-content: center;
            background: rgba(30, 64, 175, 0.10);
            color: #0f172a;
            font-size: 16px;
        }
        
        .matches-panel-title {
            font-family: 'Montserrat', sans-serif;
            font-size: 17px;
            font-weight: 900;
            color: #0f172a;
            text-transform: uppercase;
            letter-spacing: 0.01em;
        }
        
        .matches-scroll {
            height: 315px;
            overflow-y: auto;
            padding-right: 6px;
        }
        
        .matches-scroll::-webkit-scrollbar {
            width: 6px;
        }
        
        .matches-scroll::-webkit-scrollbar-track {
            background: rgba(226, 232, 240, 0.55);
            border-radius: 999px;
        }
        
        .matches-scroll::-webkit-scrollbar-thumb {
            background: rgba(15, 23, 42, 0.22);
            border-radius: 999px;
        }
        
        .match-card {
            padding: 12px 13px;
            margin-bottom: 9px;
            border-radius: 15px;
            background: rgba(248, 250, 252, 0.92);
            border: 1px solid rgba(226, 232, 240, 0.85);
            transition: all 0.18s ease;
        }
        
        .match-card:hover {
            transform: translateY(-1px);
            box-shadow: 0 8px 18px rgba(15, 23, 42, 0.08);
        }
        
        .match-meta {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 11px;
            font-size: 10px;
            font-weight: 900;
            color: #94a3b8;
            text-transform: uppercase;
            letter-spacing: 0.06em;
        }
        
        .match-body {
            display: grid;
            grid-template-columns: 1fr 72px 1fr;
            align-items: center;
            gap: 12px;
        }
        
        .team-side {
            display: flex;
            align-items: center;
            gap: 8px;
            min-width: 0;
        }
        
        .team-side.left {
            justify-content: flex-end;
            text-align: right;
        }
        
        .team-side.right {
            justify-content: flex-start;
            text-align: left;
        }
        
        .team-name {
            font-family: 'Inter', sans-serif;
            font-size: 13px;
            font-weight: 900;
            color: #0f172a;
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
        }
        
        .flag-img {
            width: 28px;
            height: 20px;
            object-fit: cover;
            border-radius: 4px;
            box-shadow: 0 2px 5px rgba(15, 23, 42, 0.16);
            flex-shrink: 0;
        }
        
        .flag-fallback {
            font-size: 20px;
            flex-shrink: 0;
        }
        
        .score-pill {
            background: #07111F;
            color: #f8fafc;
            border-radius: 10px;
            padding: 7px 8px;
            text-align: center;
            font-family: 'Montserrat', sans-serif;
            font-size: 16px;
            font-weight: 900;
            letter-spacing: 0.08em;
            box-shadow:
                inset 0 1px 0 rgba(255,255,255,0.08),
                0 6px 16px rgba(7,17,31,0.16);
        }
        
        .score-pill.pending {
            background: rgba(7,17,31,0.08);
            color: #64748b;
            border: 1px solid rgba(148, 163, 184, 0.35);
            box-shadow: none;
        }
        
        .matches-empty {
            height: 245px;
            display: flex;
            align-items: center;
            justify-content: center;
            text-align: center;
            color: #94a3b8;
            font-size: 13px;
            font-weight: 800;
        }
        
        @media (max-width: 768px) {
            .matches-panel {
                padding: 12px;
            }
        
            .matches-panel-title {
                font-size: 15px;
            }
        
            .matches-scroll {
                height: 315px;
            }
        
            .match-body {
                grid-template-columns: 1fr 62px 1fr;
                gap: 8px;
            }
        
            .team-name {
                font-size: 12px;
            }
        
            .flag-img {
                width: 24px;
                height: 17px;
            }
        
            .score-pill {
                font-size: 14px;
                padding: 7px 6px;
            }
        
            .match-meta {
                font-size: 9px;
            }
        }
        </style>
        """, unsafe_allow_html=True)
        
        from html import escape
        
        def flag_html(flag_value):
            flag_value = str(flag_value)
        
            if flag_value.startswith("data:image"):
                return f'<img src="{flag_value}" class="flag-img">'
        
            return f'<span class="flag-fallback">{escape(flag_value)}</span>'
        
        
        df_res["VIZ_CHECK"] = df_res["VIZ"].astype(str).str.strip().str.upper()
        
        df_mostrar_partidos = (
            df_res[
                df_res["VIZ_CHECK"].isin(
                    ["TRUE", "1", "1.0", "VERDADERO", "T"]
                )
            ]
            .sort_values("N_PARTIDO", ascending=False)
        )
        
        matches_html = '<div class="matches-panel">'
        matches_html += '<div class="matches-panel-header"><div class="matches-panel-icon">⚽</div><div class="matches-panel-title">Resultados Oficiales</div></div>'
        matches_html += '<div class="matches-scroll">'
        
        if df_mostrar_partidos.empty:
            matches_html += '<div class="matches-empty">No hay partidos visibles por ahora.</div>'
        else:
            for _, row in df_mostrar_partidos.iterrows():
                equipo_1_raw = row.get("Equipo_1", "")
                equipo_2_raw = row.get("Equipo_2", "")
        
                equipo_1 = escape(str(equipo_1_raw))
                equipo_2 = escape(str(equipo_2_raw))
        
                r1_raw = row.get("R1")
                r2_raw = row.get("R2")
        
                resultado_cargado = pd.notna(r1_raw) and pd.notna(r2_raw)
        
                if resultado_cargado:
                    score_text = f"{int(r1_raw)} : {int(r2_raw)}"
                    score_class = "score-pill"
                else:
                    score_text = "VS"
                    score_class = "score-pill pending"
        
                flag_1 = mapa_banderas.get(equipo_1_raw, "⚽")
                flag_2 = mapa_banderas.get(equipo_2_raw, "⚽")
        
                try:
                    partido = int(row.get("N_PARTIDO", 0))
                except:
                    partido = row.get("N_PARTIDO", "")
        
                dia = escape(str(row.get("DIA", "")))
                hora = escape(str(row.get("HORA", "")))
        
                matches_html += '<div class="match-card">'
                matches_html += f'<div class="match-meta"><span>Partido #{partido}</span><span>{dia} | {hora}</span></div>'
                matches_html += '<div class="match-body">'
                matches_html += f'<div class="team-side left"><span class="team-name">{equipo_1}</span>{flag_html(flag_1)}</div>'
                matches_html += f'<div class="{score_class}">{score_text}</div>'
                matches_html += f'<div class="team-side right">{flag_html(flag_2)}<span class="team-name">{equipo_2}</span></div>'
                matches_html += '</div>'
                matches_html += '</div>'
        
        matches_html += '</div></div>'
        
        st.markdown(matches_html, unsafe_allow_html=True)
        # ============================================================
        # CHAT / FORO — CARD INTEGRADA CON FOOTER OSCURO
        # ============================================================
        
        st.markdown("""
        <style>
        .chat-panel {
            background: rgba(255, 255, 255, 0.94);
            border: 1px solid rgba(226, 232, 240, 0.9);
            border-bottom: none;
            border-radius: 18px 18px 0 0;
            padding: 14px 14px 0 14px;
            box-shadow: 0 12px 30px rgba(15, 23, 42, 0.06);
            overflow: hidden;
        }
        
        .chat-panel-header {
            display: flex;
            align-items: center;
            gap: 10px;
            padding: 4px 4px 14px 4px;
            margin-bottom: 8px;
            border-bottom: 1px solid rgba(226, 232, 240, 0.75);
        }
        
        .chat-panel-icon {
            width: 30px;
            height: 30px;
            border-radius: 10px;
            display: flex;
            align-items: center;
            justify-content: center;
            background: rgba(244, 197, 66, 0.16);
            color: #0f172a;
            font-size: 16px;
        }
        
        .chat-panel-title {
            font-family: 'Montserrat', sans-serif;
            font-size: 17px;
            font-weight: 900;
            color: #0f172a;
            letter-spacing: -0.01em;
        }
        
        .chat-scroll {
            height: 315px;
            overflow-y: auto;
            padding: 8px 8px 4px 8px;
            border-radius: 15px 15px 0 0;
            background: rgba(248, 250, 252, 0.72);
            border: 1px solid rgba(226, 232, 240, 0.75);
            border-bottom: none;
        }
        
        .chat-scroll::-webkit-scrollbar {
            width: 6px;
        }
        
        .chat-scroll::-webkit-scrollbar-track {
            background: rgba(226, 232, 240, 0.55);
            border-radius: 999px;
        }
        
        .chat-scroll::-webkit-scrollbar-thumb {
            background: rgba(15, 23, 42, 0.22);
            border-radius: 999px;
        }
        
        .chat-row {
            display: flex;
            gap: 8px;
            margin-bottom: 12px;
            align-items: flex-start;
        }
        
        .chat-row.me {
            flex-direction: row-reverse;
        }
        
        .chat-avatar {
            width: 28px;
            height: 28px;
            border-radius: 50%;
            object-fit: cover;
            flex-shrink: 0;
            border: 2px solid rgba(255,255,255,0.95);
            box-shadow: 0 3px 8px rgba(15, 23, 42, 0.16);
        }
        
        .chat-bubble-new {
            max-width: 82%;
            border-radius: 16px;
            padding: 9px 11px;
            background: rgba(255, 255, 255, 0.96);
            border: 1px solid rgba(226, 232, 240, 0.95);
            color: #1e293b;
            box-shadow: 0 5px 14px rgba(15, 23, 42, 0.04);
        }
        
        .chat-row.me .chat-bubble-new {
            background: linear-gradient(135deg, rgba(244,197,66,0.22), rgba(255,255,255,0.96));
            border: 1px solid rgba(244, 197, 66, 0.48);
        }
        
        .chat-head {
            display: flex;
            align-items: center;
            gap: 7px;
            margin-bottom: 4px;
        }
        
        .chat-user {
            font-size: 11px;
            font-weight: 900;
            color: #1e3a8a;
            line-height: 1;
        }
        
        .chat-row.me .chat-user {
            color: #92400e;
        }
        
        .chat-time {
            font-size: 10px;
            font-weight: 700;
            color: #94a3b8;
            line-height: 1;
        }
        
        .chat-message {
            font-size: 13px;
            font-weight: 500;
            line-height: 1.35;
            color: #334155;
            word-break: break-word;
        }
        
        .chat-empty {
            height: 220px;
            display: flex;
            align-items: center;
            justify-content: center;
            color: #94a3b8;
            font-size: 13px;
            font-weight: 700;
            text-align: center;
        }
        
        /* FORMULARIO COMO FOOTER OSCURO */
        div[data-testid="stForm"] {
            background:
                linear-gradient(
                    135deg,
                    rgba(7,17,31,0.98),
                    rgba(15,23,42,0.94)
                ) !important;
            border: 1px solid rgba(255,255,255,0.08) !important;
            border-radius: 0 0 18px 18px !important;
            padding: 20px 12px !important;
            margin-top: -1px !important;
            width: 100% !important;
            box-sizing: border-box !important;
            box-shadow: 0 12px 30px rgba(15, 23, 42, 0.06) !important;
        }
        
        /* Input */
        div[data-testid="stForm"] input {
            background: rgba(255,255,255,0.94) !important;
            color: #0f172a !important;
            border: 1px solid rgba(226,232,240,0.85) !important;
            border-radius: 12px !important;
            font-size: 13px !important;
        }
        
        div[data-testid="stForm"] input::placeholder {
            color: #94a3b8 !important;
        }
        
        /* Botón */
        div[data-testid="stForm"] button {
            background: rgba(244,197,66,0.16) !important;
            border: 1px solid rgba(244,197,66,0.38) !important;
            border-radius: 12px !important;
            color: #F8FAFC !important;
            font-weight: 900 !important;
        }
        
        div[data-testid="stForm"] button:hover {
            background: rgba(244,197,66,0.26) !important;
            border-color: rgba(244,197,66,0.55) !important;
        }
        
        @media (max-width: 768px) {
            .chat-panel {
                padding: 12px 12px 0 12px;
            }
        
            .chat-panel-title {
                font-size: 15px;
            }
        
            .chat-scroll {
                height: 300px;
            }
        
            .chat-bubble-new {
                max-width: 86%;
            }
        
            .chat-message {
                font-size: 13px;
            }
        }
        </style>
        """, unsafe_allow_html=True)
        
        from html import escape
               
        columnas_foro = [
            "FECHA",
            "USUARIO",
            "NOMBRE",
            "MENSAJE",
            "PARTIDO_ID",
            "LIKES",
            "DISLIKES",
            "HORA"
        ]
        
        for col in columnas_foro:
            if col not in df_foro.columns:
                df_foro[col] = ""
        
        chat_html = '<div class="chat-panel">'
        chat_html += '<div class="chat-panel-header"><div class="chat-panel-icon">💬</div><div class="chat-panel-title">En los pasillos de la Villa se Comenta...</div></div>'
        chat_html += '<div class="chat-scroll">'
        
        if df_foro.empty:
            chat_html += '<div class="chat-empty">Todavía no hay comentarios.<br>¡Sé el primero en tirar una chicana mundialista!</div>'
        else:
            # Últimos mensajes primero
            df_foro_mostrar = df_foro.tail(20).iloc[::-1]
        
            for _, msg in df_foro_mostrar.iterrows():
                usuario_msg = str(msg.get("USUARIO", "Usuario"))
        
                nombre_raw = msg.get("NOMBRE", "")
                hora_raw = msg.get("HORA", "")
                mensaje_raw = msg.get("MENSAJE", "")
        
                nombre_msg = (
                    str(nombre_raw)
                    if pd.notna(nombre_raw)
                    and str(nombre_raw).lower() != "nan"
                    and str(nombre_raw).strip()
                    else usuario_msg
                )
        
                hora = (
                    str(hora_raw)
                    if pd.notna(hora_raw)
                    and str(hora_raw).lower() != "nan"
                    else ""
                )
        
                mensaje = escape(str(mensaje_raw)) if pd.notna(mensaje_raw) else ""
        
                es_propio = usuario_msg == st.session_state["user_data"]["USUARIO"]
        
                u_info = df_usuarios[df_usuarios["USUARIO"] == usuario_msg]
        
                if not u_info.empty and pd.notna(u_info["AVATAR_URL"].values[0]):
                    avatar = str(u_info["AVATAR_URL"].values[0])
                else:
                    avatar = AVATAR_GENERICO
        
                clase_me = "me" if es_propio else ""
        
                chat_html += f'<div class="chat-row {clase_me}">'
                chat_html += f'<img src="{avatar}" class="chat-avatar">'
                chat_html += '<div class="chat-bubble-new">'
                chat_html += f'<div class="chat-head"><span class="chat-user">{escape(nombre_msg)}</span>'
        
                if hora:
                    chat_html += f'<span class="chat-time">{escape(hora)}</span>'
        
                chat_html += '</div>'
                chat_html += f'<div class="chat-message">{mensaje}</div>'
                chat_html += '</div></div>'
        
        chat_html += '</div></div>'  # cierra chat-scroll y chat-panel
        
        st.markdown(chat_html, unsafe_allow_html=True)
        
        # Formulario de envío
        with st.form("form_foro_premium", clear_on_submit=True):
            c_txt, c_btn = st.columns([0.86, 0.14])
        
            nuevo_msg = c_txt.text_input(
                "Escribe...",
                label_visibility="collapsed",
                placeholder="¿Qué opinas del partido?"
            )
        
            enviar = c_btn.form_submit_button(
                "🚀",
                use_container_width=True
            )
        
            if enviar and nuevo_msg.strip():
                usuario_actual = st.session_state["user_data"]["USUARIO"]
        
                try:
                    nombre_actual = st.session_state["user_data"].get("NOMBRE", usuario_actual)
                except:
                    nombre_actual = usuario_actual
        
                ahora = datetime.now()
        
                nuevo_reg = {
                    "FECHA": ahora.strftime("%Y-%m-%d"),
                    "USUARIO": usuario_actual,
                    "NOMBRE": nombre_actual,
                    "MENSAJE": nuevo_msg.strip(),
                    "PARTIDO_ID": "",
                    "LIKES": 0,
                    "DISLIKES": 0,
                    "HORA": ahora.strftime("%H:%M")
                }
        
                df_nuevo_reg = pd.DataFrame([nuevo_reg], columns=columnas_foro)
        
                if df_foro.empty:
                    df_nuevo = df_nuevo_reg
                else:
                    df_nuevo = pd.concat(
                        [df_foro[columnas_foro], df_nuevo_reg],
                        ignore_index=True
                    )
        
                conn.update(
                    worksheet="FORO",
                    data=df_nuevo
                )
        
                st.cache_data.clear()
                st.rerun()
