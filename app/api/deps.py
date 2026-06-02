"""Shared API dependencies and service initialization."""

from functools import lru_cache

from app.config import settings
from app.embeddings.generator import EmbeddingService
from app.rag.qdrant_store import QdrantStore
from app.services.database import DatabaseService


@lru_cache
def get_embedding_service() -> EmbeddingService:
    return EmbeddingService(settings)


@lru_cache
def get_qdrant_store() -> QdrantStore:
    return QdrantStore(settings)


@lru_cache
def get_database_service() -> DatabaseService:
    return DatabaseService(settings)
