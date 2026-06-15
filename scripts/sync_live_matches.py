import os
import sys
from pathlib import Path

import pandas as pd
from supabase import create_client


ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from services.football_data_service import sugerir_estados_partidos_api


ESTADOS_AUTOMATICOS = {"Pendiente", "En Vivo", "Entretiempo"}


def _required_env(name):
    value = str(os.getenv(name, "") or "").strip()
    if not value:
        raise RuntimeError(f"Falta variable de entorno requerida: {name}")
    return value


def _es_visible(value):
    return str(value).strip().upper() in {
        "TRUE",
        "1",
        "1.0",
        "VERDADERO",
        "T",
        "SI",
        "SÍ",
    }


def _normalizar_resultados(df):
    rename_map = {
        "n_partido": "N_PARTIDO",
        "equipo_1": "Equipo_1",
        "equipo_2": "Equipo_2",
        "dia": "DIA",
        "hora": "HORA",
        "viz": "VIZ",
        "live": "LIVE",
        "live_r1": "LIVE_R1",
        "live_r2": "LIVE_R2",
        "estado_partido": "ESTADO_PARTIDO",
    }

    return df.rename(columns={k: v for k, v in rename_map.items() if k in df.columns})


def _leer_partidos_visibles(supabase):
    response = (
        supabase
        .table("resultados")
        .select(
            "n_partido,equipo_1,equipo_2,dia,hora,viz,live,live_r1,live_r2,estado_partido"
        )
        .neq("estado_partido", "Finalizado")
        .order("n_partido")
        .execute()
    )

    df = _normalizar_resultados(pd.DataFrame(response.data or []))
    if df.empty or "VIZ" not in df.columns:
        return df

    return df[df["VIZ"].apply(_es_visible)].copy()


def _actualizar_estado_visual(supabase, sugerencia):
    n_partido = int(sugerencia["n_partido"])
    estado_api = str(sugerencia.get("estado") or "").strip()
    status_api = str(sugerencia.get("status_api") or "").strip().upper()

    data_update = {
        "live_r1": sugerencia.get("r1"),
        "live_r2": sugerencia.get("r2"),
    }

    if status_api != "FINISHED" and estado_api in ESTADOS_AUTOMATICOS:
        data_update["estado_partido"] = estado_api
        data_update["live"] = estado_api in {"En Vivo", "Entretiempo"}

    (
        supabase
        .table("resultados")
        .update(data_update)
        .eq("n_partido", n_partido)
        .execute()
    )

    return data_update


def main():
    dry_run = os.getenv("SYNC_LIVE_DRY_RUN", "").strip() == "1"

    supabase_url = _required_env("SUPABASE_URL")
    supabase_key = _required_env("SUPABASE_SERVICE_ROLE_KEY")
    _required_env("FOOTBALL_DATA_API_TOKEN")

    supabase = create_client(supabase_url, supabase_key)
    df_partidos = _leer_partidos_visibles(supabase)

    if df_partidos.empty:
        print("No hay partidos visibles no finalizados para sincronizar.")
        return

    resultado_api = sugerir_estados_partidos_api(df_partidos)
    if not resultado_api.get("ok"):
        raise RuntimeError(resultado_api.get("mensaje", "Error consultando API."))

    actualizados = 0
    finalizados_detectados = 0
    no_encontrados = 0

    for sugerencia in resultado_api.get("sugerencias", []):
        n_partido = sugerencia.get("n_partido")

        if not sugerencia.get("ok"):
            no_encontrados += 1
            print(f"NO_MATCH partido #{n_partido}: {sugerencia.get('mensaje')}")
            continue

        if str(sugerencia.get("status_api") or "").upper() == "FINISHED":
            finalizados_detectados += 1

        data_update = {
            "live_r1": sugerencia.get("r1"),
            "live_r2": sugerencia.get("r2"),
        }

        if str(sugerencia.get("status_api") or "").upper() != "FINISHED":
            data_update["estado_partido"] = sugerencia.get("estado")
            data_update["live"] = sugerencia.get("estado") in {
                "En Vivo",
                "Entretiempo",
            }

        print(
            "SYNC",
            f"partido=#{n_partido}",
            f"api={sugerencia.get('status_api')}",
            f"estado={sugerencia.get('estado_visual')}",
            f"resultado={sugerencia.get('r1')}-{sugerencia.get('r2')}",
            f"update={data_update}",
        )

        if not dry_run:
            _actualizar_estado_visual(supabase, sugerencia)

        actualizados += 1

    print(
        "Resumen:",
        f"actualizados={actualizados}",
        f"finalizados_detectados={finalizados_detectados}",
        f"no_encontrados={no_encontrados}",
        f"dry_run={dry_run}",
    )


if __name__ == "__main__":
    main()
