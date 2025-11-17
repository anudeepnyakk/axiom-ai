# 🚀 IMMEDIATE ACTION REQUIRED - Deploy Axiom AI (Permanent Solution)

## What You're About to Do

You'll deploy Axiom AI as **two separate services**:
1. **Backend on Railway** (already set up, just needs verification)
2. **Frontend on HuggingFace** (needs code sync)

**Time required:** 10-15 minutes  
**Result:** Rock-solid, production-ready RAG system that will never crash

---

## Step 1: Verify Your Railway Backend (5 minutes)

### 1.1 Check if Railway is Running

Open your Railway dashboard: https://railway.app/dashboard

Find your `axiom-ai` project. It should show "Active" status.

### 1.2 Get Your Backend URL

In Railway dashboard:
- Click your project
- Click "Settings" tab
- Look for "Domains" section
- Copy the URL (looks like: `https://axiom-ai-production-xxxx.up.railway.app`)

**⚠️ SAVE THIS URL - YOU NEED IT IN STEP 2**

### 1.3 Test Backend is Working

Open a new browser tab and visit:
```
https://your-railway-url.railway.app/health
```

You should see:
```json
{"status":"healthy","service":"axiom-metrics","version":"1.0.0"}
```

✅ If you see this → Railway backend is working! Proceed to Step 2.

❌ If you see error → Railway needs to be deployed first. Run:
```bash
cd "C:\Users\HP\Documents\Axiom AI"
railway login
railway up
```

---

## Step 2: Push Latest Code to HuggingFace (5 minutes)

### 2.1 Clone Your HuggingFace Space

```powershell
cd C:\Users\HP\Documents
git clone https://huggingface.co/spaces/anudeepp/axiom-ai hf-axiom
```

### 2.2 Copy Latest Files from Main Project

```powershell
# Copy essential files
Copy-Item "Axiom AI\app_hf.py" "hf-axiom\" -Force
Copy-Item "Axiom AI\streamlit_app.py" "hf-axiom\" -Force
Copy-Item "Axiom AI\config.yaml" "hf-axiom\" -Force
Copy-Item "Axiom AI\README_SPACE.md" "hf-axiom\README.md" -Force

# Copy frontend folder
Copy-Item "Axiom AI\frontend" "hf-axiom\" -Recurse -Force

# Copy backend code (needed for imports only)
Copy-Item "Axiom AI\axiom" "hf-axiom\" -Recurse -Force
```

### 2.3 Update README.md Header

Open `hf-axiom\README.md` in a text editor.

Make sure the YAML header at the top looks like this:

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

### 2.4 Push to HuggingFace

```powershell
cd hf-axiom
git add .
git commit -m "Deploy production-ready frontend with Railway backend"
git push
```

HuggingFace will start rebuilding your Space (takes 2-3 minutes).

---

## Step 3: Configure BACKEND_URL in HuggingFace (2 minutes)

### 3.1 Open Space Settings

Go to: https://huggingface.co/spaces/anudeepp/axiom-ai

Click: **Settings** tab (top right)

### 3.2 Set Environment Variable

Scroll down to "Repository secrets" or "Variables" section.

Click "New secret" or "Add variable"

**Name:** `BACKEND_URL`  
**Value:** `https://your-railway-url.railway.app` (from Step 1.2)

**⚠️ IMPORTANT:** 
- No trailing slash `/` at the end
- Must start with `https://`
- Must match your Railway URL exactly

Click "Save"

### 3.3 Restart Space

Scroll to bottom of Settings page.

Click **"Factory reboot"** button.

Wait 2-3 minutes for rebuild.

---

## Step 4: Test Everything Works (3 minutes)

### 4.1 Open Your Space

Go to: https://huggingface.co/spaces/anudeepp/axiom-ai

You should see:
- ✅ Green dot + "Backend Connected" in header
- ✅ Sidebar with "📁 Ingestion" section
- ✅ No error messages

### 4.2 Test Upload

1. Click "Upload Document" in sidebar
2. Upload a small PDF (any PDF, < 5MB)
3. Wait for progress bar to reach 100%
4. You should see: "✅ filename.pdf uploaded (X chunks)"
5. Refresh page (F5)
6. Document appears in "View indexed documents"

**✅ If upload works → SUCCESS! You're done!**

**❌ If upload fails:**
- Check Railway logs: `railway logs`
- Check HF logs: Space → Logs tab (Container)
- Verify `BACKEND_URL` is set correctly in HF Settings

### 4.3 Test Query

1. Go to "💬 Intelligence" tab
2. Ask a question about your uploaded document
3. You should get:
   - An answer from GPT-4
   - Source citations
   - "Show Evidence" button

**✅ If query works → COMPLETE SUCCESS!**

---

## ✅ Checklist (Mark as you go)

- [ ] Railway backend URL copied
- [ ] Railway `/health` returns {"status":"healthy"}
- [ ] HF Space cloned to local folder
- [ ] Latest code copied to HF folder
- [ ] README.md header updated
- [ ] Code pushed to HF Space
- [ ] `BACKEND_URL` set in HF Settings
- [ ] Space factory rebooted
- [ ] Frontend shows "Backend Connected"
- [ ] PDF upload works
- [ ] Query returns answer with sources

---

## 🐛 If Something Goes Wrong

### Problem: Can't clone HF Space

**Solution:**
```powershell
# Install git-lfs first
git lfs install
# Then try clone again
git clone https://huggingface.co/spaces/anudeepp/axiom-ai hf-axiom
```

### Problem: Railway backend shows 503 error

**Solution:**
Railway needs to be deployed:
```powershell
cd "C:\Users\HP\Documents\Axiom AI"
railway login
railway up
```

### Problem: HF shows "Backend Offline"

**Solution:**
1. Check `BACKEND_URL` in HF Settings → exactly matches Railway URL
2. Factory reboot the Space
3. Wait 3 minutes for full rebuild

### Problem: Upload times out

**Solution:**
1. Try a smaller PDF (< 1MB)
2. Check Railway logs for errors: `railway logs`
3. Verify OpenAI API key is set in Railway

---

## 🎉 When Everything Works

You now have a **production-grade RAG system** that:
- ✅ Never crashes on file uploads
- ✅ Persists documents forever (Railway disk storage)
- ✅ Scales independently (upgrade Railway without touching HF)
- ✅ Shows backend health status in real-time
- ✅ Professional architecture for interviews

**Next:** Update your resume/portfolio with the live demo link!

---

**Questions?** Open the full guide: `DEPLOYMENT.md`

