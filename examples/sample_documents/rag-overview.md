# RAG Architecture Overview

## What is RAG?

Retrieval-Augmented Generation (RAG) combines information retrieval with large language model generation. Instead of relying solely on the LLM's training data, RAG retrieves relevant documents at query time and grounds the response in that context.

## Architecture Components

### Ingestion Pipeline

Documents flow through chunking, embedding generation, and vector storage:

1. **Chunking**: Documents split into 512-token segments with 64-token overlap
2. **Embedding**: Each chunk converted to a 1536-dimensional vector using OpenAI embeddings
3. **Storage**: Vectors stored in Qdrant with metadata payloads for filtering

### Retrieval Pipeline

Queries follow a hybrid retrieval strategy:

1. **Dense search**: Query embedded and matched against vector store (cosine similarity)
2. **Metadata filtering**: Results filtered by source, department, or classification
3. **Re-ranking**: Combined dense + keyword score fusion
4. **Context assembly**: Top-3 chunks assembled into LLM context window

### Generation Pipeline

The LLM receives a structured prompt with retrieved context and generates a grounded response with source citations.

## Hybrid Retrieval Strategy

Pure vector search excels at semantic similarity but misses exact keyword matches. Our hybrid approach combines:

- Dense retrieval (70% weight): Semantic similarity via embeddings
- Keyword matching (30% weight): Token overlap for exact terms

This improves recall for queries containing product codes, acronyms, and proper nouns.

## Evaluation Framework

Quality is measured across seven dimensions: context relevance, answer relevance, faithfulness, groundedness, latency, cost per query, and retrieval accuracy. See the evaluation framework documentation for scorecard templates and thresholds.
