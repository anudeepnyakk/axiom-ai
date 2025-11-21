import pytest
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document
from langchain_core.prompts import ChatPromptTemplate

# 1. TEST CHUNKING STRATEGY (CRITICAL)
# If chunks are too small, you lose context. If too big, you confuse the LLM.
def test_chunking_logic():
    text = "A" * 1000  # 1000 characters
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=50
    )
    chunks = splitter.split_text(text)
    
    # Assertions
    assert len(chunks) > 1, "Text should be split into multiple chunks"
    assert len(chunks[0]) <= 500, "Chunk exceeds max size limit"
    assert isinstance(chunks[0], str), "Output must be string"

# 2. TEST PROMPT TEMPLATE
# Ensures your prompt injection doesn't fail silently
def test_prompt_rendering():
    template = "Answer this: {question} based on {context}"
    prompt = ChatPromptTemplate.from_template(template)
    
    messages = prompt.format_messages(
        question="What is RAG?", 
        context="RAG is Retrieval Augmented Generation."
    )
    
    content = messages[0].content
    assert "What is RAG?" in content
    assert "RAG is Retrieval Augmented Generation." in content

