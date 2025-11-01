## Axiom AI — Execution Checklist (12 Items)

Use this as a sprint board to reach “100% ready.” Each item maps to the Readiness Guide.

1) Evaluation harness (baseline)
- Build a small test set (EN 50–100, HI 30–50). Run Recall@1/5/10, MRR, avg retrieval latency.
- Commit `baseline.json` and a one‑command script.

2) /metrics and structured logs
- Expose Prometheus metrics: request_count, errors_total, latency histograms per stage, token_usage_total, vector_store_size.
- Add JSON logs with `request_id` across stages.

3) Dockerization + Compose
- Dockerfiles for backend/UI and `docker-compose.yml` for backend+UI+Chroma with volumes and healthchecks.
- README: two commands to run; sample `curl`.

4) CI pipeline
- GitHub Actions: unit tests + lint + retrieval‑eval smoke + image build under 2 minutes.

5) Multilingual retrieval (Hindi)
- Language detection on queries; enable multilingual embeddings.
- Curate HI test set; report Recall@5/MRR.

6) Provider abstraction validation
- Demonstrate swapping embeddings/LLM (OpenAI ↔ local embedding; document local LLM plan).

7) Deterministic chunking & tests
- Ensure stable chunking via config; add snapshot tests on representative docs.

8) Vector store persistence & health
- Verify restart → same results; add healthcheck; write round‑trip tests.

9) Reliability controls
- Retries with exponential backoff; timeouts; simple degraded mode (fallback model or cached answer).

10) Safety & grounding
- PII redaction step; hallucination overlap score added to responses; document policy.

11) Observability dashboard & alerts
- Provide Grafana panel JSON/screenshots for p50/p95/p99 per stage and error rate; document two alert examples.

12) Docs & demo
- Update README, `docs/architecture.md`, `docs/EVAL.md`, `docs/security.md`, `docs/deployment.md`.
- Record ≤3‑minute demo video and include link in README.

Completion rule: All 12 items checked and reproducible via README instructions.



