# Axiom AI - Quick Start Guide

## 🚀 Get Running in 3 Steps

### Prerequisites
- Python 3.11+
- OpenAI API key

---

## Step 1: Install Dependencies (2 min)

```bash
# Install all requirements
pip install -r requirements.txt
```

---

## Step 2: Configure (1 min)

Create a `.env` file in the project root:

```bash
# Copy example
cp env.example .env

# Edit .env and add your OpenAI key
OPENAI_API_KEY=sk-your-key-here
```

Or set environment variable directly:
```bash
# Windows PowerShell
$env:OPENAI_API_KEY="sk-your-key-here"

# Linux/Mac
export OPENAI_API_KEY="sk-your-key-here"
```

---

## Step 3: Ingest Documents & Run (5 min)

### Ingest Documents
```bash
# Add your documents to axiom/data/
# Then run ingestion
python scripts/ingest.py
```

### Run Frontend
```bash
cd frontend
streamlit run app.py
```

The UI will open at `http://localhost:8501`

---

## ✅ Verify It Works

1. **Frontend loads** → You see "Backend Connected" in green
2. **Ask a question** → Type in chat and hit Send
3. **Get answer** → See AI-generated response
4. **Check sources** → Click "📎 Sources" to see retrieved documents

---

## 🐳 Alternative: Run with Docker

```bash
# Set your OpenAI key in .env first
docker-compose up -d

# Access at http://localhost:8501
```

---

## 🧪 Run Tests

```bash
# Test PII redaction
python scripts/test_pii_redaction.py

# Test API auth
python scripts/test_api_auth.py

# Test LRU cache
python scripts/test_lru_cache.py

# All should show: ✅ ALL TESTS PASSED!
```

---

## 📊 Check Metrics

Start metrics server:
```bash
python scripts/start_metrics_server.py
```

View metrics:
```
http://localhost:5000/metrics  # Prometheus format
http://localhost:5000/health   # Health check
```

---

## 🔧 Troubleshooting

### "Backend Error" in UI
**Problem**: Documents not ingested  
**Solution**: Run `python scripts/ingest.py`

### "ModuleNotFoundError"
**Problem**: Missing dependencies  
**Solution**: `pip install -r requirements.txt`

### "No API key"
**Problem**: OpenAI key not set  
**Solution**: Set `OPENAI_API_KEY` environment variable

### "ChromaDB error"
**Problem**: Database corrupt  
**Solution**: Delete `chroma_db/` and re-run ingestion

---

## 📚 Next Steps

- Read `docs/architecture.md` for system design
- Read `docs/EVAL.md` for evaluation details
- Read `docs/SECURITY.md` for security features
- Check `docs/DAY*_CHECKLIST.md` for implementation details

---

## 🎯 You're Ready!

Your RAG system is now running with:
- ✅ Document ingestion
- ✅ Vector search
- ✅ LLM synthesis  
- ✅ Beautiful UI
- ✅ Source citations
- ✅ Security (PII redaction, API auth)
- ✅ Performance (LRU cache)
- ✅ Observability (metrics, logs)

**Ask questions and watch it work!** 🚀

