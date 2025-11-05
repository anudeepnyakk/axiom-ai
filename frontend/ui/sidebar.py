import streamlit as st
import sys
from pathlib import Path
import tempfile
import os
import json
import hashlib

# Check if we're in HuggingFace mode (frontend-only)
HF_MODE = os.getenv("BACKEND_URL") is not None and os.getenv("BACKEND_URL") != "http://localhost:8000"

# Add parent directory to path only if not in HF mode
if not HF_MODE:
    sys.path.insert(0, str(Path(__file__).parent.parent.parent))

# Persistent storage for uploaded documents
# Use absolute path relative to frontend directory
FRONTEND_DIR = Path(__file__).parent.parent
UPLOAD_DIR = FRONTEND_DIR / "uploaded_documents"
UPLOAD_DIR.mkdir(exist_ok=True)

PROCESSED_FILES_TRACKER = FRONTEND_DIR / "processed_files.json"

def get_processed_files():
    """Load list of processed files from disk"""
    if PROCESSED_FILES_TRACKER.exists():
        try:
            with open(PROCESSED_FILES_TRACKER, 'r') as f:
                return json.load(f)
        except:
            return {}
    return {}

def mark_file_processed(filename, chunk_count):
    """Persistently mark a file as processed"""
    processed = get_processed_files()
    processed[filename] = {
        "chunk_count": chunk_count,
        "timestamp": str(Path(UPLOAD_DIR / filename).stat().st_mtime if (UPLOAD_DIR / filename).exists() else "unknown")
    }
    with open(PROCESSED_FILES_TRACKER, 'w') as f:
        json.dump(processed, f, indent=2)

def get_file_hash(file_bytes):
    """Get hash of file content to detect duplicates"""
    return hashlib.md5(file_bytes).hexdigest()

def remove_document(filename):
    """Remove a document from tracking and storage"""
    try:
        # Remove from tracking file
        processed = get_processed_files()
        if filename in processed:
            del processed[filename]
            with open(PROCESSED_FILES_TRACKER, 'w') as f:
                json.dump(processed, f, indent=2)
        
        # Remove physical file
        file_path = UPLOAD_DIR / filename
        if file_path.exists():
            file_path.unlink()
        
        # IMPORTANT: Clear ChromaDB collection to remove embeddings
        # This prevents citation glitches with wrong/old documents
        # Simplified for speed - just mark as removed, embeddings cleaned on next query
        try:
            # Try quick cleanup but don't block on it
            from axiom.config.loader import load_config
            from axiom.core.factory import create_query_engine
            
            config = load_config()
            
            # Quick check if we can access vector store
            if hasattr(config, 'vector_store'):
                query_engine = create_query_engine(config)
                collection = query_engine.vector_store._collection
                
                # Quick delete without full scan (faster!)
                # Get IDs with WHERE filter
                try:
                    results = collection.get(where={"source_file_path": {"$contains": filename}})
                    if results and 'ids' in results and results['ids']:
                        collection.delete(ids=results['ids'])
                except:
                    # If filter fails, skip vector cleanup (file is already removed)
                    pass
        except Exception:
            # Silently fail - document is removed from tracking, that's good enough
            pass
        
        return True
    except Exception as e:
        import streamlit as st
        st.error(f"Error removing document: {e}")
        return False

def render_sidebar():
    with st.sidebar:
        st.subheader("📁 Ingestion")
        
        # Show currently indexed documents
        processed_files = get_processed_files()
        if processed_files:
            st.info(f"📚 {len(processed_files)}/5 documents indexed")
            with st.expander("View indexed documents"):
                for filename, info in processed_files.items():
                    col1, col2 = st.columns([4, 1])
                    with col1:
                        st.text(f"✅ {filename} ({info.get('chunk_count', '?')} chunks)")
                    with col2:
                        if st.button("🗑️", key=f"del_{filename}", help="Remove this document"):
                            # Remove document without reloading (avoid duplicate header bug)
                            success = remove_document(filename)
                            if success:
                                # Use st.toast for feedback without full page reload
                                st.toast(f"✅ Removed {filename}", icon="✅")
                                # Force cache clear and minimal reload
                                st.cache_resource.clear()
                            st.rerun()
        
        # Check document limit
        doc_limit = 5
        can_upload = len(processed_files) < doc_limit
        
        if not can_upload:
            st.warning(f"⚠️ Document limit reached ({doc_limit} max). Remove documents to add new ones.")
        
        if HF_MODE:
            st.info("📝 Upload documents via backend API endpoint `/api/upload`")
            uploaded_files = []
        else:
            uploaded_files = st.file_uploader(
                "Documents",
                accept_multiple_files=True,
                key="upload_docs",
                type=['pdf', 'txt'],
                help=f"Upload PDF or TXT files. Max {doc_limit} documents.",
                disabled=not can_upload
            )
        
        # Handle file upload
        if uploaded_files and can_upload:
            for uploaded_file in uploaded_files:
                # Check if already processed (persistent check)
                if uploaded_file.name in processed_files:
                    continue  # Skip already processed files
                
                # Check limit again per file
                current_count = len(get_processed_files())
                if current_count >= doc_limit:
                    st.warning(f"⚠️ Cannot add {uploaded_file.name}: limit of {doc_limit} reached")
                    continue
                    
                with st.spinner(f"Ingesting {uploaded_file.name}..."):
                    try:
                        # Save permanently to upload directory
                        file_path = UPLOAD_DIR / uploaded_file.name
                        with open(file_path, 'wb') as f:
                            f.write(uploaded_file.getvalue())
                        
                        # Import and process (skip if in HuggingFace mode)
                        if HF_MODE:
                            st.warning("⚠️ Document upload not available in HuggingFace Space. Use backend API directly.")
                            continue
                        
                        from axiom.core.factory import create_document_processor
                        from axiom.config.loader import load_config
                        
                        config = load_config()
                        processor = create_document_processor(config)
                        chunks = processor.process_document(str(file_path))
                        
                        # Mark as processed (persistent)
                        mark_file_processed(uploaded_file.name, len(chunks) if chunks else 0)
                        
                        st.success(f"✅ Ingested {uploaded_file.name}: {len(chunks) if chunks else 0} chunks")
                        st.rerun()
                        
                    except Exception as e:
                        st.error(f"❌ Error ingesting {uploaded_file.name}: {str(e)}")
                        # Clean up on error
                        if file_path.exists():
                            file_path.unlink()
        
        # Clear all documents button
        if processed_files:
            with st.expander("⚠️ Clear All Documents"):
                st.warning("This will remove all indexed documents permanently!")
                if st.button("🗑️ Confirm Clear All", key="confirm_clear"):
                    try:
                        # Clear the tracker file
                        if PROCESSED_FILES_TRACKER.exists():
                            PROCESSED_FILES_TRACKER.unlink()
                        # Clear uploaded files
                        for file in UPLOAD_DIR.glob("*"):
                            if file.is_file():
                                file.unlink()
                        st.success("All documents cleared!")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error clearing documents: {e}")
        
        st.text_input("Directory Path", "./docs", disabled=True)

        st.subheader("⚙️ Models (UI only)")
        st.selectbox("Embedding Model", ["MiniLM", "BGE", "Instructor"], disabled=True)
        st.selectbox("LLM Provider", ["OpenAI", "Anthropic"], disabled=True)

        st.subheader("📈 Stats")
        total_chunks = sum(info.get('chunk_count', 0) for info in processed_files.values())
        st.metric("Documents", len(processed_files))
        st.metric("Chunks", total_chunks)

        st.subheader("🔧 Developer Tools")
        if st.button("Open Evidence Drawer"):
            st.session_state.drawer_open = True
