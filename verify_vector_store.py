#!/usr/bin/env python3
"""
Simple verification script for VectorStore.
Run this when Python environment is available.
"""

import sys
import os
sys.path.insert(0, '.')

try:
    from axiom import create_vector_store
    print("✅ VectorStore import successful")
    
    # Test creation
    vector_store = create_vector_store("./test_chroma", "test_collection")
    print("✅ VectorStore instance created")
    
    # Test collection initialization
    vector_store.init_collection(384)  # Standard dimension for all-MiniLM-L6-v2
    print("✅ Collection initialized")
    
    # Test stats
    stats = vector_store.stats()
    print(f"✅ Stats retrieved: {stats}")
    
    print("\n🎉 VectorStore is working correctly!")
    
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("💡 Install dependencies with: pip install chromadb sentence-transformers")
except Exception as e:
    print(f"❌ Error: {e}")
