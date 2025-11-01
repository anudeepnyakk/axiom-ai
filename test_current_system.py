"""
Test script to verify all current Axiom features are working.

Tests:
1. Basic query functionality
2. Retrieval from ChromaDB
3. Multiple query types
"""

import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from axiom.config.loader import load_config
from axiom.core.factory import create_query_engine


def test_basic_query():
    """Test 1: Basic query functionality"""
    print("\n" + "="*60)
    print("TEST 1: BASIC QUERY")
    print("="*60)
    
    config = load_config()
    query_engine = create_query_engine(config)
    
    query = "What is the main focus of Chip War?"
    print(f"\nQuery: {query}")
    print("-"*60)
    
    result = query_engine.query(query, top_k=3)
    
    if result and result.answer:
        print(f"\n✅ Query successful!")
        print(f"\nQuestion: {result.question}")
        print(f"\nAnswer: {result.answer}")
        print(f"\nContext chunks retrieved: {len(result.context_chunks)}")
        if result.context_chunks:
            print(f"First chunk preview: {result.context_chunks[0].text[:150]}...")
    else:
        print("❌ No results found")
    
    return result is not None and result.answer


def test_factual_query():
    """Test 2: Factual query"""
    print("\n" + "="*60)
    print("TEST 2: FACTUAL QUERY")
    print("="*60)
    
    config = load_config()
    query_engine = create_query_engine(config)
    
    query = "What is TSMC?"
    print(f"\nQuery: {query}")
    print("-"*60)
    
    result = query_engine.query(query, top_k=3)
    
    if result and result.answer:
        print(f"\n✅ Query successful!")
        print(f"\nAnswer: {result.answer[:300]}...")
    else:
        print("❌ No results found")
    
    return result is not None and result.answer


def test_comparative_query():
    """Test 3: Comparative query"""
    print("\n" + "="*60)
    print("TEST 3: COMPARATIVE QUERY")
    print("="*60)
    
    config = load_config()
    query_engine = create_query_engine(config)
    
    query = "How does China's chip industry compare to Taiwan?"
    print(f"\nQuery: {query}")
    print("-"*60)
    
    result = query_engine.query(query, top_k=5)
    
    if result and result.answer:
        print(f"\n✅ Query successful!")
        print(f"\nContext chunks used: {len(result.context_chunks)}")
        print(f"\nAnswer: {result.answer}")
    else:
        print("❌ No results found")
    
    return result is not None and result.answer


def test_collection_stats():
    """Test 4: Check ChromaDB collection stats"""
    print("\n" + "="*60)
    print("TEST 4: DATABASE STATISTICS")
    print("="*60)
    
    config = load_config()
    query_engine = create_query_engine(config)
    
    # Access vector store stats
    if hasattr(query_engine, 'vector_store'):
        # ChromaVectorStore uses _collection internally
        if hasattr(query_engine.vector_store, '_collection'):
            count = query_engine.vector_store._collection.count()
            print(f"\n✅ Total chunks in database: {count}")
            
            # Get sample data to see what's actually stored
            sample = query_engine.vector_store._collection.get(limit=5)
            if sample and 'documents' in sample:
                print(f"\n📄 Sample documents:")
                for i, doc in enumerate(sample['documents'][:3], 1):
                    print(f"\n[Sample {i}]: {doc[:150]}...")
            return count > 0
        else:
            print("❌ Cannot access collection")
            return False
    else:
        print("❌ Cannot access vector store")
        return False


def main():
    """Run all tests"""
    print("\n" + "="*60)
    print("🧪 AXIOM SYSTEM TEST SUITE")
    print("="*60)
    print("\nTesting all features after embedding completion...")
    
    results = {
        "Basic Query": test_basic_query(),
        "Factual Query": test_factual_query(),
        "Comparative Query": test_comparative_query(),
        "Database Stats": test_collection_stats(),
    }
    
    # Summary
    print("\n" + "="*60)
    print("📊 TEST SUMMARY")
    print("="*60)
    
    passed = sum(results.values())
    total = len(results)
    
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name:25} {status}")
    
    print(f"\n{passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 ALL TESTS PASSED! Your system is working!")
    else:
        print("\n⚠️ Some tests failed. Check the output above.")
    
    return passed == total


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

