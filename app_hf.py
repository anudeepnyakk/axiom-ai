"""
Axiom AI - Split-Pane RAG Interface (HuggingFace Spaces)

Production-grade RAG interface with split-pane layout:
- Left: PDF viewer (source document)
- Right: Chat interface (intelligence)
- Sidebar: Uploads, metrics, and system health
"""

import streamlit as st
import requests
import os
import traceback
from streamlit_pdf_viewer import pdf_viewer

# Try to import UI components with error handling
try:
    from frontend.ui.theme import apply_theme
    from frontend.ui.sidebar import render_sidebar
    from frontend.ui.chat import render_chat_split_pane
except ImportError as e:
    st.error(f"⚠️ Import Error: {str(e)}")
    st.code(traceback.format_exc())
    st.info("Check that all UI modules exist in frontend/ui/")
    st.stop()
except Exception as e:
    st.error(f"⚠️ Error loading UI: {str(e)}")
    st.code(traceback.format_exc())
    st.stop()

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
    """Main application entry point"""
    # Apply theme FIRST
    try:
        apply_theme()
    except Exception as e:
        st.warning(f"⚠️ Theme Error: {str(e)}")

    # Initialize backend status
    try:
        backend_connected, backend_error = check_backend_status()
    except Exception as e:
        backend_connected = False
        backend_error = str(e)

    # Store in session state
    st.session_state['backend_url'] = BACKEND_URL
    st.session_state['backend_connected'] = backend_connected

    # Render sidebar (uploads, metrics, settings)
    try:
        processed_files, active_file = render_sidebar()
    except Exception as e:
        st.sidebar.error(f"⚠️ Sidebar Error: {str(e)}")
        st.sidebar.code(traceback.format_exc())
        processed_files = {}
        active_file = None

    # Main split-pane layout
    try:
        # Check if we have an uploaded file to display
        uploaded_file = st.session_state.get('current_pdf_file')
        
        if uploaded_file or active_file:
            # Split-pane layout: Document (left) + Chat (right)
            doc_col, chat_col = st.columns([5, 4])

            with doc_col:
                st.markdown("### 📄 Source Document")
                
                # Display PDF if we have binary data
                if uploaded_file:
                    try:
                        binary_data = uploaded_file.getvalue()
                        pdf_viewer(input=binary_data, width=700)
                    except Exception as e:
                        st.error(f"Error displaying PDF: {str(e)}")
                        st.info("PDF viewer requires the file to be uploaded. Please upload a PDF in the sidebar.")
                else:
                    st.info("👈 Upload a PDF in the sidebar to view it here")

            with chat_col:
                st.markdown("### 🤖 Intelligence")
                
                # Render chat interface with split-pane styling
                try:
                    render_chat_split_pane(active_file)
                except Exception as e:
                    st.error(f"⚠️ Chat Error: {str(e)}")
                    st.code(traceback.format_exc())

        else:
            # Empty state - no document uploaded
            st.info("👈 Upload a document in the sidebar to activate Axiom.")
            
            # Show backend status if disconnected
            if not backend_connected:
                st.warning(f"⚠️ Backend not connected. Set BACKEND_URL environment variable.")
                st.info(f"Current backend URL: `{BACKEND_URL}`")
                st.code(f"# Set in HF Spaces Settings → Variables:\nBACKEND_URL=https://your-backend-url.com")

    except Exception as e:
        st.error("⚠️ **Application Error**")
        st.error(f"An unexpected error occurred: {str(e)}")
        st.code(traceback.format_exc())
        st.info("Try refreshing the page (F5).")

# Only run main if this file is executed directly (not imported)
if __name__ == "__main__":
    main()
