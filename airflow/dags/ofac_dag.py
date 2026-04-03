"""OFAC DAG — Ingests sanctions data daily from OpenSanctions."""
from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator

default_args = {
    "owner": "maritime-sentinel",
    "retries": 2,
    "retry_delay": timedelta(minutes=5),
}

with DAG(
    dag_id="ofac_ingest",
    default_args=default_args,
    description="Ingest OFAC sanctions from OpenSanctions into Snowflake Bronze",
    schedule_interval="0 4 * * *",  # Daily at 4 AM
    start_date=datetime(2026, 4, 2),
    catchup=False,
    tags=["ingestion", "ofac", "sanctions"],
) as dag:

    def extract_ofac(**context):
        """Download OpenSanctions OFAC consolidated dataset."""
        # TODO: Download JSON, parse maritime entities (vessels, shipping companies)
        pass

    def load_to_bronze(**context):
        """Upsert into Snowflake Bronze with change detection."""
        pass

    def trigger_embedding(**context):
        """Embed new/changed sanctions entity descriptions into ChromaDB."""
        pass

    extract = PythonOperator(task_id="extract_ofac", python_callable=extract_ofac)
    load = PythonOperator(task_id="load_to_bronze", python_callable=load_to_bronze)
    embed = PythonOperator(task_id="trigger_embedding", python_callable=trigger_embedding)

    extract >> load >> embed
