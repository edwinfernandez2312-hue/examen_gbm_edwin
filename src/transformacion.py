import pandas as pd

def transformar_datos(archivo_csv):
    """
    Ingiere el archivo, aplica limpieza de duplicados, tratamiento de nulos
    y cálculo de columna booleana según reglas de negocio.
    """
    # Ingestión
    df = pd.read_csv(archivo_csv)

    # 1. Duplicación de Registros
    # Eliminación basada en el identificador único 'id_transaccion'
    df = df.drop_duplicates(subset=['id_transaccion'])

    # 2. Tratamiento de Valores Faltantes (Nulos)
    # Regla: Si monto_usd es nulo y estado es 'rechazada', asignar 0.0
    mask_nulos = (df['monto_usd'].isna()) & (df['estado_transaccion'] == 'rechazada')
    df.loc[mask_nulos, 'monto_usd'] = 0.0

    # 3. Clasificación de Montos Inusuales
    # Regla: True si > 1500 y tipo_comercio es 'internacional'
    df['es_monto_inusual'] = (df['monto_usd'] > 1500) & (df['tipo_comercio'] == 'internacional')

    return df

# Ejecución (Ejemplo de uso)
if __name__ == "__main__":
    df_procesado = transformar_datos('transacciones_diarias.csv')
    print("Transformación completada con éxito.")
    print(df_procesado.head())