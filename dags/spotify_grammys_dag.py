"""
DAG: spotify_grammys_etl

read_csv -> validate_csv -> transform_csv --\
                                             +--> merge -> load -> store
read_db  -> transform_db  -----------------/
"""
from datetime import datetime

try:                                              # Airflow 3
    from airflow.sdk import DAG
    from airflow.providers.standard.operators.python import PythonOperator
except ImportError:                               # Airflow 2
    from airflow import DAG
    from airflow.operators.python import PythonOperator

from src import tasks

with DAG(
    dag_id="spotify_grammys_etl",
    start_date=datetime(2024, 1, 1),
    schedule=None,
    catchup=False,
    tags=["workshop", "etl"],
) as dag:
    t_read_csv = PythonOperator(task_id="read_csv", python_callable=tasks.read_csv)
    t_validate = PythonOperator(task_id="validate_csv", python_callable=tasks.validate_csv)
    t_transform_csv = PythonOperator(task_id="transform_csv", python_callable=tasks.transform_csv)
    t_read_db = PythonOperator(task_id="read_db", python_callable=tasks.read_db)
    t_transform_db = PythonOperator(task_id="transform_db", python_callable=tasks.transform_db)
    t_merge = PythonOperator(task_id="merge", python_callable=tasks.merge)
    t_load = PythonOperator(task_id="load", python_callable=tasks.load)
    t_store = PythonOperator(task_id="store", python_callable=tasks.store)

    t_read_csv >> t_validate >> t_transform_csv >> t_merge
    t_read_db >> t_transform_db >> t_merge
    t_merge >> t_load >> t_store

# Orden de respaldo (solo se usa si dag.test() no pudiera ejecutarse en el entorno)
FALLBACK_ORDER = ["read_csv", "validate_csv", "transform_csv", "read_db",
                  "transform_db", "merge", "load", "store"]
