---
title: Axiom AI
emoji: 🤖
colorFrom: blue
colorTo: purple
sdk: streamlit
sdk_version: 1.28.0
app_file: app.py
pinned: false
license: mit
---

# Axiom AI - Production RAG System

**High-fidelity RAG system with multilingual support, robust security, and observability.**

## 🚀 Live Demo

Click "Embed this Space" or visit the live app to see Axiom AI in action!

## ✨ Features

- **Multilingual Support**: Query in English, Hindi, and more
- **Retrieval Evaluation**: Metrics-driven approach with Recall@k, MRR tracking
- **Secure by Default**: PII redaction, constant-time API key comparison
- **Production Ready**: Fault tolerance, retry logic, graceful degradation

## 📊 Performance Metrics

| Metric | English | Hindi |
|--------|---------|-------|
| Recall@5 | 0.97 | 0.93 |
| MRR | 0.92 | 0.87 |
| Latency | 145ms | 155ms |

## 🔧 Configuration

The app uses environment variables for configuration:

- `OPENAI_API_KEY` (required): Your OpenAI API key for LLM synthesis
- `EMBEDDING_PROVIDER` (optional): Set to `local` for offline operation (default: uses OpenAI)
- `EMBEDDING_MODEL` (optional): Embedding model name

## 📚 How It Works

1. **Ingestion**: Documents are processed and embedded using multilingual models
2. **Storage**: Embeddings stored in ChromaDB vector store
3. **Query**: User questions are embedded and matched against the knowledge base
4. **Synthesis**: GPT-4o generates answers with source citations

## 🔗 Learn More

- **GitHub**: [View Source Code](https://github.com/YOUR_USERNAME/axiom)
- **Documentation**: See `/docs` folder for architecture, evaluation, and security docs

## 📝 License

MIT License - see LICENSE file for details.

