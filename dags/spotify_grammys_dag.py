from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator

import src.quality as quality
import src.transform as transform
import src.load as load
import src.database as database

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(2026, 1, 1),
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=1),
}

dag = DAG(
    'spotify_grammys_pipeline',
    default_args=default_args,
    description='Pipeline ETL que combina datos de Spotify y los Premios Grammy',
    schedule_interval=None,
    catchup=False,
)

def task_read_csv():
    quality.extract_and_validate_spotify()

def task_read_db():
    database.read_grammys_from_db()

def task_transform_csv():
    transform.transform_spotify_data()

def task_transform_db():
    transform.transform_grammys_data()

def task_merge():
    transform.merge_spotify_and_grammys()

def task_load():
    load.load_merged_data_to_db()

def task_store():
    load.store_merged_data_to_csv()

# Definición de Operadores
t1 = PythonOperator(task_id='read_csv', python_callable=task_read_csv, dag=dag)
t2 = PythonOperator(task_id='read_db', python_callable=task_read_db, dag=dag)
t3 = PythonOperator(task_id='transform_csv', python_callable=task_transform_csv, dag=dag)
t4 = PythonOperator(task_id='transform_db', python_callable=task_transform_db, dag=dag)
t5 = PythonOperator(task_id='merge', python_callable=task_merge, dag=dag)
t6 = PythonOperator(task_id='load', python_callable=task_load, dag=dag)
t7 = PythonOperator(task_id='store', python_callable=task_store, dag=dag)

# Dependencias del Flujo ETL
t1 >> t3
t2 >> t4
[t3, t4] >> t5 >> t6 >> t7
