---
title: Axiom AI: Production-Grade Multilingual RAG Engine
emoji: 🤖
colorFrom: blue
colorTo: purple
sdk: docker
app_port: 7860
pinned: false
license: mit
---

# Axiom AI

![Python](https://img.shields.io/badge/python-3.11-blue)
![Docker](https://img.shields.io/badge/container-docker-blue)
![ChromaDB](https://img.shields.io/badge/vectorstore-ChromaDB-orange)
![License: MIT](https://img.shields.io/badge/license-MIT-green)

**A high-fidelity RAG system engineered for multilingual support, robust security, and observability.**

Unlike standard RAG implementations, Axiom AI decouples retrieval evaluation from generation, enabling measurable precision improvements. It features a production-ready infrastructure with **PII redaction**, **distributed tracing**, and **multi-stage Docker builds**.

<div align="center">
  <img src="https://github.com/user-attachments/assets/2758b38c-4717-4cff-ae0a-a23361bb8fd5" alt="Axiom AI Interface" width="48%" />
  <img src="https://github.com/user-attachments/assets/3655f327-ecf6-451e-9548-4e665c2c5769" alt="Axiom AI Query Interface" width="48%" />
</div>

## 📊 Benchmarks
Retrieval performance evaluated on a baseline of ~30 queries per language (see `docs/EVAL.md`).

| Metric | English | Hindi | Latency (Avg) |
| :--- | :--- | :--- | :--- |
| **Recall@5** | **0.97** | **0.93** | ~150ms |
| **MRR** | 0.92 | 0.87 | - |

---

## 🏗️ Architecture

```mermaid
graph TD
    User[User Query] -->|API/UI| Gateway[API Gateway]
    Gateway -->|Auth & PII Redaction| Secure[Security Layer]
    Secure -->|Clean Text| Embed[Embedding Model]
    
    subgraph "Ingestion Pipeline"
        Docs[PDF/Text Docs] --> Chunker[Modular Chunker]
        Chunker -->|Vectors| Chroma[(ChromaDB)]
    end

    Embed -->|Vector Search| Chroma
    Chroma -->|Top-K Context| LLM[GPT-4o-mini]
    LLM -->|Synthesis + Citations| Response[Final Answer]
    
    subgraph "Observability"
        Prometheus[Prometheus Metrics] -.-> Chroma
        Prometheus -.-> Gateway
    end
````

**Core Components:**

  * **Vector Store:** ChromaDB with HNSW indexing.
  * **Embeddings:** `all-MiniLM-L6-v2` (Optimized for sentence-level similarity).
  * **Synthesis:** GPT-4o-mini with strict instruction tuning for source citation.

-----

## ⚡ Quick Start

### Option 1: Docker (Recommended)

Spin up the entire stack (App, ChromaDB, Prometheus) with one command.

```bash
# 1. Clone the repository
git clone [https://github.com/anudeepnyakk/axiom-ai.git](https://github.com/anudeepnyakk/axiom-ai.git)
cd axiom-ai

# 2. Set your API Key
export OPENAI_API_KEY="sk-your-key"

# 3. Build and Run
docker-compose up --build
```

### Option 2: Local Python

```bash
pip install -r requirements.txt
export OPENAI_API_KEY="sk-your-key"

# Ingest documents
python scripts/ingest.py

# Run Frontend
streamlit run frontend/app.py
```

*UI launches at `http://localhost:8501`*

-----

## 🛡️ Key Features

### 1\. Observability & Monitoring

  * **Prometheus Metrics:** Real-time tracking of retrieval latency, token usage, and error rates.
  * **Distributed Tracing:** JSON structured logging with request ID correlation.

### 2\. Enterprise-Grade Security

  * **PII Redaction:** Middleware automatically detects and redacts sensitive data (emails, phone numbers).
  * **Constant-Time Auth:** API key comparison uses constant-time algorithms to prevent timing attacks.
  * **Non-Root Containers:** All Docker services run as non-privileged users.

### 3\. Fault Tolerance

  * **Retry Logic:** Implements exponential backoff for LLM calls.
  * **Degraded Mode:** System maintains retrieval capability even if generation service fails.

-----

## 📚 Documentation
* [**Architecture Design**](docs/architecture.md): Deep dive into component interaction.
* [**Evaluation Methodology**](docs/EVAL.md): Details on the harness used to calculate Recall/MRR.
* [**Security Model**](docs/SECURITY.md): Threat model and PII handling protocols.
* [**Docker Deployment**](docs/DOCKER_SETUP.md): Production deployment guide.

## License

Distributed under the MIT License. See `LICENSE` for more information.

```
