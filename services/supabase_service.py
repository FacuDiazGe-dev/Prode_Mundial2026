import streamlit as st
import pandas as pd
from supabase import create_client


# ============================================================
# CLIENTE SUPABASE
# Las claves salen de .streamlit/secrets.toml o Streamlit Cloud.
# No escribir claves reales dentro del codigo.
# ============================================================

@st.cache_resource
def get_supabase_client():
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_SERVICE_ROLE_KEY"]

    return create_client(url, key)


# ============================================================
# LECTURAS CRUDAS
# Devuelven DataFrames casi igual a como vienen de Supabase.
# Luego las funciones *_app() renombran columnas para la app.
# ============================================================

@st.cache_data(ttl=300)
def get_resultados_supabase():
    supabase = get_supabase_client()

    response = (
        supabase
        .table("resultados")
        .select("*")
        .order("n_partido")
        .execute()
    )

    data = response.data or []

    return pd.DataFrame(data)


@st.cache_data(ttl=300)
def get_usuarios_supabase():
    supabase = get_supabase_client()

    response = (
        supabase
        .table("usuarios")
        .select("*")
        .order("usuario")
        .execute()
    )

    data = response.data or []

    return pd.DataFrame(data)


@st.cache_data(ttl=300)
def get_pronosticos_supabase():
    supabase = get_supabase_client()

    batch_size = 1000
    start = 0
    data = []

    while True:
        response = (
            supabase
            .table("pronosticos")
            .select("*")
            .order("usuario")
            .order("n_partido")
            .range(start, start + batch_size - 1)
            .execute()
        )

        batch = response.data or []
        data.extend(batch)

        if len(batch) < batch_size:
            break

        start += batch_size

    return pd.DataFrame(data)


@st.cache_data(ttl=300)
def get_eliminatoria_supabase():
    """Lee la tabla de fase eliminatoria sin modificar datos."""

    supabase = get_supabase_client()
    table_name = str(
        st.secrets.get(
            "SUPABASE_ELIMINATORIA_TABLE",
            "resultados_eliminatoria"
        )
    ).strip() or "resultados_eliminatoria"

    response = (
        supabase
        .table(table_name)
        .select("*")
        .order("n_partido")
        .execute()
    )

    data = response.data or []

    return pd.DataFrame(data)


@st.cache_data(ttl=300)
def get_pronosticos_eliminatoria_supabase():
    """Lee pronosticos de fase eliminatoria sin modificar datos."""

    supabase = get_supabase_client()
    table_name = str(
        st.secrets.get(
            "SUPABASE_PRONOSTICOS_ELIMINATORIA_TABLE",
            "pronosticos_eliminatoria"
        )
    ).strip() or "pronosticos_eliminatoria"

    response = (
        supabase
        .table(table_name)
        .select("*")
        .order("usuario")
        .order("n_partido")
        .execute()
    )

    data = response.data or []

    return pd.DataFrame(data)

# ============================================================
# ESCRITURA DE PRONOSTICOS
# Usa upsert: crea el pronostico si no existe o actualiza si ya
# existe para el mismo usuario y partido.
# ============================================================

def guardar_pronosticos_supabase(df_nuevos):
    """
    Guarda pronósticos en Supabase usando upsert.
    Si ya existe usuario + n_partido, actualiza p1 y p2.
    Si no existe, crea el registro.
    """

    supabase = get_supabase_client()

    if df_nuevos is None or df_nuevos.empty:
        return False, "No hay pronósticos para guardar."

    df_save = df_nuevos.copy()

    # Normalizamos nombres por si vienen desde el formato viejo
    rename_map = {
        "USUARIO": "usuario",
        "N_PARTIDO": "n_partido",
        "P1": "p1",
        "P2": "p2"
    }

    df_save = df_save.rename(columns=rename_map)

    columnas_requeridas = [
        "usuario",
        "n_partido",
        "p1",
        "p2"
    ]

    for col in columnas_requeridas:
        if col not in df_save.columns:
            return False, f"Falta la columna requerida: {col}"

    df_save = df_save[columnas_requeridas].copy()

    df_save["usuario"] = df_save["usuario"].astype(str)
    df_save["n_partido"] = df_save["n_partido"].astype(int)
    df_save["p1"] = df_save["p1"].astype(int)
    df_save["p2"] = df_save["p2"].astype(int)

    records = df_save.to_dict(orient="records")

    try:
        response = (
            supabase
            .table("pronosticos")
            .upsert(
                records,
                on_conflict="usuario,n_partido"
            )
            .execute()
        )

        # Limpiamos solo las funciones cacheadas de Supabase
        get_pronosticos_supabase.clear()

        return True, "Pronósticos guardados correctamente en Supabase."

    except Exception as e:
        return False, f"Error al guardar en Supabase: {e}"


def guardar_pronosticos_eliminatoria_supabase(df_nuevos):
    """
    Guarda pronosticos de fase eliminatoria usando upsert.
    No toca la tabla historica de pronosticos de fase de grupos.
    """

    supabase = get_supabase_client()
    table_name = str(
        st.secrets.get(
            "SUPABASE_PRONOSTICOS_ELIMINATORIA_TABLE",
            "pronosticos_eliminatoria"
        )
    ).strip() or "pronosticos_eliminatoria"

    if df_nuevos is None or df_nuevos.empty:
        return False, "No hay pronosticos para guardar."

    df_save = df_nuevos.copy()

    rename_map = {
        "USUARIO": "usuario",
        "N_PARTIDO": "n_partido",
        "P1": "p1",
        "P2": "p2",
        "CLASIFICADO_LADO": "clasificado_lado",
        "clasificado_lado": "clasificado_lado",
    }

    df_save = df_save.rename(columns=rename_map)
    columnas_requeridas = ["usuario", "n_partido", "p1", "p2"]

    for col in columnas_requeridas:
        if col not in df_save.columns:
            return False, f"Falta la columna requerida: {col}"

    if "clasificado_lado" not in df_save.columns:
        df_save["clasificado_lado"] = None

    df_save = df_save[columnas_requeridas + ["clasificado_lado"]].copy()
    df_save["usuario"] = df_save["usuario"].astype(str).str.strip()
    df_save["n_partido"] = pd.to_numeric(
        df_save["n_partido"],
        errors="coerce"
    )
    df_save["p1"] = pd.to_numeric(df_save["p1"], errors="coerce")
    df_save["p2"] = pd.to_numeric(df_save["p2"], errors="coerce")

    df_save = df_save.dropna(subset=["usuario", "n_partido", "p1", "p2"])

    if df_save.empty:
        return False, "No hay pronosticos validos para guardar."

    df_save["n_partido"] = df_save["n_partido"].astype(int)
    df_save["p1"] = df_save["p1"].astype(int)
    df_save["p2"] = df_save["p2"].astype(int)

    def resolver_clasificado(row):
        if row["p1"] > row["p2"]:
            return "equipo_1"

        if row["p2"] > row["p1"]:
            return "equipo_2"

        valor = str(row.get("clasificado_lado") or "").strip()

        if valor in ["equipo_1", "equipo_2"]:
            return valor

        return "equipo_1"

    df_save["clasificado_lado"] = df_save.apply(resolver_clasificado, axis=1)

    records = df_save.to_dict(orient="records")

    try:
        (
            supabase
            .table(table_name)
            .upsert(records, on_conflict="usuario,n_partido")
            .execute()
        )

        get_pronosticos_eliminatoria_supabase.clear()

        return True, "Pronosticos de eliminatoria guardados correctamente."

    except Exception as e:
        return False, f"Error al guardar pronosticos de eliminatoria: {e}"
        
# ============================================================
# ADAPTADORES PARA LA APP
# Convierten nombres de columnas de la base al formato historico
# que usan app.py y las pantallas.
# ============================================================

def get_resultados_app():
    df = get_resultados_supabase()

    if df.empty:
        return pd.DataFrame(
            columns=[
                "N_PARTIDO",
                "Equipo_1",
                "R1",
                "Equipo_2",
                "R2",
                "DIA",
                "HORA",
                "VIZ",
                "FECHA",
                "LIVE",
                "LIVE_R1",
                "LIVE_R2",
                "ESTADO_PARTIDO"
            ]
        )

    df = df.rename(
        columns={
            "n_partido": "N_PARTIDO",
            "equipo_1": "Equipo_1",
            "r1": "R1",
            "equipo_2": "Equipo_2",
            "r2": "R2",
            "dia": "DIA",
            "hora": "HORA",
            "viz": "VIZ",
            "fecha": "FECHA",
            "live": "LIVE",
            "live_r1": "LIVE_R1",
            "live_r2": "LIVE_R2",
            "estado_partido": "ESTADO_PARTIDO"
        }
    )

    columnas_necesarias = [
        "N_PARTIDO",
        "Equipo_1",
        "R1",
        "Equipo_2",
        "R2",
        "DIA",
        "HORA",
        "VIZ",
        "FECHA",
        "LIVE",
        "LIVE_R1",
        "LIVE_R2",
        "ESTADO_PARTIDO"
    ]

    for col in columnas_necesarias:
        if col not in df.columns:
            if col == "LIVE":
                df[col] = False
            elif col in ["LIVE_R1", "LIVE_R2"]:
                df[col] = None
            elif col == "ESTADO_PARTIDO":
                df[col] = "Pendiente"
            else:
                df[col] = ""

    df["LIVE"] = (
        df["LIVE"]
        .fillna(False)
        .astype(str)
        .str.strip()
        .str.upper()
        .isin(["TRUE", "1", "1.0", "VERDADERO", "T", "SI", "SÍ"])
    )

    df["ESTADO_PARTIDO"] = (
        df["ESTADO_PARTIDO"]
        .fillna("Pendiente")
        .astype(str)
        .str.strip()
        .replace({"": "Pendiente", "Sin live": "Pendiente"})
    )

    return df[columnas_necesarias]




def get_eliminatoria_app():
    """
    Devuelve la llave eliminatoria normalizada para Inicio V2.
    Si Supabase no responde o la tabla todavia no existe, devuelve un DataFrame vacio
    para que la vista use su mock local como respaldo.
    """

    columnas_necesarias = [
        "partido",
        "slot",
        "equipo_1",
        "equipo_2",
        "fase",
        "dia",
        "hora",
        "llave",
        "origen_1",
        "origen_2",
        "sig",
        "lado",
        "r1",
        "r2",
        "live",
        "live_r1",
        "live_r2",
        "estado_partido",
        "viz",
        "ganador",
        "perdedor",
        "clasificado_lado",
    ]

    try:
        df = get_eliminatoria_supabase()
    except Exception:
        return pd.DataFrame(columns=columnas_necesarias)

    if df.empty:
        return pd.DataFrame(columns=columnas_necesarias)

    df = df.rename(
        columns={
            "n_partido": "partido",
            "HS": "hora",
            "hs": "hora",
            "partido_origen1": "origen_1",
            "partido_origen2": "origen_2",
            "siguiente_partido_ganador": "sig",
            "lado_siguiente_ganador": "lado",
            "r1_live": "live_r1",
            "r2_live": "live_r2",
        }
    )

    for col in columnas_necesarias:
        if col not in df.columns:
            if col in ["partido", "slot"]:
                df[col] = 0
            elif col in ["r1", "r2", "live_r1", "live_r2", "origen_1", "origen_2", "sig"]:
                df[col] = None
            elif col in ["live", "viz"]:
                df[col] = False
            elif col == "estado_partido":
                df[col] = "Pendiente"
            else:
                df[col] = ""

    for col in ["partido", "slot", "origen_1", "origen_2", "sig"]:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    for col in ["r1", "r2", "live_r1", "live_r2"]:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    for col in ["equipo_1", "equipo_2", "fase", "dia", "hora", "llave", "lado", "estado_partido", "ganador", "perdedor", "clasificado_lado"]:
        df[col] = df[col].fillna("").astype(str).str.strip()

    df["estado_partido"] = df["estado_partido"].replace({"": "Pendiente"})
    df["clasificado_lado"] = df["clasificado_lado"].where(
        df["clasificado_lado"].isin(["equipo_1", "equipo_2"]),
        ""
    )

    fase_orden = {
        "16avos": 1,
        "Octavos": 2,
        "Cuartos": 3,
        "Semifinal": 4,
        "Final": 5,
        "Tercer Puesto": 6,
    }
    df["_fase_orden"] = df["fase"].map(fase_orden).fillna(99)

    df = df.sort_values(
        by=["_fase_orden", "llave", "slot", "partido"],
        na_position="last"
    )

    return df[columnas_necesarias]


def actualizar_equipos_eliminatoria_supabase(df_equipos):
    """
    Actualiza manualmente los equipos base de 16avos.
    No modifica resultados, estados ni la logica de avance del bracket.
    """

    supabase = get_supabase_client()
    table_name = str(
        st.secrets.get(
            "SUPABASE_ELIMINATORIA_TABLE",
            "resultados_eliminatoria"
        )
    ).strip() or "resultados_eliminatoria"

    if df_equipos is None or df_equipos.empty:
        return False, "No hay equipos para guardar."

    df_save = df_equipos.copy()
    df_save = df_save.rename(
        columns={
            "N_PARTIDO": "n_partido",
            "partido": "n_partido",
            "Equipo_1": "equipo_1",
            "Equipo_2": "equipo_2",
            "EQUIPO_1": "equipo_1",
            "EQUIPO_2": "equipo_2",
        }
    )

    columnas_requeridas = ["n_partido", "equipo_1", "equipo_2"]
    faltantes = [col for col in columnas_requeridas if col not in df_save.columns]

    if faltantes:
        return False, f"Faltan columnas requeridas: {', '.join(faltantes)}"

    df_save["n_partido"] = pd.to_numeric(df_save["n_partido"], errors="coerce")
    df_save = df_save.dropna(subset=["n_partido"]).copy()
    df_save["n_partido"] = df_save["n_partido"].astype(int)
    df_save = df_save[
        df_save["n_partido"].between(1, 16)
    ].copy()

    if df_save.empty:
        return False, "No hay partidos de 16avos para actualizar."

    try:
        actualizados = 0

        for _, row in df_save.iterrows():
            n_partido = int(row["n_partido"])
            equipo_1 = str(row.get("equipo_1", "")).strip() or "Equipo 1"
            equipo_2 = str(row.get("equipo_2", "")).strip() or "Equipo 2"

            supabase.table(table_name).update(
                {
                    "equipo_1": equipo_1,
                    "equipo_2": equipo_2,
                }
            ).eq(
                "n_partido",
                n_partido
            ).execute()

            actualizados += 1

        get_eliminatoria_supabase.clear()

        return True, f"Equipos iniciales actualizados: {actualizados} partidos."

    except Exception as e:
        return False, f"Error al actualizar equipos de eliminatoria: {e}"


def guardar_resultado_eliminatoria_supabase(
    n_partido,
    r1,
    r2,
    clasificado_lado=None,
    estado_partido="Finalizado"
):
    """
    Guarda el estado de un partido eliminatorio.
    En Vivo/Entretiempo actualiza marcador live. Finalizado actualiza resultado oficial.
    """

    supabase = get_supabase_client()
    table_name = str(
        st.secrets.get(
            "SUPABASE_ELIMINATORIA_TABLE",
            "resultados_eliminatoria"
        )
    ).strip() or "resultados_eliminatoria"

    try:
        n_partido = int(n_partido)
    except (TypeError, ValueError):
        return False, "Selecciona un partido valido."

    r1_val = pd.to_numeric(r1, errors="coerce")
    r2_val = pd.to_numeric(r2, errors="coerce")

    estado_normalizado = str(estado_partido or "").strip()
    if estado_normalizado == "Sin live":
        estado_normalizado = "Pendiente"

    estados_validos = ["Pendiente", "En Vivo", "Entretiempo", "Finalizado"]

    if estado_normalizado not in estados_validos:
        return False, "Selecciona un estado valido."

    if pd.isna(r1_val) or pd.isna(r2_val):
        return False, "Carga ambos resultados."

    r1_val = int(r1_val)
    r2_val = int(r2_val)

    try:
        es_visual = estado_normalizado in ["En Vivo", "Entretiempo"]
        es_finalizado = estado_normalizado == "Finalizado"
        lado = str(clasificado_lado or "").strip()

        data_update = {
            "estado_partido": estado_normalizado,
            "live": es_visual,
        }

        data_update["clasificado_lado"] = (
            lado
            if lado in ["equipo_1", "equipo_2"]
            else None
        )

        if estado_normalizado == "Pendiente":
            data_update.update(
                {
                    "live": False,
                    "live_r1": None,
                    "live_r2": None,
                }
            )

        if es_visual:
            data_update.update(
                {
                    "live_r1": r1_val,
                    "live_r2": r2_val,
                }
            )

        if not es_finalizado:
            try:
                (
                    supabase
                    .table(table_name)
                    .update(data_update)
                    .eq("n_partido", n_partido)
                    .execute()
                )
            except Exception:
                data_update_alt = dict(data_update)

                if "live_r1" in data_update_alt:
                    data_update_alt["r1_live"] = data_update_alt.pop("live_r1")

                if "live_r2" in data_update_alt:
                    data_update_alt["r2_live"] = data_update_alt.pop("live_r2")

                try:
                    (
                        supabase
                        .table(table_name)
                        .update(data_update_alt)
                        .eq("n_partido", n_partido)
                        .execute()
                    )
                except Exception:
                    data_update_min = {
                        "estado_partido": estado_normalizado,
                    }
                    (
                        supabase
                        .table(table_name)
                        .update(data_update_min)
                        .eq("n_partido", n_partido)
                        .execute()
                    )

            get_eliminatoria_supabase.clear()
            return True, f"Estado del partido #{n_partido} actualizado."

        response = (
            supabase
            .table(table_name)
            .select("equipo_1,equipo_2")
            .eq("n_partido", n_partido)
            .limit(1)
            .execute()
        )

        rows = response.data or []

        if not rows:
            return False, f"No se encontro el partido #{n_partido}."

        partido = rows[0]
        equipo_1 = str(partido.get("equipo_1", "") or "").strip()
        equipo_2 = str(partido.get("equipo_2", "") or "").strip()

        lado = str(clasificado_lado or "").strip()

        if r1_val > r2_val:
            lado = "equipo_1"
        elif r2_val > r1_val:
            lado = "equipo_2"
        elif lado not in ["equipo_1", "equipo_2"]:
            return False, "En un empate selecciona que equipo clasifica."

        ganador = equipo_1 if lado == "equipo_1" else equipo_2
        perdedor = equipo_2 if lado == "equipo_1" else equipo_1

        data_update = {
            "r1": r1_val,
            "r2": r2_val,
            "estado_partido": estado_normalizado,
            "clasificado_lado": lado,
            "ganador": ganador,
            "perdedor": perdedor,
        }

        data_update_con_live = {
            **data_update,
            "live": False,
            "live_r1": None,
            "live_r2": None,
        }

        try:
            (
                supabase
                .table(table_name)
                .update(data_update_con_live)
                .eq("n_partido", n_partido)
                .execute()
            )
        except Exception:
            data_update_con_live_alt = {
                **data_update,
                "live": False,
                "r1_live": None,
                "r2_live": None,
            }

            try:
                (
                    supabase
                    .table(table_name)
                    .update(data_update_con_live_alt)
                    .eq("n_partido", n_partido)
                    .execute()
                )
            except Exception:
                (
                    supabase
                    .table(table_name)
                    .update(data_update)
                    .eq("n_partido", n_partido)
                    .execute()
                )

        get_eliminatoria_supabase.clear()

        return True, f"Resultado oficial del partido #{n_partido} guardado."

    except Exception as e:
        return False, f"Error al guardar resultado eliminatorio: {e}"


def get_pronosticos_eliminatoria_app():
    """
    Devuelve pronosticos de eliminatoria normalizados.
    Si la tabla todavia no existe, devuelve vacio para que Inicio V2 no falle.
    """

    columnas_necesarias = [
        "USUARIO",
        "N_PARTIDO",
        "P1",
        "P2",
        "CLASIFICADO_LADO",
    ]

    try:
        df = get_pronosticos_eliminatoria_supabase()
    except Exception:
        return pd.DataFrame(columns=columnas_necesarias)

    if df.empty:
        return pd.DataFrame(columns=columnas_necesarias)

    df = df.rename(
        columns={
            "usuario": "USUARIO",
            "n_partido": "N_PARTIDO",
            "p1": "P1",
            "p2": "P2",
            "clasificado_lado": "CLASIFICADO_LADO",
        }
    )

    for col in columnas_necesarias:
        if col not in df.columns:
            if col in ["N_PARTIDO", "P1", "P2"]:
                df[col] = None
            else:
                df[col] = ""

    df["USUARIO"] = df["USUARIO"].fillna("").astype(str).str.strip()
    df["N_PARTIDO"] = pd.to_numeric(df["N_PARTIDO"], errors="coerce")
    df["P1"] = pd.to_numeric(df["P1"], errors="coerce")
    df["P2"] = pd.to_numeric(df["P2"], errors="coerce")
    df["CLASIFICADO_LADO"] = (
        df["CLASIFICADO_LADO"]
        .fillna("")
        .astype(str)
        .str.strip()
    )

    return df[columnas_necesarias]


def get_usuarios_app():
    df = get_usuarios_supabase()

    if df.empty:
        return pd.DataFrame(
            columns=[
                "ID",
                "USUARIO",
                "NOMBRE",
                "CONTRASEÑA",
                "EQUIPO FAVORITO",
                "AVATAR_URL",
                "EDAD",
                "DESCRIPCION",
                "ROL",
                "APORTE_REALIZADO",
                "ELIMINATORIA"
            ]
        )

    df = df.rename(
        columns={
            "id": "ID",
            "usuario": "USUARIO",
            "nombre": "NOMBRE",
            "contrasena": "CONTRASEÑA",
            "equipo_favorito": "EQUIPO FAVORITO",
            "avatar_url": "AVATAR_URL",
            "edad": "EDAD",
            "descripcion": "DESCRIPCION",
            "rol": "ROL",
            "aporte_realizado": "APORTE_REALIZADO",
            "eliminatoria": "ELIMINATORIA"
        }
    )

    columnas_necesarias = [
        "ID",
        "USUARIO",
        "NOMBRE",
        "CONTRASEÑA",
        "EQUIPO FAVORITO",
        "AVATAR_URL",
        "EDAD",
        "DESCRIPCION",
        "ROL",
        "APORTE_REALIZADO",
        "ELIMINATORIA"
    ]

    for col in columnas_necesarias:
        if col not in df.columns:
            if col == "ID":
                df[col] = range(1, len(df) + 1)
            elif col == "APORTE_REALIZADO":
                df[col] = False
            elif col == "ELIMINATORIA":
                df[col] = True
            else:
                df[col] = ""

    df["APORTE_REALIZADO"] = (
        df["APORTE_REALIZADO"]
        .fillna(False)
        .astype(str)
        .str.strip()
        .str.upper()
        .isin(["TRUE", "1", "1.0", "VERDADERO", "T", "SI", "SÍ"])
    )

    df["ELIMINATORIA"] = (
        df["ELIMINATORIA"]
        .fillna(True)
        .astype(str)
        .str.strip()
        .str.upper()
        .isin(["TRUE", "1", "1.0", "VERDADERO", "T", "SI", "SÍ"])
    )

    return df[columnas_necesarias]

def get_pronosticos_app():
    df = get_pronosticos_supabase()

    if df.empty:
        return pd.DataFrame(
            columns=[
                "N_PARTIDO",
                "USUARIO",
                "P1",
                "P2"
            ]
        )

    df = df.rename(
        columns={
            "n_partido": "N_PARTIDO",
            "usuario": "USUARIO",
            "p1": "P1",
            "p2": "P2"
        }
    )

    columnas_necesarias = [
        "N_PARTIDO",
        "USUARIO",
        "P1",
        "P2"
    ]

    for col in columnas_necesarias:
        if col not in df.columns:
            df[col] = ""

    return df[columnas_necesarias]
@st.cache_data(ttl=300)
def get_foro_supabase():
    supabase = get_supabase_client()

    response = (
        supabase
        .table("foro")
        .select("*")
        .order("id", desc=True)
        .execute()
    )

    data = response.data or []

    return pd.DataFrame(data)


@st.cache_data(ttl=300)
def get_noticias_supabase():
    supabase = get_supabase_client()

    response = (
        supabase
        .table("noticias")
        .select("*")
        .order("prioridad", desc=False)
        .order("id", desc=True)
        .execute()
    )

    data = response.data or []

    return pd.DataFrame(data)


def get_foro_app():
    df = get_foro_supabase()

    columnas_app = [
        "ID",
        "FECHA",
        "USUARIO",
        "NOMBRE",
        "MENSAJE",
        "PARTIDO_ID",
        "LIKES",
        "DISLIKES",
        "FORO_IMG_URL"
    ]

    if df.empty:
        return pd.DataFrame(columns=columnas_app)

    df = df.rename(
        columns={
            "id": "ID",
            "fecha": "FECHA",
            "usuario": "USUARIO",
            "nombre": "NOMBRE",
            "mensaje": "MENSAJE",
            "partido_id": "PARTIDO_ID",
            "likes": "LIKES",
            "dislikes": "DISLIKES",
            "foro_img_url": "FORO_IMG_URL"
        }
    )

    for col in columnas_app:
        if col not in df.columns:
            if col in ["ID", "PARTIDO_ID", "LIKES", "DISLIKES"]:
                df[col] = 0
            else:
                df[col] = ""

    df["ID"] = pd.to_numeric(
        df["ID"],
        errors="coerce"
    ).fillna(0).astype(int)

    df["PARTIDO_ID"] = pd.to_numeric(
        df["PARTIDO_ID"],
        errors="coerce"
    ).fillna(0).astype(int)

    df["LIKES"] = pd.to_numeric(
        df["LIKES"],
        errors="coerce"
    ).fillna(0).astype(int)

    df["DISLIKES"] = pd.to_numeric(
        df["DISLIKES"],
        errors="coerce"
    ).fillna(0).astype(int)

    return df[columnas_app]


def get_noticias_app():
    df = get_noticias_supabase()

    columnas_app = [
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

    if df.empty:
        return pd.DataFrame(columns=columnas_app)

    df = df.rename(
        columns={
            "id": "ID",
            "fecha": "FECHA",
            "tipo": "TIPO",
            "titulo": "TITULO",
            "texto": "TEXTO",
            "autor": "AUTOR",
            "visible": "VISIBLE",
            "prioridad": "PRIORIDAD",
            "link": "LINK",
            "imagen_url": "IMAGEN_URL",
            "fuente": "FUENTE"
        }
    )

    for col in columnas_app:
        if col not in df.columns:
            if col == "ID":
                df[col] = None
            elif col == "PRIORIDAD":
                df[col] = 99
            elif col == "VISIBLE":
                df[col] = True
            else:
                df[col] = ""

    # Para compatibilidad con tu código actual, dejamos visible como TRUE/FALSE.
    df["VISIBLE"] = (
        df["VISIBLE"]
        .astype(str)
        .str.upper()
        .replace(
            {
                "TRUE": "TRUE",
                "FALSE": "FALSE",
                "1": "TRUE",
                "0": "FALSE",
                "NAN": "TRUE",
                "NONE": "TRUE"
            }
        )
    )

    return df[columnas_app]

# ============================================================
# FORO Y NOTICIAS
# Estas funciones escriben en la base real si los secretos
# locales apuntan al proyecto productivo.
# ============================================================

def insertar_foro_supabase(df_nuevo):
    """
    Inserta uno o más mensajes nuevos en la tabla foro.
    No borra ni reemplaza mensajes anteriores.
    """

    supabase = get_supabase_client()

    if df_nuevo is None:
        return False, "No hay mensaje para guardar."

    if isinstance(df_nuevo, dict):
        df_save = pd.DataFrame([df_nuevo])
    else:
        df_save = df_nuevo.copy()

    if df_save.empty:
        return False, "No hay mensaje para guardar."

    rename_map = {
        "FECHA": "fecha",
        "USUARIO": "usuario",
        "NOMBRE": "nombre",
        "MENSAJE": "mensaje",
        "PARTIDO_ID": "partido_id",
        "LIKES": "likes",
        "DISLIKES": "dislikes",
        "FORO_IMG_URL": "foro_img_url"
    }

    df_save = df_save.rename(columns=rename_map)

    columnas = [
        "fecha",
        "usuario",
        "nombre",
        "mensaje",
        "partido_id",
        "likes",
        "dislikes",
        "foro_img_url"
    ]

    for col in columnas:
        if col not in df_save.columns:
            if col in ["partido_id", "likes", "dislikes"]:
                df_save[col] = 0
            else:
                df_save[col] = ""

    df_save = df_save[columnas].copy()

    columnas_texto = [
        "fecha",
        "usuario",
        "nombre",
        "mensaje",
        "foro_img_url"
    ]

    for col in columnas_texto:
        df_save[col] = (
            df_save[col]
            .fillna("")
            .astype(str)
            .replace("nan", "")
            .replace("None", "")
        )

    df_save["partido_id"] = pd.to_numeric(
        df_save["partido_id"],
        errors="coerce"
    ).fillna(0).astype(int)

    df_save["likes"] = pd.to_numeric(
        df_save["likes"],
        errors="coerce"
    ).fillna(0).astype(int)

    df_save["dislikes"] = pd.to_numeric(
        df_save["dislikes"],
        errors="coerce"
    ).fillna(0).astype(int)

    df_save = df_save.where(pd.notnull(df_save), None)

    records = df_save.to_dict(orient="records")

    try:
        supabase.table("foro").insert(records).execute()

        get_foro_supabase.clear()

        return True, "Mensaje publicado correctamente en Supabase."

    except Exception as e:
        return False, f"Error al publicar mensaje en Supabase: {e}"


def guardar_noticias_supabase(df_noticias):
    """
    Guarda noticias sin borrar la tabla completa.

    - Si la fila tiene ID: actualiza esa noticia.
    - Si la fila no tiene ID: inserta una noticia nueva.
    - No borra noticias anteriores.
    """

    supabase = get_supabase_client()

    if df_noticias is None:
        return False, "No hay datos de noticias para guardar."

    df_save = df_noticias.copy()
    
    # Evita guardar filas completamente vacías generadas por el editor.
    df_save = df_save.dropna(
        how="all"
    ).copy()
    
    if df_save.empty:
        return False, "No hay noticias válidas para guardar."
    
    rename_map = {
        "ID": "id",
        "FECHA": "fecha",
        "TIPO": "tipo",
        "TITULO": "titulo",
        "TEXTO": "texto",
        "AUTOR": "autor",
        "VISIBLE": "visible",
        "PRIORIDAD": "prioridad",
        "LINK": "link",
        "IMAGEN_URL": "imagen_url",
        "FUENTE": "fuente"
    }

    df_save = df_save.rename(columns=rename_map)

    columnas = [
        "id",
        "fecha",
        "tipo",
        "titulo",
        "texto",
        "autor",
        "visible",
        "prioridad",
        "link",
        "imagen_url",
        "fuente"
    ]

    for col in columnas:
        if col not in df_save.columns:
            if col == "id":
                df_save[col] = None
            elif col == "prioridad":
                df_save[col] = 99
            elif col == "visible":
                df_save[col] = True
            else:
                df_save[col] = ""

    # Validación mínima: no insertar noticias totalmente vacías.
    df_save["titulo"] = df_save["titulo"].fillna("").astype(str).str.strip()
    df_save["texto"] = df_save["texto"].fillna("").astype(str).str.strip()
    
    df_save = df_save[
        (df_save["titulo"] != "") | (df_save["texto"] != "")
    ].copy()
    
    if df_save.empty:
        return False, "La noticia debe tener al menos título o texto."

    # ------------------------------------------------------------
    # NORMALIZAR TEXTO
    # ------------------------------------------------------------

    columnas_texto = [
        "fecha",
        "tipo",
        "titulo",
        "texto",
        "autor",
        "link",
        "imagen_url",
        "fuente"
    ]

    for col in columnas_texto:
        df_save[col] = (
            df_save[col]
            .fillna("")
            .astype(str)
            .replace("nan", "")
            .replace("None", "")
        )

    # ------------------------------------------------------------
    # NORMALIZAR NÚMEROS Y BOOLEANOS
    # ------------------------------------------------------------

    df_save["prioridad"] = pd.to_numeric(
        df_save["prioridad"],
        errors="coerce"
    ).fillna(99).astype(int)

    df_save["visible"] = (
        df_save["visible"]
        .fillna(True)
        .astype(str)
        .str.strip()
        .str.upper()
        .isin(["TRUE", "1", "1.0", "VERDADERO", "T", "SI", "SÍ"])
    )

    df_save["id"] = pd.to_numeric(
        df_save["id"],
        errors="coerce"
    )

    # Limpieza final contra NaN
    df_save = df_save.where(pd.notnull(df_save), None)

    try:
        # ------------------------------------------------------------
        # ACTUALIZAR FILAS EXISTENTES
        # ------------------------------------------------------------

        df_existentes = df_save[
            df_save["id"].notna()
        ].copy()

        for _, row in df_existentes.iterrows():
            noticia_id = int(row["id"])

            record = row.drop(labels=["id"]).to_dict()

            supabase.table("noticias").update(record).eq(
                "id",
                noticia_id
            ).execute()

        # ------------------------------------------------------------
        # INSERTAR FILAS NUEVAS
        # ------------------------------------------------------------

        df_nuevas = df_save[
            df_save["id"].isna()
        ].copy()

        if not df_nuevas.empty:
            records_nuevos = (
                df_nuevas
                .drop(columns=["id"], errors="ignore")
                .to_dict(orient="records")
            )

            supabase.table("noticias").insert(records_nuevos).execute()

        get_noticias_supabase.clear()

        return True, "Noticias guardadas correctamente en Supabase."

    except Exception as e:
        return False, f"Error al guardar noticias en Supabase: {e}"

def actualizar_reaccion_foro_supabase(post_id, likes=None, dislikes=None):
    """
    Actualiza likes/dislikes de un mensaje puntual del foro.
    No reemplaza toda la tabla.
    """

    supabase = get_supabase_client()

    try:
        post_id = int(post_id)

        if post_id <= 0:
            return False, "ID de mensaje inválido."

        data_update = {}

        if likes is not None:
            data_update["likes"] = int(likes)

        if dislikes is not None:
            data_update["dislikes"] = int(dislikes)

        if not data_update:
            return False, "No hay datos para actualizar."

        supabase.table("foro").update(data_update).eq(
            "id",
            post_id
        ).execute()

        get_foro_supabase.clear()

        return True, "Reacción actualizada correctamente."

    except Exception as e:
        return False, f"Error al actualizar reacción: {e}"


def borrar_mensaje_foro_supabase(post_id):
    """
    Borra un mensaje puntual del foro por ID.
    No reemplaza ni limpia toda la tabla.
    """

    supabase = get_supabase_client()

    try:
        post_id = int(post_id)

        if post_id <= 0:
            return False, "ID de mensaje inválido."

        response = (
            supabase
            .table("foro")
            .delete()
            .eq("id", post_id)
            .select("id")
            .execute()
        )

        data = response.data or []

        if len(data) == 0:
            return False, f"No se encontró el mensaje con ID {post_id}."

        get_foro_supabase.clear()

        return True, "Mensaje eliminado correctamente."

    except Exception as e:
        return False, f"Error al borrar mensaje: {e}"

def insertar_noticia_supabase(noticia):
    """
    Inserta una noticia nueva en Supabase.
    No borra ni modifica noticias anteriores.
    """

    supabase = get_supabase_client()

    if noticia is None:
        return False, "No hay noticia para guardar."

    if isinstance(noticia, dict):
        df_save = pd.DataFrame([noticia])
    else:
        df_save = noticia.copy()

    if df_save.empty:
        return False, "No hay noticia para guardar."

    rename_map = {
        "ID": "id",
        "FECHA": "fecha",
        "TIPO": "tipo",
        "TITULO": "titulo",
        "TEXTO": "texto",
        "AUTOR": "autor",
        "VISIBLE": "visible",
        "PRIORIDAD": "prioridad",
        "LINK": "link",
        "IMAGEN_URL": "imagen_url",
        "FUENTE": "fuente"
    }

    df_save = df_save.rename(columns=rename_map)

    columnas = [
        "fecha",
        "tipo",
        "titulo",
        "texto",
        "autor",
        "visible",
        "prioridad",
        "link",
        "imagen_url",
        "fuente"
    ]

    for col in columnas:
        if col not in df_save.columns:
            if col == "prioridad":
                df_save[col] = 99
            elif col == "visible":
                df_save[col] = True
            else:
                df_save[col] = ""

    df_save = df_save[columnas].copy()

    columnas_texto = [
        "fecha",
        "tipo",
        "titulo",
        "texto",
        "autor",
        "link",
        "imagen_url",
        "fuente"
    ]

    for col in columnas_texto:
        df_save[col] = (
            df_save[col]
            .fillna("")
            .astype(str)
            .replace("nan", "")
            .replace("None", "")
        )

    df_save["prioridad"] = pd.to_numeric(
        df_save["prioridad"],
        errors="coerce"
    ).fillna(99).astype(int)

    df_save["visible"] = (
        df_save["visible"]
        .fillna(True)
        .astype(str)
        .str.strip()
        .str.upper()
        .isin(["TRUE", "1", "1.0", "VERDADERO", "T", "SI", "SÍ"])
    )

    df_save = df_save.where(pd.notnull(df_save), None)

    records = df_save.to_dict(orient="records")

    try:
        supabase.table("noticias").insert(records).execute()

        get_noticias_supabase.clear()

        return True, "Noticia publicada correctamente en Supabase."

    except Exception as e:
        return False, f"Error al publicar noticia en Supabase: {e}"

# ============================================================
# USUARIOS Y ROLES
# Gestiona perfil, registro, eliminacion y permisos.
# ============================================================

def actualizar_usuario_supabase(usuario, datos):
    """
    Actualiza datos de un usuario en Supabase.
    No modifica otros usuarios.
    """

    supabase = get_supabase_client()

    if not usuario:
        return False, "Usuario inválido."

    if datos is None or not isinstance(datos, dict):
        return False, "No hay datos para actualizar."

    rename_map = {
        "USUARIO": "usuario",
        "NOMBRE": "nombre",
        "CONTRASEÑA": "contrasena",
        "EQUIPO FAVORITO": "equipo_favorito",
        "AVATAR_URL": "avatar_url",
        "EDAD": "edad",
        "DESCRIPCION": "descripcion",
        "ROL": "rol",
        "APORTE_REALIZADO": "aporte_realizado",
        "ELIMINATORIA": "eliminatoria"
    }

    data_update = {}

    for key, value in datos.items():
        col = rename_map.get(key, key)

        if col in [
            "nombre",
            "contrasena",
            "equipo_favorito",
            "avatar_url",
            "edad",
            "descripcion",
            "rol",
            "aporte_realizado",
            "eliminatoria"
        ]:
            if pd.isna(value):
                value = None

            if col == "edad":
                try:
                    value = int(value)
                except Exception:
                    value = None

            if col == "aporte_realizado":
                value = (
                    str(value)
                    .strip()
                    .upper()
                    in ["TRUE", "1", "1.0", "VERDADERO", "T", "SI", "SÍ"]
                )

            if col == "eliminatoria":
                value = (
                    str(value)
                    .strip()
                    .upper()
                    in ["TRUE", "1", "1.0", "VERDADERO", "T", "SI", "SÍ"]
                )

            data_update[col] = value

    if not data_update:
        return False, "No hay campos válidos para actualizar."

    try:
        supabase.table("usuarios").update(data_update).eq(
            "usuario",
            str(usuario)
        ).execute()

        get_usuarios_supabase.clear()

        return True, "Usuario actualizado correctamente en Supabase."

    except Exception as e:
        return False, f"Error al actualizar usuario en Supabase: {e}"


def actualizar_aporte_usuario_supabase(usuario, aporte_realizado):
    """
    Marca si un usuario ya realizo el aporte.
    Actualiza solo la columna aporte_realizado en Supabase.
    """

    if not usuario:
        return False, "Usuario invalido."

    try:
        aporte_bool = bool(aporte_realizado)

        return actualizar_usuario_supabase(
            usuario=usuario,
            datos={"APORTE_REALIZADO": aporte_bool}
        )

    except Exception as e:
        return False, f"Error al actualizar aporte del usuario: {e}"


def actualizar_eliminatoria_usuario_supabase(usuario, eliminatoria):
    """
    Marca si un usuario participa en la fase eliminatoria.
    Actualiza solo la columna eliminatoria en Supabase.
    """

    if not usuario:
        return False, "Usuario invalido."

    try:
        eliminatoria_bool = bool(eliminatoria)

        return actualizar_usuario_supabase(
            usuario=usuario,
            datos={"ELIMINATORIA": eliminatoria_bool}
        )

    except Exception as e:
        return False, f"Error al actualizar eliminatoria del usuario: {e}"

def registrar_usuario_supabase(
    nombre,
    usuario,
    contrasena,
    avatar_url,
    equipo_favorito,
    rol="jugador"
):
    """
    Registra un usuario nuevo en Supabase.
    No usa Google Sheets.
    """

    supabase = get_supabase_client()

    nombre = str(nombre).strip()
    usuario = str(usuario).strip()
    contrasena = str(contrasena).strip()
    equipo_favorito = str(equipo_favorito).strip()

    if not nombre or not usuario or not contrasena:
        return False, "Nombre, usuario y contraseña son obligatorios."

    try:
        existente = (
            supabase
            .table("usuarios")
            .select("usuario")
            .eq("usuario", usuario)
            .execute()
        )

        if existente.data:
            return False, "Ese usuario ya existe. Elegí otro nick."

        nuevo_usuario = {
            "usuario": usuario,
            "nombre": nombre,
            "contrasena": contrasena,
            "equipo_favorito": equipo_favorito,
            "avatar_url": avatar_url,
            "edad": None,
            "descripcion": "",
            "rol": rol,
            "aporte_realizado": False,
            "eliminatoria": True
        }

        response = (
            supabase
            .table("usuarios")
            .insert(nuevo_usuario)
            .execute()
        )

        if not response.data:
            return False, "No se pudo registrar el usuario."

        get_usuarios_supabase.clear()

        return True, "Usuario registrado correctamente."

    except Exception as e:
        return False, f"Error al registrar usuario en Supabase: {e}"

def eliminar_usuario_supabase(usuario):
    """
    Elimina un usuario y sus pronósticos asociados.
    No elimina mensajes del foro ni noticias.
    """

    supabase = get_supabase_client()

    if not usuario:
        return False, "Usuario inválido."

    usuario = str(usuario).strip()

    try:
        # Primero borramos pronósticos asociados
        supabase.table("pronosticos").delete().eq(
            "usuario",
            usuario
        ).execute()

        # Después borramos el usuario
        response = (
            supabase
            .table("usuarios")
            .delete()
            .eq("usuario", usuario)
            .select("*")
            .execute()
        )

        data = response.data or []

        if len(data) == 0:
            return False, f"No se encontró el usuario '{usuario}' para eliminar."

        get_usuarios_supabase.clear()
        get_pronosticos_supabase.clear()

        return True, f"Usuario '{usuario}' eliminado correctamente."

    except Exception as e:
        return False, f"Error al eliminar usuario en Supabase: {e}"


def actualizar_rol_usuario_supabase(usuario, nuevo_rol):
    """
    Cambia el rol de un usuario.
    Roles esperados: jugador, colaborador, admin.
    """

    supabase = get_supabase_client()

    if not usuario:
        return False, "Usuario inválido."

    usuario = str(usuario).strip()
    nuevo_rol = str(nuevo_rol).strip().lower()

    roles_validos = ["jugador", "colaborador", "admin"]

    if nuevo_rol not in roles_validos:
        return False, "Rol inválido."

    try:
        response = (
            supabase
            .table("usuarios")
            .update({"rol": nuevo_rol})
            .eq("usuario", usuario)
            .select("*")
            .execute()
        )

        data = response.data or []

        if len(data) == 0:
            return False, f"No se encontró el usuario '{usuario}'."

        get_usuarios_supabase.clear()

        return True, f"Rol de '{usuario}' actualizado a '{nuevo_rol}'."

    except Exception as e:
        return False, f"Error al actualizar rol en Supabase: {e}"

# ============================================================
# CONFIGURACION GENERAL
# Controla mantenimiento, registro y cierre de pronosticos.
# ============================================================

@st.cache_data(ttl=300)
def get_config_supabase():
    supabase = get_supabase_client()

    response = (
        supabase
        .table("config")
        .select("*")
        .execute()
    )

    data = response.data or []

    return pd.DataFrame(data)


def get_config_app():
    df = get_config_supabase()

    valores_default = {
        "mantenimiento": "OFF",
        "registro": "ON",
        "pronosticos_estado": "ON",
        "cierre_pronosticos": "2026-06-11 15:00",
        "pronosticos_eliminatoria_estado": "ON",
        "cierre_eliminatoria_16avos": "2026-06-28 15:00",
        "cierre_eliminatoria_octavos": "2026-07-03 23:59",
        "cierre_eliminatoria_cuartos": "2026-07-08 23:59",
        "cierre_eliminatoria_semifinal": "2026-07-13 23:59",
        "cierre_eliminatoria_final": "2026-07-17 23:59"
    }

    config_dict = valores_default.copy()

    if df is not None and not df.empty:
        if "clave" in df.columns and "valor" in df.columns:
            for _, row in df.iterrows():
                clave = str(row.get("clave", "")).strip().lower()
                valor = str(row.get("valor", "")).strip()

                if clave in config_dict and valor != "":
                    config_dict[clave] = valor

    mantenimiento = str(config_dict["mantenimiento"]).strip().upper()
    registro = str(config_dict["registro"]).strip().upper()
    pronosticos_estado = str(config_dict["pronosticos_estado"]).strip().upper()
    cierre_pronosticos = str(config_dict["cierre_pronosticos"]).strip()
    pronosticos_eliminatoria_estado = (
        str(config_dict["pronosticos_eliminatoria_estado"]).strip().upper()
    )

    if mantenimiento not in ["ON", "OFF"]:
        mantenimiento = "OFF"

    if registro not in ["ON", "OFF"]:
        registro = "ON"

    if pronosticos_estado not in ["ON", "OFF"]:
        pronosticos_estado = "ON"

    if pronosticos_eliminatoria_estado not in ["ON", "OFF"]:
        pronosticos_eliminatoria_estado = "ON"

    if cierre_pronosticos == "":
        cierre_pronosticos = "2026-06-11 15:00"

    return pd.DataFrame(
        [
            {
                "MANTENIMIENTO": mantenimiento,
                "REGISTRO": registro,
                "PRONOSTICOS_ESTADO": pronosticos_estado,
                "CIERRE_PRONOSTICOS": cierre_pronosticos,
                "PRONOSTICOS_ELIMINATORIA_ESTADO": pronosticos_eliminatoria_estado,
                "CIERRE_ELIMINATORIA_16AVOS": str(config_dict["cierre_eliminatoria_16avos"]).strip(),
                "CIERRE_ELIMINATORIA_OCTAVOS": str(config_dict["cierre_eliminatoria_octavos"]).strip(),
                "CIERRE_ELIMINATORIA_CUARTOS": str(config_dict["cierre_eliminatoria_cuartos"]).strip(),
                "CIERRE_ELIMINATORIA_SEMIFINAL": str(config_dict["cierre_eliminatoria_semifinal"]).strip(),
                "CIERRE_ELIMINATORIA_FINAL": str(config_dict["cierre_eliminatoria_final"]).strip()
            }
        ]
    )


def actualizar_config_supabase(campo, valor):
    """
    Actualiza un valor de configuración en tabla config tipo clave/valor.

    Estructura esperada:
    - clave
    - valor
    - updated_at
    """

    supabase = get_supabase_client()

    campo = str(campo).strip().lower()

    campos_validos = [
        "mantenimiento",
        "registro",
        "pronosticos_estado",
        "cierre_pronosticos",
        "pronosticos_eliminatoria_estado",
        "cierre_eliminatoria_16avos",
        "cierre_eliminatoria_octavos",
        "cierre_eliminatoria_cuartos",
        "cierre_eliminatoria_semifinal",
        "cierre_eliminatoria_final"
    ]

    if campo not in campos_validos:
        return False, "Campo de configuración inválido."

    if campo in [
        "mantenimiento",
        "registro",
        "pronosticos_estado",
        "pronosticos_eliminatoria_estado"
    ]:
        valor = str(valor).strip().upper()

        if valor not in ["ON", "OFF"]:
            return False, "Valor inválido. Usá ON u OFF."

    elif campo in [
        "cierre_pronosticos",
        "cierre_eliminatoria_16avos",
        "cierre_eliminatoria_octavos",
        "cierre_eliminatoria_cuartos",
        "cierre_eliminatoria_semifinal",
        "cierre_eliminatoria_final"
    ]:
        valor = str(valor).strip()

        if not valor:
            return False, "La fecha de cierre de pronósticos no puede estar vacía."

    try:
        response = (
            supabase
            .table("config")
            .upsert(
                {
                    "clave": campo,
                    "valor": valor
                },
                on_conflict="clave"
            )
            .execute()
        )

        get_config_supabase.clear()

        return True, "Configuración actualizada correctamente."

    except Exception as e:
        return False, f"Error al actualizar configuración: {e}"


def guardar_resultados_supabase(df_resultados):
    """
    Actualiza resultados oficiales en Supabase.
    No inserta partidos nuevos.
    Actualiza cada partido existente por n_partido.
    """

    supabase = get_supabase_client()

    if df_resultados is None or df_resultados.empty:
        return False, "No hay resultados para guardar."

    df_save = df_resultados.copy()

    rename_map = {
        "N_PARTIDO": "n_partido",
        "Equipo_1": "equipo_1",
        "R1": "r1",
        "Equipo_2": "equipo_2",
        "R2": "r2",
        "DIA": "dia",
        "HORA": "hora",
        "VIZ": "viz",
        "FECHA": "fecha"
    }

    df_save = df_save.rename(columns=rename_map)

    columnas = [
        "n_partido",
        "equipo_1",
        "r1",
        "equipo_2",
        "r2",
        "dia",
        "hora",
        "viz",
        "fecha"
    ]

    for col in columnas:
        if col not in df_save.columns:
            if col in ["r1", "r2", "fecha"]:
                df_save[col] = None
            elif col == "viz":
                df_save[col] = False
            else:
                df_save[col] = ""

    df_save = df_save[columnas].copy()

    # ------------------------------------------------------------
    # N_PARTIDO — entero obligatorio
    # ------------------------------------------------------------

    df_save["n_partido"] = pd.to_numeric(
        df_save["n_partido"],
        errors="coerce"
    )

    df_save = df_save.dropna(
        subset=["n_partido"]
    ).copy()

    df_save["n_partido"] = df_save["n_partido"].apply(
        lambda x: int(float(x))
    )

    # ------------------------------------------------------------
    # R1 / R2 — enteros o NULL
    # ------------------------------------------------------------

    for col in ["r1", "r2"]:
        df_save[col] = pd.to_numeric(
            df_save[col],
            errors="coerce"
        )

        df_save[col] = df_save[col].apply(
            lambda x: int(float(x)) if pd.notna(x) else None
        )

    # ------------------------------------------------------------
    # FECHA — tanda 1 / 2 / 3 o NULL
    # ------------------------------------------------------------

    df_save["fecha"] = pd.to_numeric(
        df_save["fecha"],
        errors="coerce"
    )

    df_save["fecha"] = df_save["fecha"].apply(
        lambda x: int(float(x)) if pd.notna(x) else None
    )

    # ------------------------------------------------------------
    # VIZ — booleano
    # ------------------------------------------------------------

    df_save["viz"] = (
        df_save["viz"]
        .fillna(False)
        .astype(str)
        .str.strip()
        .str.upper()
        .isin(["TRUE", "1", "1.0", "VERDADERO", "T", "SI", "SÍ"])
    )


    # ------------------------------------------------------------
    # Textos visuales
    # ------------------------------------------------------------

    for col in ["equipo_1", "equipo_2", "dia", "hora"]:
        df_save[col] = (
            df_save[col]
            .fillna("")
            .astype(str)
            .replace("nan", "")
            .replace("None", "")
        )

    try:
        actualizados = 0

        for _, row in df_save.iterrows():
            n_partido = int(row["n_partido"])

            data_update = {
                "equipo_1": str(row["equipo_1"]).strip(),
                "r1": None if pd.isna(row["r1"]) else int(row["r1"]),
                "equipo_2": str(row["equipo_2"]).strip(),
                "r2": None if pd.isna(row["r2"]) else int(row["r2"]),
                "dia": str(row["dia"]).strip(),
                "hora": str(row["hora"]).strip(),
                "viz": bool(row["viz"]),
                "fecha": None if pd.isna(row["fecha"]) else int(row["fecha"]),
            }

            response = (
                supabase
                .table("resultados")
                .update(data_update)
                .eq("n_partido", n_partido)
                .execute()
            )

            actualizados += 1

        get_resultados_supabase.clear()

        return True, f"Resultados actualizados correctamente. Partidos actualizados: {actualizados}."

    except Exception as e:
        return False, f"Error al guardar resultados en Supabase: {e}"


def guardar_estado_partido_supabase(
    n_partido,
    estado_partido,
    live_r1=None,
    live_r2=None
):
    """
    Actualiza el estado visual de un solo partido.
    Si el estado es Finalizado, copia los goles a R1/R2 para que aplique al ranking.
    En otros estados, los goles quedan como live_r1/live_r2 y no afectan el ranking.
    """

    supabase = get_supabase_client()

    try:
        n_partido = int(n_partido)
    except (TypeError, ValueError):
        return False, "Seleccioná un partido válido."

    estado_normalizado = str(estado_partido or "").strip()
    if estado_normalizado == "Sin live":
        estado_normalizado = "Pendiente"

    estados_validos = ["Pendiente", "En Vivo", "Entretiempo", "Finalizado"]

    if estado_normalizado not in estados_validos:
        return False, "Seleccioná un estado válido."

    r1_live = pd.to_numeric(live_r1, errors="coerce")
    r2_live = pd.to_numeric(live_r2, errors="coerce")
    r1_live = int(r1_live) if pd.notna(r1_live) else None
    r2_live = int(r2_live) if pd.notna(r2_live) else None

    es_finalizado = estado_normalizado == "Finalizado"
    es_visual = estado_normalizado in ["En Vivo", "Entretiempo"]

    data_update = {
        "live": es_visual,
        "live_r1": r1_live,
        "live_r2": r2_live,
        "estado_partido": estado_normalizado,
    }

    if es_finalizado:
        if r1_live is None or r2_live is None:
            return False, "Para finalizar un partido cargá ambos resultados."

        data_update.update(
            {
                "r1": r1_live,
                "r2": r2_live,
                "live": False,
            }
        )

    if estado_normalizado == "Pendiente":
        data_update.update(
            {
                "live": False,
                "live_r1": None,
                "live_r2": None,
            }
        )

    try:
        (
            supabase
            .table("resultados")
            .update(data_update)
            .eq("n_partido", n_partido)
            .execute()
        )

        get_resultados_supabase.clear()

        return True, "Estado del partido actualizado correctamente."

    except Exception as e:
        return False, f"Error al guardar estado del partido en Supabase: {e}"
