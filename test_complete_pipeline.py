"""
Complete RAG Pipeline Test - Project Axiom

This script demonstrates the complete end-to-end RAG system:
1. Document ingestion and processing
2. Embedding generation and storage
3. Query engine with retrieval and generation
4. Professional logging and state tracking

This is your portfolio piece - a working AI system!
"""

import sys
from pathlib import Path

# --- Force correct environment ---
# This is a workaround for stubborn pathing issues where pytest does not see
# the installed packages in the virtual environment. This forcefully adds the
# site-packages directory of the active virtual environment to the system path.
venv_path = Path(__file__).parent.parent / ".venv"
site_packages = venv_path / "Lib" / "site-packages"
if site_packages.exists() and str(site_packages) not in sys.path:
    sys.path.insert(0, str(site_packages))
# --- End workaround ---

import pytest
import tempfile
from axiom.config.loader import load_config
from axiom.core.factory import create_components
from axiom.core.query_engine import QueryResult
from axiom.state_tracker import FileStatus

@pytest.fixture(scope="module")
def full_system_components():
    """
    A module-scoped pytest fixture to set up the complete, real RAG system.
    'scope="module"' means this will only run once for all tests in this file,
    which is efficient as initializing the embedding model can be slow.
    """
    config = load_config()
    # Note: This requires a valid OPENAI_API_KEY in the environment.
    query_engine, document_processor, state_tracker, vector_store = create_components(config)
    
    yield query_engine, document_processor, vector_store
    
    # --- Teardown ---
    state_tracker.close()

@pytest.fixture
def knowledge_base(full_system_components):
    """
    A pytest fixture that creates and ingests a temporary knowledge base
    for the duration of a single test.
    """
    query_engine, document_processor, vector_store = full_system_components
    
    with tempfile.TemporaryDirectory() as temp_dir:
        test_dir = Path(temp_dir)
        
        # Create test documents with specific, searchable content
        docs = {
            "ai.txt": "Artificial Intelligence is the future of technology.",
            "rag.txt": "Retrieval-Augmented Generation combines search with language models.",
            "axiom.txt": "Axiom is a sovereign AI system built for accuracy."
        }

    file_paths = []
        for filename, content in docs.items():
            file_path = test_dir / filename
            file_path.write_text(content)
        file_paths.append(str(file_path))
    
        # --- Ingestion ---
        # 1. Process documents into chunks
        chunks_lists = document_processor.process_batch(file_paths)
        all_chunks = [chunk for sublist in chunks_lists for chunk in sublist]
        
        # 2. Generate embeddings
        embeddings = query_engine.embedding_generator.embed_batch(all_chunks)
        
        # 3. Store in vector database
        vector_store.add(chunks=all_chunks, embeddings=embeddings)
        
        yield # The test runs at this point
        
        # --- Teardown ---
        vector_store.clear() # Clear the vector store for the next test

def test_end_to_end_retrieval(full_system_components, knowledge_base):
    """
    Tests the full end-to_end pipeline with a focus on accurate retrieval and generation.
    This requires a valid OPENAI_API_KEY to be set in the environment.
    """
    query_engine, _, _ = full_system_components
    
    # 1. Test a query that should have a clear answer from the knowledge base
    question = "What is Axiom?"
    result = query_engine.query(question, top_k=1)
    
    # Assert that the answer is reasonable and based on the context
    # We check for keywords rather than an exact match, as LLM output can vary slightly.
    answer = result.answer.lower()
    assert "axiom" in answer
    assert "sovereign" in answer
    assert "accuracy" in answer
    
    # Assert that the correct source document was retrieved
    assert len(result.context_chunks) > 0
    retrieved_source = result.context_chunks[0].metadata.get("file_name")
    assert retrieved_source == "axiom.txt"

def test_no_information_response(full_system_components, knowledge_base):
    """
    Tests that the system correctly states when it does not have enough information.
    """
    query_engine, _, _ = full_system_components
    
    # 2. Test a query that cannot be answered from the documents
    question = "What is the capital of France?"
    result = query_engine.query(question, top_k=1)
    
    # Assert that the system admits it doesn't know the answer
    # This is a critical test for honesty and hallucination-reduction.
    answer = result.answer.lower()
    assert "not enough information" in answer or "do not contain" in answer


# --- Runnable Script Block ---
# This allows the test to be run directly as a Python script, bypassing pytest
# and its environment issues. This is a powerful debugging technique to ensure
# the correct Python interpreter and environment are being used.

if __name__ == "__main__":
    print("--- Running End-to-End Test Suite as a Script ---")

    # Manually set up the components
    print("\n[1/4] Initializing components...")
    components = full_system_components()
    print("Components initialized successfully.")

    # Manually set up the knowledge base fixture
    print("\n[2/4] Setting up knowledge base...")
    try:
        # We need to simulate the 'yield' of a pytest fixture
        knowledge_base_generator = knowledge_base(components)
        next(knowledge_base_generator)
        print("Knowledge base created and populated.")

        # Run the first test
        print("\n[3/4] Running test: test_end_to_end_retrieval...")
        test_end_to_end_retrieval(components, None) # knowledge_base is not directly used, fixture handles it
        print("✅ PASSED: test_end_to_end_retrieval")

        # Run the second test
        print("\n[4/4] Running test: test_no_information_response...")
        test_no_information_response(components, None)
        print("✅ PASSED: test_no_information_response")

        print("\n--- All tests passed successfully! ---")

    finally:
        # Manually tear down the knowledge base
        try:
            next(knowledge_base_generator) # This runs the teardown part of the fixture
        except StopIteration:
            pass # This is expected
        print("\nKnowledge base cleaned up.")
