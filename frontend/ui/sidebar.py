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
            # Sidebar CSS for cleaner look
            st.markdown("""
                <style>
                /* Sidebar header styling */
                [data-testid="stSidebar"] h2, [data-testid="stSidebar"] h3 {
                    font-size: 14px;
                    font-weight: 600;
                    color: #0D0D0D;
                    margin-top: 24px;
                    margin-bottom: 12px;
                    text-transform: uppercase;
                    letter-spacing: 0.5px;
                }
                
                /* Clean expander styling */
                [data-testid="stSidebar"] .streamlit-expanderHeader {
                    font-size: 13px;
                    font-weight: 500;
                    background: transparent !important;
                }
                
                /* Metric styling */
                [data-testid="stSidebar"] [data-testid="stMetricValue"] {
                    font-size: 24px;
                    font-weight: 600;
                }
                
                [data-testid="stSidebar"] [data-testid="stMetricLabel"] {
                    font-size: 12px;
                    color: #6E6E80;
                    text-transform: uppercase;
                    letter-spacing: 0.5px;
                }
                
                /* File uploader */
                [data-testid="stSidebar"] .stFileUploader {
                    border: 1px dashed #D1D5DB;
                    border-radius: 8px;
                    padding: 16px;
                    background: #F9FAFB;
                }
                
                [data-testid="stSidebar"] .stFileUploader label {
                    font-size: 13px;
                    font-weight: 500;
                    color: #374151;
                }
                </style>
            """, unsafe_allow_html=True)
            
            # Initialize session state
            if 'processed_this_session' not in st.session_state:
                st.session_state.processed_this_session = set()
            
            # Get documents from backend
            processed_files = get_processed_files()
            
            # === STATS SECTION (at top) ===
            st.markdown("### Knowledge Base")
            total_chunks = sum(info.get('chunk_count', 0) for info in processed_files.values())
            
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Documents", len(processed_files), delta=None)
            with col2:
                st.metric("Chunks", total_chunks, delta=None)
            
            st.markdown("<div style='margin-top: 8px; margin-bottom: 20px;'></div>", unsafe_allow_html=True)
            
            # === UPLOADED DOCUMENTS ===
            if processed_files:
                with st.expander(f"📄 {len(processed_files)} document(s)", expanded=False):
                    for filename, info in processed_files.items():
                        chunk_count = info.get('chunk_count', '?')
                        st.markdown(f"""
                            <div style='padding: 8px 0; border-bottom: 1px solid #E5E5E5;'>
                                <div style='font-size: 13px; font-weight: 500; color: #0D0D0D;'>{filename}</div>
                                <div style='font-size: 12px; color: #6E6E80; margin-top: 2px;'>{chunk_count} chunks</div>
                            </div>
                        """, unsafe_allow_html=True)
            
            st.markdown("<div style='margin-top: 24px;'></div>", unsafe_allow_html=True)
            
            # === UPLOAD SECTION ===
            st.markdown("### Upload Document")
            
            # Check document limit
            doc_limit = 5
            can_upload = len(processed_files) < doc_limit
            
            if not can_upload:
                st.info(f"📚 Limit reached ({doc_limit} max). Clear documents to upload more.")
            
            # File uploader
            uploaded_file = st.file_uploader(
                "Choose file",
                type=['pdf', 'txt'],
                help=f"Supports PDF and TXT files up to 200MB",
                disabled=not can_upload,
                label_visibility="collapsed"
            )
            
            # Handle file upload
            if uploaded_file and can_upload:
                if uploaded_file.name in st.session_state.processed_this_session:
                    st.success(f"✓ Already uploaded this session")
                else:
                    with st.spinner(""):
                        try:
                            if HF_MODE:
                                import requests
                                backend_url = st.session_state.get('backend_url', os.getenv('BACKEND_URL'))
                                
                                if not backend_url:
                                    st.error("Backend not connected")
                                else:
                                    files = {'file': (uploaded_file.name, uploaded_file.getvalue(), uploaded_file.type or 'application/pdf')}
                                    response = requests.post(f"{backend_url}/api/upload", files=files, timeout=180)
                                    response.raise_for_status()
                                    result = response.json()
                                    
                                    if result.get('success'):
                                        st.session_state.processed_this_session.add(uploaded_file.name)
                                        st.success(f"✓ Uploaded {result.get('chunks', 0)} chunks")
                                        st.info("Refresh page (F5) to see in list")
                                    else:
                                        st.error(f"Upload failed: {result.get('error', 'Unknown error')}")
                            else:
                                st.warning("Local mode not implemented")
                        except Exception as e:
                            st.error(f"Upload error: {str(e)}")
            
            # === DANGER ZONE ===
            if processed_files:
                st.markdown("<div style='margin-top: 32px;'></div>", unsafe_allow_html=True)
                with st.expander("🗑️ Clear All", expanded=False):
                    st.markdown("""
                        <div style='padding: 12px; background: #FEF2F2; border-radius: 6px; border: 1px solid #FEE2E2; margin-bottom: 12px;'>
                            <div style='font-size: 13px; color: #991B1B; font-weight: 500;'>⚠️ Warning</div>
                            <div style='font-size: 12px; color: #7F1D1D; margin-top: 4px;'>This permanently removes all documents from the knowledge base.</div>
                        </div>
                    """, unsafe_allow_html=True)
                    if st.button("Delete All Documents", key="confirm_clear", type="secondary"):
                        try:
                            if PROCESSED_FILES_TRACKER.exists():
                                PROCESSED_FILES_TRACKER.unlink()
                            for file in UPLOAD_DIR.glob("*"):
                                if file.is_file():
                                    file.unlink()
                            st.success("Documents cleared")
                            st.info("Refresh page to update")
                        except Exception as e:
                            st.error(f"Clear failed: {e}")
            
            # === SETTINGS (collapsed by default) ===
            st.markdown("<div style='margin-top: 32px;'></div>", unsafe_allow_html=True)
            with st.expander("⚙️ Settings", expanded=False):
                st.selectbox("LLM Provider", ["OpenAI"], disabled=True, key="llm_prov")
                st.selectbox("Embedding Model", ["all-MiniLM-L6-v2"], disabled=True, key="embed_model")
                st.caption("Production configuration")
            
            # === DEVELOPER TOOLS ===
            st.markdown("<div style='margin-top: 32px;'></div>", unsafe_allow_html=True)
            with st.expander("🔧 Developer", expanded=False):
                if st.button("Open Sources Drawer", key="dev_drawer"):
                    st.session_state.drawer_open = True
                st.caption("View RAG sources and metadata")
                
    except Exception as e:
        st.error(f"Sidebar error: {str(e)}")
        import traceback
        st.code(traceback.format_exc())
