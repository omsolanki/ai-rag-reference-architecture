"""PostgreSQL service for metadata and audit logging."""

import json
import logging

from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError

from app.config import Settings

logger = logging.getLogger(__name__)


class DatabaseService:
    """Manages document metadata and query audit logs in PostgreSQL."""

    def __init__(self, settings: Settings):
        self.settings = settings
        self.engine = create_engine(
            settings.postgres_url,
            pool_pre_ping=True,
            pool_size=5,
        )

    def record_document(
        self,
        document_id: str,
        title: str,
        source: str,
        chunk_count: int,
        metadata: dict | None = None,
    ) -> None:
        try:
            with self.engine.connect() as conn:
                conn.execute(
                    text("""
                        INSERT INTO documents (document_id, title, source, chunk_count, metadata)
                        VALUES (:document_id, :title, :source, :chunk_count, :metadata)
                        ON CONFLICT (document_id) DO UPDATE SET
                            title = EXCLUDED.title,
                            chunk_count = EXCLUDED.chunk_count,
                            metadata = EXCLUDED.metadata,
                            updated_at = NOW()
                    """),
                    {
                        "document_id": document_id,
                        "title": title,
                        "source": source,
                        "chunk_count": chunk_count,
                        "metadata": json.dumps(metadata or {}),
                    },
                )
                conn.commit()
        except SQLAlchemyError as exc:
            logger.warning("Failed to record document metadata: %s", exc)

    def log_query(
        self,
        query_text: str,
        response_text: str,
        retrieved_chunk_ids: list[str],
        latency_ms: int,
        token_count: int,
        estimated_cost_usd: float,
    ) -> None:
        try:
            with self.engine.connect() as conn:
                conn.execute(
                    text("""
                        INSERT INTO query_logs
                            (query_text, response_text, retrieved_chunk_ids,
                             latency_ms, token_count, estimated_cost_usd)
                        VALUES
                            (:query_text, :response_text, :retrieved_chunk_ids,
                             :latency_ms, :token_count, :estimated_cost_usd)
                    """),
                    {
                        "query_text": query_text,
                        "response_text": response_text,
                        "retrieved_chunk_ids": retrieved_chunk_ids,
                        "latency_ms": latency_ms,
                        "token_count": token_count,
                        "estimated_cost_usd": estimated_cost_usd,
                    },
                )
                conn.commit()
        except SQLAlchemyError as exc:
            logger.warning("Failed to log query: %s", exc)

    def health_check(self) -> bool:
        try:
            with self.engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            return True
        except SQLAlchemyError:
            return False
