# HuggingFace Spaces Deployment Guide

This guide walks you through deploying Axiom AI to HuggingFace Spaces.

## Prerequisites

1. **HuggingFace Account**: Sign up at https://huggingface.co
2. **GitHub Repository**: Your code should be on GitHub
3. **OpenAI API Key**: For LLM synthesis (optional if using local embeddings only)

## Quick Deploy (5 minutes)

### Step 1: Create New Space

1. Go to https://huggingface.co/spaces
2. Click "Create new Space"
3. Fill in:
   - **Space name**: `axiom-ai` (or your choice)
   - **SDK**: Select `Streamlit`
   - **Visibility**: Public (for demo) or Private
   - Click "Create Space"

### Step 2: Configure Space

1. In your Space settings, go to "Repository" tab
2. Connect your GitHub repository
3. Set the **Root directory** to your repo root (or leave blank if `app.py` is at root)

### Step 3: Set Environment Variables

In Space settings → "Variables and secrets", add:

- `OPENAI_API_KEY`: Your OpenAI API key (required for LLM synthesis)
- `EMBEDDING_PROVIDER`: Set to `local` for offline embeddings (optional)
- `EMBEDDING_MODEL`: Model name (optional, defaults to all-MiniLM-L6-v2)

### Step 4: Update Requirements

Ensure your `requirements-streamlit.txt` or `requirements.txt` includes:

```
streamlit>=1.28.0
sentence-transformers>=2.7.0
chromadb<0.5
openai<2.0.0
...
```

### Step 5: Deploy

1. Push your code to GitHub
2. HuggingFace Spaces will automatically build and deploy
3. Wait 5-10 minutes for first build
4. Visit your Space URL: `https://huggingface.co/spaces/YOUR_USERNAME/axiom-ai`

## Files Required

Your repository should have:

```
.
├── app.py                    # Entry point (imports frontend/app.py)
├── requirements-streamlit.txt # Dependencies
├── README_SPACE.md           # Space README (optional)
├── config.yaml               # Configuration
├── frontend/
│   └── app.py               # Streamlit app
├── axiom/                    # Backend code
└── scripts/
    └── prepare_space.py      # Sample document initialization
```

## Auto-Initialization

The `app.py` entry point automatically:
1. Checks if vector store is empty
2. If empty, loads sample documents from `scripts/prepare_space.py`
3. Initializes embeddings (using local or OpenAI)

Users can then:
- Query immediately with sample documents
- Upload their own documents via the sidebar

## Configuration for Spaces

### Local Embeddings (Recommended for Demo)

Set environment variable:
```bash
EMBEDDING_PROVIDER=local
```

This uses `sentence-transformers` models (no API key needed for embeddings).

### OpenAI Embeddings (Better Quality)

Set environment variable:
```bash
OPENAI_API_KEY=sk-your-key
EMBEDDING_PROVIDER=openai  # Optional, defaults to local if not set
```

## Customization

### Change Sample Documents

Edit `scripts/prepare_space.py` to customize the demo documents.

### Modify UI

Edit `frontend/ui/*.py` files to customize the Streamlit interface.

### Update Config

Edit `config.yaml` to change:
- Chunk size/overlap
- Embedding model
- Vector store settings

## Troubleshooting

### Build Fails

- Check `requirements-streamlit.txt` for all dependencies
- Ensure Python version is compatible (3.8+)
- Check build logs in Space settings

### App Crashes on Load

- Check environment variables are set
- Verify `OPENAI_API_KEY` is valid (if using OpenAI)
- Check logs: Space → "Logs" tab

### Empty Vector Store

- Sample documents should auto-initialize
- If not, users can upload documents via sidebar
- Check `scripts/prepare_space.py` runs correctly

### Slow Performance

- First load takes time (downloading models)
- Subsequent loads are faster (cached)
- Consider using smaller embedding models for faster startup

## Monitoring

- **Logs**: View in Space → "Logs" tab
- **Metrics**: Check Streamlit analytics
- **Usage**: Monitor in Space dashboard

## Security Notes

- **Never commit API keys** to repository
- Use Space secrets for sensitive data
- PII redaction is enabled by default
- Vector store is isolated per Space instance

## Cost Considerations

### Free Tier Limits

- **CPU**: 2 vCPU
- **RAM**: 16GB
- **Storage**: 50GB
- **Sleep**: Spaces sleep after 48h inactivity (wake on visit)

### Optimizations

- Use local embeddings (free, no API costs)
- Cache embeddings (persistent storage)
- Optimize chunk size for faster queries

## Next Steps

1. **Customize**: Add your own documents
2. **Monitor**: Track usage and performance
3. **Share**: Get feedback from users
4. **Iterate**: Improve based on usage patterns

## Support

- **Documentation**: See `/docs` folder
- **Issues**: Report on GitHub
- **Community**: HuggingFace Spaces Discord

---

**Ready to deploy?** Follow the Quick Deploy steps above!

