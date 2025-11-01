# Axiom AI - Evaluation Methodology

This document provides a comprehensive overview of how Axiom AI's retrieval-augmented generation (RAG) system is evaluated, what metrics are tracked, and how to interpret the results.

---

## Table of Contents

1. [Overview](#overview)
2. [Evaluation Framework](#evaluation-framework)
3. [Metrics](#metrics)
4. [Test Sets](#test-sets)
5. [Baseline Results](#baseline-results)
6. [Running Evaluations](#running-evaluations)
7. [Interpreting Results](#interpreting-results)
8. [Continuous Improvement](#continuous-improvement)

---

## Overview

### Why Evaluate?

RAG systems are complex with multiple failure modes:
- **Retrieval failures**: Relevant documents not found
- **Ranking failures**: Irrelevant documents ranked higher than relevant ones
- **Synthesis failures**: LLM generates incorrect or hallucinated answers

**Axiom AI uses a metrics-driven approach** to measure and improve each component.

### Evaluation Philosophy

1. **Retrieval-first**: Measure retrieval quality independently of LLM
2. **Multilingual**: Validate performance across languages (English, Hindi)
3. **Continuous**: Track metrics over time to detect regressions
4. **Fast**: Evaluation runs complete in <5 minutes

---

## Evaluation Framework

### Architecture

```
┌──────────────────────────────────────────────────┐
│           Evaluation Harness                      │
├──────────────────────────────────────────────────┤
│                                                   │
│  1. Load Test Set (JSONL)                        │
│     └─ {query, query_id, relevant_doc_ids}       │
│                                                   │
│  2. For each query:                               │
│     ├─ Embed query                                │
│     ├─ Search vector store (top_k)                │
│     └─ Record retrieved doc IDs                   │
│                                                   │
│  3. Compute Metrics:                              │
│     ├─ Recall@1, Recall@5, Recall@10             │
│     ├─ MRR (Mean Reciprocal Rank)                │
│     ├─ Precision@k                                │
│     ├─ NDCG (Normalized Discounted Cumulative Gain)
│     └─ Latency (query time)                      │
│                                                   │
│  4. Save Results (JSON)                           │
│     └─ Baseline for comparison                    │
└──────────────────────────────────────────────────┘
```

### Components

**Test Set** (`test_set.jsonl`):
```json
{"query_id": "q1", "query": "What is Axiom AI?", "relevant_doc_ids": ["doc1.txt"]}
{"query_id": "q2", "query": "How does RAG work?", "relevant_doc_ids": ["doc1.txt", "doc2.txt"]}
```

**Evaluation Script** (`evaluation/run_evaluation.py`):
- Loads test set
- Runs retrieval for each query
- Computes metrics
- Saves results

**Baseline** (`evaluation/baseline_en.json`, `evaluation/baseline_hi.json`):
- Reference results to detect regressions
- Captured after system optimization
- Re-run after major changes

---

## Metrics

### 1. Recall@k

**Definition**: Proportion of relevant documents retrieved in top-k results.

**Formula**:
```
Recall@k = |{relevant docs} ∩ {top k retrieved docs}| / |{relevant docs}|
```

**Example**:
- Query has 2 relevant docs: `[doc1, doc3]`
- Top 5 retrieved: `[doc1, doc2, doc3, doc4, doc5]`
- Recall@5 = 2/2 = 100%

**Interpretation**:
- **Recall@1 = 90%**: 90% of queries have at least 1 relevant doc in top 1
- **Recall@5 = 95%**: 95% of queries have at least 1 relevant doc in top 5
- **Recall@10 = 98%**: 98% of queries have at least 1 relevant doc in top 10

**Axiom AI Targets**:
- Recall@1: ≥85%
- Recall@5: ≥95%
- Recall@10: ≥98%

---

### 2. Mean Reciprocal Rank (MRR)

**Definition**: Average of reciprocal ranks of the first relevant document.

**Formula**:
```
MRR = (1/N) * Σ(1 / rank_i)
```
Where `rank_i` is the position of the first relevant doc for query `i`.

**Example**:
- Query 1: First relevant doc at rank 1 → 1/1 = 1.0
- Query 2: First relevant doc at rank 3 → 1/3 = 0.333
- Query 3: First relevant doc at rank 1 → 1/1 = 1.0
- MRR = (1.0 + 0.333 + 1.0) / 3 = 0.778

**Interpretation**:
- **MRR = 1.0**: Perfect - every query's first result is relevant
- **MRR = 0.5**: On average, first relevant doc is at rank 2
- **MRR = 0.1**: On average, first relevant doc is at rank 10

**Axiom AI Target**: MRR ≥0.85

---

### 3. Precision@k

**Definition**: Proportion of retrieved documents that are relevant.

**Formula**:
```
Precision@k = |{relevant docs} ∩ {top k retrieved docs}| / k
```

**Example**:
- Top 5 retrieved: `[doc1, doc2, doc3, doc4, doc5]`
- Relevant: `[doc1, doc3]`
- Precision@5 = 2/5 = 40%

**Interpretation**:
- **Precision@5 = 80%**: 4 out of 5 top results are relevant
- High precision = Less noise in results

**Axiom AI Target**: Precision@5 ≥60%

---

### 4. NDCG (Normalized Discounted Cumulative Gain)

**Definition**: Measures ranking quality, giving more weight to relevant docs at top positions.

**Formula**:
```
DCG@k = Σ(rel_i / log2(i + 1))  for i=1 to k
NDCG@k = DCG@k / IDCG@k
```
Where IDCG is the ideal DCG (perfect ranking).

**Interpretation**:
- **NDCG = 1.0**: Perfect ranking
- **NDCG = 0.8**: Good ranking, but some relevant docs pushed down
- **NDCG < 0.5**: Poor ranking

**Axiom AI Target**: NDCG@10 ≥0.8

---

### 5. Latency

**Definition**: Time taken to process a query (embedding + retrieval).

**Measured**:
- Average latency across all queries
- P50, P95, P99 latencies

**Example**:
```
Average: 150ms
P50: 120ms
P95: 250ms
P99: 400ms
```

**Interpretation**:
- **P50 (median)**: Half of queries complete in ≤120ms
- **P95**: 95% of queries complete in ≤250ms
- **P99**: 99% of queries complete in ≤400ms

**Axiom AI Targets**:
- Average latency: ≤200ms
- P95 latency: ≤300ms
- P99 latency: ≤500ms

---

## Test Sets

### English Test Set

**Location**: `evaluation/test_set.jsonl`

**Coverage**:
- 30-50 queries
- Factual questions ("What is X?")
- Conceptual questions ("How does X work?")
- Comparison questions ("What is the difference between X and Y?")

**Example**:
```json
{"query_id": "q1", "query": "What is the primary function of AxiomAI?", "relevant_doc_ids": ["eval_doc_1.txt"]}
{"query_id": "q2", "query": "How does the retrieval system work?", "relevant_doc_ids": ["eval_doc_1.txt"]}
```

### Hindi Test Set

**Location**: `evaluation/hi_test_set.jsonl`

**Coverage**:
- 30-50 Hindi queries
- Tests multilingual embedding model (`all-MiniLM-L6-v2`)
- Same document corpus as English (tests cross-lingual retrieval)

**Example**:
```json
{"query_id": "hi_q1", "query": "Axiom AI क्या है?", "relevant_doc_ids": ["hindi_doc_1.txt"]}
{"query_id": "hi_q2", "query": "RAG सिस्टम कैसे काम करता है?", "relevant_doc_ids": ["hindi_doc_1.txt"]}
```

---

## Baseline Results

### English Performance

**Configuration**:
- Embedding model: `all-MiniLM-L6-v2` (local, 384 dims)
- Vector store: ChromaDB
- Top-k: 5

**Metrics** (from `evaluation/baseline_en.json`):
```json
{
  "recall@1": 0.90,
  "recall@5": 0.97,
  "recall@10": 0.99,
  "mrr": 0.92,
  "precision@5": 0.65,
  "ndcg@10": 0.88,
  "avg_latency_ms": 145,
  "p95_latency_ms": 220,
  "p99_latency_ms": 350
}
```

**Analysis**:
- ✅ **Recall@5 = 97%**: Excellent retrieval coverage
- ✅ **MRR = 0.92**: Relevant docs almost always in top position
- ✅ **Latency < 200ms**: Fast enough for real-time use

---

### Hindi Performance

**Configuration**:
- Same as English (multilingual model)

**Metrics** (from `evaluation/baseline_hi.json`):
```json
{
  "recall@1": 0.85,
  "recall@5": 0.93,
  "recall@10": 0.97,
  "mrr": 0.87,
  "precision@5": 0.58,
  "ndcg@10": 0.82,
  "avg_latency_ms": 155,
  "p95_latency_ms": 240,
  "p99_latency_ms": 380
}
```

**Analysis**:
- ✅ **Recall@5 = 93%**: Strong cross-lingual retrieval
- ✅ **MRR = 0.87**: Good ranking quality
- ⚠️ **5-10% drop vs English**: Expected for cross-lingual (still good)

---

## Running Evaluations

### Prerequisites

```bash
# Install dependencies
pip install -r requirements.txt

# Ingest documents
python scripts/ingest.py
```

### Run English Evaluation

```bash
cd evaluation

# Run evaluation
python run_evaluation.py

# Capture baseline (after optimization)
python capture_baseline_en.py

# View results
cat baseline_en.json
```

### Run Hindi Evaluation

```bash
cd evaluation

# Ensure Hindi doc is ingested
python run_evaluation.py --test-set hi_test_set.jsonl

# Capture baseline
python capture_baseline_hi.py

# View results
cat baseline_hi.json
```

### Custom Evaluation

```python
from axiom.config.loader import load_config
from axiom.core.factory import create_query_engine
from evaluation.run_evaluation import run_retrieval_eval

# Load system
config = load_config()
query_engine = create_query_engine(config)

# Run custom test set
results = run_retrieval_eval(
    query_engine=query_engine,
    test_set_path="custom_test.jsonl",
    top_k=10
)

print(f"Recall@10: {results['recall@10']:.2%}")
print(f"MRR: {results['mrr']:.3f}")
```

---

## Interpreting Results

### Good Performance

```json
{
  "recall@5": 0.95,
  "mrr": 0.90,
  "avg_latency_ms": 150
}
```

**Interpretation**:
- **Recall@5 ≥95%**: Retrieval is working well
- **MRR ≥0.90**: Ranking is excellent
- **Latency ≤200ms**: Fast enough for production

**Action**: System is ready for deployment

---

### Degraded Performance

```json
{
  "recall@5": 0.70,
  "mrr": 0.60,
  "avg_latency_ms": 500
}
```

**Interpretation**:
- **Recall@5 = 70%**: Missing 30% of relevant docs
- **MRR = 0.60**: Poor ranking (relevant docs buried)
- **Latency = 500ms**: Too slow for real-time

**Potential Causes**:
1. **Low recall**: Poor embedding quality, chunking issues
2. **Low MRR**: Similarity metric mismatch, need reranking
3. **High latency**: Too many chunks, slow embedding model

**Actions**:
- Improve chunking strategy
- Try different embedding model
- Add reranking layer
- Optimize vector store indexing

---

### Regression Detection

**Scenario**: After a code change, recall drops from 95% to 85%.

**Steps**:
1. Run evaluation: `python run_evaluation.py`
2. Compare with baseline: `diff baseline_en.json results.json`
3. Identify root cause:
   - Changed embedding model?
   - Modified chunking?
   - Updated vector store config?
4. Revert or fix the change
5. Re-run evaluation to confirm fix

---

## Continuous Improvement

### Workflow

1. **Baseline**: Capture current performance
2. **Hypothesis**: "Changing chunk size will improve recall"
3. **Experiment**: Modify `config.yaml`, re-run ingestion
4. **Evaluate**: Run `run_evaluation.py`
5. **Compare**: Check if metrics improved
6. **Decision**:
   - **Improved**: Update baseline, commit changes
   - **Degraded**: Revert changes

### Tracking Over Time

```bash
# After each significant change
python evaluation/run_evaluation.py > results_$(date +%Y%m%d).json

# Compare historical results
python analysis/compare_results.py results_*.json
```

### A/B Testing

```python
# Test two configurations
config_a = load_config("config_a.yaml")
config_b = load_config("config_b.yaml")

results_a = run_evaluation(config_a, test_set)
results_b = run_evaluation(config_b, test_set)

# Statistical significance test
if results_b["recall@5"] > results_a["recall@5"] + 0.02:  # 2% improvement
    print("Config B is significantly better")
```

---

## Best Practices

### 1. Test Set Quality

✅ **Good Test Set**:
- Representative of real user queries
- Diverse question types
- Clear relevance judgments
- 30-50 queries minimum

❌ **Bad Test Set**:
- Too few queries (<10)
- All the same type
- Ambiguous relevance

### 2. Evaluation Frequency

- **After every major change**: Chunking, embedding model, vector store
- **Before each release**: Ensure no regressions
- **Weekly**: Track long-term trends

### 3. Metrics Balance

Don't optimize for a single metric:
- High recall but low precision = Too much noise
- High precision but low recall = Missing relevant docs
- Fast but inaccurate = Useless

**Aim for balanced improvement across all metrics.**

---

## Future Enhancements

### Planned Additions

1. **End-to-end evaluation**: Include LLM synthesis quality
2. **Human evaluation**: Manual relevance judgments
3. **Adversarial testing**: Intentionally hard queries
4. **Multilingual expansion**: Spanish, French, German
5. **Real-time dashboard**: Live metrics visualization

### Integration with CI/CD

Currently: Smoke test runs on every push (validates retrieval works)

**Future**: Full evaluation suite runs nightly, alerts on regressions

---

## References

### Academic Papers

- [BEIR: A Heterogeneous Benchmark for Zero-shot Evaluation of Information Retrieval Models](https://arxiv.org/abs/2104.08663)
- [Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks](https://arxiv.org/abs/2005.11401)

### Tools

- [pytrec_eval](https://github.com/cvangysel/pytrec_eval): Python implementation of trec_eval
- [BEIR](https://github.com/beir-cellar/beir): Benchmark for retrieval evaluation

---

## Support

For questions about evaluation:
1. Check this document
2. Review test sets in `evaluation/`
3. Run evaluation locally: `python evaluation/run_evaluation.py`
4. Compare with baselines in `evaluation/baseline_*.json`

---

*Evaluation is not just about numbers—it's about understanding your system and making it better, one metric at a time.* 📊

