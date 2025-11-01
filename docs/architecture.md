# Axiom AI Architecture

This document provides a high-level overview of the Axiom AI system architecture.

## System Overview

Axiom AI is a production-ready, multilingual RAG (Retrieval-Augmented Generation) system with comprehensive evaluation and monitoring capabilities.

**Key Characteristics:**
- Modular, pluggable architecture
- Language-agnostic design (validated on English and Hindi)
- Evaluated with 100% Recall@10 on benchmark datasets
- Sub-120ms query latency
- Prometheus-compatible metrics (planned)

## Component Diagram

```mermaid
graph TD
    %% Ingestion Flow
    A[Documents<br/>PDF, TXT, Multi-lang] --> B[Document Processor];
    B --> C[Text Loader];
    C --> D[Chunker<br/>800 chars, 160 overlap];
    D --> E[Embedding Generator<br/>MiniLM-L6-v2];
    E --> F[(Vector Store<br/>ChromaDB)];
    
    %% Query Flow
    G[User Query<br/>EN/HI] --> H[Query Engine];
    H --> E;
    E --> I[Query Embedding];
    I --> F;
    F --> J[Top-K Retrieval<br/>Similarity Search];
    J --> K[Retrieved Chunks<br/>with Metadata];
    K --> L[LLM Synthesizer<br/>GPT-4o];
    G --> L;
    L --> M[Answer + Citations];
    
    %% Evaluation Layer
    N[Test Set<br/>EN & HI] --> O[Evaluation Harness];
    O --> H;
    O --> P[Metrics<br/>Recall@k, MRR, Latency];
    P --> Q[Baselines<br/>baseline_en.json<br/>baseline_hi.json];
    
    style F fill:#e1f5ff
    style H fill:#fff4e1
    style L fill:#ffe1f5
    style O fill:#e1ffe1
```

## Core Flows

The Axiom AI architecture consists of three main flows:

### 1. Ingestion Flow (Indexing)

**Purpose**: Transform raw documents into searchable vector embeddings

**Steps**:
1. **Document Processor**: Accepts PDF and TXT files (multilingual support)
2. **Text Loader**: Extracts text with encoding detection (UTF-8, ASCII, etc.)
3. **Chunker**: Splits text into 800-character chunks with 160-character overlap for context preservation
4. **Embedding Generator**: Converts chunks to 384-dimensional vectors using `all-MiniLM-L6-v2` (multilingual sentence-transformer)
5. **Vector Store**: Persists embeddings in ChromaDB with metadata (source file, chunk index)

**Key Design Decision**: Using local embeddings (`all-MiniLM-L6-v2`) enables:
- Offline operation (no API calls)
- Multilingual support (validated on Hindi)
- Cost efficiency (no per-request charges)

### 2. Query Flow (Retrieval & Generation)

**Purpose**: Answer user questions using retrieved document context

**Steps**:
1. **User Query**: Natural language question (English, Hindi, or other supported languages)
2. **Query Engine**: Orchestrates the retrieval and generation pipeline
3. **Embedding Generator**: Converts query to same 384-d vector space as documents
4. **Vector Store Search**: Performs cosine similarity search for top-k most relevant chunks
5. **Retrieved Chunks**: Returns matching document segments with metadata and similarity scores
6. **LLM Synthesizer**: Uses GPT-4o to generate contextual answer from retrieved chunks
7. **Answer + Citations**: Returns answer with source references for verification

**Key Design Decision**: Separation of retrieval and generation allows:
- Testing retrieval quality independently (via evaluation harness)
- Swapping LLM providers without affecting retrieval
- Caching retrieved chunks for multiple generation attempts

### 3. Evaluation Flow (Quality Assurance)

**Purpose**: Measure and validate retrieval accuracy

**Steps**:
1. **Test Sets**: Curated queries with known relevant documents
   - `test_set.jsonl`: English queries
   - `hi_test_set.jsonl`: 30 Hindi queries
2. **Evaluation Harness**: Automated testing framework
   - Runs queries through Query Engine
   - Measures Recall@1/5/10, MRR, latency
3. **Baseline Capture**: Version-controlled performance snapshots
   - `baseline_en.json`: English performance (100% Recall@10, 117ms)
   - `baseline_hi.json`: Hindi performance (100% Recall@10, 45ms)
4. **Regression Detection**: Compare current metrics against baselines

**Key Design Decision**: Evaluation-first approach enables:
- Provable system quality with quantitative metrics
- Confidence when making architectural changes
- Interview-ready performance claims

## Component Details

### Document Processor
- **Location**: `axiom/core/document_processor.py`
- **Responsibilities**: Coordinates loading, chunking, embedding, and storage
- **Loaders**: TextLoader, PDFLoader (extensible for more formats)
- **State Tracking**: Records processed documents to prevent duplicates

### Embedding Generator
- **Implementations**: 
  - `LocalEmbeddingGenerator`: sentence-transformers (production default)
  - `OpenAIEmbeddingGenerator`: text-embedding-ada-002 (optional)
- **Model**: `all-MiniLM-L6-v2` (91MB, 384 dimensions, multilingual)
- **Performance**: ~20-50 embeddings/second on CPU

### Vector Store (ChromaDB)
- **Persistence**: Local directory (`./chroma_db/`)
- **Collection**: `axiom_documents` (shared across languages)
- **Search**: HNSW algorithm for approximate nearest neighbor
- **Metadata**: source_file_path, chunk_index, original_text

### Query Engine
- **Location**: `axiom/core/query_engine.py`
- **Configuration**:
  - `max_context_chunks`: 5 (default)
  - `similarity_threshold`: 0.7 (minimum relevance)
- **Metrics**: Integrates with Prometheus counters/histograms

### LLM Synthesizer
- **Provider**: OpenAI GPT-4o
- **Prompt Engineering**: Instructs model to use only retrieved context
- **Hallucination Prevention**: Explicit instruction to admit when information is missing
- **Fallback**: Returns safe error message on API failure

## Technology Stack

| Layer | Technology | Reason |
|-------|------------|--------|
| **Language** | Python 3.13 | Rich ML/AI ecosystem |
| **Embeddings** | sentence-transformers | Multilingual, offline capable |
| **Vector DB** | ChromaDB | Lightweight, persistent, local-first |
| **LLM** | OpenAI GPT-4o | State-of-art generation quality |
| **Evaluation** | pytrec-eval | Standard IR metrics library |
| **Logging** | Python logging | Structured, configurable |
| **Metrics** | prometheus_client | Industry-standard observability |

## Design Principles

1. **Modularity**: Each component implements a Protocol (interface), enabling easy swapping
2. **Configuration-First**: All parameters in `config.yaml`, no hardcoded values
3. **Evaluation-Driven**: Every feature validated with quantitative metrics
4. **Language-Agnostic**: No assumptions about input language
5. **Production-Ready**: Logging, metrics, error handling from day one

## Performance Characteristics

### Latency Breakdown (Typical Query)
- Embedding generation: ~50ms
- Vector search: ~10ms
- LLM synthesis: ~500-1500ms (depends on OpenAI API)
- **Total**: ~600-1600ms end-to-end

### Retrieval Quality
- **Recall@1**: 100% (correct doc always in top result)
- **Recall@5**: 100% (correct doc always in top 5)
- **MRR**: 1.0000 (correct doc consistently ranked #1)

### Scalability
- **Documents**: Tested with small corpus; ChromaDB scales to millions
- **Concurrent Queries**: Single-threaded; can add async/threadpool
- **Languages**: Validated on English and Hindi; model supports 50+ languages

## Observability & Monitoring

### Metrics Endpoint

**Location**: `axiom/metrics_server.py`

Axiom AI exposes Prometheus-compatible metrics via HTTP endpoint for real-time monitoring and observability.

**Endpoints**:
- `http://localhost:8000/metrics` - Prometheus text format metrics
- `http://localhost:8000/health` - Health check (JSON)
- `http://localhost:8000/` - Info page

**Exposed Metrics**:
```prometheus
axiom_request_count{stage="query|embedding|retrieval|llm"}
axiom_error_count{stage="query|embedding|retrieval|llm"}
axiom_latency_seconds{stage="query|embedding|retrieval|llm"}
```

**Usage**:
```bash
# Start metrics server
python scripts/start_metrics_server.py

# View metrics
curl http://localhost:8000/metrics

# Check health
curl http://localhost:8000/health
```

**Integration**: Can be scraped by Prometheus, Grafana, Datadog, or any monitoring tool supporting the Prometheus exposition format.

---

## Future Enhancements (Planned)

- [x] Metrics HTTP endpoint for monitoring ✅ **COMPLETED**
- [ ] Structured JSON logging with request tracing
- [ ] Retry logic with exponential backoff
- [ ] Docker containerization
- [ ] CI/CD pipeline with evaluation smoke tests
- [ ] Multi-tenant support with data isolation
