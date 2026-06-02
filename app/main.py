"""RAG Platform API — Reference Architecture."""

import logging

from fastapi import FastAPI, Response
from prometheus_client import CONTENT_TYPE_LATEST, generate_latest

from app.api.deps import get_database_service, get_qdrant_store
from app.api.routes import ingestion, query, retrieval
from app.api.schemas import HealthResponse
from app.config import settings

logging.basicConfig(level=settings.log_level)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="AI RAG Reference Architecture",
    description="Production-style RAG platform reference implementation",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

app.include_router(ingestion.router)
app.include_router(retrieval.router)
app.include_router(query.router)


@app.get("/health", response_model=HealthResponse, tags=["health"])
async def health_check() -> HealthResponse:
    qdrant_ok = get_qdrant_store().health_check()
    postgres_ok = get_database_service().health_check()

    status = "healthy" if qdrant_ok and postgres_ok else "degraded"

    return HealthResponse(
        status=status,
        qdrant="connected" if qdrant_ok else "disconnected",
        postgres="connected" if postgres_ok else "disconnected",
    )


@app.get("/metrics", tags=["observability"])
async def metrics() -> Response:
    return Response(content=generate_latest(), media_type=CONTENT_TYPE_LATEST)


@app.get("/", tags=["root"])
async def root():
    return {
        "name": "AI RAG Reference Architecture",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health",
    }
