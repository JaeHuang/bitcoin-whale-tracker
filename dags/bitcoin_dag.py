import sys
import os
from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime

sys.path.append("/opt/airflow")


# import custom functions
from scripts.fetch_block import fetch_block_transactions, clean_and_store_transactions


with DAG(
    dag_id="bitcoin_whale_tracker",
    start_date=datetime(2024, 1, 1),
    schedule_interval=None,
    catchup=False,
    tags=["btc"],
) as dag:

    fetch_task = PythonOperator(
        task_id="fetch_block_transactions",
        python_callable=fetch_block_transactions,
        provide_context=True,
    )

    clean_task = PythonOperator(
        task_id="clean_and_store_transactions",
        python_callable=clean_and_store_transactions,
        provide_context=True,
    )

    fetch_task >> clean_task
