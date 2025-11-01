"""
Captures Hindi baseline metrics for Axiom AI retrieval evaluation.

This script runs the evaluation on Hindi queries and saves a baseline report
to validate multilingual capabilities.

Usage:
    python evaluation/capture_baseline_hi.py
"""

import json
import time
import sys
from pathlib import Path
from datetime import datetime

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

import asyncio
from axiom.core.factory import create_query_engine
from axiom.config.loader import load_config
from axiom.core.interfaces import DocumentChunk


async def run_retrieval_with_latency(query_engine, query: str, top_k: int = 10):
    """Run retrieval and measure latency."""
    start_time = time.time()
    
    question_embedding = await asyncio.to_thread(
        query_engine.embedding_generator.embed_batch,
        [DocumentChunk(text=query, metadata={})]
    )
    
    search_results = await asyncio.to_thread(
        query_engine.vector_store.query,
        query_vector=question_embedding[0],
        top_k=top_k
    )
    
    latency_ms = (time.time() - start_time) * 1000
    
    # Extract doc IDs from results
    retrieved_docs = [
        Path(chunk.metadata.get('source_file_path', '')).name
        for chunk in search_results
    ]
    
    return retrieved_docs, latency_ms


async def main():
    """Main function to capture Hindi baseline."""
    print("Capturing Hindi (हिंदी) baseline for Axiom AI...")
    
    # 1. Load configuration and create components
    config = load_config()
    query_engine = create_query_engine(config)
    
    # 2. Load the Hindi test set
    test_set_path = Path(__file__).parent / "hi_test_set.jsonl"
    test_cases = []
    with open(test_set_path, "r", encoding="utf-8") as f:
        for line in f:
            test_cases.append(json.loads(line))
    
    # 3. Run retrieval for all queries and collect metrics
    print(f"Running retrieval for {len(test_cases)} Hindi queries...")
    
    recall_at_1 = []
    recall_at_5 = []
    recall_at_10 = []
    reciprocal_ranks = []
    latencies = []
    
    for test_case in test_cases:
        query_id = test_case["query_id"]
        query_text = test_case["query"]
        relevant_docs = set(test_case["relevant_doc_ids"])
        
        print(f"  - Running query: {query_id}")
        retrieved_docs, latency = await run_retrieval_with_latency(query_engine, query_text, top_k=10)
        latencies.append(latency)
        
        # Calculate metrics
        # Recall@k: Did we retrieve at least one relevant doc in top-k?
        recall_at_1.append(1.0 if any(doc in relevant_docs for doc in retrieved_docs[:1]) else 0.0)
        recall_at_5.append(1.0 if any(doc in relevant_docs for doc in retrieved_docs[:5]) else 0.0)
        recall_at_10.append(1.0 if any(doc in relevant_docs for doc in retrieved_docs[:10]) else 0.0)
        
        # MRR: Reciprocal rank of first relevant document
        rr = 0.0
        for rank, doc in enumerate(retrieved_docs, 1):
            if doc in relevant_docs:
                rr = 1.0 / rank
                break
        reciprocal_ranks.append(rr)
    
    # 4. Aggregate metrics
    baseline_metrics = {
        "run_timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "language": "Hindi (हिंदी)",
        "total_queries": len(test_cases),
        "document_source": "evaluation/hi_test_data",
        "metrics": {
            "Recall@1": sum(recall_at_1) / len(recall_at_1),
            "Recall@5": sum(recall_at_5) / len(recall_at_5),
            "Recall@10": sum(recall_at_10) / len(recall_at_10),
            "MRR": sum(reciprocal_ranks) / len(reciprocal_ranks),
            "average_latency_ms": sum(latencies) / len(latencies)
        }
    }
    
    # 5. Save baseline
    output_path = Path(__file__).parent / "baseline_hi.json"
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(baseline_metrics, f, indent=4, ensure_ascii=False)
    
    print(f"\nHindi baseline captured successfully: {output_path}")
    print("\nMetrics:")
    print(json.dumps(baseline_metrics["metrics"], indent=4))
    
    # 6. Also print summary
    print("\n" + "="*60)
    print("MULTILINGUAL EVALUATION SUMMARY")
    print("="*60)
    print(f"Language: {baseline_metrics['language']}")
    print(f"Total Queries: {baseline_metrics['total_queries']}")
    print(f"Recall@1: {baseline_metrics['metrics']['Recall@1']:.2%}")
    print(f"Recall@5: {baseline_metrics['metrics']['Recall@5']:.2%}")
    print(f"Recall@10: {baseline_metrics['metrics']['Recall@10']:.2%}")
    print(f"MRR: {baseline_metrics['metrics']['MRR']:.4f}")
    print(f"Avg Latency: {baseline_metrics['metrics']['average_latency_ms']:.2f}ms")
    print("="*60)


if __name__ == "__main__":
    asyncio.run(main())

