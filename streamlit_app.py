"""
Axiom AI - Streamlit App Entry Point for HuggingFace Spaces

HuggingFace Spaces expects streamlit_app.py when using Streamlit template.
This file imports our frontend-only app_hf.py which calls the backend API.
"""

import streamlit as st
import sys
import traceback
from pathlib import Path

# Set page config immediately (must be first)
try:
    st.set_page_config(page_title="Axiom Enterprise", layout="wide")
except Exception:
    pass  # Already set, ignore

# Add frontend directory to path so imports work
frontend_dir = Path(__file__).parent / "frontend"
sys.path.insert(0, str(frontend_dir))
sys.path.insert(0, str(Path(__file__).parent))

# Always show something - wrap everything in try-except
# Use a placeholder container that will be replaced
placeholder = st.empty()

try:
    # Import frontend-only app (this will replace placeholder content)
    from app_hf import *
    # If we get here, app loaded successfully - placeholder will be replaced by app_hf content
except ImportError as e:
    with placeholder.container():
        st.error("⚠️ Import Error - Failed to load Axiom AI application")
        st.error(f"**Error:** `{str(e)}`")
        st.code(traceback.format_exc())
        
        st.info("""
        **Troubleshooting:**
        1. Check that all files are present in the `frontend/` directory
        2. Check HuggingFace Space logs for detailed errors
        3. Verify `BACKEND_URL` environment variable is set correctly
        """)
        
        # Show diagnostic info
        st.text(f"Current directory: {Path(__file__).parent}")
        st.text(f"Frontend directory: {frontend_dir}")
        st.text(f"Frontend exists: {frontend_dir.exists()}")
        
        if frontend_dir.exists():
            files = list(frontend_dir.glob('*'))
            st.text(f"Files in frontend/: {[f.name for f in files]}")
except Exception as e:
    with placeholder.container():
        st.error("⚠️ Failed to load Axiom AI application")
        st.error(f"**Error:** `{str(e)}`")
        st.code(traceback.format_exc())
        
        st.info("""
        **Troubleshooting:**
        1. Check HuggingFace Space logs for detailed errors
        2. Verify all dependencies are installed
        3. Check that `BACKEND_URL` environment variable is set correctly
        """)
        
        st.text(f"Current directory: {Path(__file__).parent}")
        st.text(f"Frontend directory: {frontend_dir}")
        st.text(f"Frontend exists: {frontend_dir.exists()}")

