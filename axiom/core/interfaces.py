"""
Core interfaces for Project Axiom.
Defines the contracts for major components using Protocols.
"""

from typing import Protocol, List, Dict, Any, Tuple, Optional
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class QueryResult:
    """Standardized output for a query from the QueryEngine."""
    question: str
    answer: str
    context_chunks: List['DocumentChunk']

@dataclass
class DocumentChunk:
    """
    A dataclass representing a single chunk of text from a document.
    This is the data contract for what flows between the DocumentProcessor
    and the EmbeddingGenerator.
    """
    text: str
    metadata: Dict[str, Any] = field(default_factory=dict)


class LoaderProtocol(Protocol):
    """
    Loader component responsible for extracting raw text and metadata from a file.
    Implementations: TextLoader, PDFLoader, etc.
    """
    def supports(self, file_path: Path) -> bool: ...
    def load(self, file_path: Path) -> Optional[DocumentChunk]: ...


class ChunkerProtocol(Protocol):
    """
    Chunker component responsible for splitting text into chunks with metadata.
    Implementations: BasicChunker, SemanticChunker, etc.
    """
    def chunk(self, document: DocumentChunk, file_hash: str) -> List[DocumentChunk]: ...


class EmbeddingGenerator(Protocol):
    """
    Interface for a component that generates embeddings from text.
    """
    def embed_batch(self, chunks: List[DocumentChunk]) -> List[List[float]]:
        """
        Embed a batch of document chunks.

        Args:
            chunks: A list of DocumentChunk objects to embed.

        Returns:
            A list of embeddings, where each embedding is a list of floats.
            
        Raises:
            Exception: If the embedding process fails for any reason.
        """
        ...

    def get_provider_info(self) -> Dict[str, Any]:
        """
        Get information about the embedding model provider.

        Returns:
            A dictionary containing provider metadata, such as provider name,
            model name, etc.
        """
        ...


class DocumentProcessor(Protocol):
    """
    Interface for a component that processes a single document into chunks.
    This contract is designed to be highly extensible and testable, separating
    validation, loading, metadata extraction, and chunking into distinct steps.
    """

    def validate_path(self, path: str) -> None:
        """
        Validate that a path is a supported and accessible file.

        Args:
            path: The path to the file.
            
        Raises:
            ValueError: If the path is not a file, does not exist, or is an unsupported extension.
            IOError: If the file cannot be read.
        """
        ...

    def get_supported_extensions(self) -> List[str]:
        """
        Get the list of file extensions supported by this processor.

        Returns:
            A list of strings, e.g., [".pdf", ".txt"].
        """
        ...

    def load_text(self, path: str) -> str:
        """
        Load the raw text content from a document.

        Args:
            path: The path to the file.

        Returns:
            The full text content of the document as a single string.
            
        Raises:
            Exception: If loading or text extraction fails.
        """
        ...

    def extract_metadata(self, path: str) -> Dict[str, Any]:
        """
        Extract metadata from a document.

        Args:
            path: The path to the file.

        Returns:
            A dictionary of metadata (e.g., file_size, creation_date, page_count).
        """
        ...

    def chunk_text(self, text: str, metadata: Dict[str, Any]) -> List[DocumentChunk]:
        """
        Split a single block of text into smaller chunks.

        Args:
            text: The text to be chunked.
            metadata: The document-level metadata to be associated with each chunk.

        Returns:
            A list of DocumentChunk objects.
        """
        ...

    def process_document(self, path: str) -> List[DocumentChunk]:
        """
        Orchestrate the full processing of a single document.

        This is the main high-level entry point for processing one file. It should
        typically call the other methods of the protocol in sequence.

        Args:
            path: The path to the document.

        Returns:
            A list of DocumentChunk objects for the processed document.
        """
        ...

    def process_batch(self, paths: List[str]) -> List[List[DocumentChunk]]:
        """
        Orchestrate the full processing of a batch of documents.

        Args:
            paths: A list of file paths to process.

        Returns:
            A list where each item is a list of DocumentChunk objects for a document.
        """
        ...


class VectorStore(Protocol):
    """
    Interface for a component that stores and retrieves vector embeddings.
    This contract defines the core functionality needed for the RAG pipeline.
    """

    def add(self, chunks: List[DocumentChunk], embeddings: List[List[float]]) -> List[str]:
        """
        Store new embeddings and their corresponding document chunks.

        Args:
            chunks: A list of DocumentChunk objects.
            embeddings: A list of vector embeddings.

        Returns:
            A list of unique IDs for the stored items.
        """
        ...

    def query(self, query_vector: List[float], top_k: int, metadata_filter: Optional[Dict[str, Any]] = None) -> List[DocumentChunk]:
        """
        The low-level method to search for similar vectors.

        Args:
            query_vector: The vector to search against.
            top_k: The number of results to return.
            metadata_filter: Optional dictionary to filter results.

        Returns:
            A list of the most similar DocumentChunk objects.
        """
        ...


class LLMProvider(Protocol):
    """
    An interface for a Large Language Model provider (e.g., OpenAI, Anthropic, local model).
    This ensures our QueryEngine can be provider-agnostic, a key architectural goal.
    """
    def generate_answer(self, query: str, context: str, history: Optional[str] = None) -> str:
        """
        Generates an answer based on the query and the provided context.

        Args:
            query: The user's original question.
            context: The synthesized context string from retrieved document chunks.
            history: An optional string of the previous conversation history.

        Returns:
            The final answer generated by the LLM.
        """
        ...

    def get_provider_info(self) -> Dict[str, Any]:
        """
        Returns information about the LLM provider and model being used.
        """
        ...

