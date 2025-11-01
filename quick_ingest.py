"""
Quick Document Ingestion Script
Add multiple documents to Axiom AI quickly
"""

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from axiom.config.loader import load_config
from axiom.core.factory import create_document_processor


async def main():
    print("\n" + "="*70)
    print("  📄 AXIOM AI - QUICK DOCUMENT INGESTION")
    print("="*70)
    
    # Look for documents in common locations
    search_paths = [
        Path("axiom/data"),
        Path("documents"),
        Path("docs"),
        Path("."),
    ]
    
    documents = []
    for path in search_paths:
        if path.exists():
            for ext in ["*.pdf", "*.txt"]:
                documents.extend(list(path.glob(ext)))
    
    if not documents:
        print("\n❌ No PDF or TXT files found in:")
        for path in search_paths:
            print(f"   • {path}")
        print("\n💡 TIP: Place PDF/TXT files in axiom/data/ directory")
        return
    
    print(f"\n📚 Found {len(documents)} document(s):")
    for i, doc in enumerate(documents, 1):
        size_mb = doc.stat().st_size / (1024 * 1024)
        print(f"   [{i}] {doc.name} ({size_mb:.2f} MB)")
    
    print("\n🚀 Starting ingestion...")
    print("-"*70)
    
    config = load_config()
    doc_processor = create_document_processor(config)
    
    success_count = 0
    for i, doc_path in enumerate(documents, 1):
        print(f"\n[{i}/{len(documents)}] Processing: {doc_path.name}")
        
        try:
            result = await asyncio.to_thread(doc_processor.process_document, str(doc_path))
            if result:
                print(f"   ✅ Success!")
                success_count += 1
            else:
                print(f"   ❌ Failed (check logs)")
        except Exception as e:
            print(f"   ❌ Error: {str(e)[:100]}")
    
    print("\n" + "="*70)
    print(f"  SUMMARY: {success_count}/{len(documents)} documents ingested successfully")
    print("="*70)
    
    if success_count > 0:
        print("\n✅ Done! You can now:")
        print("   1. Run: python test_final_system.py")
        print("   2. Or start UI: cd frontend && streamlit run app.py")


if __name__ == "__main__":
    asyncio.run(main())

