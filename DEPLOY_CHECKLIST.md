# HuggingFace Spaces Deployment Checklist

## ✅ Pre-Deployment Checklist

Before deploying to HuggingFace Spaces, verify:

### Files Required
- [x] `app.py` at root (entry point)
- [x] `requirements-streamlit.txt` (or `requirements.txt`) with all dependencies
- [x] `README_SPACE.md` (optional but recommended)
- [x] `config.yaml` (configuration file)
- [x] `frontend/app.py` (Streamlit app)
- [x] `scripts/prepare_space.py` (sample document initialization)

### Code Verification
- [x] Frontend-backend integration working
- [x] Error handling in place
- [x] Sample documents script works
- [x] Environment variables documented

### Configuration
- [x] Config uses environment variables for API keys
- [x] Local embedding option available (for free demo)
- [x] Vector store persistence configured

## 🚀 Deployment Steps

### 1. Create Space
1. Go to https://huggingface.co/spaces
2. Click "Create new Space"
3. Select:
   - Name: `axiom-ai` (or your choice)
   - SDK: `Streamlit`
   - Visibility: Public/Private

### 2. Connect Repository
1. Connect your GitHub repository
2. Set root directory (if `app.py` is in subdirectory)

### 3. Set Environment Variables
In Space settings → Variables and secrets:
- `OPENAI_API_KEY`: Your OpenAI API key
- `EMBEDDING_PROVIDER`: `local` (optional, for offline embeddings)

### 4. Deploy
1. Push code to GitHub
2. Wait for build (5-10 minutes first time)
3. Visit Space URL

## 🔍 Post-Deployment Verification

### Check App Loads
- [ ] App loads without errors
- [ ] Backend status shows "Connected"
- [ ] Sample documents initialized

### Test Functionality
- [ ] Query works (test with sample questions)
- [ ] Document upload works
- [ ] Sources display correctly
- [ ] Error messages are user-friendly

### Monitor
- [ ] Check logs for errors
- [ ] Verify embeddings are generated
- [ ] Test multilingual queries (if applicable)

## 📝 Notes

- **First Load**: Takes 5-10 minutes (downloading models)
- **Subsequent Loads**: Faster (cached)
- **Sleep Mode**: Spaces sleep after 48h inactivity (wake on visit)
- **Storage**: 50GB limit on free tier

## 🐛 Troubleshooting

### Build Fails
- Check `requirements-streamlit.txt` has all dependencies
- Verify Python version compatibility
- Check build logs in Space settings

### App Crashes
- Check environment variables are set
- Verify `OPENAI_API_KEY` is valid
- Check logs for specific errors

### Empty Vector Store
- Sample docs should auto-initialize
- Check `scripts/prepare_space.py` runs correctly
- Verify config.yaml paths are correct

## ✨ Ready to Deploy!

Once all checks pass, you're ready to deploy!

**Next**: Follow the steps in `docs/DEPLOY_HF_SPACES.md`

