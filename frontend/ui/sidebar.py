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
# HuggingFace Spaces has a read-only filesystem - use /tmp when in HF mode
if HF_MODE:
    FRONTEND_DIR = Path(tempfile.gettempdir())
    UPLOAD_DIR = FRONTEND_DIR / "axiom_uploads"
    PROCESSED_FILES_TRACKER = FRONTEND_DIR / "axiom_processed_files.json"
else:
    FRONTEND_DIR = Path(__file__).parent.parent
    UPLOAD_DIR = FRONTEND_DIR / "uploaded_documents"
    PROCESSED_FILES_TRACKER = FRONTEND_DIR / "processed_files.json"

# Make sure the upload directory exists (ignore errors in read-only environments)
try:
    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
except PermissionError:
    if HF_MODE:
        # Fallback to a guaranteed-writable temp directory
        UPLOAD_DIR = Path(tempfile.mkdtemp(prefix="axiom_uploads_"))
        PROCESSED_FILES_TRACKER = Path(tempfile.gettempdir()) / "axiom_processed_files.json"
    else:
        raise

def get_processed_files():
    """Get list of processed files from backend API"""
    if HF_MODE:
        try:
            import requests
            backend_url = st.session_state.get('backend_url', os.getenv('BACKEND_URL'))
            if not backend_url:
                return {}
            response = requests.get(f"{backend_url}/api/documents", timeout=5)
            if response.status_code == 200:
                return response.json().get('documents', {})
        except:
            pass
        return {}
    else:
        # Local mode - not used on HuggingFace
        return {}

def render_sidebar():
    try:
        with st.sidebar:
            st.subheader("📁 Ingestion")
            
            # Initialize session state
            if 'processed_this_session' not in st.session_state:
                st.session_state.processed_this_session = set()
            
            # Get documents from backend
            processed_files = get_processed_files()
            
            if processed_files:
                st.info(f"📚 {len(processed_files)}/5 documents indexed")
                with st.expander("View indexed documents"):
                    for filename, info in processed_files.items():
                        st.text(f"✅ {filename} ({info.get('chunk_count', '?')} chunks)")
            
            # Check document limit
            doc_limit = 5
            can_upload = len(processed_files) < doc_limit
            
            if not can_upload:
                st.warning(f"⚠️ Document limit reached ({doc_limit} max).")
            
            # File uploader
            uploaded_file = st.file_uploader(
                "Upload Document",
                type=['pdf', 'txt'],
                help=f"Upload PDF or TXT files. Max {doc_limit} documents.",
                disabled=not can_upload
            )
            
            # Handle file upload - SIMPLIFIED
            if uploaded_file and can_upload:
                # Check if already processed this session
                if uploaded_file.name in st.session_state.processed_this_session:
                    st.info(f"✓ {uploaded_file.name} already uploaded")
                else:
                    with st.spinner(f"Uploading {uploaded_file.name}..."):
                        try:
                            if HF_MODE:
                                # HF mode: send directly to backend, NO local files
                                import requests
                                backend_url = st.session_state.get('backend_url', os.getenv('BACKEND_URL'))
                                
                                if not backend_url:
                                    st.error("❌ Backend URL not set")
                                else:
                                    files = {'file': (uploaded_file.name, uploaded_file.getvalue(), uploaded_file.type or 'application/pdf')}
                                    response = requests.post(f"{backend_url}/api/upload", files=files, timeout=60)
                                    response.raise_for_status()
                                    result = response.json()
                                    
                                    if result.get('success'):
                                        st.session_state.processed_this_session.add(uploaded_file.name)
                                        st.success(f"✅ {uploaded_file.name} uploaded ({result.get('chunks', 0)} chunks)")
                                        st.info("↻ Refresh (F5) to see in list")
                                    else:
                                        st.error(f"❌ {result.get('error', 'Upload failed')}")
                            else:
                                # Local mode (not used on HF)
                                st.warning("Local mode not implemented")
                        except Exception as e:
                            import traceback, sys
                            print("[DBG] UPLOAD HANDLER EXCEPTION", file=sys.stderr)
                            traceback.print_exc()
                            sys.stderr.flush()
                            sys.stdout.flush()
                            st.error(f"❌ Upload failed: {str(e)}")
            
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
                            st.info("↻ Refresh page to update")
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
    except Exception as e:
        st.error(f"⚠️ Sidebar Error: {str(e)}")
        import traceback
        st.code(traceback.format_exc())
