---
title: Axiom AI
emoji: 👑
colorFrom: blue
colorTo: purple
sdk: streamlit
sdk_version: "1.39.0"
app_file: app.py
pinned: false
---

# 👑 Axiom AI: Production-Grade RAG Engine

![Python](https://img.shields.io/badge/python-3.11-blue)
![Streamlit](https://img.shields.io/badge/frontend-streamlit-red)
![LangChain](https://img.shields.io/badge/framework-langchain-green)
![OpenAI](https://img.shields.io/badge/LLM-GPT--4o--mini-purple)
![License: MIT](https://img.shields.io/badge/license-MIT-green)

**A high-fidelity RAG system optimized for precision, speed, and citations.**

Axiom AI v2.0 is a monolithic Streamlit application that delivers **Hybrid Search (Vector + Keyword)**, **Strict Source Citations**, and **Deep Linking** for PDF evidence. It is engineered to run efficiently on Hugging Face Spaces (Free Tier) without memory spikes.

<div align="center">
  <a href="https://www.loom.com/share/60b56802c38845448b1e018b79430d95">
    <img src="https://cdn.loom.com/sessions/thumbnails/60b56802c38845448b1e018b79430d95-with-play.gif" alt="Watch the Demo" width="100%" />
  </a>
  <br/><br/>
  <img src="https://github.com/user-attachments/assets/cab3a2c6-ddcc-4db0-bf98-eb577e674ee4" alt="Axiom AI Split-Pane Interface" width="100%" />
  <br/><br/>
  <img src="https://github.com/user-attachments/assets/ec60c417-f490-4025-a7a3-a3ec6a816a6d" alt="Axiom AI Citations" width="100%" />
</div>

---

## ✨ Key Features

### 🧠 Smart Retrieval
- **Hybrid Search:** Combines `ChromaDB` (Vector) + `BM25` (Keyword) to achieve **High Recall**.
- **Lazy Loading:** Ingestion pipeline streams large PDFs page-by-page, keeping RAM usage low.
- **Smart Caching:** Uses `InMemoryCache` to eliminate redundant API calls and costs.

### 👁️ User Experience
- **Split-Pane UI:** View source documents and chat logic side-by-side (Lawyer/Analyst workflow).
- **Interactive Citations:** Citations map to exact PDF page coordinates for instant auditability.
- **Multi-File Support:** Ingest and query multiple research papers simultaneously.

### 🛡️ Security & Infrastructure
- **PII Redaction:** Middleware automatically detects and masks sensitive data (Emails, SSNs) before ingestion.
- **Non-Root Docker:** Containerized deployment runs as a dedicated user (UID 1000) for production-grade security.
- **System Health:** Real-time latency monitoring and degraded mode fail-safes.

---

## 📊 Performance
*Evaluated on a controlled test set using 30+ domain-specific questions.*

| Metric | Value | Notes |
| :--- | :--- | :--- |
| **Recall@5** | **>95%** | Hybrid Search (Ensemble) on synthetic evaluation set |
| **Retrieval** | **<200ms** | Vector Search Latency (Cached) |
| **Response** | **~2-5s** | End-to-end Latency (including LLM generation) |
| **Cost** | **<$0.01** | Per 100 Queries (GPT-4o-mini) |

---

## 🚀 v2.0 Updates (Production Ready)

**What's New in v2.0:**

* **Hybrid Search:** Combines BM25 (Keyword) + ChromaDB (Vector) to improve recall on keyword-heavy queries.
* **Interactive Citations:** Clicking `[Page 12]` auto-scrolls the PDF viewer to the exact evidence.
* **Lazy Loading Architecture:** Streams large PDFs page-by-page, significantly reducing memory usage.
* **Strict Citations:** Every answer includes source metadata (filename + page number) in a consistent format.
* **Secure by Design:** Integrated PII Redaction middleware and non-root container architecture.

---

## 🏗️ Architecture

Axiom AI uses a **Streamlit Monolith** architecture. It eliminates the complexity of microservices in favor of a robust, single-container deployment ideal for rapid iteration.

```mermaid
graph LR
    User --> Streamlit
    Streamlit -->|PII Redaction| Redactor[Middleware]
    Redactor -->|Clean Text| Hybrid[Ensemble: Vector + BM25]
    Hybrid -->|Top-K Chunks| LLM[GPT-4o-mini]
    LLM -->|Answer + Page Refs| User
```

## ⚡ Quick Start

### Prerequisites

  - Python 3.11+
  - OpenAI API Key

### Installation

```bash
# 1. Clone the repository
git clone https://github.com/anudeepnyakk/axiom-ai.git
cd axiom-ai

# 2. Install Dependencies
pip install -r requirements.txt

# 3. Set API Key (Linux/Mac)
export OPENAI_API_KEY="sk-..."

# 4. Run the App
streamlit run app.py
```

-----

## 📚 Documentation

  - **[🎥 Video Walkthrough](https://www.loom.com/share/60b56802c38845448b1e018b79430d95)**
  - **[Live Demo on Hugging Face](https://huggingface.co/spaces/anudeepp/axiom-ai)**
  - **Deployment:** For Hugging Face Spaces deployment, ensure `app.py` is set as the entry point in your Space settings.

## License

Distributed under the MIT License. See `LICENSE` for more information.
