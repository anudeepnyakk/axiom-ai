# Axiom AI

![Python](https://img.shields.io/badge/python-3.11-blue)
![Docker](https://img.shields.io/badge/docker-ready-blue)
![ChromaDB](https://img.shields.io/badge/vectorstore-ChromaDB-orange)
![License: MIT](https://img.shields.io/badge/license-MIT-green)

A robust RAG (Retrieval-Augmented Generation) system with security, observability, and fault tolerance.

## 🚀 Quick Start

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Set OpenAI API key
export OPENAI_API_KEY="sk-your-key"

# 3. Ingest documents
python scripts/ingest.py

# 4. Run frontend
cd frontend && streamlit run app.py
```

Visit `http://localhost:8501` and start asking questions!

**Full guide**: See [QUICKSTART.md](QUICKSTART.md)

---

## 🎯 Key Features

### Core RAG Pipeline
- ✅ **Document Ingestion**: PDF & TXT loaders
- ✅ **Vector Search**: ChromaDB integration
- ✅ **LLM Synthesis**: OpenAI GPT-4o-mini
- ✅ **Local Embeddings**: Cost-effective all-MiniLM-L6-v2
- ✅ **Multilingual**: English + Hindi support

### Security
- ✅ **PII Redaction**: Automatic email/phone/SSN removal from logs
- ✅ **API Authentication**: Constant-time key comparison (prevents timing attacks)
- ✅ **Container Security**: Non-root user, multi-stage builds

### Performance & Reliability
- ✅ **LRU Cache**: 600K+ ops/sec, 50% cost reduction
- ✅ **Retry Logic**: Exponential backoff for API failures
- ✅ **Degraded Mode**: Returns raw chunks if LLM fails
- ✅ **Query Latency**: ~150ms (cached), ~500ms (with LLM synthesis)

### Observability
- ✅ **Prometheus Metrics**: /metrics endpoint
- ✅ **JSON Logging**: Structured logs with request IDs
- ✅ **Distributed Tracing**: Request ID correlation across pipeline stages

### Infrastructure
- ✅ **Docker**: Multi-stage builds, containerized deployment
- ✅ **CI/CD**: GitHub Actions (<120s pipeline)
- ✅ **Documentation**: Architecture diagrams, evaluation methodology, security design

---

## 📊 Performance Benchmarks

### Evaluation Results

Tested on small internal dataset (~30 queries per language) for baseline benchmarking:

### English Performance
- **Recall@1**: 0.91
- **Recall@5**: 0.97
- **Recall@10**: 0.99
- **MRR**: 0.92
- **Avg Latency**: 145ms (retrieval only)

### Hindi (हिंदी) Performance
- **Recall@1**: 0.85
- **Recall@5**: 0.93
- **Recall@10**: 0.97
- **MRR**: 0.87
- **Avg Latency**: 155ms (retrieval only)

*See [Evaluation Guide](docs/EVAL.md) for methodology and [evaluation/](evaluation/) for full results.*

---

## 📚 Documentation

- **[Architecture](docs/architecture.md)**: System design and component details
- **[Evaluation](docs/EVAL.md)**: Metrics methodology and baseline results
- **[Security](docs/SECURITY.md)**: Security features and threat model
- **[Docker Setup](DOCKER_SETUP.md)**: Deployment guide

---

## 🔮 Future Work

- Reranking layer for improved precision
- Support for additional document formats (DOCX, Markdown)
- Streaming responses for faster UX
- Multi-tenant support with user isolation

---

## 📄 License

MIT License - see [LICENSE](LICENSE) for details.
