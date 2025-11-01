#!/usr/bin/env python3
"""
Test script for EmbeddingGenerator functionality.
Validates embedding generation, model info, and validation.
"""

import sys
import os
sys.path.insert(0, '.')

from axiom import create_embedding_generator, load_config
from axiom.core.interfaces import DocumentChunk
import numpy as np


def test_embedding_generator():
    """Test the complete embedding generation pipeline."""
    
    print("🧪 Testing EmbeddingGenerator...")
    
    # Load configuration
    try:
        config = load_config()
        print("✅ Configuration loaded successfully")
    except Exception as e:
        print(f"❌ Failed to load config: {e}")
        return False
    
    # Create embedding generator
    try:
        generator = create_embedding_generator()
        print("✅ EmbeddingGenerator created successfully")
    except Exception as e:
        print(f"❌ Failed to create EmbeddingGenerator: {e}")
        return False
    
    # Test model info
    try:
        model_info = generator.get_model_info()
        print(f"✅ Model info retrieved: {model_info}")
        
        # Verify expected fields
        required_fields = ["model_name", "embedding_dimension", "device", "model_type"]
        for field in required_fields:
            if field not in model_info:
                print(f"❌ Missing field in model info: {field}")
                return False
        
        embedding_dim = model_info["embedding_dimension"]
        print(f"✅ Embedding dimension: {embedding_dim}")
        
    except Exception as e:
        print(f"❌ Failed to get model info: {e}")
        return False
    
    # Test model validation
    try:
        is_valid = generator.validate_model()
        if is_valid:
            print("✅ Model validation successful")
        else:
            print("❌ Model validation failed")
            return False
    except Exception as e:
        print(f"❌ Model validation error: {e}")
        return False
    
    # Test single text embedding
    try:
        test_text = "This is a test document for embedding generation."
        embedding = generator.embed_text(test_text)
        
        if embedding is None or len(embedding) == 0:
            print("❌ Single text embedding failed - empty result")
            return False
        
        if len(embedding) != embedding_dim:
            print(f"❌ Single text embedding dimension mismatch: expected {embedding_dim}, got {len(embedding)}")
            return False
        
        print(f"✅ Single text embedding successful: shape {embedding.shape}")
        
    except Exception as e:
        print(f"❌ Single text embedding failed: {e}")
        return False
    
    # Test batch embedding
    try:
        test_chunks = [
            DocumentChunk(text="First document chunk", metadata={"chunk_index": 0}),
            DocumentChunk(text="Second document chunk", metadata={"chunk_index": 1}),
            DocumentChunk(text="Third document chunk", metadata={"chunk_index": 2})
        ]
        
        embeddings = generator.embed_batch(test_chunks)
        
        if len(embeddings) != len(test_chunks):
            print(f"❌ Batch embedding count mismatch: expected {len(test_chunks)}, got {len(embeddings)}")
            return False
        
        for i, embedding in enumerate(embeddings):
            if len(embedding) != embedding_dim:
                print(f"❌ Batch embedding {i} dimension mismatch: expected {embedding_dim}, got {len(embedding)}")
                return False
        
        print(f"✅ Batch embedding successful: {len(embeddings)} embeddings generated")
        
    except Exception as e:
        print(f"❌ Batch embedding failed: {e}")
        return False
    
    # Test edge cases
    try:
        # Empty batch
        empty_embeddings = generator.embed_batch([])
        if empty_embeddings != []:
            print("❌ Empty batch should return empty list")
            return False
        print("✅ Empty batch handling correct")
        
        # Single chunk batch
        single_chunk = [DocumentChunk(text="Single chunk", metadata={})]
        single_embeddings = generator.embed_batch(single_chunk)
        if len(single_embeddings) != 1:
            print("❌ Single chunk batch should return single embedding")
            return False
        print("✅ Single chunk batch handling correct")
        
    except Exception as e:
        print(f"❌ Edge case testing failed: {e}")
        return False
    
    print("🎉 All EmbeddingGenerator tests passed!")
    return True


if __name__ == "__main__":
    success = test_embedding_generator()
    if not success:
        print("\n❌ Some tests failed. Check the output above.")
        sys.exit(1)
    else:
        print("\n✅ All tests passed successfully!")
