#------------------------------------------------MENU INICIO-----------------------------------------------
import streamlit as st
import pandas as pd
import textwrap

from html import escape

from styles_config import (
    AVATAR_GENERICO,
    HEADER_BACKGROUND
)
from services.supabase_service import insertar_foro_supabase

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
    
            u_info = df_usuarios[
                df_usuarios["USUARIO"] == row["USUARIO"]
            ]
    
            foto = (
                u_info["AVATAR_URL"].values[0]
                if not u_info.empty
                and pd.notna(u_info["AVATAR_URL"].values[0])
                else AVATAR_GENERICO
            )
    
            nombre = str(row.get("JUGADOR", "-")).split(" ")[0]
            puntos = int(row.get("PUNTOS", 0))
            exactos = int(row.get("EXACTOS", 0))
            generales = int(row.get("GENERALES", 0))
    
            return nombre, puntos, foto, exactos, generales
    
        return "-", 0, AVATAR_GENERICO, 0, 0

    n1, p1, f1, e1, g1 = get_pod_data(0)
    n2, p2, f2, e2, g2 = get_pod_data(1)
    n3, p3, f3, e3, g3 = get_pod_data(2)

    try:
        row_user = df_ranking[df_ranking['USUARIO'] == st.session_state['user_data']['USUARIO']]
        pos_display = row_user.index[0]
        pts_usr = int(row_user['PUNTOS'].values[0])
        dif = int(p1 - pts_usr)
        dif_ref = "¡Eres el Líder! 🏆" if dif <= 0 else f"↑ a {dif} Pts. del Líder"
    except:
        pos_display, pts_usr, dif_ref = "-", 0, "..."

    # ============================================================
    # BADGES DEL USUARIO EN HERO
    # Solo muestra insignias obtenidas.
    # Máximo 3 visibles + contador si hay más.
    # ============================================================

    usuario_actual = st.session_state["user_data"]["USUARIO"]

    BADGE_ASSET_BASE_URL = "https://storage.googleapis.com/foto-prode2026/badges"

    hero_badge_order = [
        "Puntero",
        "Sr. Prode",
        "Siempre Suma",
        "Optimista del Gol",
        "El Cholo",
        "Rey del Empate",
        "El Macaya",
        "El Misterioso",
        "El Distinto",
    ]

    hero_badge_asset_map = {
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

    def normalizar_badges_inicio(valor):
        if valor is None:
            return []

        if isinstance(valor, list):
            return [
                str(b).strip()
                for b in valor
                if str(b).strip()
            ]

        if isinstance(valor, str):
            limpio = (
                valor
                .replace("[", "")
                .replace("]", "")
                .replace("'", "")
                .replace('"', "")
            )

            return [
                b.strip()
                for b in limpio.split(",")
                if b.strip()
            ]

        return []

    def get_user_badges_inicio(usuario):
        # TEST TEMPORAL HERO BADGES — BORRAR DESPUÉS DE PROBAR
        if str(usuario) == str(st.session_state["user_data"]["USUARIO"]):
            return [
                "Puntero",
                "Sr. Prode",
                "Siempre Suma",
                "Optimista del Gol",
                "El Cholo",
                "Rey del Empate",
                "El Macaya",
                "El Misterioso",
                "El Distinto",
            ]

        if df_ranking is None or df_ranking.empty:
            return []

        if "BADGES" not in df_ranking.columns:
            return []
        if df_ranking is None or df_ranking.empty:
            return []

        if "BADGES" not in df_ranking.columns:
            return []

        row_badges = df_ranking[
            df_ranking["USUARIO"].astype(str) == str(usuario)
        ]

        if row_badges.empty:
            return []

        return normalizar_badges_inicio(
            row_badges.iloc[0].get("BADGES", [])
        )

    def build_hero_badges_html(usuario):
        earned_badges = get_user_badges_inicio(usuario)

        if not earned_badges:
            return ""

        earned_ordered = [
            badge
            for badge in hero_badge_order
            if badge in earned_badges
        ]

        if not earned_ordered:
            return ""

        visibles = earned_ordered[:3]
        restantes = max(0, len(earned_ordered) - len(visibles))

        badges_html = ""

        for badge_name in visibles:
            badge_url = hero_badge_asset_map.get(badge_name, "")

            if badge_url:
                badges_html += (
                    f'<div class="hero-badge-chip" title="{escape(badge_name)}">'
                    f'<img src="{escape(badge_url, quote=True)}" '
                    f'class="hero-badge-img" '
                    f'alt="{escape(badge_name)}" '
                    f'loading="lazy">'
                    f'</div>'
                )

        if restantes > 0:
            badges_html += (
                f'<div class="hero-badge-more" title="Más insignias">+{restantes}</div>'
            )

        if badges_html == "":
            return ""

        return f"""
<div class="hero-badges-wrap">
<div class="hero-badges-list">
{badges_html}
</div>
</div>
"""

    hero_badges_html = build_hero_badges_html(usuario_actual)
    pos_badge_class = "has-badges" if hero_badges_html else "no-badges"

    
      
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
        padding: 18px 20px 4px 20px;
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
        opacity: 0.56;
        letter-spacing: 2px;
        margin-top: 5px;
        text-transform: uppercase;
        font-weight: 800;
    }
    
    .divider-h {
        height: 1px;
        background: linear-gradient(
            90deg,
            transparent,
            rgba(255,255,255,0.16),
            transparent
        );
        margin: 8px 60px 0 60px;
    }
    
    .content-bottom {
        display: grid;
        grid-template-columns: 22% 58% 20%;
        align-items: center;
        min-height: 230px;
        padding: 0 26px 26px 26px;
        gap: 18px;
    }

    .pos-section {
        min-height: 156px;
        max-width: 360px;
        background:
            radial-gradient(
                circle at 0% 0%,
                rgba(244,197,66,0.22),
                transparent 34%
            ),
            linear-gradient(
                135deg,
                rgba(7, 17, 31, 0.92),
                rgba(15, 23, 42, 0.68)
            );

        border: 1px solid rgba(244,197,66,0.30);
        border-radius: 20px;
        padding: 18px 16px;

        box-shadow:
            0 0 28px rgba(244,197,66,0.13),
            0 16px 34px rgba(0,0,0,0.34),
            inset 0 1px 0 rgba(255,255,255,0.10);

        backdrop-filter: blur(5px);
        position: relative;
        overflow: visible;
    }

    .pos-section.has-badges {
        display: grid;
        grid-template-columns: minmax(0, 1fr) auto;
        align-items: center;
        gap: 10px;
    }

    .pos-section.no-badges {
        display: flex;
        flex-direction: column;
        justify-content: center;
    }

    .pos-main {
        min-width: 0;
    }

    .label-pos {
        font-size: 10px;
        color: rgba(248,250,252,0.58);
        font-weight: 900;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        margin-bottom: 6px;
    }

    .val-pos {
        font-family: 'Montserrat', sans-serif;
        font-size: 62px;
        font-weight: 900;
        line-height: 0.86;
        margin: 4px 0 12px 0;
        color: #F8FAFC;
        letter-spacing: -2.4px;
        text-shadow:
            0 0 18px rgba(255,255,255,0.34),
            0 0 34px rgba(244,197,66,0.34),
            0 5px 14px rgba(0,0,0,0.62);
    }

    .pts-box {
        display: inline-flex;
        align-items: baseline;
        gap: 5px;

        font-family: 'Montserrat', sans-serif;
        font-size: 22px;
        font-weight: 900;
        line-height: 1;

        color: #F4C542;
        padding: 5px 9px;

        border-radius: 999px;
        background: rgba(244,197,66,0.12);
        border: 1px solid rgba(244,197,66,0.22);
    }

    .pts-box span {
        font-size: 11px;
        color: rgba(248,250,252,0.62);
        font-weight: 900;
    }

    .msg-status {
        font-size: 11px;
        margin-top: 9px;
        color: rgba(248,250,252,0.78);
        font-weight: 800;
        line-height: 1.25;
    }

    .hero-badges-wrap {
        display: flex;
        align-items: center;
        justify-content: center;
    }

    .hero-badges-list {
        display: flex;
        flex-direction: column;
        align-items: center;
        gap: 7px;
    }

    .hero-badge-chip {
        width: 42px;
        height: 42px;

        display: flex;
        align-items: center;
        justify-content: center;

        border-radius: 13px;
        background:
            linear-gradient(
                180deg,
                rgba(255,255,255,0.72),
                rgba(248,250,252,0.46)
            );

        border: 1px solid rgba(244,197,66,0.36);

        box-shadow:
            inset 0 1px 0 rgba(255,255,255,0.72),
            0 8px 16px rgba(0,0,0,0.22),
            0 0 14px rgba(244,197,66,0.12);
    }

    .hero-badge-img {
        width: 36px;
        height: 36px;
        object-fit: contain;
        display: block;

        filter: drop-shadow(0 4px 7px rgba(0,0,0,0.22));
    }

    .hero-badge-more {
        width: 34px;
        height: 24px;

        display: flex;
        align-items: center;
        justify-content: center;

        border-radius: 999px;

        background: rgba(7,17,31,0.92);
        border: 1px solid rgba(244,197,66,0.34);

        color: #F4C542;
        font-size: 10px;
        font-weight: 900;

        box-shadow:
            inset 0 1px 0 rgba(255,255,255,0.08),
            0 6px 12px rgba(0,0,0,0.22);
    }
    
    /* ============================================================
       PODIO PREMIUM — TOP 3
    ============================================================ */

    .podium-section {
        position: relative;
    
        display: flex;
        justify-content: center;
        align-items: flex-end;
        gap: 22px;
    
        padding: 58px 10px 42px 10px;
        min-height: 250px;
    
        transform: translateX(-42px);
    }
    .podium-section::before {
        content: "";
    
        position: absolute;
        left: 50%;
        bottom: 8px;
        transform: translateX(-50%);
    
        width: 86%;
        height: 58px;
    
        border-radius: 999px;
    
        background:
            radial-gradient(
                circle at 50% 0%,
                rgba(244,197,66,0.16),
                transparent 45%
            ),
            linear-gradient(
                180deg,
                rgba(255,255,255,0.10),
                rgba(15,23,42,0.92) 46%,
                rgba(7,17,31,0.98)
            );
    
        border: 1px solid rgba(244,197,66,0.34);
    
        box-shadow:
            0 18px 36px rgba(0,0,0,0.48),
            inset 0 1px 0 rgba(255,255,255,0.12),
            inset 0 -1px 0 rgba(244,197,66,0.18),
            0 0 26px rgba(244,197,66,0.14);
    
        z-index: 0;
    }

    .podium-section::after {
        content: "PRODE TOP 3";
    
        position: absolute;
        left: 50%;
        bottom: 22px;
        transform: translateX(-50%);
    
        font-family: inter; #'Montserrat', sans-serif;
        font-size: 15px;
        font-weight: 900;
        letter-spacing: 0.28em;
        color: rgba(244,197,66,0.72);
        
        opacity: 0.78;
        
        text-shadow:
            0 2px 8px rgba(0,0,0,0.75),
            0 0 12px rgba(244,197,66,0.18);
    
        z-index: 1;
        pointer-events: none;
    }

    .pod-card {
        position: relative;
        z-index: 2;

        width: 136px;
        min-height: 132px;
        margin-bottom: 18px;

        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: flex-end;

        padding: 58px 12px 14px 12px;

        border-radius: 18px;

        background:
            radial-gradient(
                circle at 50% 0%,
                rgba(255,255,255,0.10),
                transparent 38%
            ),
            linear-gradient(
                180deg,
                rgba(15,23,42,0.84),
                rgba(7,17,31,0.96)
            );

        border: 1px solid rgba(255,255,255,0.16);

        box-shadow:
            0 16px 30px rgba(0,0,0,0.36),
            inset 0 1px 0 rgba(255,255,255,0.10);

        backdrop-filter: blur(4px);
    }

    .pod-card.first {
        border: 1px solid rgba(244,197,66,0.82);
        box-shadow:
            0 22px 44px rgba(0,0,0,0.48),
            0 0 30px rgba(244,197,66,0.28),
            inset 0 1px 0 rgba(255,255,255,0.16),
            inset 0 0 22px rgba(244,197,66,0.055);
    }
    
    .pod-card.second {
        border: 1px solid rgba(229,231,235,0.62);
        box-shadow:
            0 16px 30px rgba(0,0,0,0.36),
            0 0 18px rgba(229,231,235,0.12),
            inset 0 1px 0 rgba(255,255,255,0.12);
    }
    
    .pod-card.third {
        border: 1px solid rgba(205,127,50,0.76);
        box-shadow:
            0 16px 30px rgba(0,0,0,0.36),
            0 0 18px rgba(205,127,50,0.14),
            inset 0 1px 0 rgba(255,255,255,0.12);
    }

    .pod-card::after {
        content: "";

        position: absolute;
        left: 18px;
        right: 18px;
        bottom: -9px;

        height: 14px;
        border-radius: 0 0 18px 18px;

        background: rgba(7,17,31,0.94);
        border: 1px solid rgba(255,255,255,0.10);
        border-top: none;

        box-shadow:
            0 10px 18px rgba(0,0,0,0.30),
            inset 0 1px 0 rgba(255,255,255,0.06);

        z-index: -1;
    }

    .pod-card.first::after {
        border-color: rgba(244,197,66,0.45);
        box-shadow:
            0 12px 20px rgba(0,0,0,0.36),
            0 0 18px rgba(244,197,66,0.18);
    }

    .pod-avatar-wrap {
        position: absolute;
        top: -48px;
        left: 50%;
        transform: translateX(-50%);

        display: flex;
        align-items: center;
        justify-content: center;
    }

    .pod-card.first .pod-avatar-wrap {
        top: -62px;
    }

    .pod-avatar {
        display: block;
    
        aspect-ratio: 1 / 1;
        border-radius: 50%;
    
        object-fit: cover;
        object-position: center;
    
        box-sizing: border-box;
        background: #F8FAFC;
    
        max-width: none;
        flex-shrink: 0;
    
        box-shadow:
            0 12px 30px rgba(0,0,0,0.58),
            inset 0 1px 0 rgba(255,255,255,0.25);
    }

    .pod-avatar.gold {
        width: 112px;
        height: 112px;

        border: 6px solid #F4C542;

        box-shadow:
            0 14px 34px rgba(0,0,0,0.64),
            0 0 30px rgba(244,197,66,0.52),
            inset 0 1px 0 rgba(255,255,255,0.30);
    }

    .pod-avatar.silver {
        width: 88px;
        height: 88px;

        border: 5px solid #E5E7EB;

        box-shadow:
            0 12px 28px rgba(0,0,0,0.56),
            0 0 18px rgba(229,231,235,0.30);
    }

    .pod-avatar.bronze {
        width: 88px;
        height: 88px;

        border: 5px solid #CD7F32;

        box-shadow:
            0 12px 28px rgba(0,0,0,0.56),
            0 0 18px rgba(205,127,50,0.34);
    }

    .pod-rank-badge {
        position: absolute;
        top: -4px;
        right: -6px;

        width: 28px;
        height: 28px;

        border-radius: 50%;

        display: flex;
        align-items: center;
        justify-content: center;

        font-family: 'Montserrat', sans-serif;
        font-size: 13px;
        font-weight: 900;

        box-shadow:
            0 6px 12px rgba(0,0,0,0.36),
            inset 0 1px 0 rgba(255,255,255,0.30);
    }

    .pod-rank-badge.gold {
        background: linear-gradient(135deg, #FFD700, #F4A900);
        color: #111827;
    }

    .pod-rank-badge.silver {
        background: linear-gradient(135deg, #F8FAFC, #9CA3AF);
        color: #111827;
    }

    .pod-rank-badge.bronze {
        background: linear-gradient(135deg, #E59A52, #9A5A22);
        color: white;
    }

    .pod-name {
        font-family: 'Montserrat', sans-serif;
        font-weight: 900;
        font-size: 15px;

        margin-top: 4px;

        text-transform: uppercase;
        color: #F8FAFC;
        text-shadow: 0 2px 8px rgba(0,0,0,0.68);

        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
        max-width: 126px;
    }

    .pod-card.first .pod-name {
        color: #F4C542;
        font-size: 17px;
    }

    .pod-pts {
        margin-top: 5px;

        display: inline-flex;
        align-items: center;
        justify-content: center;

        min-width: 62px;
        padding: 5px 9px;

        border-radius: 999px;

        background: rgba(7,17,31,0.78);
        border: 1px solid rgba(244,197,66,0.30);

        color: rgba(248,250,252,0.82);
        font-family: 'Montserrat', sans-serif;
        font-size: 11px;
        font-weight: 900;
    }

    .pod-card.first .pod-pts {
        color: #F4C542;
        border-color: rgba(244,197,66,0.48);
    }

    .pod-divider {
        width: 72%;
        height: 1px;

        margin: 10px 0 9px 0;

        background:
            linear-gradient(
                90deg,
                transparent,
                rgba(244,197,66,0.45),
                transparent
            );
    }

    .pod-stats {
        width: 100%;

        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 6px;
    }

    .pod-stat {
        min-width: 0;

        display: flex;
        align-items: center;
        justify-content: center;
        gap: 4px;

        padding: 6px 5px;

        border-radius: 10px;

        background: rgba(255,255,255,0.055);
        border: 1px solid rgba(255,255,255,0.10);

        color: rgba(248,250,252,0.86);
        font-size: 10px;
        font-weight: 900;

        box-shadow:
            inset 0 1px 0 rgba(255,255,255,0.05);
    }

    .pod-stat span {
        font-size: 13px;
        line-height: 1;
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

        .pos-section,
        .pos-section.has-badges,
        .pos-section.no-badges {
            width: 100%;
            min-height: auto;
            padding: 17px 16px;
            text-align: center;
            box-sizing: border-box;

            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;

            gap: 9px;
        }

        .val-pos {
            font-size: 52px;
            margin-bottom: 10px;
        }

        .pts-box {
            font-size: 20px;
        }

        .msg-status {
            margin-top: 8px;
            font-size: 11px;
        }

        .hero-badges-wrap {
            width: 100%;
            margin-top: 2px;
        }

        .hero-badges-list {
            flex-direction: row;
            justify-content: center;
            gap: 7px;
        }

        .hero-badge-chip {
            width: 38px;
            height: 38px;
            border-radius: 12px;
        }

        .hero-badge-img {
            width: 33px;
            height: 33px;
        }

        .hero-badge-more {
            width: 32px;
            height: 24px;
            font-size: 10px;
        }
    
        .podium-section {
            width: 100%;
            gap: 7px;
            padding: 44px 0 18px 0;
            min-height: 190px;
            justify-content: space-between;
            transform: none;
        }

        .podium-section::before {
            bottom: 2px;
            height: 34px;
            width: 74%;
            opacity: 0.82;
        }
        .podium-section::after {
            font-size: 10px;
            letter-spacing: 0.24em;
            bottom: 18px;
        }

        .pod-card {
            width: 31%;
            min-height: 106px;
            padding: 45px 6px 10px 6px;
            border-radius: 14px;
        }

        .pod-card.first {
            width: 34%;
            min-height: 122px;
            padding-top: 54px;
            transform: translateY(-28px);
        }

        .pod-avatar-wrap {
            top: -34px;
        }

        .pod-card.first .pod-avatar-wrap {
            top: -44px;
        }

        .pod-avatar.gold {
            width: 82px;
            height: 82px;
            border-width: 5px;
        }

        .pod-avatar.silver,
        .pod-avatar.bronze {
            width: 66px;
            height: 66px;
            border-width: 4px;
        }

        .pod-rank-badge {
            width: 22px;
            height: 22px;
            font-size: 10px;
            top: -2px;
            right: -5px;
        }

        .pod-name {
            font-size: 10px;
            max-width: 100%;
        }

        .pod-card.first .pod-name {
            font-size: 11px;
        }

        .pod-pts {
            min-width: 48px;
            padding: 4px 6px;
            font-size: 9px;
            margin-top: 4px;
        }

        .pod-divider {
            margin: 7px 0 6px 0;
        }

        .pod-stats {
            gap: 4px;
        }

        .pod-stat {
            padding: 5px 3px;
            border-radius: 8px;
            font-size: 9px;
            gap: 2px;
        }

        .pod-stat span {
            font-size: 11px;
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

<div class="pos-section __POS_BADGE_CLASS__">
    <div class="pos-main">
        <div class="label-pos">Tu posición</div>
        <div class="val-pos">__POS_DISPLAY__°</div>
        <div class="pts-box">__PTS_USR__ <span>PTS.</span></div>
        <div class="msg-status">__DIF_REF__</div>
    </div>
    __HERO_BADGES_HTML__
</div>

<div class="podium-section">

<div class="pod-card second">
<div class="pod-avatar-wrap">
    <img src="__F2__" class="pod-avatar silver" loading="lazy" alt="__N2__">
    <div class="pod-rank-badge silver">2</div>
</div>

<div class="pod-name">__N2__</div>
<div class="pod-pts">__P2__ PTS.</div>

<div class="pod-divider"></div>

<div class="pod-stats">
    <div class="pod-stat"><span>🎯</span>__E2__</div>
    <div class="pod-stat"><span>✅</span>__G2__</div>
</div>
</div>

<div class="pod-card first">
<div class="pod-avatar-wrap">
    <img src="__F1__" class="pod-avatar gold" loading="lazy" alt="__N1__">
    <div class="pod-rank-badge gold">1</div>
</div>

<div class="pod-name">__N1__</div>
<div class="pod-pts">__P1__ PTS.</div>

<div class="pod-divider"></div>

<div class="pod-stats">
    <div class="pod-stat"><span>🎯</span>__E1__</div>
    <div class="pod-stat"><span>✅</span>__G1__</div>
</div>
</div>

<div class="pod-card third">
<div class="pod-avatar-wrap">
    <img src="__F3__" class="pod-avatar bronze" loading="lazy" alt="__N3__">
    <div class="pod-rank-badge bronze">3</div>
</div>

<div class="pod-name">__N3__</div>
<div class="pod-pts">__P3__ PTS.</div>

<div class="pod-divider"></div>

<div class="pod-stats">
    <div class="pod-stat"><span>🎯</span>__E3__</div>
    <div class="pod-stat"><span>✅</span>__G3__</div>
</div>
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
        .replace("__POS_BADGE_CLASS__", str(pos_badge_class))
        .replace("__HERO_BADGES_HTML__", str(hero_badges_html))
        .replace("__F1__", str(f1))
        .replace("__F2__", str(f2))
        .replace("__F3__", str(f3))
        .replace("__N1__", str(n1))
        .replace("__N2__", str(n2))
        .replace("__N3__", str(n3))
        .replace("__P1__", str(p1))
        .replace("__P2__", str(p2))
        .replace("__P3__", str(p3))
        .replace("__E1__", str(e1))
        .replace("__E2__", str(e2))
        .replace("__E3__", str(e3))
        .replace("__G1__", str(g1))
        .replace("__G2__", str(g2))
        .replace("__G3__", str(g3))
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

    FONDO_CARD_INICIO = "https://storage.googleapis.com/foto-prode2026/Banners/FONDO_CARD_INICIO.png"

    c_izq, c_der = st.columns([1, 1.1], gap="large")

# ------------------ COLUMNA IZQUIERDA: LÍDERES Y TENDENCIAS ------------------
    with c_izq:
        ranking_css = """
        <style>
        /* ============================================================
           RANKING GENERAL — PANEL PREMIUM TEXTURADO
        ============================================================ */
        
        .ranking-panel {
            position: relative;
            overflow: hidden;
        
            background:
                linear-gradient(
                    180deg,
                    rgba(255,255,255,0.96),
                    rgba(248,250,252,0.92)
                );
        
            border: 1px solid rgba(203,213,225,0.92);
            border-radius: 20px;
        
            padding: 15px;
        
            box-shadow:
                0 16px 36px rgba(15,23,42,0.075),
                inset 0 1px 0 rgba(255,255,255,0.82);
        
            width: 100%;
            box-sizing: border-box;
        }
        
        .ranking-panel::before {
            content: "";
        
            position: absolute;
            inset: 0;
        
            background:
                radial-gradient(
                    circle at 0% 0%,
                    rgba(244,197,66,0.08),
                    transparent 36%
                );
        
            pointer-events: none;
            z-index: 0;
        }
        
        .ranking-panel > * {
            position: relative;
            z-index: 1;
        }
        
        .ranking-panel-header {
            display: flex;
            align-items: center;
            gap: 11px;
        
            padding: 5px 5px 14px 5px;
            margin-bottom: 10px;
        
            border-bottom: 1px solid rgba(148,163,184,0.30);
        }
        
        .ranking-panel-icon {
            width: 34px;
            height: 34px;
            border-radius: 12px;
        
            display: flex;
            align-items: center;
            justify-content: center;
        
            background:
                linear-gradient(
                    180deg,
                    rgba(244,197,66,0.18),
                    rgba(244,197,66,0.07)
                );
        
            border: 1px solid rgba(244,197,66,0.18);
        
            color: #0f172a;
            font-size: 17px;
        
            box-shadow:
                inset 0 1px 0 rgba(255,255,255,0.78),
                0 6px 14px rgba(15,23,42,0.06);
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
           SCROLL
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
            background: rgba(226,232,240,0.55);
            border-radius: 999px;
        }
        
        .ranking-scroll::-webkit-scrollbar-thumb {
            background: rgba(15,23,42,0.24);
            border-radius: 999px;
        }
        
        /* ============================================================
           FILAS BASE
        ============================================================ */
        
        .ranking-row {
            position: relative;
            overflow: hidden;
        
            width: 100% !important;
            box-sizing: border-box !important;
        
            display: grid !important;
            grid-template-columns: 42px minmax(0, 1fr) 72px !important;
            align-items: center !important;
            gap: 12px !important;
        
            padding: 11px 12px;
            margin-bottom: 9px;
        
            border-radius: 16px;
        
            background:
                linear-gradient(
                    180deg,
                    rgba(255,255,255,0.74),
                    rgba(248,250,252,0.60)
                ),
                url('__FONDO_CARD_INICIO__');
        
            background-size: cover;
            background-position: center;
            background-repeat: no-repeat;
        
            border: 1px solid rgba(148,163,184,0.32);
        
            box-shadow:
                0 8px 18px rgba(15,23,42,0.05),
                inset 0 1px 0 rgba(255,255,255,0.75);
        
            transition:
                transform 0.18s ease,
                box-shadow 0.18s ease,
                border-color 0.18s ease;
        }
        
        .ranking-row::before {
            content: "";
        
            position: absolute;
            inset: 0;
        
            background:
                linear-gradient(
                    90deg,
                    rgba(255,255,255,0.30),
                    rgba(255,255,255,0.10)
                );
        
            pointer-events: none;
            z-index: 0;
        }
        
        .ranking-row > * {
            position: relative;
            z-index: 1;
        }
        
        .ranking-row:last-child {
            margin-bottom: 0;
        }
        
        .ranking-row:hover {
            transform: translateY(-1px);
            border-color: rgba(244,197,66,0.40);
        
            box-shadow:
                0 12px 24px rgba(15,23,42,0.085),
                0 0 14px rgba(244,197,66,0.08),
                inset 0 1px 0 rgba(255,255,255,0.82);
        }
        
        /* ============================================================
           JERARQUÍA: TOP 3 / TOP 5 / RESTO
        ============================================================ */
        
        .ranking-row.top-1 {
            min-height: 74px;
        
            background:
                radial-gradient(
                    circle at 0% 50%,
                    rgba(244,197,66,0.24),
                    transparent 44%
                ),
                linear-gradient(
                    180deg,
                    rgba(255,248,220,0.86),
                    rgba(255,255,255,0.68)
                ),
                url('__FONDO_CARD_INICIO__');
        
            background-size: cover;
            background-position: center;
        
            border-color: rgba(244,197,66,0.66);
        
            box-shadow:
                0 12px 26px rgba(244,197,66,0.14),
                0 10px 22px rgba(15,23,42,0.07),
                inset 0 1px 0 rgba(255,255,255,0.85);
        }
        
        .ranking-row.top-2 {
            min-height: 72px;
        
            background:
                radial-gradient(
                    circle at 0% 50%,
                    rgba(203,213,225,0.34),
                    transparent 44%
                ),
                linear-gradient(
                    180deg,
                    rgba(248,250,252,0.86),
                    rgba(255,255,255,0.68)
                ),
                url('__FONDO_CARD_INICIO__');
        
            background-size: cover;
            background-position: center;
        
            border-color: rgba(148,163,184,0.56);
        }
        
        .ranking-row.top-3 {
            min-height: 72px;
        
            background:
                radial-gradient(
                    circle at 0% 50%,
                    rgba(205,127,50,0.22),
                    transparent 44%
                ),
                linear-gradient(
                    180deg,
                    rgba(255,247,237,0.80),
                    rgba(255,255,255,0.66)
                ),
                url('__FONDO_CARD_INICIO__');
        
            background-size: cover;
            background-position: center;
        
            border-color: rgba(205,127,50,0.54);
        }
        
        .ranking-row.top-5 {
            background:
                radial-gradient(
                    circle at 0% 50%,
                    rgba(244,197,66,0.12),
                    transparent 42%
                ),
                linear-gradient(
                    180deg,
                    rgba(255,255,255,0.76),
                    rgba(248,250,252,0.62)
                ),
                url('__FONDO_CARD_INICIO__');
        
            background-size: cover;
            background-position: center;
        
            border-color: rgba(244,197,66,0.30);
        }
        
        /* ============================================================
           USUARIO ACTUAL
        ============================================================ */
        
        .ranking-row.me {
            border-color: rgba(244,197,66,0.72);
        
            box-shadow:
                0 12px 26px rgba(244,197,66,0.16),
                0 8px 18px rgba(15,23,42,0.07),
                inset 0 1px 0 rgba(255,255,255,0.86);
        }
        
        .ranking-row.me::after {
            content: "TÚ";
        
            position: absolute;
            top: 8px;
            right: 10px;
        
            padding: 3px 7px;
            border-radius: 999px;
        
            background: rgba(7,17,31,0.90);
            border: 1px solid rgba(244,197,66,0.35);
        
            color: #F4C542;
            font-size: 8px;
            font-weight: 900;
            letter-spacing: 0.08em;
        
            z-index: 3;
        }
        
        /* ============================================================
           POSICIÓN
        ============================================================ */
        
        .rank-pos {
            width: 34px;
            height: 34px;
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
        
            box-shadow:
                inset 0 1px 0 rgba(255,255,255,0.70),
                0 4px 9px rgba(15,23,42,0.10);
        }
        
        .rank-pos.gold {
            width: 38px;
            height: 38px;
        
            background: linear-gradient(135deg, #FFD700, #F4A900);
            color: #111827;
        
            box-shadow:
                0 6px 14px rgba(244,197,66,0.28),
                inset 0 1px 0 rgba(255,255,255,0.35);
        }
        
        .rank-pos.silver {
            width: 37px;
            height: 37px;
        
            background: linear-gradient(135deg, #F8FAFC, #9CA3AF);
            color: #111827;
        }
        
        .rank-pos.bronze {
            width: 37px;
            height: 37px;
        
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
            font-size: 13.5px;
            font-weight: 900;
            color: #0f172a;
        
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
        }
        
        .ranking-row.top-1 .player-name,
        .ranking-row.top-2 .player-name,
        .ranking-row.top-3 .player-name {
            font-size: 14px;
        }
        
        .player-sub {
            margin-top: 3px;
        
            font-size: 10px;
            font-weight: 800;
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
            font-size: 22px;
            font-weight: 900;
            color: #0f172a;
            line-height: 1;
        }
        
        .ranking-row.top-1 .points-main,
        .ranking-row.top-2 .points-main,
        .ranking-row.top-3 .points-main {
            font-size: 24px;
        }
        
        .points-label {
            font-size: 9px;
            font-weight: 900;
            color: #94a3b8;
            text-transform: uppercase;
            margin-top: 2px;
        }
        
        .ranking-row.top-1 .points-label {
            color: rgba(180,83,9,0.72);
        }
        
        /* ============================================================
           MOBILE
        ============================================================ */
        
        @media (max-width: 768px) {
            .ranking-panel {
                padding: 12px;
                border-radius: 17px;
            }
        
            .ranking-panel-title {
                font-size: 15px;
            }
        
            .ranking-panel-icon {
                width: 31px;
                height: 31px;
                border-radius: 11px;
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
                border-radius: 15px;
            }
        
            .ranking-row.top-1,
            .ranking-row.top-2,
            .ranking-row.top-3 {
                min-height: 66px;
            }
        
            .rank-pos,
            .rank-pos.gold,
            .rank-pos.silver,
            .rank-pos.bronze {
                width: 30px;
                height: 30px;
                font-size: 12px;
            }
        
            .player-name,
            .ranking-row.top-1 .player-name,
            .ranking-row.top-2 .player-name,
            .ranking-row.top-3 .player-name {
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
        
            .points-main,
            .ranking-row.top-1 .points-main,
            .ranking-row.top-2 .points-main,
            .ranking-row.top-3 .points-main {
                font-size: 16px;
            }
        
            .ranking-row.me::after {
                top: 6px;
                right: 7px;
                font-size: 7px;
                padding: 2px 6px;
            }
        }
        </style>
        """
        
        ranking_css = ranking_css.replace(
            "__FONDO_CARD_INICIO__",
            FONDO_CARD_INICIO
        )
        
        st.markdown(ranking_css, unsafe_allow_html=True)
        
        
        
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
            medalla = clase_medalla(posicion_num).

            if posicion_num == 1:
                clase_tier = "top-1"
            elif posicion_num == 2:
                clase_tier = "top-2"
            elif posicion_num == 3:
                clase_tier = "top-3"
            elif posicion_num <= 5:
                clase_tier = "top-5"
            else:
                clase_tier = "normal"
        
            subtitulo = "Tu posición actual" if es_usuario_actual else "Participante"
        
            badges_html = build_ranking_badges_html(
                row.get("BADGES", [])
            )
        
            ranking_html += f"""
<div class="ranking-row {clase_usuario} {clase_tier}">
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

        st.markdown(f"""
        <style>
        /* ============================================================
           RESULTADOS OFICIALES — PANEL PREMIUM TEXTURADO
        ============================================================ */
        
        .matches-panel {{
            position: relative;
            overflow: hidden;
        
            background:
                linear-gradient(
                    180deg,
                    rgba(255,255,255,0.96),
                    rgba(248,250,252,0.92)
                );
        
            border: 1px solid rgba(203,213,225,0.92);
            border-radius: 20px;
        
            padding: 15px;
        
            box-shadow:
                0 16px 36px rgba(15,23,42,0.075),
                inset 0 1px 0 rgba(255,255,255,0.82);
        }}
        
        .matches-panel::before {{
            content: "";
        
            position: absolute;
            inset: 0;
        
            background:
                radial-gradient(
                    circle at 0% 0%,
                    rgba(244,197,66,0.08),
                    transparent 36%
                );
        
            pointer-events: none;
            z-index: 0;
        }}
        
        .matches-panel > * {{
            position: relative;
            z-index: 1;
        }}
        
        .matches-panel-header {{
            display: flex;
            align-items: center;
            gap: 11px;
        
            padding: 5px 5px 14px 5px;
            margin-bottom: 10px;
        
            border-bottom: 1px solid rgba(148,163,184,0.30);
        }}
        
        .matches-panel-icon {{
            width: 34px;
            height: 34px;
            border-radius: 12px;
        
            display: flex;
            align-items: center;
            justify-content: center;
        
            background:
                linear-gradient(
                    180deg,
                    rgba(30,64,175,0.12),
                    rgba(15,23,42,0.06)
                );
        
            border: 1px solid rgba(30,64,175,0.14);
        
            color: #0f172a;
            font-size: 17px;
        
            box-shadow:
                inset 0 1px 0 rgba(255,255,255,0.78),
                0 6px 14px rgba(15,23,42,0.06);
        }}
        
        .matches-panel-title {{
            font-family: 'Montserrat', sans-serif;
            font-size: 17px;
            font-weight: 900;
            color: #0f172a;
        
            text-transform: uppercase;
            letter-spacing: 0.01em;
        }}
        
        .matches-scroll {{
            height: 315px;
            overflow-y: auto;
            padding-right: 6px;
        }}
        
        .matches-scroll::-webkit-scrollbar {{
            width: 6px;
        }}
        
        .matches-scroll::-webkit-scrollbar-track {{
            background: rgba(226,232,240,0.55);
            border-radius: 999px;
        }}
        
        .matches-scroll::-webkit-scrollbar-thumb {{
            background: rgba(15,23,42,0.24);
            border-radius: 999px;
        }}
        
        /* ============================================================
           MINI CARD DE PARTIDO
        ============================================================ */
        
        .match-card {{
            position: relative;
            overflow: hidden;
        
            padding: 12px 13px;
            margin-bottom: 10px;
        
            border-radius: 16px;
        
            background:
                linear-gradient(
                    180deg,
                    rgba(255,255,255,0.72),
                    rgba(248,250,252,0.58)
                ),
                url('{FONDO_CARD_INICIO}');
        
            background-size: cover;
            background-position: center;
            background-repeat: no-repeat;
        
            border: 1px solid rgba(148,163,184,0.38);
        
            box-shadow:
                0 8px 18px rgba(15,23,42,0.055),
                inset 0 1px 0 rgba(255,255,255,0.75);
        
            transition:
                transform 0.18s ease,
                box-shadow 0.18s ease,
                border-color 0.18s ease;
        }}
        
        .match-card::before {{
            content: "";
        
            position: absolute;
            inset: 0;
        
            background:
                radial-gradient(
                    circle at 0% 0%,
                    rgba(244,197,66,0.10),
                    transparent 38%
                ),
                linear-gradient(
                    90deg,
                    rgba(255,255,255,0.28),
                    rgba(255,255,255,0.10)
                );
        
            pointer-events: none;
        }}
        
        .match-card:hover {{
            transform: translateY(-1px);
            border-color: rgba(244,197,66,0.48);
        
            box-shadow:
                0 12px 24px rgba(15,23,42,0.09),
                0 0 14px rgba(244,197,66,0.10),
                inset 0 1px 0 rgba(255,255,255,0.82);
        }}
        
        .match-card > * {{
            position: relative;
            z-index: 1;
        }}
        
        .match-meta {{
            display: flex;
            justify-content: space-between;
            align-items: center;
        
            margin-bottom: 11px;
        
            font-size: 9.5px;
            font-weight: 900;
            color: #64748b;
        
            text-transform: uppercase;
            letter-spacing: 0.065em;
        }}
        
        .match-meta span:first-child {{
            color: #334155;
        }}
        
        .match-meta span:last-child {{
            color: #64748b;
        }}
        
        .match-body {{
            display: grid;
            grid-template-columns: minmax(0, 1fr) 74px minmax(0, 1fr);
            align-items: center;
            gap: 12px;
        }}
        
        .team-side {{
            display: flex;
            align-items: center;
            gap: 8px;
            min-width: 0;
        }}
        
        .team-side.left {{
            justify-content: flex-end;
            text-align: right;
        }}
        
        .team-side.right {{
            justify-content: flex-start;
            text-align: left;
        }}
        
        .team-name {{
            font-family: 'Inter', sans-serif;
            font-size: 13px;
            font-weight: 900;
            color: #0f172a;
        
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
        }}
        
        .flag-img {{
            width: 30px;
            height: 21px;
        
            object-fit: cover;
            border-radius: 5px;
        
            border: 1px solid rgba(255,255,255,0.85);
        
            box-shadow:
                0 3px 7px rgba(15,23,42,0.18),
                inset 0 1px 0 rgba(255,255,255,0.42);
        
            flex-shrink: 0;
        }}
        
        .flag-fallback {{
            font-size: 20px;
            flex-shrink: 0;
        }}
        
        /* ============================================================
           MARCADOR / VS
        ============================================================ */
        
        .score-pill {{
            position: relative;
            overflow: hidden;
        
            background:
                radial-gradient(
                    circle at 50% 0%,
                    rgba(244,197,66,0.22),
                    transparent 48%
                ),
                linear-gradient(
                    180deg,
                    #0f172a,
                    #07111F
                );
        
            color: #f8fafc;
        
            border-radius: 12px;
            padding: 8px 8px;
        
            text-align: center;
        
            font-family: 'Montserrat', sans-serif;
            font-size: 15px;
            font-weight: 900;
            letter-spacing: 0.06em;
        
            border: 1px solid rgba(244,197,66,0.30);
        
            box-shadow:
                inset 0 1px 0 rgba(255,255,255,0.10),
                0 7px 16px rgba(7,17,31,0.20),
                0 0 12px rgba(244,197,66,0.10);
        }}
        
        .score-pill.pending {{
            background:
                linear-gradient(
                    180deg,
                    rgba(15,23,42,0.08),
                    rgba(15,23,42,0.045)
                );
        
            color: #475569;
        
            border: 1px solid rgba(148,163,184,0.36);
        
            box-shadow:
                inset 0 1px 0 rgba(255,255,255,0.72),
                0 5px 12px rgba(15,23,42,0.05);
        }}
        
        .matches-empty {{
            height: 245px;
        
            display: flex;
            align-items: center;
            justify-content: center;
        
            text-align: center;
            color: #94a3b8;
        
            font-size: 13px;
            font-weight: 800;
        
            background: rgba(248,250,252,0.74);
            border: 1px solid rgba(226,232,240,0.85);
            border-radius: 15px;
        }}
        
        /* ============================================================
           MOBILE
        ============================================================ */
        
        @media (max-width: 768px) {{
            .matches-panel {{
                padding: 12px;
                border-radius: 17px;
            }}
        
            .matches-panel-title {{
                font-size: 15px;
            }}
        
            .matches-panel-icon {{
                width: 31px;
                height: 31px;
                border-radius: 11px;
            }}
        
            .matches-scroll {{
                height: 315px;
            }}
        
            .match-card {{
                padding: 11px 10px;
                border-radius: 15px;
            }}
        
            .match-body {{
                grid-template-columns: minmax(0, 1fr) 62px minmax(0, 1fr);
                gap: 8px;
            }}
        
            .team-name {{
                font-size: 12px;
            }}
        
            .flag-img {{
                width: 25px;
                height: 18px;
                border-radius: 4px;
            }}
        
            .score-pill {{
                font-size: 13px;
                padding: 7px 6px;
                border-radius: 10px;
            }}
        
            .match-meta {{
                font-size: 8.8px;
                margin-bottom: 10px;
            }}
        }}
        </style>
        """, unsafe_allow_html=True)
        
        
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
        .chat-panel {{
            background: rgba(255, 255, 255, 0.94);
            border: 1px solid rgba(226, 232, 240, 0.9);
            border-bottom: none;
            border-radius: 18px 18px 0 0;
            padding: 14px 14px 0 14px;
            box-shadow: 0 12px 30px rgba(15, 23, 42, 0.06);
            overflow: hidden;
        }}
        
        .chat-panel-header {{
            display: flex;
            align-items: center;
            gap: 10px;
            padding: 4px 4px 14px 4px;
            margin-bottom: 8px;
            border-bottom: 1px solid rgba(226, 232, 240, 0.75);
        }}
        
        .chat-panel-icon {{
            width: 30px;
            height: 30px;
            border-radius: 10px;
            display: flex;
            align-items: center;
            justify-content: center;
            background: rgba(244, 197, 66, 0.16);
            color: #0f172a;
            font-size: 16px;
        }}
        
        .chat-panel-title {{
            font-family: 'Montserrat', sans-serif;
            font-size: 17px;
            font-weight: 900;
            color: #0f172a;
            letter-spacing: -0.01em;
        }}
        
        .chat-scroll {{
            height: 315px;
            overflow-y: auto;
            padding: 8px 8px 4px 8px;
            border-radius: 15px 15px 0 0;
            background: rgba(248, 250, 252, 0.72);
            border: 1px solid rgba(226, 232, 240, 0.75);
            border-bottom: none;
        }}
        
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
                    nombre_actual = st.session_state["user_data"].get(
                        "NOMBRE",
                        usuario_actual
                    )
                except:
                    nombre_actual = usuario_actual

                ahora = datetime.now()

                nuevo_reg = {
                    "FECHA": ahora.strftime("%Y-%m-%d"),
                    "USUARIO": usuario_actual,
                    "NOMBRE": nombre_actual,
                    "MENSAJE": nuevo_msg.strip(),
                    "PARTIDO_ID": 0,
                    "LIKES": 0,
                    "DISLIKES": 0,
                    "FORO_IMG_URL": ""
                }

                df_nuevo_reg = pd.DataFrame([nuevo_reg])

                ok, msg = insertar_foro_supabase(df_nuevo_reg)

                if ok:
                    st.cache_data.clear()
                    st.rerun()
                else:
                    st.error(msg)
