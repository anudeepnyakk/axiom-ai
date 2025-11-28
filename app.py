"""
Axiom AI - Monolithic RAG Application (Hugging Face Spaces)

Combines backend and frontend in a single Streamlit app.
Runs entirely on Hugging Face Spaces with 16GB RAM.
"""

import streamlit as st
import os
import tempfile
import time
import shutil
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()
from streamlit_pdf_viewer import pdf_viewer
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_community.vectorstores import Chroma
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from langchain_community.cache import InMemoryCache
from langchain_core.globals import set_llm_cache
from langchain_community.retrievers import BM25Retriever
from langchain_core.documents import Document
from typing import List

# Import PII Redactor (Middleware)
from axiom.security.pii_redactor import redact_pii

# --- CONSTANTS (Official Spec Sheet) ---
MAX_FILES = 10
MAX_FILE_SIZE_MB = 200

# Custom EnsembleRetriever implementation (for LangChain versions that don't include it)
class EnsembleRetriever:
    """Combines multiple retrievers with weighted scoring."""
    
    def __init__(self, retrievers: List, weights: List[float]):
        if len(retrievers) != len(weights):
            raise ValueError("Number of retrievers must match number of weights")
        if abs(sum(weights) - 1.0) > 0.001:
            raise ValueError("Weights must sum to 1.0")
        self.retrievers = retrievers
        self.weights = weights
    
    def get_relevant_documents(self, query: str) -> List[Document]:
        """Retrieve documents from all retrievers and merge with weighted scoring."""
        all_docs = {}
        
        for retriever, weight in zip(self.retrievers, self.weights):
            docs = retriever.get_relevant_documents(query)
            for idx, doc in enumerate(docs):
                # Create a unique key from content hash (first 200 chars for deduplication)
                content_hash = hash(doc.page_content[:200])
                doc_key = (content_hash, doc.metadata.get("source", ""), doc.metadata.get("page", ""))
                
                if doc_key in all_docs:
                    # If duplicate, keep the one with higher weighted score
                    existing_score = all_docs[doc_key][1]
                    new_score = weight * (1.0 / (idx + 1))  # Position-based scoring
                    if new_score > existing_score:
                        all_docs[doc_key] = (doc, new_score)
                else:
                    # Score based on weight and position
                    score = weight * (1.0 / (idx + 1))
                    all_docs[doc_key] = (doc, score)
        
        # Sort by score (descending) and return documents
        sorted_docs = sorted(all_docs.values(), key=lambda x: x[1], reverse=True)
        return [doc for doc, _ in sorted_docs]

# Enable In-Memory Caching (Free Speed)
set_llm_cache(InMemoryCache())

# Cache the LLM so we don't re-initialize the client every request
@st.cache_resource
def load_chat_llm():
    """Return a cached ChatOpenAI client with timeout safeguards."""
    return ChatOpenAI(
        model="gpt-4o-mini",
        temperature=0,
        timeout=60,  # Fail fast if OpenAI stalls
        max_retries=1,
    )

# --- PAGE CONFIG ---
st.set_page_config(layout="wide", page_title="Axiom AI")

# --- CSS STYLING (Production Polish) ---
st.markdown("""
    <style>
        /* Force Light Mode Colors */
        .stApp {
            background-color: #ffffff !important;
            color: #000000 !important;
        }
        
        /* Remove excessive padding (Production Polish) */
        .block-container {
            padding-top: 1rem !important;
            padding-bottom: 0rem !important;
        }
        
        /* Sidebar styling */
        [data-testid="stSidebar"] {
            background-color: #f8f9fa !important;
            border-right: 1px solid #e5e7eb !important;
        }
        
        /* Chat Message Styling */
        .stChatMessage {
            padding: 1rem;
            border-radius: 8px;
            margin-bottom: 0.5rem;
        }
        [data-testid="stChatMessageContent"] {
            color: #1f2937 !important;
        }
        
        /* Hide Streamlit branding & excessive headers */
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        header {visibility: hidden;}
        
        /* Button Styling */
        .stButton > button {
            width: 100%;
            border-radius: 6px;
            font-weight: 600;
        }
        
        /* Chat input pinned to bottom */
        .stChatInputContainer {
            position: sticky;
            bottom: 0.5rem;
            z-index: 50;
            background: #ffffff;
            padding-top: 0.5rem;
            padding-bottom: 1rem;
            border-top: 1px solid #e5e7eb;
        }
    </style>
""", unsafe_allow_html=True)

# --- BACKEND LOGIC (Production Optimized) ---
def get_pdf_chunks(uploaded_file):
    """Extract chunks from a single PDF using Lazy Loading"""
    # Save to temp file (PyPDFLoader requires a path)
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
        tmp_file.write(uploaded_file.getvalue())
        tmp_path = tmp_file.name

    try:
        # LAZY LOAD: Process page-by-page (Faster + Less Memory)
        loader = PyPDFLoader(tmp_path)
        
        # Optimized chunking: Bigger chunks = Fewer embeddings = Faster
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,  # Increased from 500 for speed
            chunk_overlap=100  # Increased from 50 for better context
        )
        
        chunks = []
        # Process page-by-page (The "Speed" Fix)
        for page in loader.lazy_load():
            # SECURITY: Redact PII before embedding
            page.page_content = redact_pii(page.page_content)
            
            page_chunks = text_splitter.split_documents([page])
            # Add metadata
            for chunk in page_chunks:
                chunk.metadata['source'] = uploaded_file.name
            chunks.extend(page_chunks)
        
        return chunks
        
    except Exception as e:
        st.error(f"Error processing {uploaded_file.name}: {str(e)}")
        return []
    finally:
        # Clean up temp file
        try:
            os.unlink(tmp_path)
        except:
            pass

def ingest_files(uploaded_files, status=None):
    """Process multiple PDFs and build ONE master vector store + BM25 retriever"""
    if not os.environ.get("OPENAI_API_KEY"):
        st.error("⚠️ OPENAI_API_KEY not found in Secrets!")
        return None, None

    # Use a persistent directory inside the container
    persist_directory = "./chroma_db"
    Path(persist_directory).mkdir(exist_ok=True)
    
    all_chunks = []
    total_files = len(uploaded_files)
    
    # Loop through all files and extract chunks with progress and safety
    for file_idx, uploaded_file in enumerate(uploaded_files):
        try:
            if status:
                status.write(f"📄 Parsing file {file_idx + 1}/{total_files}: {uploaded_file.name}...")
            
            file_chunks = get_pdf_chunks(uploaded_file)
            all_chunks.extend(file_chunks)
            
            # Cache successful file for viewing
            st.session_state.file_cache[uploaded_file.name] = uploaded_file.getvalue()
            
        except Exception as e:
            st.error(f"❌ Failed to parse {uploaded_file.name}: {str(e)}")
            continue

    if not all_chunks:
        return None, None

    if status:
        status.write("🧠 Generating embeddings & building index...")

    # Build ONE vector store for ALL documents
    if os.path.exists(persist_directory) and os.listdir(persist_directory):
        # Load existing vectorstore
        vectorstore = Chroma(
            persist_directory=persist_directory,
            embedding_function=OpenAIEmbeddings(model="text-embedding-3-small")
        )
        # Add new documents
        vectorstore.add_documents(all_chunks)
    else:
        # Create new vectorstore
        vectorstore = Chroma.from_documents(
            documents=all_chunks, 
            embedding=OpenAIEmbeddings(model="text-embedding-3-small"),
            persist_directory=persist_directory
        )
    
    bm25_retriever = BM25Retriever.from_documents(all_chunks)
    
    return vectorstore, bm25_retriever

def run_rag(question: str):
    """Hybrid retrieval (Vector + BM25) with strict citations."""
    if not st.session_state.vectorstore or not st.session_state.bm25_retriever:
        raise ValueError("Knowledge base not ready. Please ingest documents first.")

    vector_retriever = st.session_state.vectorstore.as_retriever(
        search_type="similarity",
        search_kwargs={"k": 4}
    )

    bm25_retriever = st.session_state.bm25_retriever
    bm25_retriever.k = 4

    hybrid_retriever = EnsembleRetriever(
        retrievers=[vector_retriever, bm25_retriever],
        weights=[0.7, 0.3]
    )

    source_docs = hybrid_retriever.get_relevant_documents(question)

    context_sections = []
    for idx, doc in enumerate(source_docs):
        raw_page = doc.metadata.get("page", 0)
        try:
            page_number = int(raw_page) + 1
        except Exception:
            page_number = raw_page or "N/A"

        doc.metadata["page_display"] = page_number
        source_name = doc.metadata.get("source", f"Source {idx+1}")
        snippet = doc.page_content.strip()
        context_sections.append(f"[Source: {source_name}, Page {page_number}]\n{snippet}")

    context_text = "\n\n".join(context_sections) if context_sections else "No context provided."

    template = """
You are a strict research assistant. Answer the question based ONLY on the following context.
If the answer is not in the context, say "I cannot find this information in the document."

CRITICAL INSTRUCTION:
You must cite the page number and document name for every statement you make. Use the format: (Page X, doc_name.pdf).

Context:
{context}

Question: {question}
"""
    prompt = ChatPromptTemplate.from_template(template)
    llm = load_chat_llm()
    chain = prompt | llm | StrOutputParser()

    try:
        response = chain.invoke({"context": context_text, "question": question})
    except Exception as exc:
        print(f"[RAG] LLM invocation failed: {exc}")
        fallback_snippet = ""
        if source_docs:
            snippet = source_docs[0].page_content.strip()
            fallback_snippet = snippet[:500] + ("..." if len(snippet) > 500 else "")
        response = (
            "⚠️ Degraded Mode: The language model did not respond in time. "
            "Showing the most relevant excerpt instead.\n\n"
            f"{fallback_snippet or 'No context available.'}"
        )

    return response, source_docs

# --- INITIALIZE SESSION STATE ---
if "vectorstore" not in st.session_state:
    st.session_state.vectorstore = None
if "bm25_retriever" not in st.session_state:
    st.session_state.bm25_retriever = None
if "messages" not in st.session_state:
    st.session_state.messages = []
if "file_cache" not in st.session_state:
    st.session_state.file_cache = {}  # Store PDF bytes: {'filename.pdf': bytes}
if "active_file_name" not in st.session_state:
    st.session_state.active_file_name = None
if "pdf_page" not in st.session_state:
    st.session_state.pdf_page = 1
if "recent_sources" not in st.session_state:
    st.session_state.recent_sources = []
if "latency_ms" not in st.session_state:
    st.session_state.latency_ms = None
if "latency_delta" not in st.session_state:
    st.session_state.latency_delta = None

# --- SIDEBAR (Upload & Status) ---
def on_upload_change():
    """Callback to reset processing state when a new file is uploaded"""
    st.session_state.vectorstore = None
    st.session_state.bm25_retriever = None
    st.session_state.pdf_page = 1
    st.session_state.recent_sources = []
    st.session_state.file_cache = {}
    st.session_state.active_file_name = None

with st.sidebar:
    st.header("System Cortex")
    
    # Display file limit info
    current_file_count = len(st.session_state.file_cache) if st.session_state.file_cache else 0
    st.caption(f"📎 Max {MAX_FILES} documents • {MAX_FILE_SIZE_MB}MB per file")
    if current_file_count >= MAX_FILES:
        st.warning(f"⚠️ Maximum limit reached ({MAX_FILES} documents)")
    
    uploaded_files = st.file_uploader(
        "Drag and drop files here", 
        type=['pdf'], 
        accept_multiple_files=True,
        help=f"Maximum {MAX_FILES} documents. Limit {MAX_FILE_SIZE_MB}MB per file.",
        key="uploaded_files_widget",
        on_change=on_upload_change
    )
    
    # Enforce file limit
    if uploaded_files:
        if len(uploaded_files) > MAX_FILES:
            st.error(f"⚠️ Too many files! Maximum {MAX_FILES} documents allowed. Please select fewer files.")
            uploaded_files = None
        else:
            # Check total file count including already cached files
            total_files = len(uploaded_files) + current_file_count
            if total_files > MAX_FILES:
                st.error(f"⚠️ File limit exceeded! You have {current_file_count} document(s) already. Maximum {MAX_FILES} documents total.")
                uploaded_files = None
            else:
                # Check individual file sizes
                oversized_files = [f.name for f in uploaded_files if f.size > MAX_FILE_SIZE_MB * 1024 * 1024]
                if oversized_files:
                    st.error(f"⚠️ File(s) too large: {', '.join(oversized_files)}. Maximum {MAX_FILE_SIZE_MB}MB per file.")
                    uploaded_files = None
    
    # Auto-Processing Status Logic (Moved inside Sidebar)
    if uploaded_files:
        # Processing Logic
        if st.session_state.vectorstore is None:
            try:
                with st.status("Ingesting library...", expanded=True) as status:
                    vectorstore, bm25_retriever = ingest_files(uploaded_files, status=status)
                    if vectorstore and bm25_retriever:
                        st.session_state.vectorstore = vectorstore
                        st.session_state.bm25_retriever = bm25_retriever
                        # Short delay for visual feedback
                        time.sleep(0.5) 
                        status.update(label="Knowledge Base Ready", state="complete", expanded=False)
                        st.toast("Library Updated!", icon="🟢")
                    else:
                        status.update(label="Ingestion Failed", state="error")
                        st.error("No chunks extracted from files.")
            except Exception as e:
                st.error(f"Error: {str(e)}")
    
    st.divider()
    
    # System Health Metrics
    col1, col2 = st.columns(2)
    latency_value = (
        f"{st.session_state.latency_ms} ms" if st.session_state.latency_ms is not None else "—"
    )
    latency_delta_value = (
        f"{st.session_state.latency_delta:+} ms" if st.session_state.latency_delta is not None else "—"
    )
    col1.metric("Latency", latency_value, latency_delta_value)
    col2.metric("Sources Served", len(st.session_state.recent_sources))

# --- MAIN LAYOUT (Production Polish) ---

# 1. Header (Production Polish)
st.title("👑 Axiom AI")
st.caption("Production-Grade RAG System | v2.0")

# Initialize messages if not exists
if "messages" not in st.session_state or len(st.session_state.messages) == 0:
    st.session_state.messages = [{"role": "assistant", "content": "Document analyzed. Ask me anything."}]

# 2. Main Split Interface
if st.session_state.vectorstore and st.session_state.file_cache:
    # Create two columns with clear separation
    col_pdf, col_chat = st.columns([1, 1])

    # LEFT COLUMN: PDF Viewer with Active Document Selector (Production Polish)
    with col_pdf:
        # border=True creates the outline (Production Polish)
        with st.container(height=700, border=True): 
            st.markdown("### 📄 Source Document")
            
            # Active Document Selector
            file_names = list(st.session_state.file_cache.keys())
            if not file_names:
                st.warning("No documents available. Please re-upload.")
                pdf_data = None
            else:
                if not st.session_state.active_file_name or st.session_state.active_file_name not in file_names:
                    st.session_state.active_file_name = file_names[0]
                default_index = file_names.index(st.session_state.active_file_name)
                selected_file = st.selectbox("View File:", file_names, index=default_index)
                st.session_state.active_file_name = selected_file
                
                # Get bytes from cache based on selection
                pdf_data = st.session_state.file_cache[selected_file]
            
            if pdf_data:
                page_to_render = st.session_state.get("pdf_page", 1)
                try:
                    page_to_render = int(page_to_render)
                except Exception:
                    page_to_render = 1
                pdf_viewer(
                    input=pdf_data, 
                    width=None, 
                    height=600,  # Forces full height visibility
                    render_text=True,
                    scroll_to_page=page_to_render
                )

    # RIGHT COLUMN: Chat Interface (Production Polish)
    with col_chat:
        # border=True creates the outline (Production Polish)
        with st.container(height=650, border=True):
            st.markdown("### 🤖 Intelligence")
            
            # Message history container (Scrollable)
            messages_container = st.container(height=480)
            
            # Display History
            with messages_container:
                for msg in st.session_state.messages:
                    with st.chat_message(msg["role"]):
                        st.write(msg["content"])
                        if msg.get("sources"):
                            with st.expander("Sources", expanded=False):
                                for source in msg["sources"]:
                                    st.markdown(f"**{source['name']} — Page {source['page']}**")
                                    st.caption(source["preview"])

            # Chat Input (Sticky at bottom of this container)
            if prompt := st.chat_input("Ask a question...", key="chat_input"):
                st.session_state.messages.append({"role": "user", "content": prompt})
                
                # Display user message in messages container
                with messages_container:
                    with st.chat_message("user"):
                        st.write(prompt)
                
                # Generate and display response
                with messages_container:
                    with st.chat_message("assistant"):
                        try:
                            start_time = time.time()
                            with st.spinner("Synthesizing answer..."):
                                response, source_docs = run_rag(prompt)
                            latency_ms = int((time.time() - start_time) * 1000)
                            previous_latency = st.session_state.latency_ms
                            st.session_state.latency_ms = latency_ms
                            st.session_state.latency_delta = (
                                latency_ms - previous_latency
                                if previous_latency is not None
                                else None
                            )

                            sources_payload = []
                            for doc in source_docs:
                                source_name = doc.metadata.get("source", "Document")
                                page_display = doc.metadata.get("page_display", "N/A")
                                preview = doc.page_content.strip()[:300] + ("..." if len(doc.page_content.strip()) > 300 else "")
                                sources_payload.append(
                                    {"name": source_name, "page": page_display, "preview": preview}
                                )

                            if source_docs:
                                top_doc = source_docs[0]
                                target_page = top_doc.metadata.get("page_display", 1)
                                try:
                                    st.session_state.pdf_page = int(target_page)
                                except Exception:
                                    st.session_state.pdf_page = 1

                                top_source_name = top_doc.metadata.get("source")
                                if top_source_name and top_source_name in st.session_state.file_cache:
                                    st.session_state.active_file_name = top_source_name

                            st.session_state.recent_sources = sources_payload

                            st.write(response)
                            st.session_state.messages.append(
                                {"role": "assistant", "content": response, "sources": sources_payload}
                            )
                        except Exception as e:
                            error_msg = f"Sorry, I encountered an error: {str(e)}"
                            st.error(error_msg)
                            st.session_state.messages.append({"role": "assistant", "content": error_msg})
                
                # Removed explicit st.rerun() to prevent clearing transient error messages/states too quickly
                # Streamlit will automatically handle the UI update.

else:
    # Empty State (Production Polish)
    st.info("👈 Upload a document in the sidebar to begin.")
    
    # API Key Warning
    if not os.environ.get("OPENAI_API_KEY"):
        st.warning("⚠️ OPENAI_API_KEY is missing. Please add it in Space Settings.")
