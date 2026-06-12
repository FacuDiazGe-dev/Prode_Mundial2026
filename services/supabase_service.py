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
                "APORTE_REALIZADO"
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
            "aporte_realizado": "APORTE_REALIZADO"
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
        "APORTE_REALIZADO"
    ]

    for col in columnas_necesarias:
        if col not in df.columns:
            if col == "ID":
                df[col] = range(1, len(df) + 1)
            elif col == "APORTE_REALIZADO":
                df[col] = False
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
        "APORTE_REALIZADO": "aporte_realizado"
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
            "aporte_realizado"
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
            "aporte_realizado": False
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
        "cierre_pronosticos": "2026-06-11 15:00"
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

    if mantenimiento not in ["ON", "OFF"]:
        mantenimiento = "OFF"

    if registro not in ["ON", "OFF"]:
        registro = "ON"

    if pronosticos_estado not in ["ON", "OFF"]:
        pronosticos_estado = "ON"

    if cierre_pronosticos == "":
        cierre_pronosticos = "2026-06-11 15:00"

    return pd.DataFrame(
        [
            {
                "MANTENIMIENTO": mantenimiento,
                "REGISTRO": registro,
                "PRONOSTICOS_ESTADO": pronosticos_estado,
                "CIERRE_PRONOSTICOS": cierre_pronosticos
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
        "cierre_pronosticos"
    ]

    if campo not in campos_validos:
        return False, "Campo de configuración inválido."

    if campo in [
        "mantenimiento",
        "registro",
        "pronosticos_estado"
    ]:
        valor = str(valor).strip().upper()

        if valor not in ["ON", "OFF"]:
            return False, "Valor inválido. Usá ON u OFF."

    elif campo == "cierre_pronosticos":
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

    estados_validos = ["Pendiente", "1T", "2T", "ET", "Finalizado"]

    if estado_normalizado not in estados_validos:
        return False, "Seleccioná un estado válido."

    r1_live = pd.to_numeric(live_r1, errors="coerce")
    r2_live = pd.to_numeric(live_r2, errors="coerce")
    r1_live = int(r1_live) if pd.notna(r1_live) else None
    r2_live = int(r2_live) if pd.notna(r2_live) else None

    es_finalizado = estado_normalizado == "Finalizado"
    es_visual = estado_normalizado in ["1T", "2T", "ET"]

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
