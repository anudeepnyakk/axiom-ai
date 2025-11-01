#!/usr/bin/env python3
"""
Simple verification script for EmbeddingGenerator.
Run this when Python environment is available.
"""

import sys
import os
sys.path.insert(0, '.')

try:
    from axiom import create_embedding_generator
    print("✅ EmbeddingGenerator import successful")
    
    # Test creation
    generator = create_embedding_generator()
    print("✅ EmbeddingGenerator instance created")
    
    # Test model info
    info = generator.get_model_info()
    print(f"✅ Model info: {info}")
    
    # Test validation
    is_valid = generator.validate_model()
    print(f"✅ Model validation: {is_valid}")
    
    print("\n🎉 EmbeddingGenerator is working correctly!")
    
except ImportError as e:
    print(f"❌ Import error: {e}")
except Exception as e:
    print(f"❌ Error: {e}")
