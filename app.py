"""
Axiom AI - HuggingFace Spaces Entry Point

This file serves as the entry point for HuggingFace Spaces deployment.
It auto-initializes sample documents if the vector store is empty,
then imports and runs the Streamlit app from the frontend directory.
"""

import sys
import os
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

# Auto-initialize sample documents for HuggingFace Spaces
def initialize_space():
    """Initialize sample documents if vector store is empty"""
    try:
        from axiom.config.loader import load_config
        from axiom.core.vector_store import ChromaVectorStore
        from axiom.core.factory import create_vector_store
        
        config = load_config()
        
        # Check if vector store has any documents
        vector_store = create_vector_store(config)
        
        # Check if store is empty
        try:
            count = vector_store.count("axiom_documents")
            if count == 0:
                raise ValueError("Empty store")
        except:
            # Vector store is empty or doesn't exist - initialize samples
            print("📚 Initializing sample documents for HuggingFace Space...")
            
            # Run preparation script
            from scripts.prepare_space import ingest_sample_documents
            ingest_sample_documents()
            print("✅ Sample documents initialized!")
            
    except Exception as e:
        # If initialization fails, continue anyway (user can upload docs)
        print(f"⚠️ Could not auto-initialize: {e}")
        print("💡 Users can upload documents via the sidebar")

# Only initialize on first run (check env var)
if os.getenv("SPACE_INITIALIZED") != "true":
    initialize_space()
    os.environ["SPACE_INITIALIZED"] = "true"

# Import and run the Streamlit app
from frontend.app import *

