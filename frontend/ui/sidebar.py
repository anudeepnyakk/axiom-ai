import streamlit as st
import sys
from pathlib import Path
import tempfile
import os
import json

# Check if we're in HuggingFace mode (frontend-only)
HF_MODE = os.getenv("BACKEND_URL") is not None and os.getenv("BACKEND_URL") != "http://localhost:8000"

# Add parent directory to path only if not in HF mode
if not HF_MODE:
    sys.path.insert(0, str(Path(__file__).parent.parent.parent))

# Persistent storage for uploaded documents
if HF_MODE:
    FRONTEND_DIR = Path(tempfile.gettempdir())
    UPLOAD_DIR = FRONTEND_DIR / "axiom_uploads"
    PROCESSED_FILES_TRACKER = FRONTEND_DIR / "axiom_processed_files.json"
else:
    FRONTEND_DIR = Path(__file__).parent.parent
    UPLOAD_DIR = FRONTEND_DIR / "uploaded_documents"
    PROCESSED_FILES_TRACKER = FRONTEND_DIR / "processed_files.json"

try:
    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
except PermissionError:
    if HF_MODE:
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
        return {}

def render_sidebar():
    try:
        with st.sidebar:
            st.title("Knowledge Base")
            
            # Initialize session state
            if 'processed_this_session' not in st.session_state:
                st.session_state.processed_this_session = set()
            
            # Get documents from backend
            processed_files = get_processed_files()
            
            # === STATS ===
            total_chunks = sum(info.get('chunk_count', 0) for info in processed_files.values())
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Documents", len(processed_files))
            with col2:
                st.metric("Chunks", total_chunks)
            
            st.markdown("---")
            
            # === UPLOAD ===
            doc_limit = 5
            can_upload = len(processed_files) < doc_limit
            
            uploaded_file = st.file_uploader(
                "Add Document",
                type=['pdf', 'txt'],
                help=f"Max {doc_limit} documents",
                disabled=not can_upload,
                key="sidebar_uploader"
            )
            
            if uploaded_file and can_upload:
                if uploaded_file.name in st.session_state.processed_this_session:
                    st.success(f"Ready: {uploaded_file.name}")
                else:
                    with st.status(f"Processing {uploaded_file.name}...", expanded=True) as status:
                        try:
                            if HF_MODE:
                                import requests
                                backend_url = st.session_state.get('backend_url', os.getenv('BACKEND_URL'))
                                
                                if not backend_url:
                                    status.update(label="Backend disconnected", state="error")
                                    st.error("Please check connection")
                                else:
                                    status.write("Uploading to backend...")
                                    files = {'file': (uploaded_file.name, uploaded_file.getvalue(), uploaded_file.type or 'application/pdf')}
                                    response = requests.post(f"{backend_url}/api/upload", files=files, timeout=180)
                                    response.raise_for_status()
                                    result = response.json()
                                    
                                    if result.get('success'):
                                        st.session_state.processed_this_session.add(uploaded_file.name)
                                        status.update(label="Complete!", state="complete")
                                        st.toast(f"Indexed {uploaded_file.name}")
                                        # Force refresh to show in list
                                        st.rerun()
                                    else:
                                        status.update(label="Failed", state="error")
                                        st.error(f"Error: {result.get('error')}")
                            else:
                                status.update(label="Local mode unavailable", state="error")
                        except Exception as e:
                            status.update(label="Error", state="error")
                            st.error(str(e))

            # === FILE LIST ===
            if processed_files:
                st.markdown("### Active Files")
                for filename, info in processed_files.items():
                    chunks = info.get('chunk_count', '?')
                    with st.expander(f"📄 {filename}", expanded=False):
                        st.caption(f"Chunks: {chunks}")
                        st.caption("Status: Indexed")

            # === ACTIONS ===
            st.markdown("---")
            with st.expander("Settings & Tools"):
                if st.button("Clear Knowledge Base", use_container_width=True, type="secondary"):
                    # This is a placeholder for clear functionality
                    st.toast("Use backend API to clear database")
                
                if st.button("View Logs", use_container_width=True):
                    st.toast("Check SystemOps tab")

    except Exception as e:
        st.sidebar.error(f"Sidebar Error: {str(e)}")
