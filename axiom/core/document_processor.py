"""
FileSystemDocumentProcessor: orchestrates loading and chunking of documents.
"""

import logging
import hashlib
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
            supported_extensions = []
            for loader in self.loaders:
                if hasattr(loader, 'get_supported_extensions'):
                    supported_extensions.extend(loader.get_supported_extensions())
                else:
                    # Infer from loader type as fallback
                    if "TextLoader" in type(loader).__name__:
                        supported_extensions.append(".txt")
                    elif "PDFLoader" in type(loader).__name__:
                        supported_extensions.append(".pdf")
            
            raise ValueError(
                f"Unsupported file type: {file_path.suffix}. "
                f"Supported extensions: {supported_extensions}"
            )

    def get_supported_extensions(self) -> List[str]:
        """Get the list of file extensions supported by this processor."""
        # For now, hardcode the extensions our loaders support
        # In a more advanced version, we could query each loader
        return [".txt", ".pdf"]

    def load_text(self, path: str) -> str:
        """Load the raw text content from a document."""
        file_path = Path(path)
        self.validate_path(path)
        
        # Find the appropriate loader
        for loader in self.loaders:
            if loader.supports(file_path):
                # We need to load the full DocumentChunk to get the text
                document_chunk = loader.load(file_path)
                return document_chunk.text if document_chunk else ""
        
        # This should never happen due to validate_path, but just in case
        raise ValueError(f"No loader found for file: {path}")

    def extract_metadata(self, path: str) -> Dict[str, Any]:
        """Extract metadata from a document."""
        file_path = Path(path)
        self.validate_path(path)
        
        # Find the appropriate loader
        for loader in self.loaders:
            if loader.supports(file_path):
                document_chunk = loader.load(file_path)
                return document_chunk.metadata if document_chunk else {}
        
        # This should never happen due to validate_path, but just in case
        raise ValueError(f"No loader found for file: {path}")

    def chunk_text(self, text: str, metadata: Dict[str, Any]) -> List[DocumentChunk]:
        """Split a single block of text into smaller chunks."""
        # Note: Hashing the text content itself as a stand-in for a file hash.
        # This is not ideal but works for ad-hoc chunking.
        text_hash = hashlib.sha256(text.encode()).hexdigest()
        document = DocumentChunk(text=text, metadata=metadata)
        return self.chunker.chunk(document, text_hash)

    def process_document(self, path: str, collection_name: Optional[str] = None) -> List[DocumentChunk]:
        """Orchestrate the full processing of a single document."""
        self.logger.info(f"Processing document: {path}")
        
        # Record file as seen if state tracking is enabled
        if self.state_tracker:
            self.state_tracker.record_file_seen(path)
        
        try:
            # Record processing start
            if self.state_tracker:
                self.state_tracker.record_processing_start(path)
            
            # Step 1: Validate the path
            self.validate_path(path)
            
            # Step 2: Load document content and metadata into a single object
            document = self._load_document_chunk(path)
            if not document:
                # The loader failed and has already logged the specific error.
                # We can safely assume this document has failed processing.
                raise ValueError(f"Loader failed to produce a DocumentChunk for: {path}")

            # Add the source path to the metadata before chunking.
            document.metadata["source_file_path"] = path

            # Step 3: Chunk the document
            # The file hash is now required for chunking to ensure unique IDs
            file_hash = _calculate_file_hash(path)
            chunks = self.chunker.chunk(document, file_hash)

            # Step 4: Generate embeddings for the chunks
            self.logger.info(f"Generating embeddings for {len(chunks)} chunks...")
            embeddings = self.embedding_generator.embed_batch(chunks)
            
            # Step 5: Add chunks and embeddings to the vector store
            self.logger.info("Adding chunks to vector store...")
            self.vector_store.add(chunks, embeddings, collection_name=collection_name)
            
            # Record successful completion
            if self.state_tracker:
                processing_metadata = {
                    "text_length": len(document.text),
                    "num_chunks": len(chunks),
                    "chunk_size": self.config.chunk_size,
                    "chunk_overlap": self.config.chunk_overlap
                }
                self.state_tracker.record_processing_complete(path, processing_metadata)
            
            self.logger.info(
                "Successfully processed document",
                extra={
                    "file_path": path,
                    "text_length": len(document.text),
                    "num_chunks": len(chunks),
                    "metadata_keys": list(document.metadata.keys())
                }
            )
            
            return chunks
            
        except Exception as e:
            # Record processing failure
            if self.state_tracker:
                error_message = f"{type(e).__name__}: {str(e)}"
                self.state_tracker.record_processing_failed(path, error_message)
            
            self.logger.error(
                f"Failed to process document: {path}",
                extra={
                    "file_path": path,
                    "error_type": type(e).__name__,
                    "error_message": str(e)
                }
            )
            raise

    def _load_document_chunk(self, path: str) -> Optional[DocumentChunk]:
        """Loads a document using the appropriate loader and returns a single DocumentChunk."""
        for loader in self.loaders:
            if loader.supports(Path(path)):
                return loader.load(Path(path))
        return None

    def process_batch(self, paths: List[str], collection_name: Optional[str] = None) -> List[List[DocumentChunk]]:
        """Orchestrate the full processing of a batch of documents."""
        self.logger.info(f"Processing batch of {len(paths)} documents")
        
        results = []
        successful = 0
        failed = 0
        
        for path in paths:
            try:
                chunks = self.process_document(path, collection_name=collection_name)
                results.append(chunks)
                successful += 1
                
            except Exception as e:
                self.logger.warning(
                    f"Failed to process document in batch: {path}",
                    extra={
                        "file_path": path,
                        "error_type": type(e).__name__,
                        "error_message": str(e)
                    },
                    exc_info=True # Log the full traceback
                )
                # For batch processing, we continue on failure, but for the test, we need to know WHY.
                # Re-raising the exception will halt the test and give us a clear error.
                raise
        
        self.logger.info(
            "Completed batch processing",
            extra={
                "total_files": len(paths),
                "successful": successful,
                "failed": failed,
                "success_rate": f"{(successful/len(paths)*100):.1f}%"
            }
        )
        
        # Log state tracking summary if enabled
        if self.state_tracker:
            stats = self.state_tracker.get_processing_stats()
            self.logger.info(
                "State tracking summary",
                extra={
                    "total_files_seen": stats.get('seen', 0),
                    "files_completed": stats.get('completed', 0),
                    "files_failed": stats.get('failed', 0),
                    "files_processing": stats.get('processing', 0)
                }
            )
        
        return results
