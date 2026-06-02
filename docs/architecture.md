# Architecture Overview

## Purpose

This document describes the production-style architecture of the AI RAG Reference Architecture — a platform designed to demonstrate enterprise-grade Retrieval-Augmented Generation patterns for knowledge-intensive applications.

## Design Principles

1. **Separation of concerns** — API, retrieval, orchestration, and storage are independently evolvable
2. **Grounded responses** — every answer is traceable to retrieved source chunks
3. **Observable by default** — latency, cost, and quality metrics are first-class
4. **Security-aware** — prompt injection mitigation and data isolation are designed in, not bolted on
5. **Scale-ready** — single-node simplicity with a clear path to Kubernetes and multi-tenant deployment

## High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         Client Layer                            │
│              (Web App, CLI, Internal Tools, API Consumers)      │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                      API Layer (FastAPI)                        │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────────┐  │
│  │  Ingestion   │  │  Retrieval   │  │  Query (Full RAG)    │  │
│  │  /ingest     │  │  /retrieve   │  │  /query              │  │
│  └──────────────┘  └──────────────┘  └──────────────────────┘  │
└────────────────────────────┬────────────────────────────────────┘
                             │
          ┌──────────────────┼──────────────────┐
          ▼                  ▼                  ▼
┌─────────────────┐ ┌───────────────┐ ┌─────────────────┐
│ Query Processing│ │  Retrieval    │ │  LLM            │
│                 │ │  Layer        │ │  Orchestration  │
│ • Normalization │ │               │ │                 │
│ • Filter build  │ │ • Hybrid      │ │ • Prompt mgmt   │
│ • Validation    │ │ • Re-ranking  │ │ • OpenAI calls  │
└─────────────────┘ │ • Context     │ │ • Grounding     │
                    └───────┬───────┘ └────────┬────────┘
                            │                  │
              ┌─────────────┴──────┐           │
              ▼                    ▼           ▼
       ┌────────────┐      ┌────────────┐  ┌──────────┐
       │   Qdrant   │      │ PostgreSQL │  │  OpenAI  │
       │  (Vectors) │      │ (Metadata) │  │   API    │
       └────────────┘      └────────────┘  └──────────┘
```

## Component Responsibilities

### API Layer

| Component | Responsibility |
|-----------|---------------|
| Ingestion Endpoint | Accept documents, chunk, embed, store in Qdrant, record metadata in PostgreSQL |
| Retrieval Endpoint | Execute hybrid retrieval with metadata filters; return ranked chunks |
| Query Endpoint | Full RAG pipeline: retrieve → context build → LLM → grounded response |

### Query Processing

Normalizes user input, applies metadata filters (source, department, classification), and validates query parameters before retrieval.

### Retrieval Layer

Implements hybrid retrieval combining dense vector search with keyword/payload matching, followed by a re-ranking stage to select the most relevant chunks for the LLM context window.

### Context Builder

Assembles retrieved chunks into a structured context block with source attribution, enforcing token budget constraints.

### LLM Orchestration

Manages prompt templates, calls OpenAI for completion, and ensures responses are grounded in retrieved context with explicit citation requirements.

### Storage

| Store | Purpose |
|-------|---------|
| Qdrant | Vector embeddings and chunk payloads for similarity search |
| PostgreSQL | Document metadata, query audit logs, evaluation scorecards |

## Data Flow

### Ingestion Flow

```
Document → Chunking → Embedding → Qdrant Upsert → PostgreSQL Metadata
```

### Query Flow

```
Question → Query Processing → Hybrid Retrieval → Re-ranking
    → Context Building → Prompt Assembly → LLM Generation → Response + Citations
```

## Non-Functional Requirements

| Requirement | Target | Implementation |
|-------------|--------|----------------|
| Latency (P95) | < 3s | Async I/O, configurable top-k, connection pooling |
| Availability | 99.9% | Health checks, graceful degradation |
| Cost per query | < $0.05 | Small embedding model, rerank top-k=3 |
| Auditability | Full query log | PostgreSQL query_logs table |

## Related Documents

- [Design Decisions](./design-decisions.md)
- [Deployment Guide](./deployment-guide.md)
- [Evaluation Framework](./evaluation-framework.md)
- [Security Considerations](./security-considerations.md)
- [Scalability Strategy](./scalability-strategy.md)
