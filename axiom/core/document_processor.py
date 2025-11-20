"""
FileSystemDocumentProcessor: orchestrates loading and chunking of documents.
"""

import logging
import hashlib
import gc
from pathlib import Path
from typing import List, Dict, Any, Optional

from .interfaces import DocumentProcessor, DocumentChunk
from .text_loader import TextLoader
from .pdf_loader import PDFLoader
from .basic_chunker import BasicChunker
from ..config.models import DocumentProcessingConfig
from ..state_tracker import StateTracker
from .interfaces import EmbeddingGenerator, VectorStore


def _calculate_file_hash(file_path: str) -> str:
    """Calculates the SHA256 hash of a file for content verification."""
    sha256_hash = hashlib.sha256()
    with open(file_path, "rb") as f:
        # Read and update hash in chunks to handle large files
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()

class FileSystemDocumentProcessor(DocumentProcessor):
    """
    Document processor that handles files from the filesystem.
    - Composes TextLoader, PDFLoader, and BasicChunker
    - Implements the Strategy pattern for file type handling
    - Integrates state tracking for processing lifecycle
    - Provides complete DocumentProcessor interface
    """

    def __init__(
        self, 
        config: DocumentProcessingConfig, 
        embedding_generator: EmbeddingGenerator,
        vector_store: VectorStore,
        state_tracker: Optional[StateTracker] = None
    ):
        self.logger = logging.getLogger(__name__)
        self.config = config
        self.embedding_generator = embedding_generator
        self.vector_store = vector_store
        self.state_tracker = state_tracker
        
        # Initialize all available loaders
        self.loaders = [
            TextLoader(config),
            PDFLoader(config)
        ]
        
        # Initialize chunker
        self.chunker = BasicChunker(config)
        
        self.logger.info(
            "Initialized FileSystemDocumentProcessor",
            extra={
                "available_loaders": [type(loader).__name__ for loader in self.loaders],
                "chunker": type(self.chunker).__name__,
                "chunk_size": config.chunk_size,
                "chunk_overlap": config.chunk_overlap,
                "state_tracking_enabled": self.state_tracker is not None
            }
        )

    def validate_path(self, path: str) -> None:
        """Validate that a path is a supported and accessible file."""
        if not isinstance(path, str):
            raise TypeError("path must be a string")
        
        file_path = Path(path)
        
        # Check if file exists
        if not file_path.exists():
            raise FileNotFoundError(f"File does not exist: {path}")
        
        # Check if it's actually a file (not a directory)
        if not file_path.is_file():
            raise ValueError(f"Path is not a file: {path}")
        
        # Check if any loader supports this file
        if not any(loader.supports(file_path) for loader in self.loaders):
            raise ValueError(f"Unsupported file type: {file_path.suffix}")

    def process_document(self, path: str, collection_name: Optional[str] = None) -> List[DocumentChunk]:
        """Orchestrate the full processing of a single document with streaming support."""
        self.logger.info(f"Processing document: {path}")
        
        if self.state_tracker:
            self.state_tracker.record_file_seen(path)
            self.state_tracker.record_processing_start(path)
        
        try:
            self.validate_path(path)
            file_hash = _calculate_file_hash(path)
            all_chunks = []
            
            # Find the loader
            loader = self._get_loader(path)
            
            # Check for lazy loading support (Streaming)
            if hasattr(loader, 'lazy_load'):
                self.logger.info(f"Using lazy loading for {path}")
                
                for page_chunk in loader.lazy_load(Path(path)):
                    # Chunk the page further if needed
                    page_chunk.metadata["source_file_path"] = path
                    page_chunks = self.chunker.chunk(page_chunk, file_hash)
                    
                    if page_chunks:
                        # Embed and store immediately (Batch of 1 page)
                        self.logger.debug(f"Processing page batch: {len(page_chunks)} chunks")
                        embeddings = self.embedding_generator.embed_batch(page_chunks)
                        self.vector_store.add(page_chunks, embeddings, collection_name=collection_name)
                        all_chunks.extend(page_chunks)
                    
                    # Clean up memory
                    del page_chunk
                    del page_chunks
                    # Optional: Force GC if memory is tight
                    # gc.collect() 

            else:
                # Traditional monolithic load
                document = loader.load(Path(path))
                if not document:
                    raise ValueError(f"Loader failed to produce a DocumentChunk for: {path}")

                document.metadata["source_file_path"] = path
                chunks = self.chunker.chunk(document, file_hash)
                
                self.logger.info(f"Generating embeddings for {len(chunks)} chunks...")
                embeddings = self.embedding_generator.embed_batch(chunks)
                
                self.vector_store.add(chunks, embeddings, collection_name=collection_name)
                all_chunks = chunks

            # Record success
            if self.state_tracker:
                self.state_tracker.record_processing_complete(path, {"num_chunks": len(all_chunks)})
            
            self.logger.info(f"Successfully processed document: {path} ({len(all_chunks)} chunks)")
            return all_chunks
            
        except Exception as e:
            if self.state_tracker:
                self.state_tracker.record_processing_failed(path, str(e))
            self.logger.error(f"Failed to process document: {path}", exc_info=True)
            raise

    def _get_loader(self, path: str):
        for loader in self.loaders:
            if loader.supports(Path(path)):
                return loader
        raise ValueError(f"No loader found for file: {path}")

    # ... (keep other methods like load_text, extract_metadata, chunk_text) ...
    def load_text(self, path: str) -> str:
        """Load the raw text content from a document."""
        file_path = Path(path)
        self.validate_path(path)
        loader = self._get_loader(path)
        document_chunk = loader.load(file_path)
        return document_chunk.text if document_chunk else ""

    def extract_metadata(self, path: str) -> Dict[str, Any]:
        """Extract metadata from a document."""
        file_path = Path(path)
        self.validate_path(path)
        loader = self._get_loader(path)
        document_chunk = loader.load(file_path)
        return document_chunk.metadata if document_chunk else {}

    def chunk_text(self, text: str, metadata: Dict[str, Any]) -> List[DocumentChunk]:
        """Split a single block of text into smaller chunks."""
        text_hash = hashlib.sha256(text.encode()).hexdigest()
        document = DocumentChunk(text=text, metadata=metadata)
        return self.chunker.chunk(document, text_hash)
        
    def process_batch(self, paths: List[str], collection_name: Optional[str] = None) -> List[List[DocumentChunk]]:
        """Orchestrate the full processing of a batch of documents."""
        results = []
        for path in paths:
            try:
                chunks = self.process_document(path, collection_name=collection_name)
                results.append(chunks)
            except Exception:
                pass # Error already logged in process_document
        return results
