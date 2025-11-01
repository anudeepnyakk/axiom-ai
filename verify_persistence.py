#!/usr/bin/env python3
"""
Day 3 Verification Script: ChromaDB Persistence Test

This script directly tests the persistence of ChromaDB as required by the Day 3
plan. It follows the "restart test" methodology.

**Execution:**

1.  **Run 1 (Ingest):** `python verify_persistence.py`
    - This will clean any old data, ingest a new document, and print the count.
    - Expected output: "Total chunks in DB: 1"

2.  **Run 2 (Verify):** `python verify_persistence.py --verify`
    - This will connect to the existing database without ingesting.
    - Expected output: "Total chunks in DB: 1"

If the count is 1 in both runs, persistence is working correctly.
"""

import os
import shutil
import argparse
from axiom import factory
from axiom.core.interfaces import DocumentChunk
from axiom.config.models import Config, VectorStoreConfig  # Import necessary models

# --- Configuration ---
# Use a dedicated directory for this test to avoid conflicts.
PERSISTENCE_DIR = "chroma_db_day3_test"
COLLECTION_NAME = "day3_test_collection"

def run_ingest(vector_store, config):
    """Cleans up, ingests a single chunk, and prints the count."""
    print("--- Running in INGEST mode ---")
    
    # The vector store will create the directory on initialization
    print(f"Initializing vector store in: {PERSISTENCE_DIR}")
    
    # 2. Create a dummy document chunk
    dummy_chunk = DocumentChunk(
        text="This is a test for persistence.",
        metadata={"source": "verify_persistence.py", "chunk_index": 0}
    )
    
    # 3. Create dummy embedding
    embedding_generator = factory.create_embedding_generator(config, use_local=True)
    embedding = embedding_generator.embed_batch([dummy_chunk])[0]

    # 4. Add to the vector store
    print("Adding 1 document chunk to the vector store...")
    vector_store.add(
        chunks=[dummy_chunk],
        embeddings=[embedding],
        collection_name=COLLECTION_NAME
    )
    
    # 5. Get and print the count
    count = vector_store.count(collection_name=COLLECTION_NAME)
    print(f"✅ Ingest complete. Total chunks in DB: {count}")

def run_verify(vector_store):
    """Connects to the existing DB and prints the chunk count."""
    print("--- Running in VERIFY mode ---")
    
    if not os.path.exists(PERSISTENCE_DIR):
        print("❌ Error: Persistence directory not found.")
        print("Please run the script without '--verify' first to ingest data.")
        return

    print(f"Connecting to existing vector store in: {PERSISTENCE_DIR}")
    count = vector_store.count(collection_name=COLLECTION_NAME)
    
    if count == 1:
        print(f"✅ Verification successful! Total chunks in DB: {count}")
    else:
        print(f"❌ Verification FAILED. Expected 1 chunk, found: {count}")

def main():
    """Main function to parse arguments and run the test."""
    parser = argparse.ArgumentParser(description="Day 3 ChromaDB Persistence Test")
    parser.add_argument(
        "--verify",
        action="store_true",
        help="Run in verification mode (checks existing DB)."
    )
    args = parser.parse_args()

    # --- Test Setup ---
    # On a fresh ingest run, completely clear out the old directory first.
    # This must be done BEFORE the vector store is initialized.
    if not args.verify and os.path.exists(PERSISTENCE_DIR):
        print(f"Removing old test directory: {PERSISTENCE_DIR}")
        shutil.rmtree(PERSISTENCE_DIR)

    # Create a default config and override the persistence directory
    config = Config.create_default()
    config.vector_store = VectorStoreConfig(persist_directory=PERSISTENCE_DIR)

    # Use the factory to create our persistent ChromaDB vector store
    vector_store = factory.create_vector_store(config, use_local=True)

    if args.verify:
        run_verify(vector_store)
    else:
        run_ingest(vector_store, config)

if __name__ == "__main__":
    main()
