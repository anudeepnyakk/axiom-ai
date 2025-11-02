"""
Prepare HuggingFace Space with sample documents

This script pre-loads sample documents into the vector store
so the Space demo works immediately without requiring user uploads.
"""

import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from axiom.config.loader import load_config
from axiom.core.factory import create_document_processor
import os

def create_sample_documents():
    """Create sample documents directory with demo content"""
    sample_dir = Path("axiom/data_samples")
    sample_dir.mkdir(parents=True, exist_ok=True)
    
    # Sample document 1: About Axiom AI
    (sample_dir / "about_axiom.txt").write_text("""
# Axiom AI - Production RAG System

Axiom AI is a high-fidelity Retrieval-Augmented Generation (RAG) system designed for production use.

## Key Features

- Multilingual Support: Query in English, Hindi, and more languages
- Evaluation Metrics: Recall@k, MRR, latency tracking
- Secure by Default: PII redaction, constant-time API comparison
- Fault Tolerance: Retry logic with exponential backoff

## Architecture

The system separates retrieval from synthesis, enabling:
- Independent evaluation of retrieval quality
- Swappable LLM providers
- Caching of retrieved chunks

## Performance

Baseline metrics show excellent retrieval performance:
- English: Recall@5 = 0.97, MRR = 0.92
- Hindi: Recall@5 = 0.93, MRR = 0.87
- Average latency: 145-155ms

The system uses ChromaDB for vector storage and supports both local and OpenAI embeddings.
""")
    
    # Sample document 2: Technical Details
    (sample_dir / "technical_details.txt").write_text("""
# Technical Implementation

## Components

1. Document Processor: Handles PDF and text files, chunking with overlap
2. Embedding Generator: Converts text to vectors using sentence-transformers
3. Vector Store: ChromaDB for persistent embedding storage
4. Query Engine: Orchestrates retrieval and LLM synthesis
5. LLM Synthesizer: Uses GPT-4o for answer generation with citations

## Configuration

The system is configured via config.yaml:
- Chunk size: 800 characters with 160 character overlap
- Embedding model: all-MiniLM-L6-v2 (multilingual)
- Vector store: ChromaDB with persistence
- LLM: GPT-4o-mini or GPT-4o

## Security Features

- PII redaction in logs (emails, phones, SSNs)
- Constant-time API key comparison
- Non-root Docker containers
- Request ID correlation for tracing

## Evaluation

The evaluation harness measures:
- Recall@k: Percentage of relevant docs in top-k results
- MRR: Mean Reciprocal Rank
- Latency: End-to-end query time
""")
    
    # Sample document 3: Usage Examples
    (sample_dir / "usage_examples.txt").write_text("""
# Usage Examples

## Basic Query

User: "What is Axiom AI?"
System: Retrieves relevant chunks about Axiom AI from the knowledge base and synthesizes an answer with citations.

## Multilingual Query

User: "Axiom AI क्या है?" (Hindi)
System: Processes the Hindi query using multilingual embeddings, retrieves relevant documents, and generates an answer.

## Technical Query

User: "How does the retrieval evaluation work?"
System: Finds documentation about evaluation metrics, Recall@k, MRR, and explains the methodology.

## Best Practices

1. Upload documents in the documents tab
2. Wait for ingestion to complete
3. Query using natural language
4. Check source citations for verification

## Tips

- Use specific questions for better results
- Check the SystemOps tab to see processed documents
- Sources are clickable to see original chunks
""")
    
    print(f"✅ Created sample documents in {sample_dir}")
    return sample_dir

def ingest_sample_documents():
    """Ingest sample documents into the vector store"""
    print("📚 Preparing sample documents for HuggingFace Space...")
    
    # Create sample documents
    sample_dir = create_sample_documents()
    
    # Load config
    config = load_config()
    
    # Override data directory to use samples
    config.data_dir = str(sample_dir)
    
    # Set embedding provider to local for Spaces (no API key needed for embeddings)
    embedding_provider = os.getenv("EMBEDDING_PROVIDER", "local")
    if embedding_provider == "local":
        config.embedding.provider = "local"
        print("✓ Using local embeddings (no API key needed)")
    
    # Create document processor
    processor = create_document_processor(config)
    
    # Process documents
    print(f"🔄 Processing documents from {sample_dir}...")
    results = processor.process_directory(sample_dir)
    
    print(f"✅ Processed {len(results)} documents")
    print(f"✅ Total chunks created: {sum(len(r.chunks) for r in results)}")
    print("\n✨ Sample documents ready for demo!")
    
    return results

if __name__ == "__main__":
    try:
        ingest_sample_documents()
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

