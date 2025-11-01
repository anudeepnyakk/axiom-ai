## Axiom AI — 3‑Minute Demo Script

Time: ~3:00. Goal: show reliability, observability, multilingual capability, and portability.

0:00–0:30 — One‑liner & architecture
- “Axiom AI is a modular RAG system. Ingest → chunk → embed → index (Chroma) → retrieve → synthesize with citations. It’s observable (/metrics), evaluated (Recall@k/MRR), and runs with Docker Compose. Hindi retrieval works via multilingual embeddings.”
- Show the triptych idea (Quarry, Forge, Autopsy) or a simple architecture diagram.

0:30–1:15 — Live query with provenance
- Trigger an example query in the UI.
- Point at the answer; click a citation to open the source chunk (Autopsy). Mention similarity scores and chunk IDs.
- Mention token budgeting: “We trim by similarity to fit the context.”

1:15–1:45 — Observability
- Open `/metrics` or Grafana panel: “Here are per‑stage latencies (embed, retrieve, synth), request counts, errors, and token usage.”
- Call out p95 latency for the request.

1:45–2:15 — Evaluation baseline
- Run the eval script or show `baseline.json`: “We track Recall@1/5/10, MRR, and retrieval latency. CI fails PRs on regressions.”
- Point to a Hindi subset and its Recall@5.

2:15–2:40 — Multilingual demo (Hindi)
- Ask a short Hindi question; show relevant Hindi passages retrieved.
- Briefly note language detection and multilingual embedding backend.

2:40–3:00 — Portability & roadmap
- “One command via docker‑compose starts backend, UI, and Chroma. Providers are swappable (OpenAI + local embeddings; local LLM path documented).”
- Roadmap sentence: “Next: streaming tokens, FAISS/Milvus for scale, and vLLM for sovereign low‑latency serving.”

Close
- “You’ve seen reliability (state + retries), observability (/metrics), evaluation (Recall@k/MRR), multilingual retrieval, and portability (Docker). This is production‑ready for demos with a clear path to scale.”















