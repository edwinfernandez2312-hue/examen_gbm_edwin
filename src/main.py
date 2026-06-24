from transformacion import transformar_datos
from carga_supabase import subir_datos
# Ejecución
if __name__ == "__main__":
    # Agregamos 'data/' antes del nombre del archivo
    df_procesado = transformar_datos('../data/transacciones_diarias.csv')
    
    print("Transformación completada con éxito.")
    print(df_procesado.head())

    # 2. Ejecutar la carga a Supabase
    print("Iniciando carga a Supabase...")
    subir_datos(df_procesado)
    
    print("Pipeline finalizado.")

   