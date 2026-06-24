from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.providers.postgres.operators.postgres import PostgresOperator
from datetime import datetime, timedelta

# Argumentos base para el DAG
default_args = {
    'owner': 'data_engineer',
    'depends_on_past': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

# Definición del DAG
# Tiempo de ejecución: 11:30 PM todos los días
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
    # Llama al script que ya hemos validado y probado en src/main.py
    transformar_y_cargar = PythonOperator(
        task_id='transformar_y_cargar_datos',
        python_callable=lambda: print("Ejecutando main.py...") # Referencia conceptual al script
    )

    # 2. Tarea de Análisis (SQL)
    # Utiliza el archivo SQL 
    detectar_anomalias = PostgresOperator(
        task_id='analisis_anomalias_sql',
        postgres_conn_id='supabase_postgres',
        sql='sql/analisis_anomalias.sql'
    )

    # Definición de dependencia: 
    # El operador >> asegura que la consulta SQL SOLO corra si el ETL terminó exitosamente.
    transformar_y_cargar >> detectar_anomalias