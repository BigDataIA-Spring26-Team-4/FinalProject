"""Bronze loader for static reference data (ports, coastlines, chokepoints)."""


def load_world_port_index(filepath: str) -> int:
    """Load World Port Index CSV into bronze_ports."""
    raise NotImplementedError


def load_coastlines(filepath: str) -> int:
    """Load Natural Earth coastlines GeoJSON into bronze_coastlines."""
    raise NotImplementedError


def seed_chokepoints(filepath: str = "data/seed/chokepoints.json") -> int:
    """Seed dim_chokepoints from application-defined reference data."""
    raise NotImplementedError
