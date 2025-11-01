"""
One-off script to ingest documents into the Axiom vector store.

This is used to populate the database before running evaluations or demos.

Usage:
    python scripts/ingest.py axiom/data/Raya_-_Srinivas_Reddy.pdf
"""

import asyncio
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from axiom.config.loader import load_config
from axiom.core.factory import create_document_processor


async def main(file_paths: list[str]):
    """
    Initializes components and processes the documents.
    """
    print("Initializing components for ingestion...")
    config = load_config()
    document_processor = create_document_processor(config)

    for file_path in file_paths:
        path = Path(file_path)
        if not path.exists():
            print(f"Error: File not found at {file_path}")
            continue

        print(f"Processing document: {path.name}...")

        # Process the document (this handles chunking, embedding, and storage internally)
        result = await asyncio.to_thread(document_processor.process_document, str(path))
        if result:
            print(f"  - Successfully ingested {path.name}.")
        else:
            print(f"  - Failed to ingest {path.name}.")

    print("\nIngestion complete.")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python scripts/ingest.py <file_path_1> <file_path_2> ...")
        sys.exit(1)
    
    document_paths = sys.argv[1:]
    asyncio.run(main(document_paths))
