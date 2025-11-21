import pytest
import shutil
import os
from langchain_community.vectorstores import Chroma
from langchain_core.documents import Document
from langchain_community.embeddings import FakeEmbeddings # SAVES MONEY

# Setup/Teardown for a clean DB every test
@pytest.fixture
def vector_store():
    # Use FakeEmbeddings to avoid OpenAI costs during testing
    # FakeEmbeddings is available in newer langchain-community
    embeddings = FakeEmbeddings(size=1536) 
    persist_dir = "./test_chroma_db"
    
    # Initialize
    # Clean up before starting if it exists
    if os.path.exists(persist_dir):
        shutil.rmtree(persist_dir)

    vs = Chroma(
        collection_name="test_collection",
        embedding_function=embeddings,
        persist_directory=persist_dir
    )
    yield vs
    # Cleanup after test
    if os.path.exists(persist_dir):
        shutil.rmtree(persist_dir, ignore_errors=True)

def test_vector_ingestion_and_retrieval(vector_store):
    # 1. Ingest Mock Data
    docs = [
        Document(page_content="The capital of France is Paris.", metadata={"source": "doc1"}),
        Document(page_content="The capital of Spain is Madrid.", metadata={"source": "doc2"}),
    ]
    vector_store.add_documents(docs)
    
    # 2. Test Retrieval
    # Note: FakeEmbeddings can't do real semantic search, 
    # so we just check if data exists or matches exact keywords if supported.
    # For 'Fake', we mostly check if it DOESN'T crash and returns *something*.
    results = vector_store.similarity_search("France", k=1)
    
    assert len(results) == 1, "Should retrieve 1 document"
    # In a real test with OpenAIEmbeddings, you'd assert results[0].content == ...

