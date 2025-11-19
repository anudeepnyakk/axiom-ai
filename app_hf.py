"""
Axiom AI - Frontend Only (HuggingFace Spaces)

This is a frontend-only Streamlit app that calls the backend API.
Backend should be deployed separately (Railway, Render, Fly.io, etc.)
"""

import streamlit as st
import requests
import os
import traceback

# Note: Page config is set in streamlit_app.py to ensure it's set first

# Import UI components
from frontend.ui.theme import apply_theme
from frontend.ui.sidebar import render_sidebar
from frontend.ui.chat import render_chat
from frontend.ui.drawer import render_drawer
from frontend.ui.documents import render_documents
from frontend.ui.status import render_status

# Backend API URL (set via environment variable or default)
BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")

def query_backend(question: str, top_k: int = 3):
    """Query the backend API"""
    try:
        response = requests.post(
            f"{BACKEND_URL}/api/query",
            json={"question": question, "top_k": top_k},
            timeout=30
        )
        response.raise_for_status()
        return response.json()
    except Exception as e:
        return {"error": str(e), "answer": None, "sources": []}

# Check backend connection (non-blocking, with timeout)
def check_backend_status():
    """Check if backend is reachable"""
    try:
        response = requests.get(f"{BACKEND_URL}/health", timeout=2)
        return response.status_code == 200, None
    except requests.exceptions.Timeout:
        return False, "Connection timeout"
    except requests.exceptions.ConnectionError:
        return False, "Connection refused"
    except Exception as e:
        return False, str(e)

def main():
    """Main app function - called on every Streamlit rerun"""
    print("[app_hf.py] main() called")
    import sys
    sys.stdout.flush()
    
    # Apply theme
    try:
        apply_theme()
    except Exception as e:
        st.warning(f"⚠️ Theme Error: {str(e)}")
    
    # Check backend
    try:
        backend_connected, backend_error = check_backend_status()
    except Exception as e:
        backend_connected = False
        backend_error = str(e)

    if backend_connected:
        status_class = "health-dot"
        status_text = "Backend Connected"
    else:
        status_class = "health-dot-error"
        status_text = "Backend Offline"

    # Show header
    st.markdown(f"""
    <div class="header">
      <div class="header-left">
        <span class="logo">AXIOM</span>
        <span class="tagline">Grounded intelligence.</span>
      </div>
      <div class="header-right">
        <span class="{status_class}"></span>
        <span class="health-text">{status_text}</span>
      </div>
    </div>
    """, unsafe_allow_html=True)

    # Show backend status
    if not backend_connected:
        st.warning(f"⚠️ Backend not connected")
        st.info(f"Backend URL: `{BACKEND_URL}`")

    # Store in session state
    st.session_state['backend_url'] = BACKEND_URL
    st.session_state['backend_connected'] = backend_connected

    # Render UI
    try:
        render_sidebar()
        
        tab1, tab2 = st.tabs(["💬 Intelligence", "📊 SystemOps"])
        with tab1:
            render_chat()
        with tab2:
            col1, col2 = st.columns([2, 1])
            with col1:
                render_documents()
            with col2:
                render_status()
        
        render_drawer()
        
    except Exception as e:
        st.error(f"⚠️ Error: {str(e)}")
        st.code(traceback.format_exc())

# Only run main if this file is executed directly (not imported)
if __name__ == "__main__":
    main()



