from supabase import create_client, Client
import pandas as pd

# CREDENCIALES DE SUPABASE
SUPABASE_URL = "https://wnyruxbpkodftjwtekdv.supabase.co"
SUPABASE_KEY = "sb_publishable_5IK987cOkusaGztuTeGpMQ_cpPcf5u_"

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

def subir_datos(df):
    """
    Toma el DataFrame procesado y lo inserta en Supabase.
    """
    print("Conectando con Supabase e iniciando carga...") 
    
    # Reemplazamos posibles valores nulos restantes por None
    df_limpio = df.where(pd.notnull(df), None)
    
    # Convertimos a lista de diccionarios
    registros = df_limpio.to_dict(orient='records')
    
    # Insertamos en la tabla
    respuesta = supabase.table('transacciones').upsert(registros).execute()
    
    print("¡Carga finalizada con éxito en la base de datos!") 
    return respuesta