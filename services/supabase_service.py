import streamlit as st
import pandas as pd
from supabase import create_client


@st.cache_resource
def get_supabase_client():
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]

    return create_client(url, key)


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

    response = (
        supabase
        .table("pronosticos")
        .select("*")
        .order("usuario")
        .execute()
    )

    data = response.data or []

    return pd.DataFrame(data)

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
                "FECHA"
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
            "fecha": "FECHA"
        }
    )

    return df[
        [
            "N_PARTIDO",
            "Equipo_1",
            "R1",
            "Equipo_2",
            "R2",
            "DIA",
            "HORA",
            "VIZ",
            "FECHA"
        ]
    ]


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
                "ROL"
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
            "rol": "ROL"
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
        "ROL"
    ]

    for col in columnas_necesarias:
        if col not in df.columns:
            if col == "ID":
                df[col] = range(1, len(df) + 1)
            else:
                df[col] = ""

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
        .order("prioridad")
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


def guardar_foro_supabase(df_foro):
    """
    Guarda la tabla completa del foro en Supabase.
    Versión compatible con la lógica actual de foro.py.
    """

    supabase = get_supabase_client()

    if df_foro is None:
        return False, "No hay datos de foro para guardar."

    df_save = df_foro.copy()

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

    records = df_save.to_dict(orient="records")

    try:
        # Reemplazo completo de tabla, compatible con tu lógica actual.
        supabase.table("foro").delete().neq("id", 0).execute()

        if records:
            supabase.table("foro").insert(records).execute()

        get_foro_supabase.clear()

        return True, "Foro guardado correctamente en Supabase."

    except Exception as e:
        return False, f"Error al guardar foro en Supabase: {e}"

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

    df_save = df_save[columnas].copy()

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
    No reemplaza toda la tabla.
    """

    supabase = get_supabase_client()

    try:
        post_id = int(post_id)

        if post_id <= 0:
            return False, "ID de mensaje inválido."

        supabase.table("foro").delete().eq(
            "id",
            post_id
        ).execute()

        get_foro_supabase.clear()

        return True, "Mensaje eliminado correctamente."

    except Exception as e:
        return False, f"Error al borrar mensaje: {e}"
