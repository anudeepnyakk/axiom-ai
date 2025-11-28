"""
Chat Interface - Split-Pane RAG Layout

Enhanced chat with status indicators showing RAG pipeline steps.
"""

import streamlit as st
from typing import List, Dict, Any


def init_state():
    """Initialize session state for chat"""
    if "messages" not in st.session_state:
        st.session_state.messages: List[Dict[str, Any]] = [
            {
                "role": "assistant",
                "content": "Hello. I am AXIOM. I have processed your documents. How can I help you today?",
            }
        ]
    if "current_sources" not in st.session_state:
        st.session_state.current_sources = []
    if "awaiting_response" not in st.session_state:
        st.session_state.awaiting_response = False


def call_backend(question: str) -> Dict[str, Any]:
    """Call backend API or local query engine"""
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


def render_chat_split_pane(active_file: str | None = None):
    """
    Render chat interface optimized for split-pane layout.
    Shows RAG pipeline status indicators.
    """
    init_state()
    
    # Chat container with fixed height (scrollable)
    messages_container = st.container(height=600)

    # Render existing messages
    with messages_container:
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])
                
                # Show sources for assistant messages
                if message["role"] == "assistant" and message.get("sources"):
                    with st.expander("📚 View Sources"):
                        for idx, source in enumerate(message["sources"], 1):
                            source_name = source.get("metadata", {}).get("source", "Unknown")
                            similarity = source.get("similarity", "N/A")
                            st.info(f"**Source {idx}:** {source_name}\n\nSimilarity: {similarity}")
                            if source.get("text"):
                                st.caption(source["text"])

    # Input area at bottom
    st.markdown("<br>", unsafe_allow_html=True)
    
    if prompt := st.chat_input("Query this document..."):
        # Add user message
        st.session_state.messages.append({"role": "user", "content": prompt})
        st.session_state.awaiting_response = True
        st.rerun()

    # Handle assistant response with RAG pipeline visualization
    if st.session_state.awaiting_response and st.session_state.messages and st.session_state.messages[-1]["role"] == "user":
        last_question = st.session_state.messages[-1]["content"]
        try:
            with st.chat_message("assistant"):
                # Show RAG pipeline steps with st.status
                with st.status("🔍 Retrieving context...", expanded=True) as status:
                    st.write("🔍 Searching vector store...")
                    
                    # Call backend
                    result = call_backend(last_question)
                    
                    st.write("⚖️ Re-ranking top chunks...")
                    st.write("🧠 Generating response...")
                    
                    status.update(label="✅ Context Found", state="complete", expanded=False)
                
                # Display answer
                answer = result.get("answer", "No answer returned.")
                sources = result.get("sources", [])
                st.markdown(answer)
                
                # Show sources in expander
                if sources:
                    with st.expander("📚 View Sources"):
                        for idx, source in enumerate(sources, 1):
                            source_name = source.get("metadata", {}).get("source", "Unknown")
                            similarity = source.get("similarity", "N/A")
                            st.info(f"**Source {idx}:** {source_name}\n\nSimilarity: {similarity}")
                            if source.get("text"):
                                st.caption(source["text"])

            # Save to session state
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
                        st.rerun()


# Legacy function for backward compatibility
def render_chat(active_file: str | None = None):
    """Legacy chat renderer - redirects to split-pane version"""
    render_chat_split_pane(active_file)
