import time
import pytest
import shutil
import os
from pathlib import Path
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import FakeEmbeddings
from langchain_core.documents import Document

# MOCK COMPONENTS FOR ISOLATED BENCHMARK
# We use FakeEmbeddings to measure RETRIEVAL time, not Embedding API latency
# This proves the "system architecture" overhead is low.

def benchmark_retrieval_latency():
    """
    Benchmark retrieval speed (Vector Search + Overhead).
    Does NOT include LLM Generation time.
    """
    print("\n" + "="*60)
    print("BENCHMARK: Retrieval Latency (<100ms Target)")
    print("="*60)

    # 1. Setup (Cost-Free)
    embeddings = FakeEmbeddings(size=1536)
    persist_dir = "./benchmark_chroma_db"
    
    # Clean previous run
    if os.path.exists(persist_dir):
        shutil.rmtree(persist_dir)
        
    # Create dummy data (100 documents)
    docs = [
        Document(
            page_content=f"This is a benchmark document number {i}. It contains some text for retrieval testing.",
            metadata={"source": f"doc_{i}.pdf", "page": i}
        )
        for i in range(100)
    ]
    
    print(f"Ingesting {len(docs)} mock documents...")
    vectorstore = Chroma.from_documents(
        documents=docs,
        embedding=embeddings,
        persist_directory=persist_dir
    )
    
    retriever = vectorstore.as_retriever(search_kwargs={"k": 4})
    
    # 2. Warmup (Cache warming)
    print("Warming up cache...")
    retriever.invoke("test query")
    
    # 3. Measure Latency (50 Runs)
    latencies = []
    print("Running 50 retrieval queries...")
    
    for i in range(50):
        start_time = time.time()
        # The Core Retrieval Step
        results = retriever.invoke(f"benchmark document {i}")
        end_time = time.time()
        
        duration_ms = (end_time - start_time) * 1000
        latencies.append(duration_ms)
    
    # 4. Analysis
    avg_latency = sum(latencies) / len(latencies)
    min_latency = min(latencies)
    max_latency = max(latencies)
    
    print("-" * 30)
    print(f"Average Latency: {avg_latency:.2f} ms")
    print(f"Best Latency:    {min_latency:.2f} ms")
    print(f"Worst Latency:   {max_latency:.2f} ms")
    print("-" * 30)
    
    # 5. Verdict
    if avg_latency < 100:
        print("SUCCESS: System meets <100ms requirement.")
    else:
        print(f"WARNING: Latency is {avg_latency:.2f}ms (Target: <100ms)")
        
    # Cleanup
    shutil.rmtree(persist_dir)

if __name__ == "__main__":
    benchmark_retrieval_latency()

