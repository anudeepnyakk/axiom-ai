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

# Try to import UI components with error handling
try:
    from ui.theme import apply_theme
    from ui.sidebar import render_sidebar
    from ui.chat import render_chat
    from ui.drawer import render_drawer
    from ui.documents import render_documents
    from ui.status import render_status
except ImportError as e:
    st.error(f"⚠️ Import Error: {str(e)}")
    st.code(traceback.format_exc())
    st.info("Check that all UI modules exist in frontend/ui/")
    st.stop()
except Exception as e:
    st.error(f"⚠️ Error loading UI: {str(e)}")
    st.code(traceback.format_exc())
    st.stop()

try:
    apply_theme()
except Exception as e:
    st.warning(f"⚠️ Theme Error: {str(e)}")
    # Continue anyway

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
        # Use shorter timeout to prevent hanging
        response = requests.get(f"{BACKEND_URL}/health", timeout=2)
        return response.status_code == 200, None
    except requests.exceptions.Timeout:
        return False, "Connection timeout"
    except requests.exceptions.ConnectionError:
        return False, "Connection refused"
    except Exception as e:
        return False, str(e)

# Initialize backend status (with error handling, non-blocking)
# Wrap in try-except to prevent crashes
try:
    backend_connected, backend_error = check_backend_status()
except Exception as e:
    backend_connected = False
    backend_error = str(e)
    # Don't show warning here - will show below if needed

if backend_connected:
    status_class = "health-dot"
    status_text = "Backend Connected"
else:
    status_class = "health-dot-error"
    status_text = "Backend Offline"

# Show header with backend status
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
    st.warning(f"⚠️ Backend not connected. Set BACKEND_URL environment variable.")
    st.info(f"Current backend URL: `{BACKEND_URL}`")
    st.code(f"# Set in HF Spaces Settings → Variables:\nBACKEND_URL=https://your-backend-url.com")

# Store backend URL in session state for chat component
st.session_state['backend_url'] = BACKEND_URL
st.session_state['backend_connected'] = backend_connected

# Wrap entire app rendering in error handling to prevent blank screens
try:
    # Render UI components with error handling
    try:
        render_sidebar()
    except Exception as e:
        st.error(f"⚠️ Sidebar Error: {str(e)}")
        st.code(traceback.format_exc())

    try:
        tab1, tab2 = st.tabs(["💬 Intelligence", "📊 SystemOps"])

        with tab1:
            try:
                render_chat()
            except Exception as e:
                st.error(f"⚠️ Chat Error: {str(e)}")
                st.code(traceback.format_exc())

        with tab2:
            col1, col2 = st.columns([2, 1])
            with col1:
                try:
                    render_documents()
                except Exception as e:
                    st.error(f"⚠️ Documents Error: {str(e)}")
            with col2:
                try:
                    render_status()
                except Exception as e:
                    st.error(f"⚠️ Status Error: {str(e)}")
    except Exception as e:
        st.error(f"⚠️ Tabs Error: {str(e)}")
        st.code(traceback.format_exc())

    # ✅ Drawer always rendered last (not in a tab)
    try:
        render_drawer()
    except Exception as e:
        st.warning(f"⚠️ Drawer Error: {str(e)}")

except Exception as e:
    # Global error handler - catches any uncaught exceptions
    st.error("⚠️ **Application Error**")
    st.error(f"An unexpected error occurred: {str(e)}")
    st.code(traceback.format_exc())
    st.info("""
    **This error was caught to prevent a blank screen.**
    
    Please report this error with the traceback above.
    """)



