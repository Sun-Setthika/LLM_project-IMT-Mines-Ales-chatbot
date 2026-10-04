# AGENTS.md

## Project Purpose

This repository contains the IMT Mines Ales Student Assistant, a bilingual
English/French chatbot for answering academic, housing, administrative, and
professional-contract questions from verified university documents.

Development takes place on `feature-agentic-rag`. The goal of this branch is
to convert the existing Colab RAG prototype into a tested, deployable,
citation-first agentic RAG application.

## Implementation Governance

The approved architecture, milestone tasks, dependencies, acceptance criteria,
tests, deliverables, and progress checklist are defined in
`docs/IMPLEMENTATION_PLAN.md`. Treat that document as the authoritative
implementation sequence when it is more specific than this file.

Implement only one milestone at a time. Before starting a milestone, confirm
that the previous milestone is marked complete and that the user has explicitly
approved continuation. After completing a milestone:

1. Run all tests required by that milestone.
2. Update the plan's progress checklist and milestone notes.
3. Explain the architecture and important implementation decisions.
4. List every modified and newly created file.
5. Report test results, metrics, unresolved issues, and deviations.
6. Stop and wait for explicit user approval before continuing.

Do not begin application development until Milestone 1 is explicitly approved.

## Current Repository

The repository currently contains:

- `ChatBot_Colab.ipynb`: legacy fine-tuning experiment.
- `ChatBotRag_Colab.ipynb`: JSON FAQ RAG and reranking experiment.
- `ChatBotRagPDF_Colab.ipynb`: PDF RAG and hybrid retrieval experiment.
- `dataset/*.json`: FAQ records with `instruction` and `output` fields.
- `FAQ.pdf`: source document used by the PDF RAG experiment.
- `README.md`: original project description.

Treat the notebooks as reference implementations. Do not extend them into the
production application, and do not delete or substantially rewrite them unless
the task explicitly requires it.

Some existing content contains incorrectly decoded characters. New and
modified text files must use UTF-8 and preserve French text such as `Alès`
correctly.

## Target Architecture

The production application should use:

- Python 3.11 or 3.12.
- FastAPI for the HTTP API and health endpoints.
- LangGraph for agent state and workflow orchestration.
- LangChain components for loading, splitting, retrieval, and integrations.
- Chroma for the initial vector store.
- BGE-M3 embeddings for production semantic retrieval.
- Mandatory hybrid retrieval combining BGE-M3 semantic search and BM25 through
  weighted reciprocal-rank fusion, followed by stable-ID deduplication and
  mandatory `BAAI/bge-reranker-large` cross-encoder reranking.
- Gemini 3.8 Flash as the only v1 generative model, behind a provider-neutral
  adapter.
- Gradio for the initial public chat interface.
- FastAPI SSE events for safe intermediate activity; emit final answers only
  after evidence and citation validation.
- The official Python MCP SDK for MCP resources and tools.
- Pytest for automated tests and RAG evaluations.
- Docker for reproducible local and production execution.
- Cloud Run as the initial deployment target.

Organize new code by responsibility:

```text
app/
  api/          HTTP routes and response schemas
  agent/        LangGraph state, nodes, edges, and decisions
  rag/          ingestion, indexing, retrieval, reranking, and citations
  mcp/          MCP server, resources, and tools
  models/       model and embedding provider adapters
  config.py     validated environment configuration
  main.py       application entry point
scripts/        explicit maintenance commands such as index rebuilding
tests/          unit, integration, retrieval, and evaluation tests
```

Keep the domain logic independent of FastAPI, Gradio, and MCP so every
interface can call the same application services.

## Agent and RAG Behavior

The LangGraph workflow should:

1. Normalize the question and resolve conversational references.
2. Retrieve candidates independently using semantic and BM25 search.
3. Fuse ranked candidates, deduplicate them, and rerank them with the approved
   BGE cross-encoder.
4. Assess whether the evidence is sufficient.
5. Retry retrieval at most once when evidence is weak.
6. Answer only from retrieved evidence or return a clear refusal.
7. Return structured, verifiable citations.

Conversation history is bounded and client-carried. Do not persist personal
conversation state in v1. The single constrained agent may use native
retrieval, but it must not call the application's own MCP endpoint.

The public application and agent must always use the complete hybrid-reranked
pipeline. Component-level measurements may diagnose semantic search, BM25,
fusion, and reranking, but these stages are not public runtime options and do
not compete to replace the approved pipeline. The original notebooks are
historical references only and are not executable evaluation baselines. Any
removal or bypass requires explicit user approval and a plan revision.

Every indexed chunk must retain available source metadata, including document
identifier, title, category, language, page or section, source URL, and update
date. Never allow the language model to invent source URLs or citation
metadata.

Generated answers must expose citations as structured data in addition to
display text. A citation should identify the source, its page or section when
available, its URL when available, and the supporting passage.

Keep model, embedding, reranker, and vector-store integrations behind small
interfaces. Do not embed provider-specific calls throughout the agent graph.

## MCP Guidelines

MCP exposes reusable project capabilities; it does not replace the internal
RAG pipeline. The initial MCP server should expose:

- `search_knowledge_base`
- `get_document_source`
- `list_knowledge_sources`

Use typed and documented input/output schemas. MCP tools must reuse the same
retrieval and source services used by the HTTP application. Do not duplicate
retrieval logic inside MCP handlers.

The v1 MCP surface is read-only and uses Streamable HTTP. Do not add write
tools without a separately approved milestone and persistence/security design.

Tools that write data or call external systems require explicit validation,
timeouts, error handling, and tests. Do not add external university tools until
a reliable data source and its access policy are known.

## Jev Policy

Jev is an optional decision-engine experiment, not a required runtime
dependency. Potential uses include intent classification, evidence grading,
passage ranking, and routing.

Define decision behavior behind a provider-neutral interface. Maintain a
deterministic or structured-LLM baseline, and enable Jev only through
configuration. Do not make Jev part of the default production path until
evaluation demonstrates a measurable accuracy, latency, or cost improvement.

## Coding Conventions

- Use UTF-8, four-space indentation, and type hints on public functions.
- Prefer `pathlib.Path` over manually constructed filesystem paths.
- Use Pydantic models for configuration and public request/response schemas.
- Keep functions focused and avoid hidden global state.
- Use dependency injection for model clients, retrievers, vector stores, and
  decision engines.
- Use structured logging instead of `print`.
- Never hardcode API keys, credentials, Colab paths, local absolute paths, or
  CUDA devices.
- Support CPU execution where practical and detect accelerator availability.
- Put secrets in environment variables and document them in `.env.example`.
- Pin direct dependencies and keep optional GPU dependencies separate.
- Use current, non-deprecated library import paths.
- Add comments only for non-obvious decisions or constraints.
- Do not commit generated vector indexes, model weights, caches, secrets, or
  local environment files.
- Preserve unrelated user changes and keep commits narrowly scoped.

The public API should use stable typed schemas. Return actionable errors
without exposing prompts, stack traces, credentials, or internal filesystem
paths.

## Testing Requirements

All behavioral changes require tests appropriate to their layer.

Unit tests must cover:

- JSON and PDF loading.
- Chunking and metadata preservation.
- Citation construction and validation.
- Configuration validation.
- Query routing and refusal rules.
- MCP tool schemas and error handling.

Retrieval tests must use a small deterministic fixture corpus and verify:

- Expected documents occur within the configured top-k results.
- Metadata survives indexing and retrieval.
- English and French queries retrieve relevant evidence.
- Reranking uses the reranker tokenizer and changes ordering when expected.
- Empty indexes and unavailable sources fail safely.

Agent tests should mock external model calls and verify:

- Supported questions reach answer generation.
- Weak evidence triggers no more than one retrieval retry.
- Unsupported questions produce a refusal.
- Citations refer only to retrieved evidence.
- Tool and model failures produce controlled responses.
- The graph always reaches a terminal state.

End-to-end evaluations may call real models and should be marked separately.
Measure answer correctness, retrieval recall, groundedness, citation validity,
refusal quality, latency, and token usage. Keep normal unit tests independent
of network access and paid APIs.

Before completing a change, run the relevant focused tests followed by the
full test suite. If a test cannot run because credentials, models, or services
are unavailable, report that limitation explicitly.

## LLMOps and Observability

Version prompts, evaluation datasets, ingestion configuration, and model
settings in Git. Record enough structured information to diagnose:

- Model and prompt version.
- Retrieval and reranking results.
- Agent route and retry count.
- Citation identifiers.
- Latency, token usage, and failures.

Do not log secrets, full sensitive conversations, or unnecessary personal
data. LangSmith tracing may be supported but must remain optional. The
application must function when tracing is disabled.

Use regression evaluations before changing prompts, models, embeddings,
rerankers, chunking, or retrieval thresholds.

## Development Workflow

1. Inspect the relevant notebook and dataset behavior before replacing it.
2. Add or update tests alongside implementation changes.
3. Keep ingestion reproducible through an explicit script or command.
4. Keep network-dependent integrations configurable and mockable.
5. Run format, static checks, focused tests, and the full test suite.
6. Update documentation when commands, configuration, APIs, tools, or
   deployment behavior change.
7. Package the application with Docker and provide a health check.
8. Keep the first public release stateless: no user accounts and no persistent
   personal conversation history.
9. Follow the milestone order and stop for approval after each milestone.

Do not introduce PostgreSQL, a dedicated vector service, multiple agent
frameworks, or authentication without a demonstrated requirement. Chroma is
the default initial vector store, and LangGraph is the sole workflow
orchestrator.

Public deployment still requires server-side secret management, request-size
limits, timeouts, basic rate limiting, and graceful dependency failures.

## Definition of Done

A change is complete when:

- Its behavior is implemented through the intended application layer.
- Relevant automated tests pass.
- Citations remain traceable to indexed source metadata.
- No secrets or generated artifacts are committed.
- CPU and missing-service failure paths are handled where applicable.
- Configuration and user-facing behavior are documented.
- Any unexecuted checks or remaining risks are clearly reported.
