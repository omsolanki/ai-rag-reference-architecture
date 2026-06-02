# ADR-003: Retrieval Strategy

## Status

Accepted

## Context

Pure dense vector retrieval excels at semantic similarity but can miss exact keyword matches (product codes, acronyms, proper nouns). Enterprise RAG systems require a retrieval strategy that balances recall, precision, and latency.

## Decision

We implement a **hybrid retrieval strategy** with three stages:

```
Query → Dense Vector Search → Metadata Filtering → Re-ranking → Top-N Context
              ↓
        Keyword/Payload Match (merged)
```

### Stage 1: Dense Retrieval

- Embed query using `text-embedding-3-small`
- Search Qdrant with cosine similarity
- Retrieve `top_k = 5` candidates (configurable)

### Stage 2: Metadata Filtering

Apply payload filters before or during search:

```python
filters = {
    "source": "engineering-handbook",
    "department": "platform"
}
```

Supports tenant isolation, document classification, and temporal filtering.

### Stage 3: Re-ranking

- Score fusion: combine dense similarity score with keyword overlap
- Select `rerank_top_k = 3` chunks for context window
- Keyword component uses token overlap ratio against query terms

## Configuration

| Parameter | Default | Purpose |
|-----------|---------|---------|
| `RETRIEVAL_TOP_K` | 5 | Initial candidate pool |
| `RERANK_TOP_K` | 3 | Chunks passed to LLM context |
| Score fusion weight | 0.7 dense / 0.3 keyword | Tunable via evaluation |

## Alternatives Considered

| Strategy | Trade-off |
|----------|-----------|
| Dense only | Simple but misses exact matches |
| BM25 + dense (true hybrid) | Requires separate search engine (Elasticsearch) |
| Cross-encoder re-ranking | Higher quality, 10x latency |
| Multi-query retrieval | Better recall, 3x embedding cost |

## Consequences

### Positive

- Improved recall for mixed semantic/keyword queries
- Metadata filtering enables enterprise access patterns
- Re-ranking reduces noise in LLM context window

### Negative

- Keyword component is simplified (payload match, not full BM25)
- No cross-encoder model adds re-ranking quality ceiling
- Score fusion weights require evaluation-driven tuning

## Evaluation Criteria

Retrieval quality measured via:

- **Retrieval Accuracy** — correct chunk in top-k
- **Context Relevance** — retrieved chunks relevant to query
- **MRR@k** — mean reciprocal rank of first relevant result

See [Evaluation Framework](../docs/evaluation-framework.md) for scorecard templates.
