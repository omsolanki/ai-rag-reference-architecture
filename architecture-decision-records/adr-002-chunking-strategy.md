# ADR-002: Chunking Strategy

## Status

Accepted

## Context

Document chunking directly impacts retrieval quality, context window utilization, and answer faithfulness. Poor chunking causes:

- Context fragmentation (answers split across chunks)
- Semantic drift (chunks lose topical coherence)
- Over-retrieval (too many irrelevant chunks consume token budget)

## Decision

We adopt a **recursive character-based splitting** strategy with the following parameters:

| Parameter | Value | Rationale |
|-----------|-------|-----------|
| Chunk size | 512 tokens (approx.) | Balances context richness with retrieval precision |
| Chunk overlap | 64 tokens (12.5%) | Preserves boundary context without excessive duplication |
| Separators | `\n\n`, `\n`, `. `, ` ` | Respects document structure hierarchy |

Implementation uses LangChain's `RecursiveCharacterTextSplitter` with token-aware length function.

## Alternatives Considered

| Strategy | Use Case | Why Not Default |
|----------|----------|-----------------|
| Fixed-size character split | Simple documents | Breaks mid-sentence, poor semantic boundaries |
| Semantic chunking | Long-form content | Higher compute cost, embedding dependency at ingest |
| Document-structure aware (Markdown/HTML) | Structured docs | Requires format-specific parsers; added complexity |
| Parent-child chunking | Large documents | Valuable at scale; deferred to future enhancement |

## Metadata Enrichment

Each chunk stores:

```json
{
  "document_id": "doc-001",
  "chunk_index": 0,
  "source": "engineering-handbook",
  "title": "Deployment Guidelines",
  "total_chunks": 12
}
```

This enables filtered retrieval and citation traceability.

## Consequences

### Positive

- Predictable chunk sizes for embedding model input limits
- Overlap reduces boundary information loss
- Metadata supports re-ranking and source attribution

### Negative

- Not optimal for tabular or code-heavy documents
- Semantic chunking would improve quality for heterogeneous corpora
- Overlap increases storage by ~12% and embedding API costs proportionally

## Future Enhancements

- Format-aware chunking (PDF, Markdown, code)
- Parent-child retrieval (small chunks for search, large chunks for context)
- Dynamic chunk sizing based on document type
