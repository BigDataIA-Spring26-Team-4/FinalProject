"""Snowflake client — connection management and query execution."""
import snowflake.connector
from maritime_sentinel.config import settings


def get_snowflake_connection():
    """Return a Snowflake connection using settings from .env."""
    return snowflake.connector.connect(
        account=settings.snowflake_account,
        user=settings.snowflake_user,
        password=settings.snowflake_password,
        warehouse=settings.snowflake_warehouse,
        database=settings.snowflake_database,
        schema=settings.snowflake_schema,
        role=settings.snowflake_role,
    )


def execute_query(sql: str, params: dict | None = None) -> list[dict]:
    """Execute a SQL query and return results as list of dicts."""
    conn = get_snowflake_connection()
    try:
        cur = conn.cursor()
        cur.execute(sql, params or {})
        columns = [desc[0].lower() for desc in cur.description]
        return [dict(zip(columns, row)) for row in cur.fetchall()]
    finally:
        conn.close()
