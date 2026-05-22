import base64
import io
import re
import time
from pathlib import Path

import requests
import streamlit as st
from google.cloud import storage


@st.cache_data(ttl=3600)
def get_flag_img(pais):
    # Diccionario de códigos ISO (Mantenemos los que ya tienes)
    codigos = {
        "Alemania": "de", "Arabia Saudita": "sa", "Argelia": "dz", "Argentina": "ar",
        "Australia": "au", "Austria": "at", "Bélgica": "be", "Bosnia y Herzegovina": "ba",
        "Brasil": "br", "Cabo Verde": "cv", "Canadá": "ca", "Catar": "qa",
        "Colombia": "co", "Corea del Sur": "kr", "Costa de Marfil": "ci", "Croacia": "hr",
        "Curazao": "cw", "Ecuador": "ec", "Egipto": "eg", "Escocia": "gb-sct",
        "España": "es", "Estados Unidos": "us", "Francia": "fr", "Ghana": "gh",
        "Haití": "ht", "Inglaterra": "gb-eng", "Irak": "iq", "Irán": "ir",
        "Japón": "jp", "Jordania": "jo", "Marruecos": "ma", "México": "mx",
        "Noruega": "no", "Nueva Zelanda": "nz", "Países Bajos": "nl", "Panamá": "pa",
        "Paraguay": "py", "Portugal": "pt", "República Checa": "cz", 
        "República Democrática del Congo": "cd", "Senegal": "sn", "Sudáfrica": "za",
        "Suecia": "se", "Suiza": "ch", "Túnez": "tn", "Turquía": "tr",
        "Uruguay": "uy", "Uzbekistán": "uz",
        "Rep. Checa": "cz","Bosnia": "ba","Bosnia-Herzegovina": "ba","EE. UU.": "us",
        "Estados Unidos": "us",
        "USA": "us",
    }
    
    code = codigos.get(pais)
    if not code: return "⚽" # Fallback si no hay código

    try:
        # Descargamos la imagen y la convertimos a Base64
        response = requests.get(f"https://flagcdn.com/w40/{code}.png", timeout=5)
        if response.status_code == 200:
            img_b64 = base64.b64encode(response.content).decode()
            return f"data:image/png;base64,{img_b64}"
    except:
        pass
    
    return "⚽" # Fallback si falla la descarga

@st.cache_data(ttl=3600) # Guarda las imágenes en RAM por 1 hora
def get_flag_img_cached(team_name):
    # Aquí va tu lógica actual de obtener la imagen (Base64 o URL)
    return get_flag_img(team_name) 

#-------------------------------- CARGAR IMÁGENES STORAGE (GCS) -----------------------------------------------------

def upload_image_to_gcs(archivo, file_name, carpeta="perfiles"):
    """
    Sube una imagen a Google Cloud Storage y devuelve la URL pública.

    Parámetros:
    - archivo: archivo subido desde st.file_uploader o bytes
    - file_name: nombre final del archivo
    - carpeta: carpeta dentro del bucket. Ej: perfiles, foro

    Retorna:
    - URL pública si salió bien
    - texto "Error: ..." si falló
    """

    try:
        creds_info = st.secrets["connections"]["gsheets"]
        client = storage.Client.from_service_account_info(creds_info)

        bucket_name = "foto-prode2026"
        bucket = client.bucket(bucket_name)

        # Limpieza básica de nombres para evitar caracteres raros
        carpeta_limpia = re.sub(r"[^a-zA-Z0-9/_-]", "_", str(carpeta)).strip("/")
        file_name_limpio = re.sub(r"[^a-zA-Z0-9._-]", "_", str(file_name))

        blob_path = f"{carpeta_limpia}/{file_name_limpio}"
        blob = bucket.blob(blob_path)

        if isinstance(archivo, bytes):
            objeto_archivo = io.BytesIO(archivo)
        else:
            objeto_archivo = archivo
            objeto_archivo.seek(0)

        tipo_mimo = getattr(archivo, "type", "image/jpeg")

        blob.upload_from_file(
            objeto_archivo,
            content_type=tipo_mimo
        )

        return f"https://storage.googleapis.com/{bucket_name}/{blob_path}"

    except Exception as e:
        return f"Error: {e}"


def upload_profile_picture(archivo, file_name):
    """
    Mantiene compatibilidad con la función existente para fotos de perfil.
    Guarda en la carpeta perfiles/.
    """

    return upload_image_to_gcs(
        archivo=archivo,
        file_name=file_name,
        carpeta="perfiles"
    )


def upload_foro_image(archivo, usuario):
    """
    Sube una imagen del foro al bucket.
    Guarda en la carpeta foro/<usuario>/.
    """

    extension = Path(archivo.name).suffix.lower()

    if extension not in [".jpg", ".jpeg", ".png", ".webp"]:
        return "Error: Formato no permitido. Usá JPG, PNG o WEBP."

    usuario_limpio = re.sub(r"[^a-zA-Z0-9_-]", "_", str(usuario))
    timestamp = int(time.time())

    file_name = f"{timestamp}_{usuario_limpio}{extension}"

    return upload_image_to_gcs(
        archivo=archivo,
        file_name=file_name,
        carpeta=f"foro/{usuario_limpio}"
    )
    
