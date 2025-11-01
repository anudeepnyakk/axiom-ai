#!/usr/bin/env python3
"""
Axiom Evaluation Harness

This script runs a retrieval evaluation on a given dataset. It measures the
effectiveness of the retrieval component of the RAG pipeline by calculating
metrics like Recall@k and Mean Reciprocal Rank (MRR).

This fulfills the requirements for Day 5 of the 21-day plan.
"""

import os
import json
import time
import logging
import argparse
import statistics
from typing import List, Dict, Any

from axiom import factory
from axiom.config.models import Config, VectorStoreConfig
from axiom.core.interfaces import DocumentChunk

# --- Constants ---
EVAL_DIR = "evaluation"
DEFAULT_TEST_SET = os.path.join(EVAL_DIR, "test_set.jsonl")
DEFAULT_DOCS_DIR = EVAL_DIR
DEFAULT_OUTPUT_FILE = os.path.join(EVAL_DIR, "baseline_en.json")
PERSISTENCE_DIR = "chroma_db_eval_test"
TEST_COLLECTION_NAME = "axiom_eval_collection"

# --- Helper Functions ---

def load_test_set(file_path: str) -> List[Dict[str, Any]]:
    """Loads a JSON Lines file into a list of dictionaries."""
    with open(file_path, 'r', encoding='utf-8') as f:
        return [json.loads(line) for line in f]

def calculate_metrics(results: List[Dict[str, Any]], k_values: List[int]) -> Dict[str, Any]:
    """Calculates Recall@k and MRR from the evaluation results."""
    
    total_queries = len(results)
    if total_queries == 0:
        return {"error": "No results to calculate."}

    metrics = {}
    
    # Calculate Recall@k
    for k in k_values:
        hits = sum(1 for r in results if r['is_correct_at_k'].get(k, False))
        metrics[f'Recall@{k}'] = hits / total_queries

    # Calculate Mean Reciprocal Rank (MRR)
    mrr_sum = sum(r['reciprocal_rank'] for r in results)
    metrics['MRR'] = mrr_sum / total_queries
    
    # Calculate average latency
    latencies = [r['latency_ms'] for r in results]
    metrics['average_latency_ms'] = statistics.mean(latencies)
    
    return metrics

# --- Main Evaluation Logic ---

def run_evaluation(docs_path: str, test_set_path: str, output_path: str):
    """
    Orchestrates the entire evaluation process.
    """
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(message)s')
    logger = logging.getLogger("AxiomEval")

    logger.info("--- Starting Axiom Retrieval Evaluation ---")

    # 1. Setup: Create a clean config for the evaluation run
    logger.info(f"Using persistence directory: {PERSISTENCE_DIR}")
    if os.path.exists(PERSISTENCE_DIR):
        shutil.rmtree(PERSISTENCE_DIR)

    config = Config.create_default()
    # Override with smaller chunk size for more granular testing
    config.document_processing.chunk_size = 200
    config.document_processing.chunk_overlap = 50
    config.vector_store = VectorStoreConfig(
        persist_directory=PERSISTENCE_DIR,
        collection_name=TEST_COLLECTION_NAME
    )
    config.data_dir = docs_path

    # 2. Ingestion: Process all documents in the specified directory
    logger.info(f"Ingesting documents from: {docs_path}")
    doc_processor = factory.create_document_processor(config)
    
    doc_files = [os.path.join(docs_path, f) for f in os.listdir(docs_path) if f.endswith('.txt')]
    for doc_file in doc_files:
        doc_processor.process_document(doc_file, collection_name=TEST_COLLECTION_NAME)
    
    logger.info(f"Ingestion complete. Processed {len(doc_files)} documents.")

    # 3. Evaluation: Run retrieval for each query in the test set
    logger.info(f"Loading test set from: {test_set_path}")
    test_set = load_test_set(test_set_path)
    
    # For retrieval evaluation, we only need the vector store and embedding generator.
    # We don't need the full QueryEngine, which avoids initializing the LLM provider.
    vector_store = factory.create_vector_store(config, use_local=True)
    embedding_generator = factory.create_embedding_generator(config, use_local=True)
    eval_results = []

    logger.info(f"Running evaluation on {len(test_set)} queries...")
    for item in test_set:
        query = item['query']
        expected_doc_id = item['expected_doc_id']
        
        start_time = time.time()
        
        # We only need the retrieval part for this evaluation
        query_embedding = embedding_generator.embed_batch([DocumentChunk(text=query, metadata={})])[0]
        retrieved_chunks = vector_store.query(
            query_vector=query_embedding,
            top_k=max(args.k_values)
        )
        
        end_time = time.time()
        latency_ms = (end_time - start_time) * 1000
        
        # Grade the results
        reciprocal_rank = 0.0
        is_correct_at_k = {}
        
        # Normalize the expected path to an absolute path for reliable comparison
        expected_abs_path = os.path.abspath(expected_doc_id)
        
        for i, chunk in enumerate(retrieved_chunks):
            rank = i + 1
            
            retrieved_path = chunk.metadata.get('source_file_path')
            if retrieved_path:
                # Also normalize the retrieved path
                retrieved_abs_path = os.path.abspath(retrieved_path)
                if retrieved_abs_path == expected_abs_path:
                    if reciprocal_rank == 0.0:
                        reciprocal_rank = 1.0 / rank
                    for k in args.k_values:
                        if rank <= k:
                            is_correct_at_k[k] = True

        eval_results.append({
            "query": query,
            "expected_doc_id": expected_doc_id,
            "reciprocal_rank": reciprocal_rank,
            "is_correct_at_k": is_correct_at_k,
            "latency_ms": latency_ms
        })

    logger.info("Evaluation loop complete.")

    # 4. Reporting: Calculate and save the final metrics
    logger.info("Calculating final metrics...")
    final_metrics = calculate_metrics(eval_results, args.k_values)
    
    # Add run metadata to the report
    report = {
        "run_timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "total_queries": len(test_set),
        "document_source": docs_path,
        "metrics": final_metrics
    }

    logger.info(f"Saving report to: {output_path}")
    with open(output_path, 'w') as f:
        json.dump(report, f, indent=4)

    logger.info("\n--- Evaluation Report ---")
    print(json.dumps(report, indent=4))
    logger.info("--- Evaluation Complete ---")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Axiom Evaluation Harness")
    parser.add_argument(
        "--docs_path", type=str, default=DEFAULT_DOCS_DIR,
        help="Path to the directory containing documents to ingest."
    )
    parser.add_argument(
        "--test_set_path", type=str, default=DEFAULT_TEST_SET,
        help="Path to the test set file (JSON Lines format)."
    )
    parser.add_argument(
        "--output_path", type=str, default=DEFAULT_OUTPUT_FILE,
        help="Path to save the final evaluation report."
    )
    parser.add_argument(
        '--k_values', nargs='+', type=int, default=[1, 5, 10],
        help="List of k values for calculating Recall@k."
    )
    
    # This is a bit of a hack to get shutil in scope for the setup phase
    import shutil
    
    args = parser.parse_args()
    run_evaluation(args.docs_path, args.test_set_path, args.output_path)
