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
    """
    Render the sidebar and return metadata needed for the main layout.
    Returns:
        tuple(dict, str | None): processed_files mapping and currently selected file name.
    """
    processed_files = {}
    active_file = None

    try:
        processed_files = get_processed_files()
        total_chunks = sum(info.get('chunk_count', 0) for info in processed_files.values())

        with st.sidebar:
            st.markdown("### Knowledge Base")

            # Stats row
            col1, col2 = st.columns(2)
            with col1:
                st.metric(label="Documents", value=len(processed_files))
            with col2:
                st.metric(label="Chunks", value=total_chunks)

            st.markdown("---")

            # File upload section
            st.markdown("#### Add Document")
            doc_limit = 5
            can_upload = len(processed_files) < doc_limit

            uploaded_file = st.file_uploader(
                "Drag and drop file here",
                type=['pdf', 'txt'],
                help="Limit 200MB per file",
                disabled=not can_upload,
                key="sidebar_uploader"
            )

            if uploaded_file and can_upload:
                if 'processed_this_session' not in st.session_state:
                    st.session_state.processed_this_session = set()

                if uploaded_file.name in st.session_state.processed_this_session:
                    st.success(f"Ready to process: {uploaded_file.name}")
                else:
                    with st.status(f"Processing {uploaded_file.name}...", expanded=True) as status:
                        try:
                            if HF_MODE:
                                import requests
                                backend_url = st.session_state.get('backend_url', os.getenv('BACKEND_URL'))
                                if not backend_url:
                                    status.update(label="Backend disconnected", state="error")
                                    st.error("Please check backend connection")
                                else:
                                    status.write("Uploading to backend…")
                                    files = {'file': (uploaded_file.name, uploaded_file.getvalue(), uploaded_file.type or 'application/pdf')}
                                    response = requests.post(f"{backend_url}/api/upload", files=files, timeout=180)
                                    response.raise_for_status()
                                    result = response.json()

                                    if result.get('success'):
                                        st.session_state.processed_this_session.add(uploaded_file.name)
                                        status.update(label="Complete", state="complete")
                                        st.toast(f"Indexed {uploaded_file.name}")
                                        st.rerun()
                                    else:
                                        status.update(label="Failed", state="error")
                                        st.error(f"Error: {result.get('error')}")
                            else:
                                status.update(label="Unavailable in local mode", state="error")
                        except Exception as e:
                            status.update(label="Error", state="error")
                            st.error(str(e))

            st.markdown("### Active Files")
            if processed_files:
                file_options = list(processed_files.keys())
                active_file = st.selectbox(
                    "Select a file to view details",
                    file_options,
                    key="active_file_select"
                )
            else:
                st.info("No files indexed yet.")

            st.markdown("---")
            with st.expander("Settings & Tools"):
                st.slider("Chunk Size", 256, 2048, 512, key="chunk_size_slider")
                st.slider("Overlap", 0, 200, 50, key="chunk_overlap_slider")
                st.toggle("Enable Hybrid Search", value=True, key="hybrid_toggle")
                st.button("Clear Cache", type="secondary")

    except Exception as e:
        st.sidebar.error(f"Sidebar Error: {str(e)}")

    return processed_files, active_file
