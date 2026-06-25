import os
import logging
from dotenv import load_dotenv
from supabase import create_client, Client
import pandas as pd

# 1. Configuración de Logging para auditoría 
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# 2. Cargar las variables de entorno desde el archivo .env
load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")


# Inicialización del cliente
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

def subir_datos(df):
    """
    Toma el DataFrame procesado y lo inserta en Supabase de forma idempotente (Upsert).
    """
    logging.info("Conectando con Supabase e iniciando carga...") 
    
    # Validación preventiva: si el dataframe está vacío, no hacemos la petición a la base de datos
    if df.empty:
        logging.warning("El DataFrame recibido está vacío. Cancelando carga.")
        return None
    
    # Reemplazamos posibles valores nulos restantes por None (compatible con JSON/Postgres)
    df_limpio = df.where(pd.notnull(df), None)
    
    # Convertimos a lista de diccionarios
    registros = df_limpio.to_dict(orient='records')
    
    # 3. Manejo de excepcionesde red
    try:
        # Insertamos en la tabla
        respuesta = supabase.table('transacciones').upsert(registros).execute()
        logging.info(f"¡Carga finalizada con éxito! {len(registros)} registros procesados.") 
        return respuesta
    except Exception as e:
        logging.error(f"Falla crítica al intentar cargar datos en Supabase: {str(e)}")
        raise e # Relanzamos el error para que el orquestador (Airflow) detecte que la tarea falló