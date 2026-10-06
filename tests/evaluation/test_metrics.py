import pytest

from evaluation.metrics import aggregate_retrieval_metrics, recall_at_k, reciprocal_rank


def test_recall_at_k_counts_all_relevant_sources() -> None:
    assert recall_at_k(["a", "b"], ["x", "a", "b"], 2) == 0.5
    assert recall_at_k(["a", "b"], ["x", "a", "b"], 3) == 1.0


def test_reciprocal_rank_uses_first_relevant_result() -> None:
    assert reciprocal_rank(["b"], ["x", "b", "b"], 10) == 0.5
    assert reciprocal_rank(["z"], ["x", "b"], 10) == 0.0


def test_aggregate_metrics_ignore_cases_without_relevant_sources() -> None:
    metrics = aggregate_retrieval_metrics(
        {"supported": ["a"], "unsupported": []},
        {"supported": ["x", "a"], "unsupported": ["x"]},
    )
    assert metrics == {
        "recall@1": 0.0,
        "recall@3": 1.0,
        "recall@5": 1.0,
        "mrr@10": 0.5,
    }


@pytest.mark.parametrize("value", [0, -1])
def test_metrics_reject_invalid_limits(value: int) -> None:
    with pytest.raises(ValueError):
        recall_at_k(["a"], ["a"], value)
    with pytest.raises(ValueError):
        reciprocal_rank(["a"], ["a"], value)

