"""
Axiom AI - Streamlit App Entry Point for HuggingFace Spaces
"""
import sys
import os

# Print diagnostic info to container logs BEFORE Streamlit starts
print("=" * 60)
print("[streamlit_app.py] Starting Axiom AI frontend...")
print(f"[streamlit_app.py] Current directory: {os.getcwd()}")
print(f"[streamlit_app.py] Python path: {sys.path[:3]}")
print(f"[streamlit_app.py] BACKEND_URL: {os.getenv('BACKEND_URL', 'NOT SET')}")

# Check if key files exist
import pathlib
cwd = pathlib.Path.cwd()
print(f"[streamlit_app.py] app_hf.py exists: {(cwd / 'app_hf.py').exists()}")
print(f"[streamlit_app.py] frontend/ exists: {(cwd / 'frontend').exists()}")
if (cwd / 'frontend').exists():
    print(f"[streamlit_app.py] frontend/ui/ exists: {(cwd / 'frontend' / 'ui').exists()}")
print("=" * 60)
sys.stdout.flush()

import streamlit as st
import traceback

# Set page config immediately (must be first)
try:
    st.set_page_config(page_title="Axiom Enterprise", layout="wide")
except Exception:
    pass  # Already set, ignore

# Import app_hf module (don't use *)
try:
    print("[streamlit_app.py] Importing app_hf...")
    sys.stdout.flush()
    
    import app_hf
    
    print("[streamlit_app.py] app_hf imported successfully!")
    sys.stdout.flush()
    
except ImportError as e:
    print(f"[streamlit_app.py] ImportError: {e}")
    print(traceback.format_exc())
    sys.stdout.flush()
    
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
    st.text(f"Current directory: {pathlib.Path(__file__).parent}")
    if pathlib.Path("app_hf.py").exists():
        st.text("✅ app_hf.py found")
    else:
        st.text("❌ app_hf.py NOT found") 
        
except Exception as e:
    print(f"[streamlit_app.py] Unexpected error: {e}")
    print(traceback.format_exc())
    sys.stdout.flush()
    
    st.error("⚠️ Failed to load Axiom AI application")
    st.error(f"**Error:** `{str(e)}`")
    st.code(traceback.format_exc())
    
    st.info("""
    **Troubleshooting:**
    1. Check HuggingFace Space logs for detailed errors
    2. Verify all dependencies are installed
    3. Check that `BACKEND_URL` environment variable is set correctly
    """)
    
    st.text(f"Current directory: {pathlib.Path(__file__).parent}")

# --- MAIN APP EXECUTION ---
# This ensures the UI is re-rendered on every Streamlit rerun
if 'app_hf' in sys.modules:
    app_hf.main()

print("[streamlit_app.py] End of script")
sys.stdout.flush()
