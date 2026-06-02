"""Full RAG query endpoint."""

import time

from fastapi import APIRouter, Depends, HTTPException

from app.api.deps import get_database_service, get_embedding_service, get_qdrant_store
from app.api.schemas import QueryRequest, QueryResponse, SourceCitation
from app.config import settings
from app.embeddings.generator import EmbeddingService
from app.rag.context_builder import ContextBuilder
from app.rag.qdrant_store import QdrantStore
from app.rag.retrieval import HybridRetriever
from app.services.database import DatabaseService
from app.services.llm_orchestration import LLMOrchestrator
from app.services.prompt_manager import PromptManager

router = APIRouter(prefix="/api/v1", tags=["query"])


@router.post("/query", response_model=QueryResponse)
async def query(
    request: QueryRequest,
    embedding_service: EmbeddingService = Depends(get_embedding_service),
    qdrant_store: QdrantStore = Depends(get_qdrant_store),
    db: DatabaseService = Depends(get_database_service),
) -> QueryResponse:
    """Full RAG pipeline: retrieve, build context, generate grounded response."""
    start = time.perf_counter()

    try:
        retriever = HybridRetriever(embedding_service, qdrant_store)
        results = retriever.retrieve(
            query=request.question,
            top_k=settings.retrieval_top_k,
            filters=request.filters,
            rerank=True,
        )

        context_builder = ContextBuilder()
        context = context_builder.build(results)

        prompt_manager = PromptManager()
        messages = prompt_manager.build_messages(request.question, context)

        orchestrator = LLMOrchestrator()
        llm_result = orchestrator.generate(messages)

        latency_ms = int((time.perf_counter() - start) * 1000)

        sources = [
            SourceCitation(
                chunk_id=r["chunk_id"],
                document_id=r["document_id"],
                title=r.get("metadata", {}).get("title", "Unknown"),
                source=r.get("metadata", {}).get("source", "Unknown"),
                relevance_score=r["score"],
            )
            for r in results
        ]

        db.log_query(
            query_text=request.question,
            response_text=llm_result["answer"],
            retrieved_chunk_ids=[r["chunk_id"] for r in results],
            latency_ms=latency_ms,
            token_count=llm_result["total_tokens"],
            estimated_cost_usd=llm_result["estimated_cost_usd"],
        )

        return QueryResponse(
            question=request.question,
            answer=llm_result["answer"],
            sources=sources,
            latency_ms=latency_ms,
            estimated_cost_usd=llm_result["estimated_cost_usd"],
            model=settings.openai_model,
        )
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Query failed: {exc}") from exc
