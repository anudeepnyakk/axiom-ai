"""
Axiom AI - Frontend Only (HuggingFace Spaces)

This is a frontend-only Streamlit app that calls the backend API.
Backend should be deployed separately (Railway, Render, Fly.io, etc.)
"""

import streamlit as st
import requests
import os
from ui.theme import apply_theme
from ui.sidebar import render_sidebar
from ui.chat_hf import render_chat  # Use API-based chat for HuggingFace
from ui.drawer import render_drawer
from ui.documents import render_documents
from ui.status import render_status

st.set_page_config(page_title="Axiom Enterprise", layout="wide")

apply_theme()

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

# Check backend connection
def check_backend_status():
    """Check if backend is reachable"""
    try:
        response = requests.get(f"{BACKEND_URL}/health", timeout=5)
        return response.status_code == 200, None
    except Exception as e:
        return False, str(e)

# Initialize backend status
backend_connected, backend_error = check_backend_status()

if backend_connected:
    status_class = "health-dot"
    status_text = "Backend Connected"
else:
    status_class = "health-dot-error"
    status_text = "Backend Offline"

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

# ✅ Drawer always rendered last (not in a tab)
render_drawer()



