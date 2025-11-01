#!/usr/bin/env python3
"""
Day 4 Verification Script: End-to-End RAG Pipeline Test

This script tests the full query pipeline as required by the Day 4 plan.
It performs the following steps:
1. Cleans up any previous test data.
2. Ingests a sample document into a persistent ChromaDB vector store.
3. Initializes a complete QueryEngine with all necessary components.
4. Asks a question that can only be answered from the ingested document.
5. Prints the synthesized answer and the context chunks used.
"""

import os
import shutil
import logging
from axiom import factory
from axiom.config.models import Config, VectorStoreConfig
from axiom.core.interfaces import DocumentChunk

# --- Test Configuration ---
PERSISTENCE_DIR = "chroma_db_day4_test"
TEST_COLLECTION_NAME = "day4_test_collection"
TEST_DOCUMENT_CONTENT = """
AxiomAI is a powerful Retrieval-Augmented Generation (RAG) system.
It was designed by a team of dedicated AI engineers.
Its primary function is to answer questions based on a given set of documents.
The core components include a document processor, an embedding generator,
a vector store, and an LLM synthesizer. The system is designed to be
modular and configurable, allowing different components to be swapped out.
For example, it can use OpenAI's GPT-4 or local models for synthesis.
The project's mascot is a wise owl named 'Lexi'.
"""
TEST_DOCUMENT_PATH = "day4_test_doc.txt"
TEST_QUESTION = "What is the name of the project's mascot?"

def setup_test_environment():
    """Prepares the test environment by cleaning up old data and creating the test document."""
    print("--- 1. Setting up test environment ---")
    
    # Clean up old database directory
    if os.path.exists(PERSISTENCE_DIR):
        shutil.rmtree(PERSISTENCE_DIR)
        print(f"Removed old test directory: {PERSISTENCE_DIR}")
        
    # Create the test document
    with open(TEST_DOCUMENT_PATH, "w") as f:
        f.write(TEST_DOCUMENT_CONTENT)
    print(f"Created test document: {TEST_DOCUMENT_PATH}")

def run_ingestion(config):
    """Ingests the test document into the vector store."""
    print("\n--- 2. Running document ingestion ---")
    
    # Use the factory to create the necessary components for ingestion
    doc_processor = factory.create_document_processor(config)
    
    # The process_document method handles chunking, embedding, and storing
    chunks = doc_processor.process_document(TEST_DOCUMENT_PATH, collection_name=TEST_COLLECTION_NAME)
    
    print(f"Successfully ingested document into {len(chunks)} chunks.")
    return chunks

def run_query(config):
    """Initializes the QueryEngine and asks the test question."""
    print("\n--- 3. Initializing QueryEngine and running query ---")
    
    # The factory wires everything together for us
    query_engine = factory.create_query_engine(config)
    
    print(f"Asking question: '{TEST_QUESTION}'")
    result = query_engine.query(TEST_QUESTION)
    
    print("\n--- 4. Displaying Results ---")
    print(f"\nAnswer:\n---\n{result.answer}\n---")
    
    print("\nContext Chunks Used:")
    if result.context_chunks:
        for i, chunk in enumerate(result.context_chunks, 1):
            print(f"  - Chunk {i} (Source: {chunk.metadata.get('source_file_path', 'N/A')}):")
            print(f"    \"{chunk.text[:100].strip()}...\"")
    else:
        print("  - No context chunks were used.")

def cleanup():
    """Removes the test document."""
    print("\n--- 5. Cleaning up ---")
    if os.path.exists(TEST_DOCUMENT_PATH):
        os.remove(TEST_DOCUMENT_PATH)
        print(f"Removed test document: {TEST_DOCUMENT_PATH}")

def main():
    """Main function to orchestrate the Day 4 verification test."""
    # Note: To run this, you must have an OPENAI_API_KEY set in your
    # environment or in your config.yaml file.
    
    # Setup basic logging to see output from the Axiom components
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(name)s - %(message)s')
    
    try:
        setup_test_environment()
        
        # Create a config object pointing to our test database and collection
        config = Config.create_default()
        config.vector_store = VectorStoreConfig(
            persist_directory=PERSISTENCE_DIR,
            collection_name=TEST_COLLECTION_NAME
        )
        config.data_dir = "." # Look for documents in the current directory
        
        # Load API keys from config.yaml if they exist
        # This allows running without environment variables if config.yaml is set up.
        try:
            from axiom import load_config
            loaded_config = load_config()
            config.api_keys = loaded_config.api_keys
        except (FileNotFoundError, ValueError):
            print("Warning: config.yaml not found or invalid. Relying on environment variables for API keys.")

        if not config.api_keys.openai:
            # You can manually set it here for testing if needed
            # config.api_keys.openai = "sk-..."
            print("\nCRITICAL: OPENAI_API_KEY not found in config.yaml or environment.")
            print("The query step will likely fail. Please configure your API key.")

        run_ingestion(config)
        run_query(config)
        
    finally:
        cleanup()

if __name__ == "__main__":
    main()
