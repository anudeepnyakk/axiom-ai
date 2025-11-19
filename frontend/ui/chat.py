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

    # ChatGPT-style container with max width
    st.markdown("""
        <style>
        /* ChatGPT-style centered chat container */
        .chat-container {
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
        }
        
        /* User message - ChatGPT style */
        .user-message {
            background: #F7F7F8;
            color: #0D0D0D;
            padding: 16px 20px;
            margin: 20px 0;
            border-radius: 10px;
            font-size: 15px;
            line-height: 1.6;
        }
        
        /* Bot message - ChatGPT style */
        .bot-message {
            background: transparent;
            color: #0D0D0D;
            padding: 16px 20px;
            margin: 20px 0;
            border-radius: 10px;
            font-size: 15px;
            line-height: 1.75;
        }
        
        /* Avatar styles */
        .message-avatar {
            width: 32px;
            height: 32px;
            border-radius: 4px;
            display: inline-block;
            text-align: center;
            line-height: 32px;
            font-weight: 600;
            margin-right: 12px;
            vertical-align: top;
        }
        
        .user-avatar {
            background: #5436DA;
            color: white;
        }
        
        .bot-avatar {
            background: #19C37D;
            color: white;
        }
        
        /* Message content */
        .message-content {
            display: inline-block;
            vertical-align: top;
            width: calc(100% - 50px);
            padding-top: 4px;
        }
        
        /* Input styling */
        .stTextInput input {
            border-radius: 12px !important;
            border: 1px solid #D1D5DB !important;
            padding: 14px 16px !important;
            font-size: 15px !important;
        }
        
        .stTextInput input:focus {
            border-color: #5436DA !important;
            box-shadow: 0 0 0 1px #5436DA !important;
        }
        
        /* Hide Streamlit form elements */
        .stForm {
            background: transparent !important;
            border: none !important;
        }
        
        /* Sources button */
        .sources-btn {
            margin-top: 8px;
            padding: 6px 12px;
            background: #F3F4F6;
            border: 1px solid #E5E7EB;
            border-radius: 6px;
            font-size: 13px;
            color: #374151;
            cursor: pointer;
            display: inline-block;
        }
        
        .sources-btn:hover {
            background: #E5E7EB;
        }
        </style>
    """, unsafe_allow_html=True)

    # Render chat history with ChatGPT style
    for i, item in enumerate(st.session_state.chat_history):
        if len(item) == 2:
            role, msg = item
            sources = []
        else:
            role, msg, sources = item
        
        if role == "user":
            st.markdown(f"""
                <div class="user-message">
                    <span class="message-avatar user-avatar">👤</span>
                    <div class="message-content">{msg}</div>
                </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
                <div class="bot-message">
                    <span class="message-avatar bot-avatar">AI</span>
                    <div class="message-content">{msg}</div>
                </div>
            """, unsafe_allow_html=True)
            
            # Sources button below bot message
            if sources:
                col1, col2 = st.columns([1, 4])
                with col1:
                    if st.button(f"📎 View {len(sources)} sources", key=f"src_{i}", use_container_width=False):
                        st.session_state.current_sources = sources
                        st.session_state.drawer_open = True
                        if 'uploading' not in st.session_state or not st.session_state.uploading:
                            st.rerun()

    # Spacing before input
    st.markdown("<div style='margin-top: 40px;'></div>", unsafe_allow_html=True)

    # Input box - ChatGPT style at bottom
    with st.form("chat_input", clear_on_submit=True):
        col1, col2 = st.columns([6, 1])
        with col1:
            text = st.text_input("Message Axiom", label_visibility="collapsed", placeholder="Ask anything about your documents...")
        with col2:
            sent = st.form_submit_button("Send", use_container_width=True)

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
