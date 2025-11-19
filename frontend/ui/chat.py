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

    # Streamlit assistant style with circular avatars
    st.markdown("""
        <style>
        /* Message container */
        .chat-message {
            display: flex;
            align-items: flex-start;
            margin-bottom: 2rem;
            gap: 1rem;
        }
        
        /* Circular avatar */
        .message-avatar {
            width: 40px;
            height: 40px;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 18px;
            font-weight: 600;
            flex-shrink: 0;
            box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        }
        
        .user-avatar {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
        }
        
        .bot-avatar {
            background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
            color: white;
        }
        
        /* Message content */
        .message-content {
            flex: 1;
            padding-top: 0.5rem;
        }
        
        .message-text {
            font-size: 15px;
            line-height: 1.6;
            color: #31333F;
            font-family: 'Source Sans Pro', sans-serif;
        }
        
        /* User message styling */
        .user-message .message-text {
            background: #F0F2F6;
            padding: 1rem 1.25rem;
            border-radius: 8px;
            display: inline-block;
        }
        
        /* Bot message styling */
        .bot-message .message-text {
            padding: 0.5rem 0;
        }
        
        /* Sources button container */
        .sources-container {
            margin-top: 0.75rem;
        }
        
        /* Input container at bottom */
        .input-container {
            position: sticky;
            bottom: 0;
            background: #FAFAFA;
            padding: 1.5rem 0;
            margin-top: 2rem;
        }
        
        /* Hide default form styling */
        .stForm {
            background: transparent !important;
            border: none !important;
        }
        
        /* Title styling */
        .chat-title {
            font-size: 32px;
            font-weight: 700;
            color: #31333F;
            margin-bottom: 2rem;
            text-align: center;
        }
        </style>
    """, unsafe_allow_html=True)

    # Show title if no chat history
    if not st.session_state.chat_history:
        st.markdown('<div class="chat-title">Axiom AI assistant</div>', unsafe_allow_html=True)

    # Render chat history with Streamlit assistant style
    for i, item in enumerate(st.session_state.chat_history):
        if len(item) == 2:
            role, msg = item
            sources = []
        else:
            role, msg, sources = item
        
        if role == "user":
            st.markdown(f"""
                <div class="chat-message user-message">
                    <div class="message-avatar user-avatar">G</div>
                    <div class="message-content">
                        <div class="message-text">{msg}</div>
                    </div>
                </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
                <div class="chat-message bot-message">
                    <div class="message-avatar bot-avatar">A</div>
                    <div class="message-content">
                        <div class="message-text">{msg}</div>
                    </div>
                </div>
            """, unsafe_allow_html=True)
            
            # Sources button below bot message
            if sources:
                col_spacer, col_btn = st.columns([0.7, 11])
                with col_btn:
                    if st.button(f"📎 {len(sources)} sources", key=f"src_{i}", use_container_width=False):
                        st.session_state.current_sources = sources
                        st.session_state.drawer_open = True
                        if 'uploading' not in st.session_state or not st.session_state.uploading:
                            st.rerun()

    # Input box at bottom
    st.markdown('<div class="input-container"></div>', unsafe_allow_html=True)
    
    with st.form("chat_input", clear_on_submit=True):
        text = st.text_input(
            "Message",
            label_visibility="collapsed",
            placeholder="Ask a follow-up..."
        )
        col1, col2 = st.columns([1, 11])
        with col2:
            sent = st.form_submit_button("Send", type="primary", use_container_width=False)

    if sent and text.strip():
        st.session_state.chat_history.append(("user", text))
        
        # Check if we're in HuggingFace mode (API-based)
        backend_url = st.session_state.get('backend_url')
        backend_connected = st.session_state.get('backend_connected', False)
        
        if backend_connected and backend_url:
            # HuggingFace mode: use API calls
            # Show a simple message instead of spinner
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
                    error_msg = f"I encountered an error while processing your request: {str(e)}\n\nPlease check the backend connection."
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
            st.session_state.chat_history.append(("bot", "I'm unable to connect to the backend. Please check the configuration.", []))
        
        # Safe rerun - only if not currently uploading
        if 'uploading' not in st.session_state or not st.session_state.uploading:
            st.rerun()
