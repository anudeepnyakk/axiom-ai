# Axiom AI v1: High-Level System Architecture

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                              AXIOM AI v1 SYSTEM                                │
│                           "The Sovereign's Blueprint"                          │
└─────────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────────┐
│                              USER INTERFACE LAYER                              │
│                                                                                 │
│  ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────────────────┐ │
│  │   Streamlit UI  │    │   Chat Session  │    │     Progress Indicators     │ │
│  │                 │    │     Memory      │    │                             │ │
│  │ • Query Input   │◄──►│ • Session State │    │ • "Processing X of Y..."    │ │
│  │ • Response      │    │ • Conversation  │    │ • Error Messages            │ │
│  │ • Source Toggle │    │   History       │    │ • Status Updates            │ │
│  └─────────────────┘    └─────────────────┘    └─────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────────────────────┘
                                        │
                                        ▼
┌─────────────────────────────────────────────────────────────────────────────────┐
│                            RETRIEVAL & SYNTHESIS LAYER                         │
│                                                                                 │
│  ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────────────────┐ │
│  │ QueryProcessor  │    │ ContextRetriever│    │     LLMSynthesizer          │ │
│  │                 │    │                 │    │                             │ │
│  │ • Query Embed   │───►│ • Top-K Search  │───►│ • Prompt Engineering        │ │
│  │ • Vector Match  │    │ • Metadata      │    │ • "Only from Sources"       │ │
│  │ • Similarity    │    │ • Chunk IDs     │    │ • Source Citations [S1]     │ │
│  └─────────────────┘    └─────────────────┘    └─────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────────────────────┘
                                        │
                                        ▼
┌─────────────────────────────────────────────────────────────────────────────────┐
│                              VECTOR STORAGE LAYER                              │
│                                                                                 │
│  ┌─────────────────────────────────────────────────────────────────────────────┐ │
│  │                              ChromaDB                                      │ │
│  │                                                                             │ │
│  │ • Persistent Local Storage                                                 │ │
│  │ • Vector Embeddings (all-MiniLM-L6-v2)                                    │ │
│  │ • Metadata: filename, chunk_id, page_number                               │ │
│  │ • Collection Management                                                    │ │
│  └─────────────────────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────────────────────┘
                                        │
                                        ▼
┌─────────────────────────────────────────────────────────────────────────────────┐
│                            INGESTION & FORGING LAYER                           │
│                                                                                 │
│  ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────────────────┐ │
│  │ DocumentLoader  │    │  TextChunker    │    │   EmbeddingGenerator        │ │
│  │                 │    │                 │    │                             │ │
│  │ • PDF/TXT Load  │───►│ • 800-token     │───►│ • SentenceTransformers      │ │
│  │ • Error Handle  │    │   Chunks        │    │ • Batch Processing          │ │
│  │ • File Validate │    │ • 20% Overlap   │    │ • Vector Generation         │ │
│  └─────────────────┘    └─────────────────┘    └─────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────────────────────┘
                                        │
                                        ▼
┌─────────────────────────────────────────────────────────────────────────────────┐
│                              FOUNDATION LAYER                                  │
│                                                                                 │
│  ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────────────────┐ │
│  │ ConfigLoader    │    │ StateTracker    │    │     Logging System          │ │
│  │                 │    │                 │    │                             │ │
│  │ • YAML Config   │    │ • SQLite DB     │    │ • Structured Logging        │ │
│  │ • Env Vars      │    │ • File Status   │    │ • Error Tracking            │ │
│  │ • Validation    │    │ • Process State │    │ • Performance Metrics       │ │
│  └─────────────────┘    └─────────────────┘    └─────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────────┐
│                              EXTERNAL DEPENDENCIES                             │
│                                                                                 │
│  ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────────────────┐ │
│  │   OpenAI API    │    │  Local Files    │    │      Docker Container       │ │
│  │                 │    │                 │    │                             │ │
│  │ • LLM Provider  │    │ • PDF Documents │    │ • Environment Consistency   │ │
│  │ • API Key Auth  │    │ • TXT Files     │    │ • Dependency Management     │ │
│  │ • Response Gen  │    │ • Config Files  │    │ • Deployment Standard       │ │
│  └─────────────────┘    └─────────────────┘    └─────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────────┐
│                              DATA FLOW SUMMARY                                 │
│                                                                                 │
│  1. DOCUMENT INGESTION: Files → Chunks → Embeddings → ChromaDB                 │
│  2. QUERY PROCESSING: User Input → Query Embed → Vector Search → Context       │
│  3. RESPONSE GENERATION: Context → LLM → Answer + Citations [S1], [S2]...     │
│  4. STATE MANAGEMENT: All operations tracked in SQLite with status updates     │
│  5. CONFIGURATION: YAML + Environment variables for flexible deployment        │
└─────────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────────┐
│                              KEY ARCHITECTURAL PRINCIPLES                      │
│                                                                                 │
│  • MODULARITY: Each layer has single responsibility and clear interfaces       │
│  • SOVEREIGNTY: Local storage, configurable providers, portable deployment     │
│  • TRANSPARENCY: Source citations, progress indicators, error visibility       │
│  • ROBUSTNESS: Error handling, state tracking, graceful degradation           │
│  • SCALABILITY: Designed for thousands of documents, tested on dozens          │
└─────────────────────────────────────────────────────────────────────────────────┘
```

## System Components Overview

### **Layer 1: User Interface Layer**
- **Streamlit Web UI**: Chat-style conversation interface
- **Session Memory**: Maintains conversation context
- **Progress Indicators**: Real-time feedback during processing
- **Source Toggle**: Show/hide source citations

### **Layer 2: Retrieval & Synthesis Layer**
- **QueryProcessor**: Converts user queries to vector embeddings
- **ContextRetriever**: Finds top-K relevant chunks from vector store
- **LLMSynthesizer**: Generates answers with strict source-only policy

### **Layer 3: Vector Storage Layer**
- **ChromaDB**: Local, persistent vector database
- **Embedding Storage**: All document chunks stored as vectors
- **Metadata Management**: File names, chunk IDs, page numbers

### **Layer 4: Ingestion & Forging Layer**
- **DocumentLoader**: Handles PDF/TXT file loading with error recovery
- **TextChunker**: Splits documents into 800-token chunks with 20% overlap
- **EmbeddingGenerator**: Converts text chunks to vectors using sentence-transformers

### **Layer 5: Foundation Layer**
- **ConfigLoader**: Manages YAML configuration and environment variables
- **StateTracker**: SQLite database for tracking processing status
- **Logging System**: Structured logging for debugging and monitoring

### **External Dependencies**
- **OpenAI API**: LLM provider for response generation
- **Local Files**: Document corpus and configuration files
- **Docker Container**: Consistent deployment environment

## Data Flow Architecture

1. **Document Ingestion Pipeline**: Files → Chunks → Embeddings → Storage
2. **Query Processing Pipeline**: Input → Embed → Search → Context → Response
3. **State Management**: All operations tracked with status updates
4. **Configuration Management**: Flexible settings via YAML and environment variables

This architecture ensures **sovereignty** (local control), **transparency** (source citations), **robustness** (error handling), and **scalability** (modular design) - the core principles of Axiom AI v1.
