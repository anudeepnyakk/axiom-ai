# Axiom v1: Internship Acceptance Criteria

*(The Minimum Standard for an Internship-Winning Project)*

**Preamble:** This document defines the finish line for Axiom v1. It is not a feature wishlist; it is a declaration of quality. Meeting these criteria signifies that the project is not merely functional, but a testament to superior engineering, architectural thinking, and professional readiness, designed to capture the attention of high-quality AI startups.

---

### 1. Core RAG Capability: The Engine of Truth

-   **Accuracy & Attribution:** Can accurately answer a suite of 100+ test questions derived from a core corpus of at least 10 complex documents (books, research papers). Every factual statement in a response is backed by **strict, inline citations** (e.g., `[S1]`, `[S2]`) pointing to the exact source (filename, page number).
-   **Synthesis:** Can synthesize insights from **multiple documents** in a single, coherent answer. It doesn't just retrieve facts; it connects ideas.
-   **Honesty:** When the answer is not present in the source material, the system must respond with a clear, unambiguous statement like, _"The provided documents do not contain enough information to answer this question."_ The hallucination rate must be below 5% in controlled testing.
-   **Scope:** The entire ingestion pipeline (loading, chunking, embedding, storing) works flawlessly for PDF and TXT files.

---

### 2. Architectural Soundness: The Sovereign's Blueprint

-   **Modularity:** The 5 core modules (as defined in the architecture blueprint) are implemented as distinct, single-responsibility components with clear interfaces.
-   **Configurability:** All key parameters (chunk size, overlap, embedding model, `K` value for retrieval, LLM provider) are configurable via a single, validated `config.yaml` file, requiring no code changes to modify.
-   **Provider Agnostic:** The architecture successfully abstracts the LLM and Embedding Model. It must be possible to swap from `all-MiniLM-L6-v2` to another model, or from OpenAI to a local LLM, by changing only the configuration file.
-   **Statefulness:** The system uses a persistent state tracking database (SQLite) to manage ingestion. It correctly tracks file processing statuses (e.g., `pending`, `processed`, `failed`) and avoids re-processing unchanged files. The vector store (ChromaDB) is also persistent across sessions.

---

### 3. Production Readiness & Deployment: The Professional's Toolkit

-   **Containerization:** The entire application is containerized using Docker. A single `docker-compose up` or `docker run` command is sufficient to build and run the entire system, including the Streamlit UI and vector database. The Dockerfile must be efficient (e.g., using multi-stage builds).
-   **Dependency Management:** All Python dependencies are explicitly pinned in a `requirements.txt` file to ensure reproducible builds.
-   **README Excellence:** A comprehensive `README.md` exists, based on the provided scaffold. It must include:
    -   A clear, concise project description.
    -   Architecture overview/diagram.
    -   Step-by-step setup instructions using Docker.
    -   Configuration guide (`.env` for API keys, `config.yaml` for parameters).
    -   Example queries and expected outputs.
-   **Logging:** Structured logging is implemented. Ingestion and query events are logged with appropriate severity levels (INFO, WARN, ERROR) to a file (`axiom.log`).

---

### 4. User Experience & Interface: The Polished Weapon

-   **Frictionless UI:** A clean, intuitive Streamlit web UI provides a chat-style conversational interface with session memory.
-   **Transparent Processing:** During the (potentially slow) ingestion process, the UI provides real-time feedback (e.g., _"Processing document 3 of 10: [filename]..."_).
-   **Source Visibility:** The UI allows the user to easily view the cited source passages for any given answer, reinforcing trust and transparency.
-   **Graceful Error Handling:** If a document fails during ingestion, the error is logged and clearly reported to the user in the UI, but the system continues processing the remaining files. Query-time errors are also displayed gracefully.
-   **Performance:** End-to-end query latency (from submitting a question to receiving the full response) is under 3 seconds on average for typical queries.

---

### 5. Internship Demo Readiness: The 3-Minute Pitch

-   **The Demo Script:** A concise, rehearsed 2-3 minute demo script is prepared, covering:
    1.  **The Hook:** A one-sentence explanation of what Axiom is.
    2.  **Ingestion:** Showing the empty state, triggering the ingestion of a small set of documents, and highlighting the UI feedback.
    3.  **The Simple Query:** A factual question answered from a single source, highlighting the answer and the citation.
    4.  **The Synthesis Query:** A complex question requiring information from multiple documents, showcasing the system's reasoning capability.
    5.  **The "Honesty" Test:** A question that cannot be answered from the documents, showing the system's safe failure mode.
    6.  **The Closer:** Highlighting the source attribution feature.
-   **Stability:** The system is stable enough to run the entire demo script five times in a row without crashes, freezes, or unexpected behavior.
