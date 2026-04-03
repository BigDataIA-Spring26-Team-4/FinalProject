"""Application configuration loaded from environment variables."""
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Central config — reads from .env file or environment."""

    # Snowflake
    snowflake_account: str = ""
    snowflake_user: str = ""
    snowflake_password: str = ""
    snowflake_warehouse: str = "MARITIME_XS"
    snowflake_database: str = "MARITIME_SENTINEL"
    snowflake_schema: str = "PUBLIC"
    snowflake_role: str = "ACCOUNTADMIN"

    # LLM
    openai_api_key: str = ""
    anthropic_api_key: str = ""

    # AIS
    aisstream_api_key: str = ""

    # ACLED
    acled_api_key: str = ""
    acled_email: str = ""

    # Weather
    weather_api_key: str = ""

    # Redis
    redis_host: str = "redis"
    redis_port: int = 6379
    redis_db: int = 0

    # ChromaDB
    chroma_host: str = "chromadb"
    chroma_port: int = 8200

    # LangSmith
    langchain_tracing_v2: bool = True
    langchain_api_key: str = ""
    langchain_project: str = "maritime-sentinel"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
