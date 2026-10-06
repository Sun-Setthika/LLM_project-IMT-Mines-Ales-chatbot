"""Validate the approved Milestone 1 evaluation dataset and source manifest."""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from evaluation.validation import load_jsonl, validate_dataset  # noqa: E402


def main() -> int:
    cases = load_jsonl(ROOT / "evaluation" / "dataset.jsonl")
    sources = load_jsonl(ROOT / "evaluation" / "source_manifest.jsonl")
    errors = validate_dataset(cases, {source["source_id"] for source in sources})
    if errors:
        for error in errors:
            print(error)
        return 1
    print(f"Validated {len(cases)} evaluation cases and {len(sources)} sources")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
