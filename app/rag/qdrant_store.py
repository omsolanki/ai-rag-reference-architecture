"""Qdrant vector storage service."""

import uuid

from qdrant_client import QdrantClient
from qdrant_client.models import (
    Distance,
    FieldCondition,
    Filter,
    MatchValue,
    PointStruct,
    VectorParams,
)

from app.config import Settings

EMBEDDING_DIMENSION = 1536


class QdrantStore:
    """Manages vector storage and search in Qdrant."""

    def __init__(self, settings: Settings):
        self.settings = settings
        self.client = QdrantClient(
            host=settings.qdrant_host,
            port=settings.qdrant_port,
        )
        self.collection = settings.qdrant_collection
        self._ensure_collection()

    def _ensure_collection(self) -> None:
        collections = [c.name for c in self.client.get_collections().collections]
        if self.collection not in collections:
            self.client.create_collection(
                collection_name=self.collection,
                vectors_config=VectorParams(
                    size=EMBEDDING_DIMENSION,
                    distance=Distance.COSINE,
                ),
            )

    def upsert_chunks(
        self,
        chunks: list[dict],
        embeddings: list[list[float]],
    ) -> None:
        points = []
        for chunk, embedding in zip(chunks, embeddings):
            point_id = str(uuid.uuid5(uuid.NAMESPACE_DNS, chunk["chunk_id"]))
            payload = {
                "chunk_id": chunk["chunk_id"],
                "document_id": chunk["document_id"],
                "content": chunk["content"],
                "chunk_index": chunk["chunk_index"],
                **chunk.get("metadata", {}),
            }
            points.append(
                PointStruct(id=point_id, vector=embedding, payload=payload)
            )

        self.client.upsert(collection_name=self.collection, points=points)

    def search(
        self,
        query_vector: list[float],
        top_k: int = 5,
        filters: dict | None = None,
    ) -> list[dict]:
        qdrant_filter = self._build_filter(filters) if filters else None

        results = self.client.search(
            collection_name=self.collection,
            query_vector=query_vector,
            limit=top_k,
            query_filter=qdrant_filter,
        )

        return [
            {
                "chunk_id": hit.payload.get("chunk_id", str(hit.id)),
                "document_id": hit.payload.get("document_id", ""),
                "content": hit.payload.get("content", ""),
                "score": hit.score,
                "metadata": {
                    k: v
                    for k, v in hit.payload.items()
                    if k not in ("chunk_id", "document_id", "content")
                },
            }
            for hit in results
        ]

    def _build_filter(self, filters: dict) -> Filter:
        conditions = [
            FieldCondition(key=key, match=MatchValue(value=value))
            for key, value in filters.items()
        ]
        return Filter(must=conditions)

    def health_check(self) -> bool:
        try:
            self.client.get_collections()
            return True
        except Exception:
            return False
