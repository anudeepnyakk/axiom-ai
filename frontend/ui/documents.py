import streamlit as st
import sys
from pathlib import Path
import json
import os
import pandas as pd

# Check if we're in HuggingFace mode (frontend-only)
HF_MODE = os.getenv("BACKEND_URL") is not None and os.getenv("BACKEND_URL") != "http://localhost:8000"

def get_processed_files():
    """Helper to get documents for the main view"""
    if HF_MODE:
        try:
            import requests
            backend_url = st.session_state.get('backend_url', os.getenv('BACKEND_URL'))
            if not backend_url:
                return {}
            response = requests.get(f"{backend_url}/api/documents", timeout=5)
            if response.status_code == 200:
                return response.json().get('documents', {})
        except:
            pass
    return {}

def render_documents():
    st.markdown("### 📄 Document Index")
    
    files = get_processed_files()
    
    if files:
        # Convert to dataframe for nice display
        data = []
        for filename, info in files.items():
            data.append({
                "Document Name": filename,
                "Chunks": info.get('chunk_count', 0),
                "Status": "✅ Indexed",
                "Type": "PDF" if filename.lower().endswith('.pdf') else "Text"
            })
        
        df = pd.DataFrame(data)
        st.dataframe(
            df,
            column_config={
                "Document Name": st.column_config.TextColumn("Document", width="large"),
                "Chunks": st.column_config.NumberColumn("Chunks", format="%d"),
                "Status": st.column_config.TextColumn("Status"),
                "Type": st.column_config.TextColumn("Type")
            },
            use_container_width=True,
            hide_index=True
        )
        
        st.caption(f"Total documents: {len(files)}")
    else:
        st.info("No documents found. Upload files using the sidebar to get started.")
