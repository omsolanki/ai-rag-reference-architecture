"""Pydantic schemas for API request/response models."""

from pydantic import BaseModel, Field


class DocumentMetadata(BaseModel):
    source: str | None = None
    department: str | None = None
    classification: str | None = None
    tags: list[str] = Field(default_factory=list)


class IngestRequest(BaseModel):
    document_id: str = Field(..., min_length=1, max_length=255)
    title: str = Field(..., min_length=1, max_length=500)
    content: str = Field(..., min_length=1, max_length=1_000_000)
    source: str = Field(default="default", max_length=255)
    metadata: DocumentMetadata | None = None


class IngestResponse(BaseModel):
    document_id: str
    title: str
    chunk_count: int
    status: str = "success"


class RetrieveRequest(BaseModel):
    query: str = Field(..., min_length=1, max_length=2000)
    top_k: int = Field(default=5, ge=1, le=20)
    filters: dict | None = None


class RetrievedChunk(BaseModel):
    chunk_id: str
    document_id: str
    content: str
    score: float
    metadata: dict = Field(default_factory=dict)


class RetrieveResponse(BaseModel):
    query: str
    chunks: list[RetrievedChunk]
    total_found: int


class QueryRequest(BaseModel):
    question: str = Field(..., min_length=1, max_length=2000)
    filters: dict | None = None


class SourceCitation(BaseModel):
    chunk_id: str
    document_id: str
    title: str
    source: str
    relevance_score: float


class QueryResponse(BaseModel):
    question: str
    answer: str
    sources: list[SourceCitation]
    latency_ms: int
    estimated_cost_usd: float
    model: str


class HealthResponse(BaseModel):
    status: str
    qdrant: str
    postgres: str
