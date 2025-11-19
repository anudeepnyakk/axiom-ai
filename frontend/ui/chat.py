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

    # Streamlit AI assistant exact styling
    st.markdown("""
        <style>
        /* Message bubbles */
        .user-msg {
            background: #F0F2F6;
            padding: 12px 16px;
            border-radius: 12px;
            margin-bottom: 16px;
            max-width: 80%;
            margin-left: auto;
            font-size: 15px;
            line-height: 1.6;
            color: #31333F;
        }
        
        .bot-msg {
            background: transparent;
            padding: 12px 0;
            margin-bottom: 16px;
            font-size: 15px;
            line-height: 1.7;
            color: #31333F;
        }
        
        /* Circular avatars */
        .message-with-avatar {
            display: flex;
            gap: 12px;
            margin-bottom: 20px;
        }
        
        .avatar {
            width: 36px;
            height: 36px;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 16px;
            font-weight: 600;
            flex-shrink: 0;
        }
        
        .user-avatar {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
        }
        
        .bot-avatar {
            background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
            color: white;
        }
        
        .message-content {
            flex: 1;
            padding-top: 6px;
        }
        
        /* Sources button */
        .sources-btn-container {
            margin-left: 48px;
            margin-top: -8px;
            margin-bottom: 16px;
        }
        </style>
    """, unsafe_allow_html=True)

    # Render chat history
    for i, item in enumerate(st.session_state.chat_history):
        if len(item) == 2:
            role, msg = item
            sources = []
        else:
            role, msg, sources = item
        
        if role == "user":
            # User message (right-aligned bubble)
            st.markdown(f'<div class="user-msg">{msg}</div>', unsafe_allow_html=True)
        else:
            # Bot message (left-aligned with avatar)
            st.markdown(f"""
                <div class="message-with-avatar">
                    <div class="avatar bot-avatar">A</div>
                    <div class="message-content">
                        <div class="bot-msg">{msg}</div>
                    </div>
                </div>
            """, unsafe_allow_html=True)
            
            # Sources button
            if sources:
                st.markdown('<div class="sources-btn-container">', unsafe_allow_html=True)
                if st.button(f"📎 {len(sources)} sources", key=f"src_{i}", use_container_width=False):
                    st.session_state.current_sources = sources
                    st.session_state.drawer_open = True
                    if 'uploading' not in st.session_state or not st.session_state.uploading:
                        st.rerun()
                st.markdown('</div>', unsafe_allow_html=True)

    # Spacing before input
    st.markdown("<br>", unsafe_allow_html=True)

    # Input form - Streamlit assistant style
    with st.form("chat_input", clear_on_submit=True):
        col1, col2 = st.columns([6, 1])
        with col1:
            text = st.text_input(
                "Message",
                label_visibility="collapsed",
                placeholder="Ask a follow-up...",
                key="chat_input_field"
            )
        with col2:
            sent = st.form_submit_button("Send", type="primary", use_container_width=True)

    if sent and text.strip():
        st.session_state.chat_history.append(("user", text))
        
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
                        json={"question": text, "top_k": 3},
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
                    result = query_engine.query(text, top_k=3)
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
