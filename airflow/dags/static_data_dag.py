"""Static Data DAG — Loads World Port Index, Natural Earth, and chokepoint seed data."""
from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator

default_args = {
    "owner": "maritime-sentinel",
    "retries": 1,
    "retry_delay": timedelta(minutes=5),
}

with DAG(
    dag_id="static_data_load",
    default_args=default_args,
    description="Load static reference data (ports, coastlines, chokepoints)",
    schedule_interval="@monthly",
    start_date=datetime(2026, 4, 2),
    catchup=False,
    tags=["ingestion", "static"],
) as dag:

    def load_world_port_index(**context):
        """Download and load World Port Index from HDX."""
        pass

    def load_coastlines(**context):
        """Download and load Natural Earth coastlines GeoJSON."""
        pass

    def seed_chokepoints(**context):
        """Seed dim_chokepoints from data/seed/chokepoints.json."""
        pass

    ports = PythonOperator(task_id="load_world_port_index", python_callable=load_world_port_index)
    coast = PythonOperator(task_id="load_coastlines", python_callable=load_coastlines)
    choke = PythonOperator(task_id="seed_chokepoints", python_callable=seed_chokepoints)

    [ports, coast, choke]
