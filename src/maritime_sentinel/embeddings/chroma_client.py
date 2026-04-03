"""ChromaDB client — semantic search over embedded maritime intelligence."""
from maritime_sentinel.config import settings


def get_chroma_client():
    """Return a ChromaDB HttpClient connected to the Docker service."""
    import chromadb
    return chromadb.HttpClient(host=settings.chroma_host, port=settings.chroma_port)


def search_documents(query: str, k: int = 10, where: dict | None = None) -> list[dict]:
    """Semantic vector search over the maritime_intelligence collection."""
    # TODO: Embed query, search ChromaDB, return results with metadata
    raise NotImplementedError
