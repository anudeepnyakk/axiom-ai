import streamlit as st
import sys
from pathlib import Path

# Add parent directory to path to import axiom
sys.path.insert(0, str(Path(__file__).parent.parent))

from ui.theme import apply_theme
from ui.sidebar import render_sidebar
from ui.chat import render_chat
from ui.drawer import render_drawer
from ui.documents import render_documents
from ui.status import render_status

# Import backend
from axiom.config.loader import load_config
from axiom.core.factory import create_query_engine

st.set_page_config(page_title="Axiom Enterprise", layout="wide")

apply_theme()

# Initialize backend (cached) - moved after theme to show errors
@st.cache_resource
def get_query_engine():
    try:
        config = load_config()
        query_engine = create_query_engine(config)
        return query_engine, None
    except Exception as e:
        import traceback
        return None, f"{str(e)}\n\n{traceback.format_exc()}"

# Try to load backend
try:
    query_engine, error = get_query_engine()
    # Store in session state for chat component
    st.session_state['query_engine'] = query_engine
except Exception as e:
    query_engine = None
    error = f"Critical error loading backend: {str(e)}"

# Determine backend status
if error:
    status_class = "health-dot-error"
    status_text = f"Backend Error"
elif query_engine:
    status_class = "health-dot"
    status_text = "Backend Connected"
else:
    status_class = "health-dot-warning"
    status_text = "Backend Loading"

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

# Show error if backend failed
if error:
    st.error(f"⚠️ Backend initialization failed: {error}")
    st.info("💡 Make sure documents are ingested: `python scripts/ingest.py`")

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
