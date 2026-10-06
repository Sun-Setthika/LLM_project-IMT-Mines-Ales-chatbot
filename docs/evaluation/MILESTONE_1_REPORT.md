# Milestone 1 Evaluation Dataset Report

## Status

Completed on 2026-09-29. The project owner approved all 80 evaluation cases,
and they are frozen as version-controlled gold data in
`evaluation/dataset.jsonl`.

No application feature or production retrieval code was implemented.

## Corpus Inventory

- 205 JSON FAQ/conversation records across eight source files.
- One PDF source page represented as `faq_pdf:p1`.
- 206 stable source-manifest entries in total.
- 80 approved evaluation cases: 64 development and 16 held out.
- 30 English and 30 French single-turn answerable cases.
- 10 unsupported and 10 multi-turn cases, evenly split by language.

## Evaluation Assets

- The JSON Schema defines the evaluation-case contract.
- Validation checks structure, group counts, split integrity, duplicate
  questions, review status, and source-ID resolution.
- Deterministic functions calculate Recall@K and MRR.
- The source-manifest builder detects changes in the repository knowledge
  sources.
- Automated tests protect the approved dataset and evaluation utilities.

## Notebook Policy

The three original notebooks remain unchanged as historical references. At the
project owner's direction, they are not executable baselines and will not be
repaired, run, or compared with the production application. The obsolete
notebook baseline profiles, manifests, result placeholders, audit script, and
execution guide were removed.

## Next Measurement Point

Milestone 2 will establish the first executable retrieval measurements using
the modular production hybrid pipeline. Component-level measurements may help
diagnose semantic retrieval, BM25, fusion, and reranking, but the required
production architecture remains hybrid retrieval followed by reranking.

Regression gates will be proposed from actual Milestone 2 measurements and
will require project-owner approval. No thresholds or results are invented.

## Verification

- Dataset validation: 80 approved cases and 206 sources.
- Source-manifest reproducibility: passed.
- Focused evaluation tests: 11 passed.
- Full test suite: 11 passed.
- Mypy: no issues in seven source files.
- Python compilation: passed.
- Ruff was unavailable and was not installed.


Repository documents
        |
build_source_manifest.py
        |
source_manifest.jsonl
        |
        | stable source IDs
        v
dataset.jsonl
        |
validation.py
        |
validate_dataset.py
        |
validated evaluation corpus
        |
metrics.py
        |
Recall@K and MRR scores
