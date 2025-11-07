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

# SHOW IMMEDIATE CONTENT TO DEBUG
st.write("# DEBUG: Streamlit is running")
st.write(f"Python path: {sys.path[:3]}")

# Add frontend directory to path so imports work
frontend_dir = Path(__file__).parent / "frontend"
sys.path.insert(0, str(frontend_dir))
sys.path.insert(0, str(Path(__file__).parent))

st.write(f"Frontend dir: {frontend_dir}")
st.write(f"Frontend exists: {frontend_dir.exists()}")

if frontend_dir.exists():
    files = list(frontend_dir.glob('*.py'))
    st.write(f"Python files in frontend/: {[f.name for f in files]}")

# Try importing
st.write("Attempting import...")
try:
    import app_hf
    st.write("✅ Import successful!")
    st.write(f"app_hf module: {app_hf}")
    st.write(f"app_hf file: {app_hf.__file__ if hasattr(app_hf, '__file__') else 'N/A'}")
except ImportError as e:
    st.error(f"❌ Import failed: {e}")
    st.code(traceback.format_exc())
except Exception as e:
    st.error(f"❌ Exception during import: {e}")
    st.code(traceback.format_exc())

st.write("End of streamlit_app.py")
