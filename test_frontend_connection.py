"""
Quick test to verify frontend can connect to backend.
Run this before starting the full Streamlit app.
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

print("Testing Backend Connection...")
print("=" * 60)

try:
    print("\n1. Importing backend modules...")
    from axiom.config.loader import load_config
    from axiom.core.factory import create_query_engine
    print("✅ Import successful")
    
    print("\n2. Loading configuration...")
    config = load_config()
    print(f"✅ Config loaded successfully")
    
    print("\n3. Creating query engine...")
    query_engine = create_query_engine(config)
    print("✅ Query engine created")
    
    print("\n4. Testing a simple query...")
    result = query_engine.query("What is this document about?", top_k=3)
    print(f"✅ Query successful!")
    print(f"   Answer length: {len(result.answer)} characters")
    print(f"   Retrieved chunks: {len(result.context_chunks)}")
    print(f"\n   First 200 chars of answer:")
    print(f"   {result.answer[:200]}...")
    
    print("\n" + "=" * 60)
    print("🎉 Backend Connection Test: PASSED")
    print("=" * 60)
    print("\n✅ Frontend is ready to connect!")
    print("Run: cd frontend && streamlit run app.py")
    
except Exception as e:
    print(f"\n❌ Error: {e}")
    print("\nTroubleshooting:")
    print("1. Make sure documents are ingested: python scripts/ingest.py")
    print("2. Check OpenAI API key is set: echo $OPENAI_API_KEY")
    print("3. Verify ChromaDB exists: ls chroma_db/")
    import traceback
    traceback.print_exc()

