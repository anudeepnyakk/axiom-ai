# ⚡ SETUP NOW - 3 Steps to Working Demo

**You need to do this BEFORE the UI will work:**

---

## Step 1: Get OpenAI API Key (2 min)

**Don't have one?**

1. Go to: https://platform.openai.com/api-keys
2. Sign up or log in
3. Click **"Create new secret key"**
4. **Copy the key** (starts with `sk-`)
5. Save it somewhere safe (you can't see it again)

**Cost**: ~$0.01 per query (very cheap for testing)

---

## Step 2: Set the API Key in Your Terminal

**Copy this command and replace `sk-your-key` with YOUR actual key:**

```powershell
$env:OPENAI_API_KEY="sk-your-actual-key-here"
```

**Then verify it's set:**
```powershell
echo $env:OPENAI_API_KEY
```

You should see your key printed.

---

## Step 3: Restart Streamlit

**You're already in `frontend/` directory, so:**

```powershell
# Stop the current Streamlit (Ctrl+C)
# Then restart:
streamlit run app.py
```

**Open**: http://localhost:8501

---

## ✅ How to Know It's Working

1. **Header shows**: "Backend Connected" (green dot)
2. **Ask**: "What is this document about?"
3. **You get**: A real AI-generated answer (takes ~5 seconds)
4. **Click**: "📎 Sources" to see retrieved documents

---

## 🚨 If It's Still Not Working

### Error: "Backend Error"
**Problem**: API key not set or wrong  
**Fix**: 
```powershell
echo $env:OPENAI_API_KEY  # Should show your key
```

### Error: "Invalid API key"
**Problem**: Wrong key or expired  
**Fix**: Get a new key from https://platform.openai.com/api-keys

### Error: "Insufficient quota"
**Problem**: Need to add billing to OpenAI account  
**Fix**: Add payment method at https://platform.openai.com/billing

---

## 💡 Alternative: Use .env File (Permanent)

**Instead of setting in terminal each time:**

1. Create file `.env` in project root
2. Add this line:
   ```
   OPENAI_API_KEY=sk-your-actual-key-here
   ```
3. Restart Streamlit

The key will be loaded automatically!

---

## 🎯 Quick Check

**Open your PowerShell where Streamlit is running.**

**Is the API key set?**
- [ ] YES → Restart Streamlit → Should work!
- [ ] NO → Set it with `$env:OPENAI_API_KEY="sk-..."`

---

## 📞 Ready to Test?

Once you've set the key and restarted:

1. Visit http://localhost:8501
2. See green "Backend Connected"
3. Ask a question
4. Get answer
5. **You're done!** 🎉

---

**The code is perfect. You just need YOUR OpenAI key.** 🔑

