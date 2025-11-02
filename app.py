"""
Axiom AI - Frontend Only for HuggingFace Spaces

This app calls the backend API.
Backend should be deployed separately (Railway, Render, Fly.io, etc.)
"""

import streamlit as st
import requests
import os
from ui.theme import apply_theme
from ui.sidebar import render_sidebar
from ui.chat import render_chat
from ui.drawer import render_drawer
from ui.documents import render_documents
from ui.status import render_status

st.set_page_config(page_title="Axiom Enterprise", layout="wide")

apply_theme()

# Backend API URL (set via environment variable)
BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")

def check_backend():
    """Check if backend is reachable"""
    try:
        response = requests.get(f"{BACKEND_URL}/health", timeout=5)
        return response.status_code == 200, None
    except:
        return False, "Backend not reachable"

backend_connected, backend_error = check_backend()

status_class = "health-dot" if backend_connected else "health-dot-error"
status_text = "Backend Connected" if backend_connected else "Backend Offline"

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

if not backend_connected:
    st.warning(f"⚠️ Backend not connected. Set BACKEND_URL in Settings → Variables")
    st.info(f"Current: `{BACKEND_URL}`")

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

render_drawer()
