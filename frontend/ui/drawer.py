import streamlit as st

def render_drawer():
    """Render sources in an expander in the main area instead of a drawer"""
    if not st.session_state.get("drawer_open", False):
        return
    
    # Show sources in an expander
    sources = st.session_state.get("current_sources", [])
    
    with st.expander("📄 **Retrieved Sources** (Click to collapse)", expanded=True):
        if sources:
            st.markdown("---")
            for i, source in enumerate(sources, 1):
                st.markdown(f"### Source {i}")
                
                # Show metadata
                metadata = source.get('metadata', {})
                # Try multiple metadata keys for source file
                source_file = (
                    metadata.get('source_file_path') or 
                    metadata.get('source') or 
                    metadata.get('filename') or
                    'Unknown'
                )
                # Clean up the file path to show just filename
                if source_file != 'Unknown':
                    import os
                    source_file = os.path.basename(source_file)
                
                st.markdown(f"**File:** `{source_file}`")
                
                # Show text in a code block (read-only and preserves formatting)
                st.markdown("**Retrieved Text:**")
                text = source.get('text', 'No text available')
                st.code(text, language=None)
                
                if i < len(sources):
                    st.markdown("---")
                    
            # Close button
            if st.button("✕ Close Sources", key="close_sources", use_container_width=True):
                st.session_state.drawer_open = False
                st.rerun()
        else:
            st.info("No sources available. Ask a question to see retrieved documents.")
            if st.button("Close", key="close_empty"):
                st.session_state.drawer_open = False
                st.rerun()
