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
    
    # Backend connection handled in parent app

    # render history with proper chat layout
    for i, item in enumerate(st.session_state.chat_history):
        if len(item) == 2:
            role, msg = item
            sources = []
        else:
            role, msg, sources = item
        
        # Create columns for proper alignment
        if role == "user":
            # User messages on the right
            col1, col2 = st.columns([1, 4])
            with col2:
                st.markdown(f"""
                <div style='display: flex; justify-content: flex-end; margin: 8px 0;'>
                    <div style='background: #1A73E8; color: white; padding: 12px 18px; 
                                border-radius: 18px 18px 4px 18px; max-width: 80%;
                                box-shadow: 0 2px 4px rgba(0,0,0,0.1);'>
                        {msg}
                    </div>
                </div>
                """, unsafe_allow_html=True)
        else:
            # Bot messages on the left
            col1, col2 = st.columns([4, 1])
            with col1:
                st.markdown(f"""
                <div style='display: flex; justify-content: flex-start; margin: 8px 0;'>
                    <div style='background: #F3F4F6; color: #111827; padding: 12px 18px; 
                                border-radius: 18px 18px 18px 4px; max-width: 80%;
                                box-shadow: 0 2px 4px rgba(0,0,0,0.08);'>
                        {msg}
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                # Sources button below bot message
                if sources:
                    if st.button(f"📎 {len(sources)} Sources", key=f"chip_{i}", use_container_width=False):
                        st.session_state.current_sources = sources
                        st.session_state.drawer_open = True
                        st.rerun()

    # input box
    with st.form("chat_input", clear_on_submit=True):
        text = st.text_input("Ask Axiom…")
        sent = st.form_submit_button("Send")

    if sent and text.strip():
        st.session_state.chat_history.append(("user", text))
        
        # Get backend URL from session state
        backend_url = st.session_state.get('backend_url')
        backend_connected = st.session_state.get('backend_connected', False)
        
        # Query backend API if available
        if backend_connected and backend_url:
            with st.spinner("🔍 Searching knowledge base..."):
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
                    error_msg = f"⚠️ Error: {str(e)}\n\nPlease check backend connection."
                    st.session_state.chat_history.append(("bot", error_msg, []))
        else:
            st.session_state.chat_history.append(("bot", "⚠️ Backend not connected. Please set BACKEND_URL environment variable.", []))
        
        st.rerun()
