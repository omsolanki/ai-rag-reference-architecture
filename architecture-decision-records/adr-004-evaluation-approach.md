# ADR-004: Evaluation Approach

## Status

Accepted

## Context

RAG systems degrade silently — retrieval quality, prompt drift, and model updates can reduce answer quality without obvious failures. A structured evaluation framework is essential for platform governance and continuous improvement.

## Decision

We adopt a **multi-dimensional evaluation framework** covering seven quality dimensions, implemented as a lightweight in-process evaluation module with PostgreSQL persistence for scorecards.

## Evaluation Dimensions

| Dimension | Definition | Measurement Method |
|-----------|------------|-------------------|
| Context Relevance | Retrieved chunks address the query topic | LLM-as-judge or keyword overlap |
| Answer Relevance | Response directly answers the question | LLM-as-judge scoring 1-5 |
| Faithfulness | Answer claims supported by retrieved context | Claim extraction + context verification |
| Groundedness | Response cites and uses retrieved sources | Citation coverage ratio |
| Latency | End-to-end query response time | P50/P95 from query logs |
| Cost per Query | Token usage × model pricing | Calculated from OpenAI usage metadata |
| Retrieval Accuracy | Expected chunk retrieved in top-k | Exact match against golden set |

## Evaluation Workflow

```
Golden Dataset → Batch Query Execution → Metric Computation → Scorecard → Trend Analysis
```

1. **Golden dataset** — curated query/expected-output pairs in `examples/`
2. **Batch execution** — run queries through full RAG pipeline
3. **Metric computation** — automated scoring per dimension
4. **Scorecard generation** — aggregate report with pass/fail thresholds
5. **Persistence** — store in `evaluation_runs` PostgreSQL table

## Pass/Fail Thresholds (Reference)

| Metric | Pass Threshold | Target |
|--------|---------------|--------|
| Context Relevance | ≥ 0.75 | 0.85 |
| Answer Relevance | ≥ 0.80 | 0.90 |
| Faithfulness | ≥ 0.85 | 0.95 |
| Groundedness | ≥ 0.80 | 0.90 |
| Latency P95 | ≤ 3000ms | 1500ms |
| Cost per Query | ≤ $0.05 | $0.02 |
| Retrieval Accuracy@3 | ≥ 0.70 | 0.85 |

## Alternatives Considered

| Approach | Trade-off |
|----------|-----------|
| RAGAS framework | Comprehensive but heavy dependency |
| Human evaluation only | Gold standard but not scalable |
| A/B testing in production | Requires traffic; deferred to enterprise phase |
| LLM-as-judge only | Fast but model-dependent bias |

## Consequences

### Positive

- Quantifiable quality gates before deployment
- Regression detection when changing chunking, retrieval, or prompts
- Cost and latency visibility for platform economics

### Negative

- LLM-as-judge introduces evaluator model bias
- Golden dataset requires ongoing curation
- Automated faithfulness checks are approximate, not definitive

## Implementation

- `app/evaluation/metrics.py` — metric computation functions
- `POST /evaluation/run` — trigger evaluation batch (future endpoint)
- Sample scorecards in [Evaluation Framework](../docs/evaluation-framework.md)
