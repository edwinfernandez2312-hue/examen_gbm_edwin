from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.providers.postgres.operators.postgres import PostgresOperator
from datetime import datetime, timedelta
# Importamos la función que sube los datos a Supabase
from src.carga_supabase import subir_datos
import pandas as pd

default_args = {
    'owner': 'data_engineer',
    'depends_on_past': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

with DAG(
    dag_id='dag_transacciones',
    default_args=default_args,
    description='Pipeline diario de limpieza y análisis de fraude',
    schedule_interval='30 23 * * *', # 11:30 PM todos los días
    start_date=datetime(2026, 6, 23),
    catchup=False,
    tags=['fraude', 'banco'],
) as dag:

    # 1. Tarea de Transformación (Python)
    
    def tarea_ingesta():
        df = pd.read_csv('data/transacciones_diarias.csv') # Ruta del CSV
        subir_datos(df) # Función que ya validamos

    transformar_y_cargar = PythonOperator(
        task_id='transformar_y_cargar_datos',
        python_callable=tarea_ingesta
    )

    # 2. Tarea de Análisis (SQL)
    # Utiliza la conexión configurada
    detectar_anomalias = PostgresOperator(
        task_id='analisis_anomalias_sql',
        postgres_conn_id='supabase_postgres',
        sql='sql/analisis_anomalias.sql'
    )

    # El operador >> asegura la dependencia: SQL solo corre si la carga fue exitosa
    transformar_y_cargar >> detectar_anomalias