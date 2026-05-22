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
