"""
BasicChunker: splits text into fixed-size chunks with configurable overlap.
"""

import logging
from typing import List, Dict, Any

from .interfaces import ChunkerProtocol, DocumentChunk
from ..config.models import DocumentProcessingConfig


class BasicChunker(ChunkerProtocol):
    """
    Fixed-size chunker with overlap measured in characters.
    - Fail-fast on invalid config values
    - Internal logging for observability
    """

    def __init__(self, config: DocumentProcessingConfig):
        """
        Initializes the chunker with a given configuration.
        """
        self._logger = logging.getLogger(__name__)
        self.chunk_size = config.chunk_size
        self.chunk_overlap = config.chunk_overlap
        self._logger.info(f"Initializing BasicChunker with config: {config}")
        self.config = config
        self._validate_config()

    def _validate_config(self) -> None:
        if self.config.chunk_size <= 0:
            raise ValueError(f"chunk_size must be > 0, got {self.config.chunk_size}")
        if self.config.chunk_overlap < 0:
            raise ValueError(f"chunk_overlap must be >= 0, got {self.config.chunk_overlap}")
        if self.config.chunk_overlap >= self.config.chunk_size:
            raise ValueError(
                f"chunk_overlap ({self.config.chunk_overlap}) must be < chunk_size ({self.config.chunk_size})"
            )

    def chunk(self, document: DocumentChunk, file_hash: str) -> List[DocumentChunk]:
        """
        Splits a document into smaller chunks of text.

        Args:
            document: The document to be chunked.
            file_hash: The SHA256 hash of the source file.

        Returns:
            A list of smaller document chunks.
        """
        if not document.text:
            return []

        chunks = []
        text = document.text
        start_offset = 0
        chunk_index = 0

        while start_offset < len(text):
            end_offset = start_offset + self.chunk_size
            chunk_text = text[start_offset:end_offset]
            
            # Create a new metadata object for each chunk
            # Inherit metadata from the parent document
            chunk_metadata = document.metadata.copy()
            
            # Add chunk-specific metadata
            chunk_metadata.update({
                "chunk_index": chunk_index,
                "start_offset": start_offset,
                "end_offset": start_offset + len(chunk_text),
                "chunk_length": len(chunk_text),
                "file_hash": file_hash  # Add the file hash here
            })

            chunks.append(DocumentChunk(
                text=chunk_text,
                metadata=chunk_metadata
            ))

            start_offset += self.chunk_size - self.chunk_overlap
            chunk_index += 1

        self._logger.info(f"Split document into {len(chunks)} chunks.")
        return chunks


