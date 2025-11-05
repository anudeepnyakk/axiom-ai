"""
Axiom AI - Streamlit App Entry Point for HuggingFace Spaces

HuggingFace Spaces expects streamlit_app.py when using Streamlit template.
This file imports our frontend-only app_hf.py which calls the backend API.
"""

import streamlit as st
import sys
import traceback
from pathlib import Path

# Set page config immediately
st.set_page_config(page_title="Axiom Enterprise", layout="wide")

# Add frontend directory to path so imports work
frontend_dir = Path(__file__).parent / "frontend"
sys.path.insert(0, str(frontend_dir))
sys.path.insert(0, str(Path(__file__).parent))

# Import frontend-only app with error handling
try:
    from app_hf import *
except Exception as e:
    st.error("⚠️ Failed to load Axiom AI application")
    st.error(f"Error: {str(e)}")
    st.code(traceback.format_exc())
    
    # Show helpful message
    st.info("""
    **Troubleshooting:**
    1. Check that all files are present in the `frontend/` directory
    2. Check HuggingFace Space logs for detailed errors
    3. Verify `BACKEND_URL` environment variable is set correctly
    """)
    
    # Show current path info
    st.text(f"Current directory: {Path(__file__).parent}")
    st.text(f"Frontend directory: {frontend_dir}")
    st.text(f"Frontend exists: {frontend_dir.exists()}")
    
    if frontend_dir.exists():
        st.text(f"Files in frontend/: {list(frontend_dir.glob('*'))}")

