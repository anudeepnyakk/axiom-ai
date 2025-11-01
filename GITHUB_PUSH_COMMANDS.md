# Quick GitHub Push Commands (PowerShell)

**Copy-paste these commands in order:**

---

## Step 1: Initialize Git

```powershell
cd "C:\Users\HP\Documents\Axiom AI"
git init
```

---

## Step 2: Verify .gitignore

```powershell
# Check what will be excluded
git status --short

# Should show many files, but NOT:
# - .env
# - chroma_db/
# - *.log
# - __pycache__/
```

---

## Step 3: Create GitHub Repository

**Go to browser**: https://github.com/new

- Name: `axiom-ai`
- Description: `Production-ready RAG system with multilingual support, enterprise security, and comprehensive observability`
- **Public** (recommended) or Private
- **DON'T** check "Initialize with README" (we have one)

Click **"Create repository"**

---

## Step 4: Add and Commit

```powershell
# Add all files (respects .gitignore)
git add .

# Create professional commit
git commit -m "feat: Complete Axiom AI - Production-ready RAG system

- Full RAG pipeline: ingestion, vector search, LLM synthesis
- Multilingual support (English + Hindi): 100% retrieval accuracy  
- Enterprise security: PII redaction, API auth, container hardening
- Production infrastructure: Docker, CI/CD, Prometheus metrics
- Performance: LRU cache (600K+ ops/sec), 50% cost reduction
- Fault tolerance: Retry logic, exponential backoff, degraded mode
- Comprehensive docs: 50,000+ words across architecture, security, evaluation"
```

---

## Step 5: Connect to GitHub

**Replace `YOUR_USERNAME` with your GitHub username:**

```powershell
# Connect to GitHub
git remote add origin https://github.com/YOUR_USERNAME/axiom-ai.git

# Set main branch
git branch -M main

# Push to GitHub
git push -u origin main
```

**If prompted for credentials:**
- Use GitHub Personal Access Token (not password)
- Generate token: https://github.com/settings/tokens
- Select scope: `repo` (full control)

---

## Step 6: Verify Success

1. **Go to**: https://github.com/YOUR_USERNAME/axiom-ai
2. **Check**:
   - ✅ All files are there
   - ✅ README displays correctly
   - ✅ No `.env` visible
   - ✅ No `chroma_db/` visible

---

## ✅ Security Check (Before Push)

```powershell
# Verify no secrets in code (should return nothing)
Select-String -Pattern "sk-[a-zA-Z0-9]{20,}" -Path "*.py","*.yaml","*.md" -Recurse
Select-String -Pattern "api_key.*=.*['\"].*['\"]" -Path "*.py" -Recurse | Where-Object { $_.Line -notmatch "example" -and $_.Line -notmatch "env" }
```

**If you see results**, remove secrets and use environment variables!

---

## 🎯 After Push: Add Repository Details

1. **Settings** → **General**
2. **Topics**: Add tags:
   - `rag`
   - `llm`
   - `vector-search`
   - `chromadb`
   - `streamlit`
   - `python`
   - `docker`
   - `production-ready`
   - `multilingual`
   - `ai`
   - `nlp`

---

## 🚨 Troubleshooting

### "Authentication failed"
- Use Personal Access Token instead of password
- Generate token: https://github.com/settings/tokens

### "Repository not found"
- Check repository name matches
- Verify you created the repo first

### "Large files detected"
- ChromaDB databases are excluded via .gitignore
- If issues persist, check file sizes: `git ls-files | ForEach-Object { Get-Item $_ | Select-Object Name, Length }`

---

**Ready?** Run Step 1-5! 🚀

