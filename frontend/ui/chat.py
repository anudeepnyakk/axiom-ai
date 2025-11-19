import streamlit as st

def init_state():
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []
    if "drawer_open" not in st.session_state:
        st.session_state.drawer_open = False
    if "current_sources" not in st.session_state:
        st.session_state.current_sources = []

def render_chat():
    init_state()
    
    # Get query engine from parent app
    query_engine = st.session_state.get('query_engine')

    # Render chat history - EXACT Streamlit assistant style
    for i, item in enumerate(st.session_state.chat_history):
        if len(item) == 2:
            role, msg = item
            sources = []
        else:
            role, msg, sources = item
        
        if role == "user":
            st.markdown(f'<div class="user-msg">{msg}</div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="bot-msg">{msg}</div>', unsafe_allow_html=True)
            
            # Sources button
            if sources:
                if st.button(f"📎 {len(sources)} sources", key=f"src_{i}", use_container_width=False):
                    st.session_state.current_sources = sources
                    st.session_state.drawer_open = True
                    if 'uploading' not in st.session_state or not st.session_state.uploading:
                        st.rerun()

    # Text Input + Button Row - EXACT Streamlit assistant style
    col1, col2 = st.columns([6, 1])
    with col1:
        user_query = st.text_input("Ask Axiom…", key="chat_input", label_visibility="collapsed", placeholder="Ask a follow-up...")
    with col2:
        send = st.button("Send", use_container_width=True, type="primary")

    if send and user_query.strip():
        st.session_state.chat_history.append(("user", user_query))
        
        # Check if we're in HuggingFace mode (API-based)
        backend_url = st.session_state.get('backend_url')
        backend_connected = st.session_state.get('backend_connected', False)
        
        if backend_connected and backend_url:
            # HuggingFace mode: use API calls
            with st.spinner(""):
                try:
                    import requests
                    response = requests.post(
                        f"{backend_url}/api/query",
                        json={"question": user_query, "top_k": 3},
                        timeout=30
                    )
                    response.raise_for_status()
                    result = response.json()
                    answer = result.get("answer", "No answer returned.")
                    sources = result.get("sources", [])
                    st.session_state.chat_history.append(("bot", answer, sources))
                except Exception as e:
                    error_msg = f"I encountered an error: {str(e)}\n\nPlease check backend connection."
                    st.session_state.chat_history.append(("bot", error_msg, []))
        elif query_engine:
            # Local mode: use query engine directly
            with st.spinner(""):
                try:
                    result = query_engine.query(user_query, top_k=3)
                    answer = result.answer
                    sources = [{"text": chunk.text[:200] + "...", "metadata": chunk.metadata} 
                              for chunk in result.context_chunks]
                    st.session_state.chat_history.append(("bot", answer, sources))
                except Exception as e:
                    error_msg = f"I encountered an error: {str(e)}\n\nPlease make sure documents are ingested."
                    st.session_state.chat_history.append(("bot", error_msg, []))
        else:
            st.session_state.chat_history.append(("bot", "Backend not connected. Please check configuration.", []))
        
        # Safe rerun - only if not currently uploading
        if 'uploading' not in st.session_state or not st.session_state.uploading:
            st.rerun()
