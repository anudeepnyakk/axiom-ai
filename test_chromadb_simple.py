"""
Simple ChromaDB Test - Isolate the issue
"""

import chromadb
from chromadb.config import Settings
import numpy as np

def test_chromadb_simple():
    """Test basic ChromaDB functionality"""
    print("🧪 Testing ChromaDB Basic Functionality")
    
    try:
        # Create a simple client
        client = chromadb.PersistentClient(
            path="test_chroma_db",
            settings=Settings(anonymized_telemetry=False)
        )
        print("✅ ChromaDB client created")
        
        # Create a collection
        collection = client.create_collection(
            name="test_collection",
            metadata={"description": "Test collection"}
        )
        print("✅ Collection created")
        
        # Test data
        documents = ["This is a test document", "Another test document"]
        embeddings = [
            np.random.randn(384).tolist(),  # Convert to list
            np.random.randn(384).tolist()
        ]
        metadatas = [{"source": "test1"}, {"source": "test2"}]
        ids = ["id1", "id2"]
        
        print(f"📝 Adding {len(documents)} documents...")
        
        # Try to add
        result = collection.add(
            documents=documents,
            embeddings=embeddings,
            metadatas=metadatas,
            ids=ids
        )
        
        print("✅ Documents added successfully!")
        print(f"Result: {result}")
        
        # Test query
        query_result = collection.query(
            query_embeddings=[np.random.randn(384).tolist()],
            n_results=2
        )
        
        print("✅ Query successful!")
        print(f"Query result: {query_result}")
        
    except Exception as e:
        print(f"❌ ChromaDB test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_chromadb_simple()
