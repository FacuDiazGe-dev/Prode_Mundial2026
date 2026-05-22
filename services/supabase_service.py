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
        "ROL": "rol"
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
            "rol"
        ]:
            if pd.isna(value):
                value = None

            if col == "edad":
                try:
                    value = int(value)
                except Exception:
                    value = None

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
            "rol": rol
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


@st.cache_data(ttl=300)
def get_config_supabase():
    supabase = get_supabase_client()

    response = (
        supabase
        .table("config")
        .select("*")
        .limit(1)
        .execute()
    )

    data = response.data or []

    return pd.DataFrame(data)


def get_config_app():
    df = get_config_supabase()

    columnas_app = [
        "MANTENIMIENTO",
        "REGISTRO"
    ]

    if df.empty:
        return pd.DataFrame(
            [
                {
                    "MANTENIMIENTO": "OFF",
                    "REGISTRO": "ON"
                }
            ]
        )

    df = df.rename(
        columns={
            "mantenimiento": "MANTENIMIENTO",
            "registro": "REGISTRO"
        }
    )

    for col in columnas_app:
        if col not in df.columns:
            if col == "MANTENIMIENTO":
                df[col] = "OFF"
            elif col == "REGISTRO":
                df[col] = "ON"

    df["MANTENIMIENTO"] = (
        df["MANTENIMIENTO"]
        .astype(str)
        .str.strip()
        .str.upper()
    )

    df["REGISTRO"] = (
        df["REGISTRO"]
        .astype(str)
        .str.strip()
        .str.upper()
    )

    return df[columnas_app]


def actualizar_config_supabase(campo, valor):
    """
    Actualiza un campo de la tabla config.
    Campos esperados: mantenimiento, registro.
    """

    supabase = get_supabase_client()

    campo = str(campo).strip().lower()
    valor = str(valor).strip().upper()

    campos_validos = [
        "mantenimiento",
        "registro"
    ]

    if campo not in campos_validos:
        return False, "Campo de configuración inválido."

    if valor not in ["ON", "OFF"]:
        return False, "Valor inválido. Usá ON u OFF."

    try:
        response = (
            supabase
            .table("config")
            .update({campo: valor})
            .eq("id", 1)
            .select("*")
            .execute()
        )

        data = response.data or []

        if len(data) == 0:
            return False, "No se encontró la fila de configuración con id = 1."

        get_config_supabase.clear()

        return True, "Configuración actualizada correctamente."

    except Exception as e:
        return False, f"Error al actualizar configuración: {e}"
