"""ACLED DAG — Ingests conflict events weekly (Tuesdays)."""
from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator

default_args = {
    "owner": "maritime-sentinel",
    "retries": 2,
    "retry_delay": timedelta(minutes=5),
}

with DAG(
    dag_id="acled_ingest",
    default_args=default_args,
    description="Ingest ACLED conflict events into Snowflake Bronze",
    schedule_interval="0 6 * * 2",  # Tuesdays at 6 AM
    start_date=datetime(2026, 4, 2),
    catchup=False,
    tags=["ingestion", "acled"],
) as dag:

    def extract_acled(**context):
        """Fetch conflict events from ACLED API, filter coastal/port-adjacent."""
        # TODO: ACLED API call with lat/lon proximity filter to dim_ports
        pass

    def load_to_bronze(**context):
        """Load raw ACLED data into Snowflake Bronze."""
        pass

    extract = PythonOperator(task_id="extract_acled", python_callable=extract_acled)
    load = PythonOperator(task_id="load_to_bronze", python_callable=load_to_bronze)

    extract >> load
