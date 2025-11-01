#!/usr/bin/env python3
"""
Test script for VectorStore functionality.
Validates storage, retrieval, and search operations.
"""

import sys
import os
import tempfile
import shutil
sys.path.insert(0, '.')

from axiom import create_vector_store, create_embedding_generator, load_config
from axiom.core.interfaces import DocumentChunk
import numpy as np


def test_vector_store():
    """Test the complete vector storage pipeline."""
    
    print("🧪 Testing VectorStore...")
    
    # Create temporary directory for testing
    temp_dir = tempfile.mkdtemp()
    print(f"✅ Created temp directory: {temp_dir}")
    
    try:
        # Load configuration
        try:
            config = load_config()
            print("✅ Configuration loaded successfully")
        except Exception as e:
            print(f"❌ Failed to load config: {e}")
            return False
        
        # Create vector store
        try:
            vector_store = create_vector_store(
                persist_directory=temp_dir,
                collection_name="test_collection"
            )
            print("✅ VectorStore created successfully")
        except Exception as e:
            print(f"❌ Failed to create VectorStore: {e}")
            return False
        
        # Create embedding generator
        try:
            embedding_generator = create_embedding_generator()
            print("✅ EmbeddingGenerator created successfully")
        except Exception as e:
            print(f"❌ Failed to create EmbeddingGenerator: {e}")
            return False
        
        # Test collection initialization
        try:
            model_info = embedding_generator.get_model_info()
            embedding_dim = model_info["embedding_dimension"]
            vector_store.init_collection(embedding_dim)
            print(f"✅ Collection initialized for dimension {embedding_dim}")
        except Exception as e:
            print(f"❌ Failed to initialize collection: {e}")
            return False
        
        # Test adding chunks
        try:
            test_chunks = [
                DocumentChunk(text="First test document chunk", metadata={"chunk_index": 0, "source": "test"}),
                DocumentChunk(text="Second test document chunk", metadata={"chunk_index": 1, "source": "test"}),
                DocumentChunk(text="Third test document chunk", metadata={"chunk_index": 2, "source": "test"})
            ]
            
            # Generate embeddings
            embeddings = embedding_generator.embed_batch(test_chunks)
            print(f"✅ Generated {len(embeddings)} embeddings")
            
            # Add to vector store
            chunk_ids = vector_store.add(test_chunks, embeddings)
            print(f"✅ Added {len(chunk_ids)} chunks to vector store")
            
            # Verify count
            count = vector_store.count()
            if count != len(test_chunks):
                print(f"❌ Count mismatch: expected {len(test_chunks)}, got {count}")
                return False
            print(f"✅ Vector store count: {count}")
            
        except Exception as e:
            print(f"❌ Failed to add chunks: {e}")
            return False
        
        # Test retrieval
        try:
            retrieved = vector_store.get(chunk_ids)
            if len(retrieved) != len(test_chunks):
                print(f"❌ Retrieval count mismatch: expected {len(test_chunks)}, got {len(retrieved)}")
                return False
            
            # Verify content
            for i, (chunk, embedding) in enumerate(retrieved):
                if chunk.text != test_chunks[i].text:
                    print(f"❌ Text mismatch at index {i}")
                    return False
                if len(embedding) != embedding_dim:
                    print(f"❌ Embedding dimension mismatch at index {i}")
                    return False
            
            print("✅ Chunk retrieval successful")
            
        except Exception as e:
            print(f"❌ Failed to retrieve chunks: {e}")
            return False
        
        # Test text search
        try:
            search_results = vector_store.search_by_text("test document", n_results=3)
            if len(search_results) == 0:
                print("❌ Text search returned no results")
                return False
            
            print(f"✅ Text search successful: {len(search_results)} results")
            
            # Verify search results contain expected content
            found_texts = [result[0].text for result in search_results]
            if not any("test document" in text.lower() for text in found_texts):
                print("❌ Text search results don't contain expected content")
                return False
            
        except Exception as e:
            print(f"❌ Failed to search by text: {e}")
            return False
        
        # Test vector search
        try:
            # Create a query embedding
            query_text = "test document chunk"
            query_embedding = embedding_generator.embed_text(query_text)
            
            search_results = vector_store.search_by_vector(query_embedding, n_results=3)
            if len(search_results) == 0:
                print("❌ Vector search returned no results")
                return False
            
            print(f"✅ Vector search successful: {len(search_results)} results")
            
        except Exception as e:
            print(f"❌ Failed to search by vector: {e}")
            return False
        
        # Test stats
        try:
            stats = vector_store.stats()
            required_fields = ["collection_name", "total_chunks", "persist_directory", "collection_exists"]
            for field in required_fields:
                if field not in stats:
                    print(f"❌ Missing field in stats: {field}")
                    return False
            
            if stats["total_chunks"] != len(test_chunks):
                print(f"❌ Stats count mismatch: expected {len(test_chunks)}, got {stats['total_chunks']}")
                return False
            
            print(f"✅ Stats retrieved: {stats}")
            
        except Exception as e:
            print(f"❌ Failed to get stats: {e}")
            return False
        
        # Test upsert
        try:
            # Update existing chunk
            updated_chunk = DocumentChunk(
                text="Updated first test document chunk",
                metadata={"chunk_index": 0, "source": "test", "updated": True}
            )
            updated_embedding = embedding_generator.embed_text(updated_chunk.text)
            
            vector_store.upsert([updated_chunk], [updated_embedding], [chunk_ids[0]])
            
            # Verify update
            retrieved = vector_store.get([chunk_ids[0]])
            if retrieved[0][0].text != updated_chunk.text:
                print("❌ Upsert failed to update content")
                return False
            
            print("✅ Upsert operation successful")
            
        except Exception as e:
            print(f"❌ Failed to upsert: {e}")
            return False
        
        # Test delete
        try:
            vector_store.delete([chunk_ids[0]])
            count_after_delete = vector_store.count()
            if count_after_delete != len(test_chunks) - 1:
                print(f"❌ Delete count mismatch: expected {len(test_chunks) - 1}, got {count_after_delete}")
                return False
            
            print("✅ Delete operation successful")
            
        except Exception as e:
            print(f"❌ Failed to delete: {e}")
            return False
        
        print("🎉 All VectorStore tests passed!")
        return True
        
    finally:
        # Cleanup
        try:
            shutil.rmtree(temp_dir)
            print(f"✅ Cleaned up temp directory: {temp_dir}")
        except Exception as e:
            print(f"⚠️ Failed to cleanup temp directory: {e}")


if __name__ == "__main__":
    success = test_vector_store()
    if not success:
        print("\n❌ Some tests failed. Check the output above.")
        sys.exit(1)
    else:
        print("\n✅ All tests passed successfully!")
