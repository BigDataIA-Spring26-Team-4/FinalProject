"""Embedding pipeline — generates vectors from unstructured text and stores in ChromaDB."""

from maritime_sentinel.config import settings

EMBEDDING_MODEL = settings.embedding_model
CHUNK_SIZE = 512
CHUNK_OVERLAP = 64
COLLECTION_NAME = "maritime_intelligence"


def embed_documents(documents: list[dict]) -> int:
    """Embed a batch of documents and upsert into ChromaDB.

    Each document dict should have: id, text, metadata (region, date, source_type, etc.)
    """
    # TODO: Chunk text, call OpenAI embedding API, upsert to ChromaDB
    raise NotImplementedError
