"""Validation helpers for the version-controlled evaluation corpus."""

import json
import re
import unicodedata
from collections import Counter
from pathlib import Path
from typing import Any

EXPECTED_GROUP_COUNTS = {
    ("answerable", "en"): 30,
    ("answerable", "fr"): 30,
    ("unsupported", "en"): 5,
    ("unsupported", "fr"): 5,
    ("multi_turn", "en"): 5,
    ("multi_turn", "fr"): 5,
}

REQUIRED_FIELDS = {
    "case_id",
    "split",
    "case_type",
    "language",
    "category",
    "turns",
    "expected_answer",
    "expected_facts",
    "relevant_source_ids",
    "allowed_citation_ids",
    "expected_tool_behavior",
    "review",
}


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    """Load non-empty JSONL records using strict UTF-8 decoding."""
    records: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8", errors="strict") as handle:
        for line_number, line in enumerate(handle, start=1):
            if not line.strip():
                continue
            try:
                records.append(json.loads(line))
            except json.JSONDecodeError as exc:
                raise ValueError(f"{path}:{line_number}: {exc.msg}") from exc
    return records


def normalize_text(value: str) -> str:
    """Normalize text for duplicate and leakage checks."""
    value = unicodedata.normalize("NFKD", value).casefold()
    value = "".join(char for char in value if not unicodedata.combining(char))
    return re.sub(r"[^a-z0-9]+", " ", value).strip()


def validate_case(case: dict[str, Any]) -> list[str]:
    """Return validation errors for one evaluation case."""
    errors: list[str] = []
    missing = REQUIRED_FIELDS.difference(case)
    if missing:
        errors.append(f"missing fields: {sorted(missing)}")
        return errors

    if case["split"] not in {"development", "heldout"}:
        errors.append("split must be development or heldout")
    if case["case_type"] not in {"answerable", "unsupported", "multi_turn"}:
        errors.append("invalid case_type")
    if case["language"] not in {"en", "fr"}:
        errors.append("language must be en or fr")
    if not isinstance(case["turns"], list) or not case["turns"]:
        errors.append("turns must be a non-empty list")
    elif case["turns"][-1].get("role") != "user":
        errors.append("the final turn must be from the user")
    if case["case_type"] == "multi_turn" and len(case["turns"]) < 3:
        errors.append("multi_turn cases require at least three turns")
    if case["case_type"] != "unsupported" and not case["relevant_source_ids"]:
        errors.append("supported cases require relevant_source_ids")
    if case["case_type"] == "unsupported" and case["relevant_source_ids"]:
        errors.append("unsupported cases cannot declare relevant sources")
    if set(case["allowed_citation_ids"]) != set(case["relevant_source_ids"]):
        errors.append("allowed citations must equal relevant sources")
    if case["review"].get("status") not in {"draft", "approved"}:
        errors.append("review status must be draft or approved")
    if case["review"].get("status") == "approved" and not case["review"].get(
        "reviewer"
    ):
        errors.append("approved cases require a reviewer")
    return errors


def validate_dataset(
    cases: list[dict[str, Any]], source_ids: set[str]
) -> list[str]:
    """Return all structural, count, source, split, and duplicate errors."""
    errors: list[str] = []
    if len(cases) != 80:
        errors.append(f"expected 80 cases, found {len(cases)}")

    case_ids = [case.get("case_id", "") for case in cases]
    duplicates = [key for key, count in Counter(case_ids).items() if count > 1]
    if duplicates:
        errors.append(f"duplicate case IDs: {duplicates}")

    group_counts = Counter(
        (case.get("case_type"), case.get("language")) for case in cases
    )
    if dict(group_counts) != EXPECTED_GROUP_COUNTS:
        errors.append(
            f"unexpected group counts: {dict(group_counts)}; "
            f"expected {EXPECTED_GROUP_COUNTS}"
        )

    split_counts = Counter(case.get("split") for case in cases)
    if split_counts != {"development": 64, "heldout": 16}:
        errors.append(f"expected 64/16 split, found {dict(split_counts)}")

    final_questions: list[str] = []
    for case in cases:
        case_id = case.get("case_id", "<missing>")
        errors.extend(f"{case_id}: {error}" for error in validate_case(case))
        missing_sources = set(case.get("relevant_source_ids", ())).difference(
            source_ids
        )
        if missing_sources:
            errors.append(f"{case_id}: unknown sources {sorted(missing_sources)}")
        if case.get("turns"):
            final_questions.append(normalize_text(case["turns"][-1]["content"]))

    duplicate_questions = [
        question
        for question, count in Counter(final_questions).items()
        if count > 1
    ]
    if duplicate_questions:
        errors.append(f"duplicate final questions: {duplicate_questions}")
    return errors
