import streamlit as st
import sys
from pathlib import Path
import json

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

def render_documents():
    st.subheader("📄 Documents")
    
    # Load actual processed files
    frontend_dir = Path(__file__).parent.parent
    tracker_file = frontend_dir / "processed_files.json"
    
    if tracker_file.exists():
        try:
            with open(tracker_file, 'r') as f:
                processed = json.load(f)
            
            if processed:
                st.success(f"✅ {len(processed)} document(s) in index")
                
                for filename, info in processed.items():
                    chunk_count = info.get('chunk_count', '?')
                    with st.expander(f"📄 {filename}"):
                        st.metric("Chunks", chunk_count)
                        st.text(f"Status: Indexed")
                        if 'timestamp' in info:
                            st.caption(f"Last modified: {info['timestamp'][:10]}")
            else:
                st.info("No documents indexed yet. Upload documents in the sidebar.")
        except Exception as e:
            st.error(f"Error loading documents: {e}")
    else:
        st.info("No documents indexed yet. Upload documents in the sidebar.")
