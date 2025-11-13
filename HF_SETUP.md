# HuggingFace Space Setup - Final Step

## ✅ What I Just Fixed

1. **Added CORS to Flask backend** - Railway will rebuild automatically
2. **Code already correct** - `app_hf.py` reads `BACKEND_URL` from environment

## 🎯 What YOU Need to Do (2 minutes)

### Step 1: Set Environment Variable on HuggingFace

1. Go to your Space: https://huggingface.co/spaces/anudeepp/axiom-ai
2. Click **"Settings"** tab (top right)
3. Scroll to **"Variables and secrets"** section
4. Click **"New variable"**
5. Add:
   ```
   Name:  BACKEND_URL
   Value: https://axiom-ai-production.up.railway.app
   ```
6. Click **"Save"**

### Step 2: Restart the Space

1. Go to **"Settings"** → **"Factory reboot"**
2. Click **"Reboot this Space"**

### Step 3: Test (Wait 2 minutes for rebuild)

1. Open your Space: https://huggingface.co/spaces/anudeepp/axiom-ai
2. You should see: **"Backend Connected ✅"** (green dot, top right)
3. Upload a PDF file
4. **Screen should NOT go blank** ✅
5. Ask a question → Get an answer

---

## 🔍 What Was Wrong

- **Before**: `BACKEND_URL` defaulted to `http://localhost:8000` on HuggingFace
- **Problem**: HuggingFace container can't reach Railway at "localhost"
- **Result**: All API calls failed → blank screen

- **Now**: `BACKEND_URL` points to Railway → API calls succeed → no crash

---

## ✅ Success Checklist

After setup, verify:

- [ ] Top right shows "Backend Connected" with green dot
- [ ] Upload PDF → progress bar → success message
- [ ] Screen stays stable (no blank)
- [ ] Ask question → get answer with sources
- [ ] Click "Sources" button → drawer opens

---

## 🚀 Once Working

Your system is **production-ready**:

- **Frontend**: https://huggingface.co/spaces/anudeepp/axiom-ai
- **Backend**: https://axiom-ai-production.up.railway.app

You can share the HuggingFace link in:
- Resume/portfolio
- LinkedIn posts
- Job applications
- Email outreach to recruiters

---

## ⚠️ If Still Issues

Check Railway logs for backend errors:
https://railway.app/project/your-project/service/axiom-ai

Check HuggingFace logs:
Your Space → "Logs" tab

Send me screenshots if needed.

