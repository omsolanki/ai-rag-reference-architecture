"""Hybrid retrieval with re-ranking."""

import re

from app.config import settings
from app.embeddings.generator import EmbeddingService
from app.rag.qdrant_store import QdrantStore


class HybridRetriever:
    """Combines dense vector search with keyword scoring and re-ranking."""

    DENSE_WEIGHT = 0.7
    KEYWORD_WEIGHT = 0.3

    def __init__(self, embedding_service: EmbeddingService, qdrant_store: QdrantStore):
        self.embedding_service = embedding_service
        self.qdrant_store = qdrant_store

    def retrieve(
        self,
        query: str,
        top_k: int | None = None,
        filters: dict | None = None,
        rerank: bool = False,
    ) -> list[dict]:
        top_k = top_k or settings.retrieval_top_k
        query_vector = self.embedding_service.embed_query(query)

        candidates = self.qdrant_store.search(
            query_vector=query_vector,
            top_k=top_k,
            filters=filters,
        )

        if rerank and candidates:
            candidates = self._rerank(query, candidates)
            candidates = candidates[: settings.rerank_top_k]

        return candidates

    def _rerank(self, query: str, candidates: list[dict]) -> list[dict]:
        query_tokens = set(self._tokenize(query))

        for candidate in candidates:
            content_tokens = set(self._tokenize(candidate["content"]))
            overlap = len(query_tokens & content_tokens)
            keyword_score = overlap / max(len(query_tokens), 1)

            candidate["score"] = (
                self.DENSE_WEIGHT * candidate["score"]
                + self.KEYWORD_WEIGHT * keyword_score
            )

        candidates.sort(key=lambda x: x["score"], reverse=True)
        return candidates

    @staticmethod
    def _tokenize(text: str) -> list[str]:
        return re.findall(r"\w+", text.lower())
