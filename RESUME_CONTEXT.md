# ANUDEEP S NAYAK - AI Engineer Profile

**AI Engineer — Retrieval Systems & Applied LLM**
Udupi, Karnataka, India • +91-7676513029 • nayakanudeep098@gmail.com
Github: github.com/anudeepnyakk
Demo: huggingface.co/spaces/anudeepp/axiom-ai

## EDUCATION

**Mangalore Institute of Technology & Engineering** — Bachelor’s (Computer Science / Engineering)
2022 – Present
Expected graduation: 2026

## PROJECTS

**Axiom AI – Production-Grade RAG Engine with Deep Linking**
*Tech Stack: Python, LangChain, Hybrid Search (BM25 + ChromaDB), Docker, GPT-4o-mini*

*   Solved the "Source of Truth" problem in LLMs by engineering a system where every answer is backed by verifiable citations with page numbers and source document names.
*   Optimized retrieval accuracy by implementing Hybrid Search (combining Keyword/BM25 + Vector retrieval), significantly reducing hallucinations compared to standard vector-only baselines.
*   Built an end-to-end deployable system (Backend + UI) with <100ms latency via in-memory caching and lazy-loading patterns for large PDF ingestion.
*   Architected a secure, non-root Docker container deployed on Hugging Face Spaces, featuring PII redaction middleware and real-time latency monitoring.

## TECHNICAL SKILLS

*   **LLMs / RAG:** GPT-4o-mini, multilingual embeddings, prompt design, context window optimization
*   **Vector DB:** ChromaDB (Persistent), HNSW Indexing, Semantic Search
*   **Backend / Cloud:** Python, Streamlit (Monolith), Docker, Hugging Face Spaces
*   **Core Engineering:** Lazy Loading Patterns, Caching Strategies (InMemory), PII Redaction
*   **Testing:** pytest, Unit Testing

## INTERESTS

Multilingual LLM research, evaluation science, retrieval architectures, model reasoning, OSS AI engineering

---

## GUIDING ANCHOR & CLAIMS

**Target Role:** AI Engineer Internship
**Goal:** Ensure codebase strictly matches these claims.

**Claims Verification:**
1.  **Hybrid Search:** Implemented via `EnsembleRetriever` (BM25 + ChromaDB).
2.  **Latency:** <100ms retrieval latency (verified via `tests/benchmark_latency.py`).
3.  **Citations:** Page numbers preserved in metadata and displayed in UI with source document names and preview snippets.
4.  **Docker Security:** Non-root user configuration in `Dockerfile`.
5.  **Model:** Strictly using `gpt-4o-mini`.

