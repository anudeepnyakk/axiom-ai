"""
Axiom Final Test Script

This script performs the definitive end-to-end test of the Axiom RAG system.
It is a standalone Python script, free of pytest complexities, to ensure it runs
in a predictable environment.

It tests two core scenarios:
1.  Successful retrieval and synthesis for a known-answer query.
2.  Graceful failure for a query outside the knowledge base's scope.
"""

import sys
import os
import tempfile
from pathlib import Path

# --- Force correct environment ---
# This workaround ensures that the Python interpreter finds the packages
# installed in our virtual environment, bypassing any system path issues.
venv_path = Path(__file__).parent / ".venv"
site_packages = venv_path / "Lib" / "site-packages"
if site_packages.exists() and str(site_packages) not in sys.path:
    print(f"--> Forcing environment path: {site_packages}")
    sys.path.insert(0, str(site_packages))
# --- End workaround ---

from axiom.config.loader import load_config
from axiom.core.factory import create_components

def setup_knowledge_base(document_processor, vector_store, embedding_generator, test_dir):
    """Creates test files and ingests them into the system."""
    print("  - Creating temporary test documents...")
    docs = {
        "axiom.txt": "Axiom is a sovereign AI system built for accuracy.",
        "rag.txt": "Retrieval-Augmented Generation combines search with language models.",
        "ai.txt": "Artificial Intelligence is the future of technology."
    }
    file_paths = []
    for filename, content in docs.items():
        file_path = test_dir / filename
        file_path.write_text(content, encoding='utf-8')
        file_paths.append(str(file_path))

    print("  - Starting document ingestion...")
    chunks_lists = document_processor.process_batch(file_paths)
    all_chunks = [chunk for sublist in chunks_lists for chunk in sublist]

    if not all_chunks:
        print("  - [ERROR] Ingestion produced no chunks. Aborting.")
        return False

    print(f"  - Ingestion successful. Produced {len(all_chunks)} chunks.")
    print("  - Generating embeddings...")
    embeddings = embedding_generator.embed_batch(all_chunks)
    
    print("  - Adding chunks and embeddings to vector store...")
    vector_store.add(chunks=all_chunks, embeddings=embeddings)
    print("  - Knowledge base setup complete.")
    return True

def run_retrieval_test(query_engine):
    """Tests a query that should have a clear answer."""
    print("\n--- Running Test (1/2): Successful Retrieval ---")
    question = "What is Axiom?"
    print(f"  - Query: \"{question}\"")
    
    result = query_engine.query(question, top_k=1)
    answer = result.answer.lower()
    
    print(f"  - Answer received: \"{result.answer[:100]}...\"")

    if "axiom" in answer and "sovereign" in answer:
        print("  - ✅ PASSED: Answer contains expected keywords.")
        return True
    else:
        print(f"  - ❌ FAILED: Answer did not contain 'axiom' and 'sovereign'.")
        return False

def run_no_info_test(query_engine):
    """Tests a query that should not have an answer."""
    print("\n--- Running Test (2/2): No Information ---")
    question = "What is the capital of France?"
    print(f"  - Query: \"{question}\"")
    
    result = query_engine.query(question, top_k=1)
    answer = result.answer.lower()
    
    print(f"  - Answer received: \"{result.answer}\"")
    
    if "not enough information" in answer or "do not contain" in answer:
        print("  - ✅ PASSED: System correctly stated it lacked information.")
        return True
    else:
        print(f"  - ❌ FAILED: System did not return the expected 'no information' response.")
        return False

def main():
    """Main execution block."""
    print("--- Axiom Final Test Suite ---")

    # We require the API key to be set
    if not os.getenv("OPENAI_API_KEY"):
        print("\n[FATAL ERROR] The 'OPENAI_API_KEY' environment variable is not set.")
        print("Please set it before running the test.")
        return

    print("\n[Step 1/4] Initializing components...")
    try:
        config = load_config()
        # The factory returns components in a specific order. We must match it.
        query_engine, document_processor, state_tracker, vector_store = create_components(config)
        # The embedding_generator is part of the query_engine.
        embedding_generator = query_engine.embedding_generator
        print("  - Components initialized successfully.")
    except Exception as e:
        print(f"  - [FATAL ERROR] Failed to initialize components: {e}")
        return

    # Use a temporary directory that is automatically cleaned up
    with tempfile.TemporaryDirectory() as temp_dir:
        test_dir = Path(temp_dir)
        print(f"\n[Step 2/4] Setting up knowledge base in temporary directory: {test_dir}")
        
        setup_successful = setup_knowledge_base(document_processor, vector_store, embedding_generator, test_dir)
        
        if not setup_successful:
            print("\n--- TEST RUN FAILED due to knowledge base setup error. ---")
            return

        print("\n[Step 3/4] Running tests...")
        retrieval_passed = run_retrieval_test(query_engine)
        no_info_passed = run_no_info_test(query_engine)

        print("\n[Step 4/4] Test execution complete.")
        
        if retrieval_passed and no_info_passed:
            print("\n===================================")
            print("  ✅ ALL TESTS PASSED SUCCESSFULLY!")
            print("===================================")
        else:
            print("\n===================================")
            print("  ❌ SOME TESTS FAILED.")
            print("===================================")

if __name__ == "__main__":
    main()
