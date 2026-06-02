"""RAG evaluation metrics."""

import re
import time
from dataclasses import dataclass


@dataclass
class EvaluationResult:
    query: str
    context_relevance: float
    answer_relevance: float
    faithfulness: float
    groundedness: float
    latency_ms: int
    cost_usd: float
    retrieval_accuracy: float


def compute_context_relevance(query: str, chunks: list[dict]) -> float:
    """Score how relevant retrieved chunks are to the query."""
    if not chunks:
        return 0.0

    query_tokens = set(_tokenize(query))
    scores = []

    for chunk in chunks:
        content_tokens = set(_tokenize(chunk.get("content", "")))
        overlap = len(query_tokens & content_tokens)
        scores.append(overlap / max(len(query_tokens), 1))

    return sum(scores) / len(scores)


def compute_faithfulness(answer: str, chunks: list[dict]) -> float:
    """Verify answer claims are supported by retrieved context."""
    context_text = " ".join(c.get("content", "") for c in chunks)
    context_tokens = set(_tokenize(context_text))

    sentences = [s.strip() for s in re.split(r"[.!?]+", answer) if s.strip()]
    if not sentences:
        return 0.0

    supported = 0
    for sentence in sentences:
        sentence_tokens = set(_tokenize(sentence))
        if not sentence_tokens:
            continue
        overlap = len(sentence_tokens & context_tokens)
        if overlap / len(sentence_tokens) >= 0.5:
            supported += 1

    return supported / len(sentences)


def compute_groundedness(answer: str, chunks: list[dict]) -> float:
    """Score citation coverage and source usage."""
    if not chunks:
        return 0.0

    cited = sum(1 for i in range(1, len(chunks) + 1) if f"source {i}" in answer.lower())
    citation_score = cited / len(chunks)

    context_used = any(
        _tokenize(chunk.get("content", ""))[0] in _tokenize(answer)
        for chunk in chunks
        if chunk.get("content")
    )

    usage_score = 0.5 if context_used else 0.0
    return 0.6 * citation_score + 0.4 * usage_score


def compute_retrieval_accuracy(
    retrieved_ids: list[str],
    expected_ids: list[str],
    k: int = 3,
) -> float:
    """Check if expected chunks appear in top-k results."""
    if not expected_ids:
        return 0.0

    top_k = set(retrieved_ids[:k])
    hits = sum(1 for eid in expected_ids if eid in top_k)
    return hits / len(expected_ids)


def evaluate_query(
    query: str,
    answer: str,
    chunks: list[dict],
    expected_chunk_ids: list[str] | None = None,
    latency_ms: int = 0,
    cost_usd: float = 0.0,
) -> EvaluationResult:
    """Run all evaluation metrics for a single query."""
    context_rel = compute_context_relevance(query, chunks)
    faith = compute_faithfulness(answer, chunks)
    grounded = compute_groundedness(answer, chunks)
    retrieval_acc = compute_retrieval_accuracy(
        [c.get("chunk_id", "") for c in chunks],
        expected_chunk_ids or [],
    )

    return EvaluationResult(
        query=query,
        context_relevance=round(context_rel, 3),
        answer_relevance=round(context_rel * 0.9 + faith * 0.1, 3),
        faithfulness=round(faith, 3),
        groundedness=round(grounded, 3),
        latency_ms=latency_ms,
        cost_usd=round(cost_usd, 6),
        retrieval_accuracy=round(retrieval_acc, 3),
    )


def generate_scorecard(results: list[EvaluationResult], run_name: str) -> dict:
    """Aggregate evaluation results into a scorecard."""
    if not results:
        return {"run_name": run_name, "sample_count": 0, "overall_status": "NO_DATA"}

    n = len(results)
    metrics = {
        "context_relevance": {
            "score": round(sum(r.context_relevance for r in results) / n, 3),
            "threshold": 0.75,
        },
        "answer_relevance": {
            "score": round(sum(r.answer_relevance for r in results) / n, 3),
            "threshold": 0.80,
        },
        "faithfulness": {
            "score": round(sum(r.faithfulness for r in results) / n, 3),
            "threshold": 0.85,
        },
        "groundedness": {
            "score": round(sum(r.groundedness for r in results) / n, 3),
            "threshold": 0.80,
        },
        "latency_p95_ms": {
            "score": sorted(r.latency_ms for r in results)[int(n * 0.95)] if n > 1 else results[0].latency_ms,
            "threshold": 3000,
        },
        "cost_per_query_usd": {
            "score": round(sum(r.cost_usd for r in results) / n, 6),
            "threshold": 0.05,
        },
        "retrieval_accuracy_at_3": {
            "score": round(sum(r.retrieval_accuracy for r in results) / n, 3),
            "threshold": 0.70,
        },
    }

    for key, val in metrics.items():
        if key == "latency_p95_ms":
            val["status"] = "PASS" if val["score"] <= val["threshold"] else "FAIL"
        elif key == "cost_per_query_usd":
            val["status"] = "PASS" if val["score"] <= val["threshold"] else "FAIL"
        else:
            val["status"] = "PASS" if val["score"] >= val["threshold"] else "FAIL"

    all_pass = all(v["status"] == "PASS" for v in metrics.values())

    return {
        "run_name": run_name,
        "sample_count": n,
        "metrics": metrics,
        "overall_status": "PASS" if all_pass else "FAIL",
        "overall_score": round(
            sum(
                v["score"] if k != "latency_p95_ms" and k != "cost_per_query_usd"
                else (1 - v["score"] / v["threshold"])
                for k, v in metrics.items()
            ) / len(metrics),
            3,
        ),
        "generated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    }


def _tokenize(text: str) -> list[str]:
    return re.findall(r"\w+", text.lower())
