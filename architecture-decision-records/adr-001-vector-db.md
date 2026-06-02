# ADR-001: Vector Database Selection — Qdrant

## Status

Accepted

## Context

The RAG platform requires a vector database to store document embeddings and support similarity search with metadata filtering. Key requirements include:

- Hybrid retrieval (dense vectors + payload/keyword filtering)
- Horizontal scalability path
- Self-hosted and managed deployment options
- Low operational overhead for reference implementation
- Strong filtering capabilities for multi-tenant and document-level access control

## Decision

We selected **Qdrant** as the vector database for this reference architecture.

## Alternatives Considered

| Option | Pros | Cons |
|--------|------|------|
| **Pinecone** | Fully managed, excellent DX | Vendor lock-in, limited self-hosted option |
| **Weaviate** | Hybrid search built-in, GraphQL | Heavier operational footprint |
| **pgvector** | Single database, simpler stack | Weaker at scale for pure vector workloads |
| **Milvus** | Enterprise scale | Complex cluster setup for small deployments |
| **Qdrant** | Fast, filter-rich, Docker-native | Smaller ecosystem than Pinecone |

## Rationale

1. **Filtering-first design** — Qdrant's payload indexing supports metadata filtering natively, which is critical for enterprise RAG (department, classification, date ranges).
2. **Deployment flexibility** — Runs locally via Docker Compose, on Kubernetes as a StatefulSet, or via Qdrant Cloud for managed production.
3. **Performance** — HNSW indexing with configurable quantization supports cost-effective scaling.
4. **Operational simplicity** — Single binary, health endpoints, and minimal configuration for reference deployments.

## Consequences

### Positive

- Clean separation between vector search (Qdrant) and relational metadata (PostgreSQL)
- Hybrid retrieval can be implemented with dense search + payload filters without additional infrastructure
- Straightforward local development experience

### Negative

- Team must operate two data stores (Qdrant + PostgreSQL)
- No built-in full-text search; keyword component uses payload matching or external integration
- Requires separate backup and disaster recovery procedures for vector data

## References

- [Qdrant Documentation](https://qdrant.tech/documentation/)
- See also: [ADR-003: Retrieval Strategy](./adr-003-retrieval-strategy.md)
