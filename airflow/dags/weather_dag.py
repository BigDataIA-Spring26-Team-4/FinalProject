"""Weather DAG — Ingests severe weather alerts hourly."""
from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator

default_args = {
    "owner": "maritime-sentinel",
    "retries": 1,
    "retry_delay": timedelta(minutes=2),
}

with DAG(
    dag_id="weather_ingest",
    default_args=default_args,
    description="Ingest severe weather alerts for chokepoint regions",
    schedule_interval="0 * * * *",  # Hourly
    start_date=datetime(2026, 4, 2),
    catchup=False,
    tags=["ingestion", "weather"],
) as dag:

    def extract_weather(**context):
        """Pull severe weather alerts from Weather Company API for chokepoint regions."""
        # TODO: Query dim_chokepoints for bounding boxes, fetch alerts per region
        pass

    def load_to_bronze(**context):
        """Load weather alerts into Snowflake Bronze."""
        pass

    extract = PythonOperator(task_id="extract_weather", python_callable=extract_weather)
    load = PythonOperator(task_id="load_to_bronze", python_callable=load_to_bronze)

    extract >> load
