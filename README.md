---
title: Axiom AI
emoji: 🤖
colorFrom: blue
colorTo: purple
sdk: streamlit
app_file: streamlit_app.py
pinned: false
license: mit
---

# Axiom AI

![Python](https://img.shields.io/badge/python-3.11-blue)
![Docker](https://img.shields.io/badge/docker-ready-blue)
![ChromaDB](https://img.shields.io/badge/vectorstore-ChromaDB-orange)
![License: MIT](https://img.shields.io/badge/license-MIT-green)

High-fidelity RAG system with multilingual support, robust security, and observability.

**Why it matters**: Separates retrieval evaluation from LLM synthesis, enabling measurable improvement and multilingual query support without translation.

<div align="center">
  <img src="https://github.com/user-attachments/assets/2758b38c-4717-4cff-ae0a-a23361bb8fd5" alt="Axiom AI Interface" width="48%" />
  <img src="https://github.com/user-attachments/assets/3655f327-ecf6-451e-9548-4e665c2c5769" alt="Axiom AI Query Interface" width="48%" />
</div>

## Quick Start

```bash
pip install -r requirements.txt
export OPENAI_API_KEY="sk-your-key"
python scripts/ingest.py && cd frontend && streamlit run app.py
```

## Run Locally (Rapid Demo)

Clone the repo, set your OpenAI API key, and run `python scripts/ingest.py` followed by `streamlit run frontend/app.py`. The Streamlit UI will launch at `http://localhost:8501` where you can upload documents and query your knowledge base. See [docs/DOCKER_SETUP.md](docs/DOCKER_SETUP.md) for Docker deployment.

## Architecture

```
Documents → Chunker → Embeddings → ChromaDB
                                    ↓
Query → Embed → Vector Search → Top-K → LLM → Answer + Citations
```

**Components**: Modular document processor, multilingual embedding generator (all-MiniLM-L6-v2), ChromaDB vector store, GPT-4o-mini synthesis with strict source citations.

*See [docs/architecture.md](docs/architecture.md) for detailed design.*

## Evaluation

Baseline evaluated on ~30 queries per language for proof-of-concept:

| Metric | English | Hindi |
|--------|---------|-------|
| Recall@5 | 0.97 | 0.93 |
| MRR | 0.92 | 0.87 |
| Latency | 145ms | 155ms |

*Retrieval-only evaluation. See [docs/EVAL.md](docs/EVAL.md) for methodology.*

---

## Features

**Fault Tolerance**: Retry logic with exponential backoff, degraded mode when LLM unavailable.

**Secure by Default**: PII redaction in logs, constant-time API key comparison, non-root containers.

**Evaluated Retrieval**: Metrics-driven approach with Recall@k, MRR, latency tracking across languages.

**Docker Reproducible**: Multi-stage builds, containerized deployment, CI/CD validation.

**Observability**: Prometheus metrics, JSON logging with request ID correlation, distributed tracing.

---

## Documentation

- [Architecture](docs/architecture.md) - System design and component details
- [Evaluation](docs/EVAL.md) - Metrics methodology and baseline results  
- [Security](docs/SECURITY.md) - Security features and threat model
- [Docker Setup](docs/DOCKER_SETUP.md) - Deployment guide

Full security and evaluation documentation included under `/docs`.

---

## Future Work

- Reranking layer for improved precision
- Multi-tenant isolation
- Streaming LLM responses

---

## License

MIT License - see [LICENSE](LICENSE) for details.
