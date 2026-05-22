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
