"""
Component Factory for Project Axiom

This module is the single source of truth for creating and wiring together
all the major components of the application (e.g., QueryEngine, VectorStore).

This "Factory" pattern solves two key architectural problems:
1.  **Circular Dependencies:** It breaks import loops by acting as a central
    hub. The main application (`app.py`) only needs to import this factory,
    and this factory imports the individual components. This creates a clean,
    one-way dependency graph.
2.  **Centralized Configuration:** It ensures that all components are
    instantiated with the correct, consistent configuration, making the
    system easier to manage and test.
"""

import logging
import os
from axiom.config.loader import load_config, Config
from axiom.core.interfaces import (
    VectorStore,
    EmbeddingGenerator,
    DocumentProcessor,
    LLMProvider
)

from axiom.core.embedding_generator import SentenceTransformerEmbeddingGenerator
from axiom.core.openai_embedding_generator import OpenAIEmbeddingGenerator
from axiom.core.vector_store import ChromaVectorStore
from axiom.core.document_processor import FileSystemDocumentProcessor
from axiom.core.llm_synthesizer import LLMSynthesizer
from axiom.core.openai_provider import get_openai_provider_from_env
from axiom.state_tracker import StateTracker
from axiom.core.query_engine import QueryEngine
from axiom.core.basic_chunker import BasicChunker
from axiom.core.simple_vector_store import SimpleVectorStore
from axiom.core.text_loader import TextLoader
from axiom.core.local_embedding_generator import LocalEmbeddingGenerator
from axiom.core.openai_provider import OpenAIProvider
from axiom.config.models import Config

# Get a logger for the factory module
logger = logging.getLogger(__name__)

def create_embedding_generator(config: Config, use_local: bool = False) -> EmbeddingGenerator:
    """Creates an embedding generator based on the provided configuration."""
    # This logic can be expanded later to support multiple providers
    # For now, we simplify based on the current config model.
    if use_local:
         return LocalEmbeddingGenerator(model_name=config.embeddings.model_name)
    
    # Default to OpenAI or another primary provider if not specified
    if not config.api_keys.openai:
        raise ValueError("OpenAI API key is missing in config.")
    
    return OpenAIEmbeddingGenerator(
        api_key=config.api_keys.openai
    )

def create_document_processor(config: Config) -> DocumentProcessor:
    """Creates a document processor with all its dependencies."""
    logger.info("Initializing DocumentProcessor...")
    state_tracker = StateTracker(config.state_tracker)
    embedding_generator = create_embedding_generator(config, use_local=True) # Use local for ingestion
    vector_store = create_vector_store(config, use_local=True)

    return FileSystemDocumentProcessor(
        config=config.document_processing,
        embedding_generator=embedding_generator,
        vector_store=vector_store,
        state_tracker=state_tracker
    )

def create_vector_store(config: Config, use_local: bool = False) -> VectorStore:
    """Creates a Chroma-based vector store."""
    logger.info("Initializing VectorStore...")
    embedding_generator = create_embedding_generator(config, use_local=use_local)
    return ChromaVectorStore(
        embedding_generator=embedding_generator,
        persist_directory=config.vector_store.persist_directory,
        collection_name=config.vector_store.collection_name
    )

def create_llm_provider(config: Config) -> LLMProvider:
    """Creates an LLM provider."""
    logger.info("Initializing LLM Synthesizer...")
    try:
        return OpenAIProvider(
            api_key=config.api_keys.openai,
            model="gpt-4o"  # Using a default model, can be made configurable later
        )
    except ValueError as e:
        logger.error(f"Failed to initialize OpenAI provider: {e}")
        # Re-raise the exception to be caught by the UI for a clean error message.
        raise

def create_llm_synthesizer(config: Config) -> LLMSynthesizer:
    """Creates the LLM synthesizer."""
    logger.info("Initializing LLMSynthesizer...")
    llm_provider = create_llm_provider(config)
    # The state tracker could also be injected here if needed for conversation memory
    return LLMSynthesizer(provider=llm_provider)

def create_chunker(config: Config) -> BasicChunker:
    """Creates a chunker."""
    logger.info("Initializing Chunker...")
    return BasicChunker(config.document_processing)

def create_query_engine(config: Config) -> QueryEngine:
    """Creates the main query engine."""
    logger.info("Initializing QueryEngine...")
    vector_store = create_vector_store(config, use_local=True)
    embedding_generator = create_embedding_generator(config, use_local=True)
    llm_synthesizer = create_llm_synthesizer(config)
    chunker = create_chunker(config)
    return QueryEngine(
        vector_store=vector_store,
        embedding_generator=embedding_generator,
        llm_synthesizer=llm_synthesizer,
        chunker=chunker,
    )

