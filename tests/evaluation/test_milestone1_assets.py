import json
import subprocess
import sys
from collections import Counter
from pathlib import Path

from evaluation.validation import load_jsonl, normalize_text, validate_dataset

ROOT = Path(__file__).resolve().parents[2]


def test_evaluation_dataset_contract() -> None:
    cases = load_jsonl(ROOT / "evaluation" / "dataset.jsonl")
    sources = load_jsonl(ROOT / "evaluation" / "source_manifest.jsonl")
    assert validate_dataset(cases, {item["source_id"] for item in sources}) == []


def test_heldout_split_is_stratified_across_case_groups() -> None:
    cases = load_jsonl(ROOT / "evaluation" / "dataset.jsonl")
    heldout = Counter(
        (case["case_type"], case["language"])
        for case in cases
        if case["split"] == "heldout"
    )
    assert heldout == {
        ("answerable", "en"): 6,
        ("answerable", "fr"): 6,
        ("unsupported", "en"): 1,
        ("unsupported", "fr"): 1,
        ("multi_turn", "en"): 1,
        ("multi_turn", "fr"): 1,
    }


def test_evaluation_schema_declares_all_runtime_required_fields() -> None:
    schema = json.loads(
        (ROOT / "evaluation" / "schema" / "evaluation_case.schema.json").read_text(
            encoding="utf-8"
        )
    )
    assert set(schema["required"]) == {
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


def test_evaluation_questions_are_not_exact_source_instructions() -> None:
    cases = load_jsonl(ROOT / "evaluation" / "dataset.jsonl")
    sources = load_jsonl(ROOT / "evaluation" / "source_manifest.jsonl")
    source_questions = {
        normalize_text(item["instruction"])
        for item in sources
        if item["document_id"] != "faq_pdf"
    }
    for case in cases:
        assert normalize_text(case["turns"][-1]["content"]) not in source_questions


def test_source_manifest_is_reproducible() -> None:
    result = subprocess.run(
        [sys.executable, "scripts/evaluation/build_source_manifest.py", "--check"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, result.stdout + result.stderr


def test_all_cases_are_approved_gold_data() -> None:
    cases = load_jsonl(ROOT / "evaluation" / "dataset.jsonl")
    assert {case["review"]["status"] for case in cases} == {"approved"}
    assert all(case["review"]["reviewer"] for case in cases)
