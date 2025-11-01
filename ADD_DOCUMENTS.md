# 📚 Adding Documents to Axiom AI

## Quick Start

1. **Place PDF/TXT files** in `axiom/data/` directory
2. **Run**: `python quick_ingest.py`
3. **Test**: `python test_final_system.py`

---

## 🎯 Recommended Documents (Free & Legal)

### Tech & Business (10+ documents to meet requirements)

1. **OpenAI Research Papers**
   - https://arxiv.org/pdf/2005.14165.pdf (GPT-3 Paper)
   - https://arxiv.org/pdf/2203.02155.pdf (InstructGPT)
   
2. **Y Combinator Startup Library**
   - http://www.paulgraham.com/articles.html (Save essays as PDFs)
   - "How to Start a Startup" essays

3. **Public Domain Business Books**
   - The Lean Startup methodology papers
   - Google's "How Search Works" whitepaper
   
4. **AI/ML Research**
   - Attention Is All You Need (Transformer paper)
   - BERT paper
   - RAG paper (original retrieval-augmented generation)

5. **Company Reports & Whitepapers**
   - AWS Well-Architected Framework (free PDF)
   - Google SRE Book (free PDF)
   - Microsoft Azure Architecture docs

### Quick Downloads

```bash
# Create directory
mkdir -p axiom/data

# Download some papers (example)
cd axiom/data
curl -o gpt3_paper.pdf https://arxiv.org/pdf/2005.14165.pdf
curl -o transformer_paper.pdf https://arxiv.org/pdf/1706.03762.pdf
curl -o rag_paper.pdf https://arxiv.org/pdf/2005.11401.pdf
```

---

## 📊 Current Status

Run this to check your document count:

```bash
python -c "from axiom.config.loader import load_config; from axiom.core.factory import create_query_engine; qe = create_query_engine(load_config()); print(f'Total chunks: {qe.vector_store._collection.count() if hasattr(qe.vector_store, \"_collection\") else \"N/A\"}')"
```

---

## ✅ Meeting the 10+ Document Requirement

**Acceptance Criteria**: At least 10 complex documents (books, research papers)

**Your Path**:
1. ✅ Blitzscaling PDF (from UI upload)
2. ✅ Build a Large Scale-Up PDF (from UI upload)
3. ⏳ Add 8 more PDFs (research papers or books)

**Easiest Solution**: Download 8 AI/ML research papers from arXiv (all free, high-quality)

---

## 🚀 After Adding Documents

1. **Re-run tests**: `python test_final_system.py`
2. **Test in UI**: `cd frontend && streamlit run app.py`
3. **Verify citations**: Check that answers include `[S1]` `[S2]` markers
4. **Test multi-document**: Ask questions spanning multiple papers

---

## 💡 Pro Tips

- **Mix document types**: PDFs + TXT for variety
- **Size matters**: 2-20 MB PDFs are perfect (not too small, not too large)
- **Content quality**: Research papers > random PDFs
- **Domain variety**: Mix tech, business, AI papers for richer testing

---

## 🎯 Your Current Setup

**Frontend Database**: `frontend/chroma_db/` (has Blitzscaling + Build a Large...)
**Backend Database**: `chroma_db/axiom_documents/` (for tests and ingestion)

**To sync**: Just re-upload documents via the UI, OR use `quick_ingest.py` for bulk ingestion


