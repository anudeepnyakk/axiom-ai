"""
Axiom Evaluation Harness

This script runs an offline evaluation of the retrieval component of the RAG pipeline.
It takes a set of queries and their known relevant documents (ground truth) and
measures the performance of the retrieval system using standard information
retrieval metrics.

Usage:
    # Install dev dependencies
    pip install -r requirements-dev.txt

    # Run the evaluation
    python evaluation/run_evaluation.py

    # The results will be saved to evaluation/results.json
"""

import asyncio
import json
import sys
from pathlib import Path
from typing import Dict

# Add the project root to the Python path to allow importing from 'axiom'
sys.path.insert(0, str(Path(__file__).parent.parent))

import pytrec_eval  # type: ignore

from axiom.core.factory import create_query_engine
from axiom.config.loader import load_config
from axiom.core.query_engine import QueryEngine
from axiom.core.interfaces import DocumentChunk


def calculate_metrics(qrels: Dict, results: Dict) -> Dict:
    """
    Calculates retrieval metrics using pytrec_eval.

    Args:
        qrels: A dictionary mapping query_id to a dictionary of relevant doc_ids and their relevance scores.
               e.g., {'q1': {'doc1': 1, 'doc2': 1}}
        results: A dictionary mapping query_id to a dictionary of retrieved doc_ids and their retrieval scores.
                 e.g., {'q1': {'doc2': 0.98, 'doc3': 0.88}}

    Returns:
        A dictionary containing the calculated metrics.
    """
    evaluator = pytrec_eval.RelevanceEvaluator(qrels, {'map', 'ndcg_cut.5,10', 'recall.5,10'})
    metrics = evaluator.evaluate(results)
    
    # Aggregate metrics
    agg_metrics = {}
    for measure in sorted(list(metrics.values())[0].keys()):
        agg_metrics[measure] = pytrec_eval.compute_aggregated_measure(
            measure, [query_measures[measure] for query_measures in metrics.values()]
        )
    return agg_metrics


async def run_retrieval_for_query(query_engine: QueryEngine, query: str, top_k: int = 10) -> Dict[str, float]:
    """
    Runs a single query through the retrieval part of the query engine.

    Returns a dictionary of retrieved document paths and their scores.
    """
    question_embedding = await asyncio.to_thread(
        query_engine.embedding_generator.embed_batch,
        [DocumentChunk(text=query, metadata={})]
    )
    
    search_results = await asyncio.to_thread(
        query_engine.vector_store.query,
        query_vector=question_embedding[0],
        top_k=top_k
    )

    # We need to simulate scores as ChromaDB wrapper doesn't return them directly yet.
    # In a real scenario, this would come from the vector DB.
    retrieved_docs = {
        Path(chunk.metadata.get('source_file_path', '')).name: (1.0 - i * 0.1)
        for i, chunk in enumerate(search_results)
    }
    return retrieved_docs


async def main():
    """Main function to run the evaluation."""
    print("Starting Axiom retrieval evaluation...")

    # 1. Load configuration and create components
    config = load_config()
    query_engine = create_query_engine(config)

    # 2. Load the test set (qrels)
    test_set_path = Path(__file__).parent / "test_set.jsonl"
    qrels = {}
    queries = {}
    with open(test_set_path, "r") as f:
        for line in f:
            item = json.loads(line)
            query_id = item["query_id"]
            queries[query_id] = item["query"]
            qrels[query_id] = {doc_id: 1 for doc_id in item["relevant_doc_ids"]}

    # 3. Run retrieval for all queries
    print(f"Running retrieval for {len(queries)} queries...")
    results = {}
    for query_id, query_text in queries.items():
        print(f"  - Running query: {query_id}")
        results[query_id] = await run_retrieval_for_query(query_engine, query_text)

    # 4. Calculate metrics
    print("Calculating metrics...")
    metrics = calculate_metrics(qrels, results)

    # 5. Save results
    output_path = Path(__file__).parent / "results.json"
    output = {
        "metrics": metrics,
        "results_per_query": results
    }
    with open(output_path, "w") as f:
        json.dump(output, f, indent=4)

    print(f"\nEvaluation complete. Results saved to {output_path}")
    print("\nAggregated Metrics:")
    print(json.dumps(metrics, indent=4))


if __name__ == "__main__":
    asyncio.run(main())
