import streamlit as st
from typing import List, Dict, Any


def init_state():
    if "messages" not in st.session_state:
        st.session_state.messages: List[Dict[str, Any]] = [
            {
                "role": "assistant",
                "content": "Hello. I am AXIOM. I have processed your documents. How can I help you today?",
            }
        ]
    if "drawer_open" not in st.session_state:
        st.session_state.drawer_open = False
    if "current_sources" not in st.session_state:
        st.session_state.current_sources = []
    if "awaiting_response" not in st.session_state:
        st.session_state.awaiting_response = False


def call_backend(question: str) -> Dict[str, Any]:
    backend_url = st.session_state.get("backend_url")
    if backend_url and st.session_state.get("backend_connected", False):
        import requests

        response = requests.post(
            f"{backend_url}/api/query",
            json={"question": question, "top_k": 3},
            timeout=30,
        )
        response.raise_for_status()
        return response.json()

    query_engine = st.session_state.get("query_engine")
    if query_engine:
        result = query_engine.query(question, top_k=3)
        sources = [
            {"text": chunk.text[:200] + "...", "metadata": chunk.metadata}
            for chunk in result.context_chunks
        ]
        return {"answer": result.answer, "sources": sources}

    raise RuntimeError("Backend not connected. Please check configuration.")


def render_chat(active_file: str | None = None):
    init_state()

    # Render existing messages with Streamlit chat components
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
            if message["role"] == "assistant" and message.get("sources"):
                with st.expander("📎 Sources"):
                    for source in message["sources"]:
                        st.write(source.get("metadata", {}).get("source", "Unknown"))

    st.markdown("<br>", unsafe_allow_html=True)

    # Input area (form for aligned input + button)
    with st.form(key="query_form", clear_on_submit=True):
        cols = st.columns([6, 1])
        with cols[0]:
            user_input = st.text_input(
                "Query",
                placeholder="Ask a follow-up...",
                label_visibility="collapsed",
            )
        with cols[1]:
            submit_button = st.form_submit_button("Send", type="primary", use_container_width=True)

        if submit_button and user_input.strip():
            st.session_state.messages.append({"role": "user", "content": user_input})
            st.session_state.awaiting_response = True
            st.rerun()

    # Handle assistant response if needed
    if st.session_state.awaiting_response and st.session_state.messages and st.session_state.messages[-1]["role"] == "user":
        last_question = st.session_state.messages[-1]["content"]
        try:
            with st.chat_message("assistant"):
                with st.spinner("Thinking..."):
                    result = call_backend(last_question)
                    answer = result.get("answer", "No answer returned.")
                    sources = result.get("sources", [])
                    st.markdown(answer)

            st.session_state.messages.append(
                {"role": "assistant", "content": answer, "sources": sources}
            )
        except Exception as e:
            error_msg = f"I encountered an error: {str(e)}"
            with st.chat_message("assistant"):
                st.error(error_msg)
            st.session_state.messages.append({"role": "assistant", "content": error_msg, "sources": []})
        finally:
            st.session_state.awaiting_response = False
