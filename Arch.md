# Project Axiom: Complete System Architecture Blueprint

## The Master Todo Architecture
*Every single detail mapped from vision to deployment*

---

## 🏗️ PHASE 1: ARCHITECTURE FOUNDATION (Current Phase)

### 1.1 Core System Architecture
- [ ] Define all 5 modules & their single responsibilities  
- [ ] Design module interfaces & communication contracts
- [ ] Map complete data flow pipeline
- [ ] Define error handling & recovery strategies

### 1.2 Data Architecture  
- [ ] Design state tracking database schema
- [ ] Define file processing status states
- [ ] Design metadata storage structure
- [ ] Plan data persistence strategy

### 1.3 Configuration Architecture
- [ ] Design config file structure & validation
- [ ] Define all configurable parameters  
- [ ] Plan configuration loading & error handling
- [ ] Design environment variable strategy

---

## 🎯 PHASE 2: SYSTEM DESIGN AGREEMENT

### 2.1 Technical Stack Finalization
- [ ] Confirm embedding model selection & rationale
- [ ] Finalize LLM provider architecture (swappable design)
- [ ] Confirm ChromaDB setup & persistence strategy
- [ ] Validate Streamlit UI architecture

### 2.2 Professional Standards Definition
- [ ] Define testing strategy for each module
- [ ] Design logging & monitoring approach  
- [ ] Plan Docker containerization architecture
- [ ] Define documentation standards

---

## ⚙️ PHASE 3: MODULE-BY-MODULE IMPLEMENTATION

### 3.1 Foundation Layer
- [ ] Configuration loader with validation
- [ ] Logging system setup
- [ ] State tracking database design
- [ ] Core abstractions & interfaces

### 3.2 Document Ingestion Pipeline  
- [ ] DocumentLoader (PDF/TXT with error handling)
- [ ] TextChunker (configurable chunking strategy)
- [ ] EmbeddingGenerator (model abstraction layer)
- [ ] VectorStore (ChromaDB wrapper with metadata)
- [ ] StateTracker (process status management)

### 3.3 Retrieval & Synthesis Engine
- [ ] QueryProcessor (embedding & search)
- [ ] ContextRetriever (top-k with metadata)  
- [ ] LLMSynthesizer (prompt engineering & response)
- [ ] SourceAttribution (citation management)

### 3.4 Interface Layer
- [ ] Streamlit chat interface
- [ ] Progress indicators & status display
- [ ] Source citation display system
- [ ] Error message handling

---

## 🚀 PHASE 4: INTEGRATION & PROFESSIONAL DEPLOYMENT

### 4.1 System Integration
- [ ] End-to-end pipeline testing
- [ ] Performance optimization & profiling
- [ ] Memory usage optimization  
- [ ] Error recovery testing

### 4.2 Production Readiness
- [ ] Docker containerization with multi-stage builds
- [ ] Environment configuration management
- [ ] Comprehensive logging & monitoring
- [ ] User documentation & setup guides
- [ ] Code documentation & architectural diagrams

---

**Total Tasks: ~35 distinct components**
**Current Status: Phase 1 - Architecture Foundation**
**Next Milestone: Complete system architecture design before any code implementation**

---

## 📅 Delivery Plan (7-Day v1 Schedule)

### Day 1 (Mon): Finalize Architecture
- Decisions: module boundaries, data contracts (data coupling + config stamp coupling), orchestration, config schema, state DB schema, error policy
- Artifacts: updated interfaces in this doc, sequence diagram, config schema draft, DoD checklists per module
- Done when: every module has input/output types, failure modes, and config keys listed

### Day 2 (Tue): Foundation Layer
- Build: config loader + validation; structured logging; SQLite state tracker (files, hashes, statuses, timestamps, error log)
- Tests: config validation; state tracker CRUD
- Done when: process records file seen/processed/failed and reloads settings without code edits

### Day 3 (Wed): Ingestion (Load + Chunk)
- Build: DocumentLoader (TXT, PDF via pypdf; skip-and-continue); TextChunker (configurable size/overlap)
- Wire: state updates on start/success/fail; store basic metadata
- Tests: corrupted PDF, empty file, large file; chunk boundary invariants
- Done when: directory → chunks with metadata; failures logged while pipeline continues

### Day 4 (Thu): Embeddings + Vector Storage
- Build: EmbeddingGenerator (SentenceTransformers all-MiniLM-L6-v2); VectorStore (ChromaDB persistent)
- Wire: batch embedding; metadata (filename, page/chunk id); idempotency via content hash
- Tests: determinism (same input → same vector), store/search smoke
- Done when: chunks → embeddings stored with metadata; collection stats retrievable

### Day 5 (Fri): Retrieval + Synthesis
- Build: query embed → top-k retrieve; strict prompt (“only from sources”); inline citations [S1]…
- Config: K, similarity metric, model provider via .env/config
- Tests: retrieves correct sources on known corpus; admits “not in context”
- Done when: CLI/mini harness returns answer + citations

### Day 6 (Sat): Streamlit UI + Progress
- Build: chat UI with session memory; ingestion progress (X of Y); show sources toggle; error surfacing
- Wire: ingestion trigger from UI; show state tracker results
- Done when: end-to-end demo via UI works on a sample directory

### Day 7 (Sun): Hardening + Deployment
- Ops: Dockerfile (multi-stage), startup script, pinned deps, README + quickstart
- QA: end-to-end test, performance pass (batch sizes), cold start test, retry sanity
- Buffer: bug fixes and polish
- Done when: docker run brings up UI; user ingests docs, asks, sees citations

Scope guardrails (v1): sequential processing; PDF/TXT only; single embedding model & LLM provider; config via file/.env; no dynamic hot-reload.

