# Axiom AI

![Python](https://img.shields.io/badge/python-3.11-blue)
![Docker](https://img.shields.io/badge/docker-ready-blue)
![ChromaDB](https://img.shields.io/badge/vectorstore-ChromaDB-orange)
![License: MIT](https://img.shields.io/badge/license-MIT-green)

Multilingual RAG system with evaluated retrieval, fault tolerance, and secure-by-default design.

**Why it matters**: Separates retrieval evaluation from LLM synthesis, enabling measurable improvement and multilingual query support without translation.

```bash
pip install -r requirements.txt
export OPENAI_API_KEY="sk-your-key"
python scripts/ingest.py && cd frontend && streamlit run app.py
```

## Architecture

```
Documents → Chunker → Embeddings → ChromaDB
                                    ↓
Query → Embed → Vector Search → Top-K → LLM → Answer + Citations
```

**Components**: Modular document processor, multilingual embedding generator (all-MiniLM-L6-v2), ChromaDB vector store, GPT-4o-mini synthesis with strict source citations.

*See [docs/architecture.md](docs/architecture.md) for detailed design.*

---

## Evaluation

Tested on internal dataset (~30 queries per language):

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
- [Docker Setup](DOCKER_SETUP.md) - Deployment guide

Full security and evaluation documentation included under `/docs`.

---

## Future Work

- Document reranking layer for improved precision
- Multi-tenant data isolation
- Streaming LLM responses

---

## License

MIT License - see [LICENSE](LICENSE) for details.
