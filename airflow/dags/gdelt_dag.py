"""GDELT DAG — Ingests Events 2.0 and GKG every 15 minutes.

Events → Snowflake Bronze (structured rows for SQL queries)
GKG → Snowflake Bronze + embedding pipeline → ChromaDB (article text for RAG)
"""
from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator

default_args = {
    "owner": "maritime-sentinel",
    "retries": 2,
    "retry_delay": timedelta(minutes=2),
}

with DAG(
    dag_id="gdelt_ingest",
    default_args=default_args,
    description="Ingest GDELT Events + GKG into Snowflake Bronze",
    schedule_interval="*/15 * * * *",
    start_date=datetime(2026, 4, 2),
    catchup=False,
    tags=["ingestion", "gdelt"],
) as dag:

    def extract_gdelt_events(**context):
        """Query BigQuery for maritime-relevant GDELT events."""
        # TODO: Use gdeltPyR or BigQuery client
        # Filter by maritime CAMEO codes
        pass

    def extract_gdelt_gkg(**context):
        """Query BigQuery for GDELT GKG records."""
        # TODO: Download GKG with maritime theme filters
        pass

    def load_to_bronze(**context):
        """Load raw GDELT data into Snowflake Bronze."""
        # TODO: COPY INTO bronze_gdelt_events / bronze_gdelt_gkg
        pass

    def trigger_embedding(**context):
        """Trigger embedding pipeline for new GKG article text."""
        # TODO: Send new GKG text to embedding pipeline → ChromaDB
        pass

    extract_events = PythonOperator(task_id="extract_gdelt_events", python_callable=extract_gdelt_events)
    extract_gkg = PythonOperator(task_id="extract_gdelt_gkg", python_callable=extract_gdelt_gkg)
    load = PythonOperator(task_id="load_to_bronze", python_callable=load_to_bronze)
    embed = PythonOperator(task_id="trigger_embedding", python_callable=trigger_embedding)

    [extract_events, extract_gkg] >> load >> embed
