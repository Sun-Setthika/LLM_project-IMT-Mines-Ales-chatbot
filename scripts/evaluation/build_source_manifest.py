"""Build or verify stable source IDs for repository knowledge sources."""

import argparse
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUTPUT_PATH = ROOT / "evaluation" / "source_manifest.jsonl"

SOURCE_CONFIG = {
    "FAQ_ADVANCED_ML.json": ("faq_advanced_ml", "Advanced Machine Learning", "academic"),
    "FAQ_DECISION_ANALYSIS.json": ("faq_decision_analysis", "Decision Analysis", "academic"),
    "FAQ_DL.json": ("faq_dl", "Deep Learning", "academic"),
    "FAQ_MATHS_ML.json": ("faq_maths_ml", "Mathematics for Machine Learning", "academic"),
    "FAQ_MEUH.json": ("faq_meuh", "Maison des Eleves", "housing"),
    "FAQ_PRO_CONTRACT.json": ("faq_pro_contract", "Professionalization Contract", "professional"),
    "FAQ_SCHOOL.json": ("faq_school", "IMT Mines Ales School FAQ", "school"),
    "GEN_CONVERSATION.json": ("gen_conversation", "General Conversation", "conversation"),
}


def canonical_json(value: object) -> bytes:
    return json.dumps(
        value, ensure_ascii=False, sort_keys=True, separators=(",", ":")
    ).encode("utf-8")


def build_records() -> list[dict[str, object]]:
    records: list[dict[str, object]] = []
    for filename in sorted(SOURCE_CONFIG):
        prefix, title, category = SOURCE_CONFIG[filename]
        path = ROOT / "dataset" / filename
        rows = json.loads(path.read_text(encoding="utf-8"))
        for index, row in enumerate(rows, start=1):
            records.append(
                {
                    "source_id": f"{prefix}:{index:04d}",
                    "document_id": prefix,
                    "record_index": index,
                    "source_path": path.relative_to(ROOT).as_posix(),
                    "title": title,
                    "category": category,
                    "language": "en",
                    "instruction": row["instruction"],
                    "content_sha256": hashlib.sha256(canonical_json(row)).hexdigest(),
                    "canonical_url": None,
                    "reviewed": False,
                }
            )

    pdf_path = ROOT / "FAQ.pdf"
    records.append(
        {
            "source_id": "faq_pdf:p1",
            "document_id": "faq_pdf",
            "record_index": 1,
            "source_path": "FAQ.pdf",
            "title": "IMT Mines Ales FAQ PDF",
            "category": "housing",
            "language": "en",
            "instruction": "FAQ PDF page 1",
            "content_sha256": hashlib.sha256(pdf_path.read_bytes()).hexdigest(),
            "canonical_url": None,
            "reviewed": False,
        }
    )
    return records


def render(records: list[dict[str, object]]) -> str:
    return "".join(
        json.dumps(record, ensure_ascii=False, sort_keys=True) + "\n"
        for record in records
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()

    expected = render(build_records())
    if args.check:
        if not OUTPUT_PATH.exists() or OUTPUT_PATH.read_text(encoding="utf-8") != expected:
            print(f"Source manifest is stale: {OUTPUT_PATH}")
            return 1
        print(f"Source manifest is current: {OUTPUT_PATH}")
        return 0

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_text(expected, encoding="utf-8", newline="\n")
    print(f"Wrote {len(build_records())} sources to {OUTPUT_PATH}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

