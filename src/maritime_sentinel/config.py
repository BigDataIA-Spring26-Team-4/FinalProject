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

    # LLM Providers
    openai_api_key: str = ""
    anthropic_api_key: str = ""

    # Model Selection (configurable per agent to control cost)
    supervisor_model: str = "claude-sonnet-4-20250514"
    news_analyst_model: str = "claude-sonnet-4-20250514"
    vessel_tracker_model: str = "gpt-4o-mini"
    conflict_monitor_model: str = "gpt-4o-mini"
    sanctions_checker_model: str = "gpt-4o-mini"
    weather_analyst_model: str = "gpt-4o-mini"
    embedding_model: str = "text-embedding-3-small"

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
    redis_gold_cache_ttl: int = 300       # 5 minutes
    redis_mcp_tool_cache_ttl: int = 120   # 2 minutes
    redis_ais_position_ttl: int = 120     # 2 minutes
    redis_embedding_cache_ttl: int = 600  # 10 minutes

    # ChromaDB
    chroma_host: str = "chromadb"
    chroma_port: int = 8200

    # LangSmith
    langchain_tracing_v2: bool = False
    langchain_api_key: str = ""
    langchain_project: str = "maritime-sentinel"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
