"""Document chunking service."""

import hashlib

from langchain_text_splitters import RecursiveCharacterTextSplitter

from app.config import settings


def chunk_document(
    content: str,
    document_id: str,
    metadata: dict | None = None,
) -> list[dict]:
    """Split document into overlapping chunks with metadata enrichment."""
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=settings.chunk_size,
        chunk_overlap=settings.chunk_overlap,
        length_function=len,
        separators=["\n\n", "\n", ". ", " ", ""],
    )

    text_chunks = splitter.split_text(content)
    base_metadata = metadata or {}

    chunks = []
    for index, text in enumerate(text_chunks):
        chunk_id = f"{document_id}-chunk-{index}"
        chunks.append(
            {
                "chunk_id": chunk_id,
                "document_id": document_id,
                "content": text,
                "chunk_index": index,
                "content_hash": hashlib.sha256(text.encode()).hexdigest()[:16],
                "metadata": {
                    **base_metadata,
                    "total_chunks": len(text_chunks),
                },
            }
        )

    return chunks
