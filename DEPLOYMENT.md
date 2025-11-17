# Axiom AI - Production Deployment Guide

## 🎯 Architecture Overview

Axiom AI uses a **two-tier architecture** for maximum reliability and scalability:

```
┌──────────────────────┐         ┌────────────────────────┐
│   Frontend (HF)      │  API    │   Backend (Railway)    │
│   - Streamlit UI     │ ──────► │   - Flask REST API     │
│   - Stateless        │  HTTPS  │   - ChromaDB           │
│   - Zero storage     │         │   - Persistent disk    │
└──────────────────────┘         │   - Embeddings         │
                                 └────────────────────────┘
```

**Why this architecture?**
- ✅ Persistent storage for documents (Railway has real disk)
- ✅ No memory limits (Railway offers 2GB-8GB RAM plans)
- ✅ Scalable independently (upgrade backend without touching frontend)
- ✅ Professional deployment pattern (industry standard for RAG systems)
- ✅ Zero HuggingFace crashes (frontend is just HTML/JS rendering)

---

## 🚂 Step 1: Deploy Backend to Railway

### 1.1 Create Railway Account
- Go to [railway.app](https://railway.app)
- Sign in with GitHub

### 1.2 Deploy from GitHub
```bash
# Railway will auto-detect your Dockerfile and docker-compose
railway login
railway init
railway up
```

**Or use the Railway Dashboard:**
1. Click "New Project"
2. Select "Deploy from GitHub repo"
3. Choose `anudeepnyakk/axiom-ai`
4. Railway auto-detects the Dockerfile

### 1.3 Configure Environment Variables

In Railway Dashboard → Variables:

```bash
OPENAI_API_KEY=sk-your-key-here
PORT=5000
```

### 1.4 Get Your Backend URL

After deployment, Railway gives you a URL like:
```
https://axiom-ai-production.up.railway.app
```

**Save this URL** — you'll use it in Step 2.

### 1.5 Test Backend Endpoints

```bash
# Health check
curl https://your-railway-url.railway.app/health

# Should return:
# {"status":"healthy","service":"axiom-metrics","version":"1.0.0"}

# Test query endpoint
curl -X POST https://your-railway-url.railway.app/api/query \
  -H "Content-Type: application/json" \
  -d '{"question":"test","top_k":3}'
```

---

## 🤗 Step 2: Deploy Frontend to Hugging Face Spaces

### 2.1 Clone Your HF Space Locally

```bash
# Install git-lfs first (required for HF)
git lfs install

# Clone the Space repo
git clone https://huggingface.co/spaces/anudeepp/axiom-ai hf-axiom
cd hf-axiom
```

### 2.2 Copy Project Files

Copy these files/folders from your main project to `hf-axiom/`:

```bash
# Core files
cp ../axiom-ai/app_hf.py .
cp ../axiom-ai/streamlit_app.py .
cp ../axiom-ai/requirements.txt .
cp ../axiom-ai/config.yaml .
cp ../axiom-ai/README_SPACE.md ./README.md

# Frontend UI components
cp -r ../axiom-ai/frontend .

# Backend code (needed for imports, but won't run locally)
cp -r ../axiom-ai/axiom .

# Keep HF-specific files
# DO NOT overwrite: .gitattributes, .git/
```

### 2.3 Configure Space Settings

Edit the Space configuration in `README.md` header:

```yaml
---
title: Axiom AI
emoji: 🤖
colorFrom: blue
colorTo: purple
sdk: streamlit
sdk_version: "1.28.0"
app_file: streamlit_app.py
pinned: false
license: mit
---
```

### 2.4 Set Environment Variables in HF

Go to your Space → **Settings → Variables**:

```bash
BACKEND_URL=https://your-railway-url.railway.app
```

**⚠️ Critical:** Make sure this matches your Railway backend URL exactly (no trailing slash).

### 2.5 Push to Hugging Face

```bash
git add .
git commit -m "Deploy Axiom AI frontend with Railway backend"
git push
```

HuggingFace will automatically rebuild and deploy your Space.

---

## ✅ Step 3: Verify End-to-End

### 3.1 Check Frontend Loads

Open your Space: `https://huggingface.co/spaces/anudeepp/axiom-ai`

You should see:
- ✅ Green "Backend Connected" indicator in header
- ✅ Sidebar shows "📁 Ingestion" section
- ✅ No error messages

If you see "Backend Offline":
- Check `BACKEND_URL` is set correctly in HF Settings
- Verify Railway backend is running: `curl https://your-railway-url/health`
- Check Railway logs for errors

### 3.2 Test Document Upload

1. Click "Upload Document" in sidebar
2. Upload a small PDF (< 5MB)
3. Wait for "✅ Uploaded successfully" message
4. Refresh page (F5)
5. Document should appear in "View indexed documents"

### 3.3 Test Query

1. Go to "💬 Intelligence" tab
2. Type a question related to your uploaded document
3. Click "Send"
4. You should get:
   - ✅ An answer from GPT-4
   - ✅ Source citations below the answer
   - ✅ "Show Evidence" button to view retrieved chunks

---

## 🐛 Troubleshooting

### Frontend shows "Backend Offline"

**Cause:** Frontend can't reach Railway backend.

**Fix:**
1. Check `BACKEND_URL` in HF Space Settings → Variables
2. Verify Railway backend is deployed and running
3. Test backend health: `curl https://your-railway-url/health`
4. Check Railway logs for startup errors

### Upload fails with timeout

**Cause:** Railway backend is processing but taking too long.

**Fix:**
1. Increase timeout in `frontend/ui/sidebar.py`:
   ```python
   response = requests.post(f"{backend_url}/api/upload", files=files, timeout=120)  # increased from 60
   ```
2. Upgrade Railway plan for more CPU/RAM
3. Test upload locally first: `curl -F "file=@test.pdf" https://your-railway-url/api/upload`

### Query returns "error" instead of answer

**Cause:** OpenAI API key not set or invalid.

**Fix:**
1. Check Railway environment variables
2. Verify `OPENAI_API_KEY` is set correctly
3. Test key: `curl https://api.openai.com/v1/models -H "Authorization: Bearer $OPENAI_API_KEY"`

### Documents don't persist after Railway redeploy

**Cause:** ChromaDB writing to ephemeral disk.

**Fix:**
1. Railway provides persistent volumes
2. Update `config.yaml` to use absolute path:
   ```yaml
   vector_store:
     persist_directory: /app/data/chroma_db
   ```
3. Mount Railway volume at `/app/data`

---

## 📊 Monitoring

### Backend Health

Railway Dashboard shows:
- CPU usage
- Memory usage
- Request logs
- Error rates

Access metrics endpoint:
```bash
curl https://your-railway-url/metrics
```

### Frontend Health

HuggingFace shows:
- Container logs
- Uptime
- Visitor analytics

---

## 🚀 Next Steps

### Add Authentication
- Railway: Add API key middleware
- HF: Use Streamlit secrets for API key

### Scale Backend
- Railway: Upgrade to Pro plan (more RAM/CPU)
- Add Redis for caching query results
- Use PostgreSQL instead of ChromaDB for production scale

### Custom Domain
- Railway: Add custom domain in settings
- HF: Upgrade to Pro for custom domain

---

## 💡 Cost Estimate

**Free Tier (Suitable for portfolio/demo):**
- Railway: $5/month (500 hours, 512MB RAM)
- HuggingFace: Free (public Spaces)
- OpenAI: Pay-per-use (~$0.50/month for light testing)

**Total: ~$5.50/month**

**Production Tier (For real users):**
- Railway: $20/month (2GB RAM, always-on)
- HuggingFace: Free or $9/month (private + persistent storage)
- OpenAI: ~$50/month (moderate usage)

**Total: ~$70-80/month**

---

## 📝 Summary Checklist

- [ ] Railway backend deployed with persistent storage
- [ ] Railway `OPENAI_API_KEY` environment variable set
- [ ] Railway backend URL copied
- [ ] HuggingFace Space configured with `BACKEND_URL`
- [ ] HF Space shows "Backend Connected" status
- [ ] Test upload works end-to-end
- [ ] Test query returns GPT-4 answer with sources
- [ ] README updated with live demo links

---

**Questions? Issues?**
- Check Railway logs: `railway logs`
- Check HF logs: Space → Logs tab
- GitHub Issues: https://github.com/anudeepnyakk/axiom-ai/issues

