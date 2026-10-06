"""Deterministic metrics for production retrieval evaluation."""

from collections.abc import Iterable, Mapping, Sequence


def recall_at_k(
    relevant_ids: Iterable[str], retrieved_ids: Sequence[str], k: int
) -> float:
    """Return the fraction of relevant sources retrieved in the first k results."""
    if k <= 0:
        raise ValueError("k must be greater than zero")

    relevant = set(relevant_ids)
    if not relevant:
        return 0.0

    retrieved = set(retrieved_ids[:k])
    return len(relevant.intersection(retrieved)) / len(relevant)


def reciprocal_rank(
    relevant_ids: Iterable[str], retrieved_ids: Sequence[str], limit: int = 10
) -> float:
    """Return the reciprocal rank of the first relevant result within limit."""
    if limit <= 0:
        raise ValueError("limit must be greater than zero")

    relevant = set(relevant_ids)
    for rank, source_id in enumerate(retrieved_ids[:limit], start=1):
        if source_id in relevant:
            return 1.0 / rank
    return 0.0


def aggregate_retrieval_metrics(
    expected: Mapping[str, Sequence[str]],
    retrieved: Mapping[str, Sequence[str]],
    recall_ks: Sequence[int] = (1, 3, 5),
    mrr_limit: int = 10,
) -> dict[str, float]:
    """Aggregate Recall@K and MRR over cases that have relevant sources."""
    case_ids = [case_id for case_id, ids in expected.items() if ids]
    if not case_ids:
        return {
            **{f"recall@{k}": 0.0 for k in recall_ks},
            f"mrr@{mrr_limit}": 0.0,
        }

    metrics = {
        f"recall@{k}": sum(
            recall_at_k(expected[case_id], retrieved.get(case_id, ()), k)
            for case_id in case_ids
        )
        / len(case_ids)
        for k in recall_ks
    }
    metrics[f"mrr@{mrr_limit}"] = sum(
        reciprocal_rank(
            expected[case_id], retrieved.get(case_id, ()), mrr_limit
        )
        for case_id in case_ids
    ) / len(case_ids)
    return metrics
