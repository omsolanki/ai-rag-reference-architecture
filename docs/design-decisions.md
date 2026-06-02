# Architecture Trade-Offs and Design Decisions

> *Written from the perspective of a Head of Engineering making platform decisions for an enterprise AI knowledge platform.*

## Executive Summary

Technology choices in an AI platform are not about selecting the "best" tool — they are about optimizing for team capability, operational maturity, time-to-value, and a credible scaling path. Every decision below reflects a deliberate trade-off between simplicity (reference implementation) and enterprise readiness (production path).

---

## Why Qdrant

**Decision:** Qdrant as the vector database.

**Rationale:**

When evaluating vector stores for an enterprise RAG platform, I prioritize filtering capabilities and deployment flexibility over ecosystem size. Qdrant provides:

- **Payload-based filtering** that maps directly to enterprise access patterns (department, classification, tenant ID)
- **Self-hosted and managed options** — Docker Compose for development, Qdrant Cloud or StatefulSet for production
- **Predictable performance** with HNSW indexing and optional quantization for cost control

**Trade-off accepted:** Operating Qdrant alongside PostgreSQL means two data stores to manage. I rejected pgvector-as-single-store because vector search at scale and rich filtering are not PostgreSQL's strength. I rejected Pinecone because vendor lock-in and lack of self-hosted options conflict with enterprise data residency requirements.

**When I would reconsider:** If the team already operates Elasticsearch at scale, a BM25 + dense hybrid via Elasticsearch + vector field may be simpler than adding Qdrant.

---

## Why LangChain

**Decision:** LangChain for orchestration primitives (text splitting, OpenAI integration, prompt templates).

**Rationale:**

LangChain is not the orchestration layer I would choose for a large production system long-term — I would likely migrate to a custom pipeline or LangGraph for complex agent workflows. For a **reference architecture**, LangChain provides:

- **Industry-standard abstractions** that engineers recognize immediately
- **Rapid integration** with OpenAI embeddings and chat models
- **Text splitting utilities** that implement our chunking strategy without custom code

**Trade-off accepted:** LangChain adds dependency weight and abstraction overhead. The implementation uses LangChain selectively — embeddings, text splitting, and chat models — without adopting the full agent framework.

**When I would reconsider:** For production agent systems with branching logic, tool use, and human-in-the-loop, LangGraph or a custom state machine provides better control.

---

## Why PostgreSQL

**Decision:** PostgreSQL for document metadata, query audit logs, and evaluation scorecards.

**Rationale:**

Vector databases excel at similarity search but are poor relational stores. PostgreSQL provides:

- **ACID compliance** for audit trails and compliance requirements
- **JSONB** for flexible metadata without schema rigidity
- **Operational familiarity** — every engineering team knows PostgreSQL
- **Future pgvector option** for small-scale hybrid deployments

**Trade-off accepted:** Two databases (Qdrant + PostgreSQL) instead of one. The separation is intentional — each store optimized for its workload.

---

## Why FastAPI

**Decision:** FastAPI as the API framework.

**Rationale:**

For an AI platform API layer, I need:

- **Async I/O** for concurrent embedding and LLM calls
- **Automatic OpenAPI documentation** for platform consumers
- **Pydantic validation** for type-safe request/response contracts
- **Python ecosystem** alignment with ML/AI tooling

FastAPI delivers all of this with minimal boilerplate. Alternatives considered:

| Framework | Why Not |
|-----------|---------|
| Flask | No native async; slower for I/O-bound AI workloads |
| Django | Over-engineered for an API-only service |
| Node.js/Express | Weaker ML ecosystem integration |

**Trade-off accepted:** Python GIL limits CPU-bound parallelism. Mitigated by horizontal scaling and offloading embedding to dedicated workers at scale.

---

## Why Docker

**Decision:** Docker and Docker Compose for local development and as the container format for all deployment targets.

**Rationale:**

Containerization is non-negotiable for AI platforms:

- **Reproducible environments** — identical behavior from laptop to production
- **Service composition** — API, Qdrant, PostgreSQL orchestrated via Compose locally
- **Deployment portability** — same container runs on ECS, Kubernetes, or Cloud Run
- **CI/CD integration** — build once, deploy anywhere

**Trade-off accepted:** Docker adds complexity for developers unfamiliar with containers. Mitigated by a single `docker compose up` command and comprehensive setup documentation.

---

## Cross-Cutting Decisions

### Minimal Code, Maximum Documentation

This repository intentionally prioritizes architecture documentation over code volume. Production systems require 10x more code (auth, rate limiting, circuit breakers, retry logic). The reference implementation demonstrates **patterns**, not **completeness**.

### OpenAI as Default LLM Provider

OpenAI is chosen for broad recognition and reliable API quality. The architecture supports provider abstraction — swap `ChatOpenAI` for Azure OpenAI, Anthropic, or local models without changing the retrieval layer.

### Evaluation as a First-Class Concern

Most RAG demos skip evaluation. This platform treats evaluation as a platform capability because **you cannot improve what you do not measure**. The evaluation framework is designed before scaling retrieval or prompt engineering efforts.

---

## Decision Log

| Decision | ADR | Status |
|----------|-----|--------|
| Vector database: Qdrant | [ADR-001](../architecture-decision-records/adr-001-vector-db.md) | Accepted |
| Chunking strategy | [ADR-002](../architecture-decision-records/adr-002-chunking-strategy.md) | Accepted |
| Hybrid retrieval | [ADR-003](../architecture-decision-records/adr-003-retrieval-strategy.md) | Accepted |
| Evaluation approach | [ADR-004](../architecture-decision-records/adr-004-evaluation-approach.md) | Accepted |
