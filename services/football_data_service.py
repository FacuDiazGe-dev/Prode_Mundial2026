import re
import os
import time
import unicodedata
from datetime import datetime, timedelta

import requests
import streamlit as st


FOOTBALL_DATA_BASE_URL = "https://api.football-data.org/v4"

MESES_ES = {
    "ene": 1,
    "feb": 2,
    "mar": 3,
    "abr": 4,
    "may": 5,
    "jun": 6,
    "jul": 7,
    "ago": 8,
    "sep": 9,
    "oct": 10,
    "nov": 11,
    "dic": 12,
}

EQUIPO_ALIASES = {
    "alemania": ["germany"],
    "arabia saudita": ["saudi arabia"],
    "argentina": ["argentina"],
    "australia": ["australia"],
    "belgica": ["belgium"],
    "bosnia y herzegovina": [
        "bosnia and herzegovina",
        "bosnia-herzegovina",
        "bosnia herzegovina",
    ],
    "brasil": ["brazil"],
    "canada": ["canada"],
    "cabo verde": ["cape verde", "cape verde islands"],
    "corea del sur": ["korea republic", "south korea"],
    "costa rica": ["costa rica"],
    "croacia": ["croatia"],
    "dinamarca": ["denmark"],
    "egipto": ["egypt"],
    "ecuador": ["ecuador"],
    "espana": ["spain"],
    "estados unidos": ["united states", "usa", "united states of america"],
    "francia": ["france"],
    "haiti": ["haiti"],
    "inglaterra": ["england"],
    "irak": ["iraq"],
    "iran": ["iran"],
    "italia": ["italy"],
    "japon": ["japan"],
    "marruecos": ["morocco"],
    "mexico": ["mexico"],
    "noruega": ["norway"],
    "nueva zelanda": ["new zealand"],
    "nigeria": ["nigeria"],
    "paises bajos": ["netherlands", "holland"],
    "paraguay": ["paraguay"],
    "polonia": ["poland"],
    "portugal": ["portugal"],
    "qatar": ["qatar"],
    "catar": ["qatar"],
    "republica checa": ["czechia", "czech republic"],
    "republica democratica del congo": ["congo dr", "dr congo", "congo democratic republic"],
    "senegal": ["senegal"],
    "serbia": ["serbia"],
    "sudafrica": ["south africa"],
    "suecia": ["sweden"],
    "suiza": ["switzerland"],
    "tunez": ["tunisia"],
    "uruguay": ["uruguay"],
    "uzbekistan": ["uzbekistan"],
    "costa de marfil": ["ivory coast", "cote d ivoire"],
    "curazao": ["curacao"],
    "argelia": ["algeria"],
}


def _get_secret(*names):
    for name in names:
        value = str(os.getenv(name, "") or "").strip()
        if value:
            return value

        try:
            value = st.secrets.get(name, "")
        except Exception:
            value = ""

        value = str(value or "").strip()
        if value:
            return value

    return ""


def _normalizar_texto(value):
    value = str(value or "").strip().lower()
    value = unicodedata.normalize("NFKD", value)
    value = "".join(ch for ch in value if not unicodedata.combining(ch))
    value = re.sub(r"[^a-z0-9]+", " ", value)
    return re.sub(r"\s+", " ", value).strip()


def _parse_fecha_partido(dia):
    dia = str(dia or "").strip().lower()
    match = re.search(r"(\d{1,2})\s*[-/ ]\s*([a-zA-Záéíóúñ]{3})", dia)

    if not match:
        return None

    dia_num = int(match.group(1))
    mes_txt = _normalizar_texto(match.group(2))[:3]
    mes_num = MESES_ES.get(mes_txt)

    if not mes_num:
        return None

    return datetime(2026, mes_num, dia_num).strftime("%Y-%m-%d")


def _fechas_posibles_partido(partido_row):
    fecha_api = _parse_fecha_partido(partido_row.get("DIA"))

    if not fecha_api:
        return []

    fechas = [fecha_api]
    hora_raw = str(partido_row.get("HORA") or "").strip()

    try:
        hora = int(hora_raw.split(":", 1)[0])
    except (TypeError, ValueError):
        hora = None

    if hora is not None and hora >= 21:
        fecha_siguiente = (
            datetime.strptime(fecha_api, "%Y-%m-%d") + timedelta(days=1)
        ).strftime("%Y-%m-%d")
        fechas.append(fecha_siguiente)

    return fechas


def _nombres_equipo(nombre):
    nombre_normalizado = _normalizar_texto(nombre)
    return [nombre_normalizado] + EQUIPO_ALIASES.get(nombre_normalizado, [])


def _coincide_equipo(nombre_prode, equipo_api):
    candidatos_prode = _nombres_equipo(nombre_prode)
    candidatos_api = [
        _normalizar_texto(equipo_api.get("name")),
        _normalizar_texto(equipo_api.get("shortName")),
        _normalizar_texto(equipo_api.get("tla")),
    ]
    candidatos_api = [item for item in candidatos_api if item]

    for prode in candidatos_prode:
        for api in candidatos_api:
            if prode == api or prode in api or api in prode:
                return True

    return False


def _score_actual(score):
    score = score or {}
    for key in ["fullTime", "regularTime", "halfTime"]:
        parcial = score.get(key) or {}
        home = parcial.get("home")
        away = parcial.get("away")

        if home is not None and away is not None:
            return int(home), int(away)

    return None, None


def _estado_desde_api(status):
    status = str(status or "").strip().upper()

    if status in ["FINISHED"]:
        return "Finalizado", "Finalizado"

    if status in ["IN_PLAY", "LIVE"]:
        return "En Vivo", "En Vivo"

    if status in ["PAUSED"]:
        return "Entretiempo", "Entretiempo"

    return "Pendiente", "Pendiente"


def _consultar_matches_api(fecha_api=None):
    token = _get_secret("FOOTBALL_DATA_API_TOKEN", "FOOTBALL_DATA_TOKEN")

    if not token:
        return None, "Falta FOOTBALL_DATA_API_TOKEN en secrets."

    competition_code = _get_secret("FOOTBALL_DATA_COMPETITION_CODE") or "WC"

    if competition_code == "WC":
        endpoint = f"{FOOTBALL_DATA_BASE_URL}/competitions/WC/matches"
        params = {"season": "2026"}
    else:
        endpoint = f"{FOOTBALL_DATA_BASE_URL}/matches"
        params = {
            "dateFrom": fecha_api,
            "dateTo": fecha_api,
            "competitions": competition_code,
        }

    last_error = None

    for intento in range(2):
        try:
            response = requests.get(
                endpoint,
                headers={"X-Auth-Token": token},
                params=params,
                timeout=12,
            )
            response.raise_for_status()
            payload = response.json()
            return payload.get("matches", []), None
        except Exception as exc:
            last_error = exc
            if intento == 0:
                time.sleep(0.8)

    return None, f"No se pudo consultar football-data.org: {last_error}"


def _sugerir_desde_matches(partido_row, matches):
    fechas_api = _fechas_posibles_partido(partido_row)
    if not fechas_api:
        return {
            "ok": False,
            "mensaje": "No pude interpretar la fecha del partido para consultar la API.",
        }

    equipo_1 = partido_row.get("Equipo_1")
    equipo_2 = partido_row.get("Equipo_2")

    for filtrar_fecha in [True, False]:
        for match in matches:
            if (
                filtrar_fecha
                and str(match.get("utcDate", "")).split("T", 1)[0] not in fechas_api
            ):
                continue

            sugerencia = _sugerir_match(partido_row, match, equipo_1, equipo_2)
            if sugerencia:
                if not filtrar_fecha:
                    sugerencia["mensaje"] = (
                        "Sugerencia obtenida por equipos. Revisar fecha/hora porque "
                        "no coincidio con la fecha local del Prode."
                    )

                return sugerencia

    return {
        "ok": False,
        "mensaje": "La API respondió, pero no encontré un partido que coincida con los equipos seleccionados.",
    }


def _sugerir_match(partido_row, match, equipo_1, equipo_2):
        home_team = match.get("homeTeam") or {}
        away_team = match.get("awayTeam") or {}

        normal = (
            _coincide_equipo(equipo_1, home_team)
            and _coincide_equipo(equipo_2, away_team)
        )
        invertido = (
            _coincide_equipo(equipo_1, away_team)
            and _coincide_equipo(equipo_2, home_team)
        )

        if not normal and not invertido:
            return None

        home_score, away_score = _score_actual(match.get("score"))
        estado_visual, estado_formulario = _estado_desde_api(match.get("status"))

        if invertido and home_score is not None and away_score is not None:
            r1, r2 = away_score, home_score
        else:
            r1, r2 = home_score, away_score

        return {
            "ok": True,
            "estado": estado_formulario,
            "estado_visual": estado_visual,
            "r1": r1,
            "r2": r2,
            "n_partido": int(partido_row.get("N_PARTIDO")),
            "equipo_1": equipo_1,
            "equipo_2": equipo_2,
            "status_api": match.get("status"),
            "utc_date": match.get("utcDate"),
            "home": home_team.get("name"),
            "away": away_team.get("name"),
            "mensaje": "Sugerencia obtenida desde football-data.org.",
        }


def sugerir_estado_partido_api(partido_row):
    """
    Consulta football-data.org y devuelve una sugerencia para el formulario live.
    No escribe en Supabase ni modifica resultados oficiales.
    """
    fecha_api = _parse_fecha_partido(partido_row.get("DIA"))
    matches, error = _consultar_matches_api(fecha_api=fecha_api)

    if error:
        return {
            "ok": False,
            "mensaje": error,
        }

    return _sugerir_desde_matches(partido_row, matches)


def sugerir_estados_partidos_api(df_partidos):
    """
    Genera sugerencias para varios partidos visibles.
    No escribe en Supabase ni modifica resultados oficiales.
    """
    matches, error = _consultar_matches_api()

    if error:
        return {
            "ok": False,
            "mensaje": error,
            "sugerencias": [],
        }

    sugerencias = []

    for _, partido_row in df_partidos.iterrows():
        sugerencia = _sugerir_desde_matches(partido_row, matches)
        sugerencia["n_partido"] = int(partido_row.get("N_PARTIDO"))
        sugerencia["equipo_1"] = partido_row.get("Equipo_1")
        sugerencia["equipo_2"] = partido_row.get("Equipo_2")
        sugerencia["estado_actual"] = str(
            partido_row.get("ESTADO_PARTIDO") or "Pendiente"
        ).strip()
        sugerencia["r1_actual"] = partido_row.get("LIVE_R1")
        sugerencia["r2_actual"] = partido_row.get("LIVE_R2")
        sugerencias.append(sugerencia)

    return {
        "ok": True,
        "mensaje": "Consulta API finalizada.",
        "sugerencias": sugerencias,
    }
