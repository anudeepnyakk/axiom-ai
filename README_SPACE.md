# Axiom AI - Enterprise RAG System

**Live Demo** | [GitHub](https://github.com/anudeepnyakk/axiom-ai)

## 🎯 What is Axiom AI?

Axiom AI is a production-grade Retrieval-Augmented Generation (RAG) system that allows users to upload documents, index them with semantic search, and query them using natural language with cited sources.

### Key Features
- 📄 **Document Ingestion**: Upload PDFs and TXT files
- 🔍 **Semantic Search**: Vector-based retrieval using sentence-transformers
- 💬 **Conversational Q&A**: GPT-4 powered answers with source citations
- 📊 **System Monitoring**: Real-time metrics and health checks
- 🎨 **Modern UI**: Clean, responsive Streamlit interface

## 🏗️ Architecture

This Space is the **frontend only**. The backend API runs separately on Railway for:
- Persistent document storage (ChromaDB)
- Heavy model inference (sentence-transformers)
- Scalable compute resources

```
┌─────────────────┐      HTTPS/API      ┌──────────────────┐
│  HuggingFace    │ ─────────────────► │  Railway Backend │
│  (Streamlit UI) │                     │  (Flask + Chroma)│
└─────────────────┘                     └──────────────────┘
```

## 🚀 Tech Stack

**Frontend (This Space)**
- Streamlit 1.28+
- Requests (API client)
- Pure stateless UI

**Backend (Railway)**
- Flask 2.3+ with CORS
- ChromaDB 0.4.x (vector store)
- Sentence-Transformers 2.7.0 (embeddings)
- OpenAI GPT-4 (synthesis)
- Prometheus metrics

## 🔧 Environment Variables

Set in Space Settings → Variables:

```bash
BACKEND_URL=https://your-railway-backend.railway.app
```

## 📖 Usage

1. **Upload Documents**: Use the sidebar to upload PDF or TXT files (max 5 documents)
2. **Ask Questions**: Type natural language questions in the chat interface
3. **View Sources**: Click "Show Evidence" to see the retrieved document chunks
4. **Monitor System**: Check the SystemOps tab for backend health and metrics

## 🎓 Built For

This project demonstrates:
- Full-stack RAG system design
- Production deployment patterns (separate frontend/backend)
- Docker containerization
- API design and error handling
- Observability and monitoring
- Modern Python best practices

## 📝 License

MIT License - see [LICENSE](https://github.com/anudeepnyakk/axiom-ai/blob/main/LICENSE)

---

**Author**: Anudeep  
**Contact**: [GitHub](https://github.com/anudeepnyakk)
