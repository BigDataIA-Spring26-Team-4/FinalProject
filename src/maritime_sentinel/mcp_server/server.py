"""MCP Server — exposes 7 maritime tools, 2 resources, 2 prompts.

Tools query Snowflake (via Redis cache) and ChromaDB for agent consumption.
"""


def create_mcp_server():
    """Initialize and return the MCP server with all tools registered."""
    # TODO: Register 7 tools, 2 resources, 2 prompts
    # TODO: Wire Redis cache layer between tools and data stores
    raise NotImplementedError
