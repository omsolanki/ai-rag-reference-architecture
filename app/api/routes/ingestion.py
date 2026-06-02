"""Document ingestion endpoint."""

from fastapi import APIRouter, Depends, HTTPException

from app.api.deps import get_database_service, get_embedding_service, get_qdrant_store
from app.api.schemas import IngestRequest, IngestResponse
from app.embeddings.generator import EmbeddingService
from app.rag.qdrant_store import QdrantStore
from app.services.chunking import chunk_document
from app.services.database import DatabaseService

router = APIRouter(prefix="/api/v1", tags=["ingestion"])


@router.post("/ingest", response_model=IngestResponse)
async def ingest_document(
    request: IngestRequest,
    embedding_service: EmbeddingService = Depends(get_embedding_service),
    qdrant_store: QdrantStore = Depends(get_qdrant_store),
    db: DatabaseService = Depends(get_database_service),
) -> IngestResponse:
    """Ingest a document: chunk, embed, store in Qdrant, record metadata."""
    try:
        metadata = request.metadata.model_dump() if request.metadata else {}
        metadata.update({"source": request.source, "title": request.title})

        chunks = chunk_document(
            content=request.content,
            document_id=request.document_id,
            metadata=metadata,
        )

        if not chunks:
            raise HTTPException(status_code=400, detail="Document produced no chunks")

        texts = [c["content"] for c in chunks]
        embeddings = embedding_service.embed_texts(texts)

        qdrant_store.upsert_chunks(chunks, embeddings)

        db.record_document(
            document_id=request.document_id,
            title=request.title,
            source=request.source,
            chunk_count=len(chunks),
            metadata=metadata,
        )

        return IngestResponse(
            document_id=request.document_id,
            title=request.title,
            chunk_count=len(chunks),
        )
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Ingestion failed: {exc}") from exc
