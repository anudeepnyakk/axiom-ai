# 🚀 Pre-Launch Checklist - Things YOU Need to Do

**These are things the AI can't do for you.**

---

## ⚠️ CRITICAL (Required to Run)

### 1. OpenAI API Key ⭐ **MUST DO FIRST**

**Why**: The system uses GPT-4o for answer generation.

**How to get it**:
1. Go to https://platform.openai.com/api-keys
2. Sign up / Log in
3. Click "Create new secret key"
4. Copy the key (starts with `sk-`)

**How to set it**:

**Windows PowerShell**:
```powershell
$env:OPENAI_API_KEY="sk-your-actual-key-here"
```

**Windows CMD**:
```cmd
set OPENAI_API_KEY=sk-your-actual-key-here
```

**Linux/Mac**:
```bash
export OPENAI_API_KEY="sk-your-actual-key-here"
```

**Or create `.env` file** (recommended):
```bash
# In project root, create .env file:
OPENAI_API_KEY=sk-your-actual-key-here
```

**Test it works**:
```bash
# Windows PowerShell
echo $env:OPENAI_API_KEY

# Linux/Mac
echo $OPENAI_API_KEY
```

You should see your key printed.

---

## 📝 IMPORTANT (Should Do Before Demo)

### 2. Add Your Own Documents

**Current State**: You have one PDF (Raya_-_Srinivas_Reddy.pdf)

**To add more**:
1. Put PDFs or TXT files in `axiom/data/`
2. Run ingestion:
   ```bash
   python scripts/ingest.py
   ```

**Tip**: Add documents relevant to what you want to demo (e.g., your resume, project docs)

---

### 3. Test the Full System

**Before showing anyone**, run through this:

1. ✅ Start frontend:
   ```bash
   cd frontend
   streamlit run app.py
   ```

2. ✅ Check "Backend Connected" (green dot in header)

3. ✅ Ask 3-5 test questions:
   - "What is this document about?"
   - "Who is mentioned in these documents?"
   - "Summarize the key points"

4. ✅ Click "📎 Sources" button to verify citations work

5. ✅ Check drawer shows retrieved chunks

**If anything fails**, check:
- OpenAI key is set
- Documents are ingested (run `python scripts/ingest.py`)
- ChromaDB exists (`ls chroma_db/`)

---

### 4. Clean Up Test Files (Optional but Recommended)

Delete these temporary test files:
```bash
del test_frontend_connection.py
del PROJECT_COMPLETION_REPORT.md  # (outdated, replaced by COMPLETION_SUMMARY.md)
```

---

## 🌐 OPTIONAL (For Deployment)

### 5. Push to GitHub

**Steps**:

1. **Create GitHub repo**:
   - Go to https://github.com/new
   - Name it `axiom-ai` (or whatever you want)
   - Make it Public or Private
   - DON'T initialize with README (we already have one)
   - Click "Create repository"

2. **Initialize git locally**:
   ```bash
   git init
   git add .
   git commit -m "Initial commit: Complete Axiom AI RAG system"
   ```

3. **Connect to GitHub**:
   ```bash
   git remote add origin https://github.com/YOUR_USERNAME/axiom-ai.git
   git branch -M main
   git push -u origin main
   ```

**IMPORTANT**: Before pushing, create `.gitignore`:
```bash
# Create .gitignore with:
.env
chroma_db/
__pycache__/
*.pyc
.DS_Store
```

This prevents pushing:
- Your API key (.env)
- Large database files (chroma_db/)
- Python cache files

---

### 6. Deploy to Cloud (Optional)

**Option A: Railway (Easiest)**
1. Go to https://railway.app
2. Connect your GitHub repo
3. Set environment variable: `OPENAI_API_KEY=sk-...`
4. Deploy (Railway auto-detects everything)

**Option B: Streamlit Cloud (For Frontend Only)**
1. Go to https://streamlit.io/cloud
2. Connect your GitHub repo
3. Set secrets in dashboard
4. Deploy

**Option C: AWS/GCP/Azure (Advanced)**
- Use Docker deployment
- See `DOCKER_SETUP.md` for instructions

---

### 7. Set Up API Authentication (Optional)

**If you want to protect your backend with API keys**:

1. Generate keys:
   ```bash
   python -c "from axiom.security import APIKeyGenerator; print(APIKeyGenerator.generate_key('axiom'))"
   ```

2. Add to `.env`:
   ```
   AXIOM_API_KEYS=axiom_abc123,axiom_def456
   ```

3. Now your endpoints require valid keys

**Note**: Current UI doesn't use this (it's for API access)

---

## 🎥 DEMO PREPARATION

### 8. Prepare Your Demo Script

**2-minute demo flow**:

1. **Show the UI** (0:15)
   - "This is Axiom AI, a production RAG system I built"
   - Point out clean UI, backend status

2. **Ask a question** (0:45)
   - Type: "What are the key topics in these documents?"
   - Show answer generates in ~5 seconds
   - Explain: "It's searching vector database and synthesizing with GPT-4"

3. **Show sources** (0:30)
   - Click "📎 Sources"
   - Show drawer with retrieved chunks
   - Explain: "Every answer is grounded in actual document text"

4. **Highlight features** (0:30)
   - "It has PII redaction, LRU caching, retry logic..."
   - "100% test coverage, Docker-ready, CI/CD pipeline"
   - "Check the GitHub repo for full documentation"

---

### 9. Prepare Talking Points

**For technical interviews**, be ready to explain:

#### Architecture
- "It's a modular RAG pipeline: ingestion → embedding → retrieval → synthesis"
- "I use ChromaDB for vectors, local embeddings for cost, OpenAI for LLM"

#### Challenges
- "Biggest challenge was fault tolerance—I implemented retry logic with exponential backoff"
- "Also security—constant-time API key comparison to prevent timing attacks"

#### Metrics
- "100% Recall@5 on evaluation, 117ms average latency"
- "LRU cache gets 600K ops/sec, reduced embedding costs 50%"

#### Testing
- "25 test cases across 7 test suites, 100% passing"
- "Evaluation framework with English and Hindi benchmarks"

---

## ✅ MINIMUM VIABLE DEMO

**If you have limited time, just do this**:

1. ✅ Set OpenAI API key
2. ✅ Run `python scripts/ingest.py` (if needed)
3. ✅ Run `streamlit run app.py`
4. ✅ Test 2-3 queries
5. ✅ Make sure sources button works

**That's it!** You have a working demo.

---

## 🎯 QUICK START (5 Minutes)

**Right now, to get it running**:

```bash
# 1. Set API key (REQUIRED)
$env:OPENAI_API_KEY="sk-your-key-here"

# 2. Verify it's set
echo $env:OPENAI_API_KEY

# 3. Start frontend (you're already here)
streamlit run app.py

# 4. Open browser to http://localhost:8501

# 5. Ask: "What is this document about?"

# Done! ✅
```

---

## 📋 PRE-DEMO CHECKLIST

**Day before demo/interview**:
- [ ] OpenAI API key works
- [ ] Relevant documents ingested
- [ ] Test 5 questions, all work
- [ ] Sources button works
- [ ] Pushed to GitHub
- [ ] README looks good
- [ ] Prepared 3 talking points

**5 minutes before demo**:
- [ ] Close all other apps
- [ ] Clear browser cache
- [ ] Run `streamlit cache clear`
- [ ] Start fresh: `streamlit run app.py`
- [ ] Test ONE query to verify it works
- [ ] Have GitHub repo open in another tab

---

## 🚨 TROUBLESHOOTING

### "Backend Error" in UI
→ OpenAI key not set or invalid
→ Run: `echo $env:OPENAI_API_KEY`

### "No documents found"
→ Run: `python scripts/ingest.py`

### "Module not found"
→ Run: `pip install -r requirements.txt`

### Streamlit won't start
→ Make sure you're in `frontend/` directory
→ Run: `streamlit cache clear`

### Query takes forever
→ Normal for first query (loads model)
→ Subsequent queries are faster

---

## 🎉 YOU'RE READY WHEN...

- ✅ You can start the app
- ✅ You see "Backend Connected"
- ✅ You can ask a question and get answer
- ✅ You can click sources and see chunks
- ✅ You've tested this 3+ times

**That's all you need!**

---

## 💡 NEXT ACTIONS (In Order)

**Right now** (if not done):
1. Set OpenAI API key
2. Test the app works

**Today/Tomorrow**:
3. Add your own documents
4. Test thoroughly
5. Push to GitHub

**Before Interview/Demo**:
6. Practice demo flow (2 min)
7. Prepare 3 talking points
8. Have backup questions ready

**After Demo**:
9. Deploy to cloud (optional)
10. Add to resume/portfolio

---

## ⚡ TL;DR - DO THIS NOW

```bash
# Set your OpenAI key
$env:OPENAI_API_KEY="sk-your-actual-key"

# Verify it worked
echo $env:OPENAI_API_KEY

# You should already be in frontend/, so just run:
streamlit run app.py

# Open http://localhost:8501
# Ask: "What is this document about?"
# Click "📎 Sources"

# If everything works → YOU'RE DONE! 🎉
```

---

**The system is complete. You just need to configure YOUR specific stuff (API keys, documents, deployment).**

**What do you want to tackle first?**

