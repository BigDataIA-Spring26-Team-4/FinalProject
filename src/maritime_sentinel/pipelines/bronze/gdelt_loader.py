"""Bronze loader for GDELT Events 2.0 and GKG data."""


def load_gdelt_events_to_bronze(data: list[dict]) -> int:
    """Load raw GDELT Events rows into bronze_gdelt_events."""
    # TODO: Snowflake COPY INTO from staged CSV
    raise NotImplementedError


def load_gdelt_gkg_to_bronze(data: list[dict]) -> int:
    """Load raw GDELT GKG rows into bronze_gdelt_gkg."""
    # TODO: Snowflake COPY INTO from staged CSV
    raise NotImplementedError
