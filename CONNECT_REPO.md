# 🔗 Connect GitHub Repository to HuggingFace Space

## Steps to Connect Your Repo

### Method 1: Via Space Settings

1. **Go to your Space**: https://huggingface.co/spaces/anudeepp/axiom-ai

2. **Click "Settings"** tab (top navigation)

3. **Scroll to "Repository" section**

4. **Connect GitHub**:
   - Click "Connect to GitHub" or "Add repository"
   - Authorize HuggingFace if needed
   - Select repository: `anudeepnyakk/axiom-ai`
   - Select branch: `main`
   - Root directory: Leave blank (or `/`)

5. **Save** - Space will auto-rebuild

### Method 2: Manual Git Push (Alternative)

If you prefer to push directly:

1. **Go to Space → Settings → Repository**
2. **Copy the Space's Git URL** (if available)
3. **Add as remote**:
   ```bash
   git remote add huggingface https://huggingface.co/spaces/anudeepp/axiom-ai
   git push huggingface main
   ```

### What Happens After Connection

1. ✅ HuggingFace pulls your code from GitHub
2. ✅ Detects `Dockerfile` or `streamlit_app.py`
3. ✅ Builds and deploys automatically
4. ✅ Your Axiom AI app loads (not default template)

### Verify It's Connected

After connecting, check:
- **Files tab** should show your actual files (not just template files)
- **Logs tab** shows build progress
- **App tab** shows your Axiom AI interface

---

**Quick Link**: https://huggingface.co/spaces/anudeepp/axiom-ai/settings

