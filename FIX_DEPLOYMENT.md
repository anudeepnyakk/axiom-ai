# 🔧 Fix: Show Axiom AI App Instead of Default Template

## Problem
Your Space is running but showing the default Streamlit template instead of Axiom AI.

## Solution

### Option 1: Update Dockerfile (Recommended)

I've created `streamlit_app.py` and updated the Dockerfile. Now:

1. **Commit and push** these changes to your GitHub repository:
   ```bash
   git add streamlit_app.py Dockerfile
   git commit -m "Fix: Use streamlit_app.py for HuggingFace Spaces"
   git push
   ```

2. **Rebuild** your Space:
   - Go to your Space settings
   - Click "Restart" or wait for auto-rebuild
   - Check logs to see if it's using the correct file

### Option 2: Manual Fix in HuggingFace Spaces

If the Dockerfile isn't being used:

1. Go to your Space → **Files** tab
2. Check if `streamlit_app.py` exists
3. If not, create it with this content:
   ```python
   from app import *
   ```

4. Or edit the Dockerfile in the Space directly:
   - Change the CMD to: `streamlit run streamlit_app.py --server.port=7860 --server.address=0.0.0.0 --server.headless=true`

### Option 3: Verify Repository Connection

1. Space Settings → **Repository**
2. Verify your GitHub repo is connected
3. Check the branch/path is correct
4. Click "Rebuild" if needed

## What Should Happen

After fixing:
- ✅ Axiom AI interface loads (not default template)
- ✅ Shows "AXIOM" header with "Grounded intelligence" tagline
- ✅ Backend status indicator
- ✅ Chat interface
- ✅ Sample documents auto-loaded

## Debug Steps

1. **Check Logs**: Space → **Logs** tab
   - Look for "📚 Initializing sample documents"
   - Check for any import errors

2. **Check Files**: Space → **Files** tab
   - Verify `app.py` exists
   - Verify `streamlit_app.py` exists
   - Verify `frontend/app.py` exists

3. **Verify Dockerfile**: Check CMD line matches:
   ```dockerfile
   CMD streamlit run streamlit_app.py --server.port=7860 --server.address=0.0.0.0 --server.headless=true
   ```

## Quick Fix Commands

If you have SSH access or can run commands:

```bash
# Check what's running
ps aux | grep streamlit

# Check if streamlit_app.py exists
ls -la streamlit_app.py

# Check Dockerfile
cat Dockerfile | grep CMD
```

---

**After fixing**: Your Space should show the Axiom AI interface, not the default template!

