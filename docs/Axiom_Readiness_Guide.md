## Axiom AI — Production Readiness Guide (Single Source of Truth)

This document is the definitive pass/fail guide for taking Axiom AI to “100% ready” for LLM/RAG startup interviews and demos.

### 1) High‑level definition

Axiom AI is ready when it is demonstrably production‑grade for RAG use cases: reliable ingestion, repeatable and measurable retrieval, auditable provenance, deployable infra, low‑friction demo, multilingual capability (at least Hindi), and an evaluation/observability stack proving quality and latency. Not just code — also tests, docs, monitoring, security, and a crisp demo story.

### 2) Hard acceptance criteria (pass/fail)

#### Core pipeline
- Ingest
  - Supports PDF, TXT, DOCX (OCR for image/PDF where applicable) and S3 uploads.
  - Idempotent ingestion with state tracker: SEEN/PROCESSING/COMPLETED/FAILED; resumable/retriable.
  - Tests: loader unit tests + integration test ingesting sample files.
- Processing / Chunking
  - `config.yaml` controls `chunk_size` and `chunk_overlap`.
  - Deterministic chunking: same input → same chunks.
  - Tests: snapshot tests for chunk boundaries on representative docs.
- Embeddings
  - Pluggable `EmbeddingGenerator` with at least two implementations: (a) OpenAI, (b) multilingual local (e.g., sentence‑transformers).
  - Embedding batching with queue and exponential backoff for retries.
  - Tests: reproducibility smoke tests; batch path covered.
- Vector store
  - `VectorStore` abstraction: Chroma (dev) implemented and persistence verified (restart → same results).
  - Healthcheck endpoint for DB and index consistency.
  - Tests: add/remove/query round‑trip and false‑negative checks.
- Retrieval & (optional) reranking
  - Top‑K retrieval by vector similarity; K configurable.
  - Hybrid (BM25 + embeddings) and cross‑encoder reranker optional/togglable.
  - Tests: Recall@K and MRR computed on local test set.
- LLM synthesis
  - `LLMProvider` with at least two providers: remote (OpenAI) and a documented local fallback path (HF/vLLM) — local can be staged if time‑boxed.
  - Token budgeting and dynamic context trimming (prefer higher‑similarity chunks).
  - Streaming support to UI (SSE/WebSocket) optional for phase 1; document plan.
  - Prompt templates embed citations (chunk ids and similarity scores) in answers.

#### Multilingual
- Language detection on ingestion and query paths.
- Multilingual embeddings enabled (e.g., LaBSE/multilingual‑mpnet) and working for at least one Indian language (Hindi): Hindi queries retrieve correct Hindi chunks.
- Evaluation includes a small Hindi test set with Recall@K / MRR reported.

#### Evaluation & experiments
- Offline evaluation harness computes: Recall@1/5/10, MRR, average retrieval latency per query, and a simple grounding score (token/char overlap with sources).
- Baseline snapshot JSON stored in repo; PRs compare against baseline.
- One‑command run; outputs machine‑readable JSON and a short human summary.

#### Observability & monitoring
- `/metrics` (Prometheus format) exposes at minimum:
  - `request_count` (labels: stage ∈ {embed,retrieve,synthesize}, provider)
  - `request_errors_total`
  - `latency_seconds` histogram per stage
  - `vector_store_size`, optional `vector_store_index_time`
  - `token_usage_total` (by model/provider)
- Structured JSON logs with `request_id` correlation across stages.
- Grafana dashboard (or exported panel JSON/screenshots) for p50/p95/p99 per stage, error rates, Recall@K.
- Documented alert examples: p95 latency > X, error rate > Y.

#### Deployment & infra
- Dockerfiles for backend and UI; `docker-compose.yml` launches backend + UI + Chroma with volumes and healthchecks; env vars for secrets.
- CI: pipeline that runs unit tests + lint + retrieval‑eval smoke on PRs; builds images.
- (Optional for phase 1) k8s manifests/Helm example with readiness/liveness probes.
- Backup/restore plan for vector DB documented (scripts or steps).

#### Security & compliance
- PII detection & redaction (pre‑LLM or ingestion); basic tests for the filter.
- Secrets via environment variables; recommend Vault/KMS for production.
- Encryption at rest for vector store/metadata (or steps to enable in prod).
- Audit logging policy for queries and source access; retention/anonymization documented.
- Access control: simple API key auth for demo; RBAC path documented.

#### Reliability & scale
- Retries with exponential backoff for transient errors; bounded timeouts.
- Graceful degradation: fallback smaller model or cached answer if provider unavailable.
- Benchmark scripts to measure throughput and p50/p95/p99 latencies.

#### Model behavior & safety
- Hallucination detector: simple grounding overlap heuristic and flag in responses.
- Output safety: basic toxicity filter (documented approach; integration example acceptable).
- Human‑in‑the‑loop labeling path (CSV export acceptable for phase 1).

#### Documentation & repo hygiene
- README: 2‑step run (docker‑compose up, curl example), architecture summary, demo link (if hosted).
- `docs/architecture.md`, `docs/EVAL.md`, `docs/security.md`, `docs/deployment.md`.
- `axiom/eval/` with test set (jsonl), eval scripts, baseline JSON.
- `axiom/observability/` helpers, Grafana panel JSON/screenshots.
- `LICENSE`, `CONTRIBUTING.md`, `CHANGELOG.md`.

### 3) Measurable targets (tune to domain/hardware)
- Retrieval: Recall@5 ≥ 0.7; MRR ≥ 0.45 on curated set (EN + Hindi subset).
- Latency: retrieval p95 ≤ 150–250 ms up to ~10k chunks on local Chroma; end‑to‑end p95 depends on LLM (document).
- CI eval runtime ≤ 120 s; demo error rate < 1%.
- Log retention ≥ 7 days in dev; prod policy documented.

### 4) Repo & artifact checklist (must exist)
- `README.md`, `docs/architecture.md`, `docs/EVAL.md`, `docs/security.md`, `docs/deployment.md`.
- `axiom/config/config.yaml`, `axiom/core/*`, `axiom/state_tracker.py`.
- `axiom/eval/` (testset jsonl, scripts, baseline.json).
- `axiom/observability/` (metrics helpers, Grafana JSON/screenshots).
- `docker/Dockerfile.backend`, `docker/Dockerfile.ui`, `docker/docker-compose.yml`.
- `ci/` (GitHub Actions YAML: tests + eval + build).
- `k8s/` (optional in phase 1).
- `demo/` (scripted demo: sample queries, expected outputs, curl examples).

### 5) Demo & interview playbook (10–12 minutes)
1. 90‑sec pitch: problem, architecture triptych (Quarry/Forge/Autopsy), differentiators (provenance, evaluation, sovereign options).
2. Live query: ingest → retrieve → answer; click citation to open source chunk in Autopsy.
3. Observability: show /metrics or Grafana for that request (per‑stage latency, retrieval time).
4. Eval harness: run and show baseline metrics; show a before/after if you optimized.
5. Repro: show `docker-compose up` and healthchecks.
6. Multilingual: run one Hindi query and show correct retrieval.
7. Roadmap: streaming, FAISS/Milvus/Qdrant, local LLM serving.

Talking points you must be ready for: hallucinations (provenance + overlap + re‑rank + HITL), Why Chroma (prototype; path to FAISS/Milvus/Qdrant), sensitive data (PII redaction, encryption, on‑prem models), success metrics (Recall@K/MRR, p95), latency reduction (batching, caching, quantized local models, streaming), multilingual strategy (detect → multilingual embeddings → bilingual eval).

### 6) Risks & trade‑offs (how to justify)
- OpenAI vs local models: quality/time‑to‑market vs sovereignty/cost/latency; show migration plan (provider abstraction + vLLM/Triton).
- Chroma for dev: easy and fast; path to FAISS/Milvus/Qdrant with a benchmark plan (recall vs latency vs memory).
- Indexing cadence: incremental vs batch; justify by data churn and cost.
- Metrics overhead: keep histograms; sample non‑critical paths if needed.

### 7) Hiring evidence (what to attach)
- Resume line: “Built Axiom AI — production‑ready RAG (ingest→embed→index→retrieve→LLM) with evaluation harness, provenance, monitoring, and Hindi retrieval.”
- Repo link + 2‑minute demo video in README.
- One‑page PDF with architecture diagram, metrics, screenshots.
- Optional notebook demonstrating retrieval + eval on sample data.

### 8) What you must be able to explain
- Exact flow of `query()` in `query_engine.py` including error handling.
- Factory/DI swaps providers/stores without code changes.
- Eval harness: how Recall@K/MRR computed; how CI gates regressions.
- Chunking choices and their effect on recall/latency.
- Steps to add a new language and the tests you run.

### 9) Final pass/fail checklist (gate)
- End‑to‑end demo via `docker-compose` in 2 commands.
- Eval harness + baseline JSON in repo.
- /metrics live and Grafana panel (or exported screenshots) present.
- Hindi retrieval demonstrated with metrics.
- Provider abstraction in place (OpenAI + local embedding; local LLM path documented).
- CI: unit tests + eval smoke + image build.
- Docs: README, architecture, EVAL, security, deployment.
- Security: PII redaction and secrets strategy documented.
- Vector DB DR plan documented (backup/restore).
- Demo video ≤ 3 minutes and a 3‑minute pitch prepared.

### 10) Immediate next actions
- Build a 50–100 Hindi query test set from a public corpus.
- Instrument three core metrics (embed_latency, retrieve_latency, recall@5) and capture a baseline JSON.
- Add simple PII redaction and document the policy.
- Record a 2‑minute demo showing ingestion → retrieval → provenance → metrics.



