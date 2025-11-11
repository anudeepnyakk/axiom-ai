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

# Import and EXECUTE the frontend app
# Using "from app_hf import *" to execute its top-level code
try:
    from app_hf import *
except ImportError as e:
    st.error("⚠️ Import Error - Failed to load Axiom AI application")
    st.error(f"**Error:** `{str(e)}`")
    st.code(traceback.format_exc())
    
    st.info("""
    **Troubleshooting:**
    1. Check that `app_hf.py` is present in the root directory
    2. Check HuggingFace Space logs for detailed errors
    3. Verify `BACKEND_URL` environment variable is set correctly
    """)
    
    # Show diagnostic info
    st.text(f"Current directory: {Path(__file__).parent}")
    if Path("app_hf.py").exists():
        st.text("✅ app_hf.py found")
    else:
        st.text("❌ app_hf.py NOT found")
except Exception as e:
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
