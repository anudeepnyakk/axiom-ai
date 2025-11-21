"""
Sidebar - Uploads, Metrics, and System Health

Clean sidebar with document upload, system metrics, and debug tools.
"""

import streamlit as st
import sys
from pathlib import Path
import tempfile
import os
import json
import requests
import traceback

# Check if we're in HuggingFace mode (frontend-only)
HF_MODE = os.getenv("BACKEND_URL") is not None and os.getenv("BACKEND_URL") != "http://localhost:8000"

def get_processed_files():
    """Get list of processed files from backend API"""
    if HF_MODE:
        try:
            backend_url = st.session_state.get('backend_url', os.getenv('BACKEND_URL'))
            if not backend_url:
                return {}
            response = requests.get(f"{backend_url}/api/documents", timeout=5)
            if response.status_code == 200:
                return response.json().get('documents', {})
        except:
            pass
    return {}

def get_system_metrics():
    """Get system metrics from backend (mock for now)"""
    # TODO: Add real metrics endpoint to backend
    return {
        "latency": "145ms",
        "latency_delta": "-12ms",
        "recall": "97%",
        "recall_delta": "+2%"
    }

def render_sidebar():
    """
    Render the sidebar with uploads, metrics, and settings.
    Returns:
        tuple(dict, str | None): processed_files mapping and currently selected file name.
    """
    processed_files = {}
    active_file = None

    try:
        processed_files = get_processed_files()
        total_chunks = sum(info.get('chunk_count', 0) for info in processed_files.values())

        with st.sidebar:
            st.header("🧠 Axiom Cortex")

            # Stats row
            col1, col2 = st.columns(2)
                    with col1:
                st.metric(label="Documents", value=len(processed_files))
                    with col2:
                st.metric(label="Chunks", value=total_chunks)

            st.divider()

            # File upload section
            st.markdown("#### 📤 Ingest Document")
        doc_limit = 5
        can_upload = len(processed_files) < doc_limit
        
            uploaded_file = st.file_uploader(
                "Drag and drop file here",
            type=['pdf', 'txt'],
                help=f"Max {doc_limit} documents. Limit 500MB per file.",
                disabled=not can_upload,
                key="sidebar_uploader"
            )

            if uploaded_file and can_upload:
                if 'processed_this_session' not in st.session_state:
                    st.session_state.processed_this_session = set()

                if uploaded_file.name in st.session_state.processed_this_session:
                    st.success(f"✅ Ready: {uploaded_file.name}")
                else:
                    with st.status(f"Processing {uploaded_file.name}...", expanded=True) as status:
                        try:
                            if HF_MODE:
                                backend_url = st.session_state.get('backend_url', os.getenv('BACKEND_URL'))
                                if not backend_url:
                                    status.update(label="Backend disconnected", state="error")
                                    st.error("Please check backend connection")
                                else:
                                    status.write("📤 Uploading to backend…")
                                    files = {'file': (uploaded_file.name, uploaded_file.getvalue(), uploaded_file.type or 'application/pdf')}
                                    response = requests.post(f"{backend_url}/api/upload", files=files, timeout=180)
                                    response.raise_for_status()
                                    result = response.json()

                                    if result.get('success'):
                                        st.session_state.processed_this_session.add(uploaded_file.name)
                                        
                                        # Store PDF for display
                                        if uploaded_file.type == 'application/pdf':
                                            st.session_state.current_pdf_file = uploaded_file
                                        
                                        status.update(label="✅ Complete", state="complete")
                                        st.toast(f"Indexed {uploaded_file.name}")
                                        # Removing st.rerun() to prevent SessionInfo errors
                                        # The UI will update naturally on next interaction
                                    else:
                                        status.update(label="❌ Failed", state="error")
                                        st.error(f"Error: {result.get('error')}")
                            else:
                                status.update(label="Unavailable in local mode", state="error")
                        except Exception as e:
                            status.update(label="❌ Error", state="error")
                            st.error(str(e))

            st.divider()

            # System Health Metrics
            st.markdown("### ⚡ System Health")
            metrics = get_system_metrics()
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Latency", metrics["latency"], metrics["latency_delta"])
            with col2:
                st.metric("Recall", metrics["recall"], metrics["recall_delta"])

            st.divider()

            # Active Files
            st.markdown("### 📄 Active Files")
        if processed_files:
                file_options = list(processed_files.keys())
                active_file = st.selectbox(
                    "Select a file to view",
                    file_options,
                    key="active_file_select"
                )
            else:
                st.info("No files indexed yet.")

            st.divider()

            # Debugger Section
            st.markdown("### 🔍 Debugger")
            show_raw_chunks = st.toggle("Show Raw Chunks", value=False, key="debug_raw_chunks")
            
            if show_raw_chunks and active_file:
                file_info = processed_files.get(active_file, {})
                chunks = file_info.get('chunk_count', 0)
                st.caption(f"Chunks: {chunks}")

            st.divider()

            # Settings (collapsed by default)
            with st.expander("⚙️ Settings & Tools"):
                st.slider("Chunk Size", 256, 2048, 512, key="chunk_size_slider")
                st.slider("Overlap", 0, 200, 50, key="chunk_overlap_slider")
                st.toggle("Enable Hybrid Search", value=True, key="hybrid_toggle")
                st.button("Clear Cache", type="secondary", key="clear_cache_btn")

    except Exception as e:
        st.sidebar.error(f"⚠️ Sidebar Error: {str(e)}")
        st.sidebar.code(traceback.format_exc())

    return processed_files, active_file
