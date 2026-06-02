"""Retrieval endpoint — hybrid search with metadata filtering."""

from fastapi import APIRouter, Depends, HTTPException

from app.api.deps import get_embedding_service, get_qdrant_store
from app.api.schemas import RetrieveRequest, RetrieveResponse, RetrievedChunk
from app.embeddings.generator import EmbeddingService
from app.rag.qdrant_store import QdrantStore
from app.rag.retrieval import HybridRetriever

router = APIRouter(prefix="/api/v1", tags=["retrieval"])


@router.post("/retrieve", response_model=RetrieveResponse)
async def retrieve_chunks(
    request: RetrieveRequest,
    embedding_service: EmbeddingService = Depends(get_embedding_service),
    qdrant_store: QdrantStore = Depends(get_qdrant_store),
) -> RetrieveResponse:
    """Execute hybrid retrieval with optional metadata filters."""
    try:
        retriever = HybridRetriever(embedding_service, qdrant_store)
        results = retriever.retrieve(
            query=request.query,
            top_k=request.top_k,
            filters=request.filters,
        )

        chunks = [
            RetrievedChunk(
                chunk_id=r["chunk_id"],
                document_id=r["document_id"],
                content=r["content"],
                score=r["score"],
                metadata=r.get("metadata", {}),
            )
            for r in results
        ]

        return RetrieveResponse(
            query=request.query,
            chunks=chunks,
            total_found=len(chunks),
        )
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Retrieval failed: {exc}") from exc
