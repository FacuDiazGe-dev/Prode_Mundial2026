import streamlit as st
import pandas as pd
import requests
import base64
from google.cloud import storage
import io 

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
        "Uruguay": "uy", "Uzbekistán": "uz"
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

#-------------------------------- CARGAR FOTO STORAGE (GCS) -----------------------------------------------------

#Definicion variable carga de la imagen
def upload_profile_picture(archivo, file_name):
    from google.cloud import storage
    import io
    try:
        creds_info = st.secrets["connections"]["gsheets"] 
        client = storage.Client.from_service_account_info(creds_info)
        
        bucket_name = "foto-prode2026" 
        bucket = client.bucket(bucket_name)
        blob = bucket.blob(f"perfiles/{file_name}")
        
        if isinstance(archivo, bytes):
            objeto_archivo = io.BytesIO(archivo)
        else:
            objeto_archivo = archivo
            objeto_archivo.seek(0)
        
        tipo_mimo = getattr(archivo, 'type', 'image/jpeg')

        blob.upload_from_file(objeto_archivo, content_type=tipo_mimo)
        
        return f"https://storage.googleapis.com/{bucket_name}/perfiles/{file_name}"
        
    except Exception as e:
        return f"Error: {e}"
