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
    
    # Apply theme FIRST
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

    # Header row (title + status) – avoids duplicate headers
    title_col, status_col = st.columns([4, 1])
    with title_col:
        st.markdown(
            '**AXIOM** <span style="color:#9ca3af; font-weight:400;">Grounded intelligence.</span>',
            unsafe_allow_html=True,
        )

    with status_col:
        status_class = "status-green" if backend_connected else "status-red"
        status_text = "Backend Connected" if backend_connected else "Backend Offline"
        st.markdown(
            f"""
            <div style="text-align: right; font-size: 0.875rem; color: #4b5563;">
                <span class="status-indicator {status_class}"></span>{status_text}
            </div>
            """,
            unsafe_allow_html=True,
        )
        if not backend_connected:
            st.caption(f"`{BACKEND_URL}`")

    # Store in session state
    st.session_state['backend_url'] = BACKEND_URL
    st.session_state['backend_connected'] = backend_connected

    # Render UI with centered layout wrapper
    try:
        processed_files, active_file = render_sidebar()
        
        # Page Layout Rewrite - Centered container like Streamlit assistant
        with st.container():
            st.markdown('<div class="main-block">', unsafe_allow_html=True)
            
            tab1, tab2 = st.tabs(["🧠 Intelligence", "📊 SystemOps"])
            
            with tab1:
                st.markdown('<div class="chat-container">', unsafe_allow_html=True)
                render_chat(active_file=active_file)
                st.markdown('</div>', unsafe_allow_html=True)
            
            with tab2:
                col1, col2 = st.columns([2, 1])
                with col1:
                    render_documents(processed_files)
                with col2:
                    render_status()
            
            st.markdown("</div>", unsafe_allow_html=True)
        
        render_drawer()
        
    except Exception as e:
        st.error(f"⚠️ Error: {str(e)}")
        st.code(traceback.format_exc())

# Only run main if this file is executed directly (not imported)
if __name__ == "__main__":
    main()
