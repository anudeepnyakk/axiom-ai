"""
TextLoader: extracts raw text and metadata from .txt files.
"""

import logging
import os
from pathlib import Path
from typing import Dict, Any, Optional

from .interfaces import LoaderProtocol
from ..config.models import DocumentProcessingConfig
import chardet
from axiom.core.interfaces import LoaderProtocol, DocumentChunk


class TextLoader(LoaderProtocol):
    """
    Loads text from .txt files.
    """
    def __init__(self, config: DocumentProcessingConfig):
        """
        Initializes the TextLoader with configuration.
        
        Args:
            config: Configuration object with chunking and file size settings.
        """
        self.logger = logging.getLogger(__name__)
        self.max_file_size_bytes = config.max_file_size_mb * 1024 * 1024
        self.logger.info(f"TextLoader initialized. Max file size: {config.max_file_size_mb} MB")

    def supports(self, file_path: Path) -> bool:
        """Checks if the loader supports the given file extension."""
        return file_path.suffix.lower() == '.txt'

    def load(self, file_path: Path) -> Optional[DocumentChunk]:
        """Loads a text file and returns its content in a DocumentChunk."""
        if not self._validate_file(file_path):
            return None

        try:
            encoding = self._detect_encoding(file_path)
            self.logger.info(f"Loading text file with detected encoding: {encoding}", extra={"file_path": str(file_path)})
            
            with open(file_path, "r", encoding=encoding) as f:
                text = f.read()

            metadata = {
                "file_path": str(file_path),
                "file_name": file_path.name,
                "file_extension": file_path.suffix,
                "detected_encoding": encoding
            }
            return DocumentChunk(text=text, metadata=metadata)

        except Exception as e:
            self.logger.error(f"Failed to load text file: {e}", extra={"file_path": str(file_path)}, exc_info=True)
            return None

    def _validate_file(self, file_path: Path) -> bool:
        """Validates file existence, type, and size."""
        if not file_path.is_file():
            self.logger.warning(f"File not found: {file_path}", extra={"file_path": str(file_path)})
            return False
        
        if not file_path.name.lower().endswith('.txt'):
            self.logger.warning(f"Unsupported file type: {file_path}", extra={"file_path": str(file_path)})
            return False
        
        file_size = file_path.stat().st_size
        if file_size > self.max_file_size_bytes:
            self.logger.warning(
                f"File {file_path} is too large: {file_size / (1024*1024):.1f}MB "
                f"(max: {self.config.max_file_size_mb}MB)",
                extra={"file_path": str(file_path)}
            )
            return False
        
        return True

    def _detect_encoding(self, file_path: Path) -> str:
        """Attempts to detect the encoding of a file using chardet."""
        try:
            with open(file_path, 'rb') as f:
                raw_data = f.read(1024) # Read a small sample
                result = chardet.detect(raw_data)
                return result['encoding']
        except Exception as e:
            self.logger.warning(f"Could not detect encoding for {file_path}: {e}", extra={"file_path": str(file_path)}, exc_info=True)
            return 'utf-8' # Fallback to utf-8

    def extract_metadata(self, path: str) -> Dict[str, Any]:
        """Extract metadata from a .txt file."""
        if not self.supports(Path(path)):
            raise ValueError(f"TextLoader cannot handle file: {path}")
        
        file_path = Path(path)
        file_size = file_path.stat().st_size
        
        # Detect encoding by trying to load a sample
        detected_encoding = "unknown"
        encodings = ['utf-8', 'utf-8-sig', 'latin-1', 'cp1252']
        
        for encoding in encodings:
            try:
                with open(path, 'r', encoding=encoding) as file:
                    file.read(100)  # Read small sample
                detected_encoding = encoding
                break
            except UnicodeDecodeError:
                continue
        
        metadata = {
            "file_path": str(file_path.absolute()),
            "file_name": file_path.name,
            "file_size_bytes": file_size,
            "file_size_mb": round(file_size / (1024 * 1024), 2),
            "file_extension": file_path.suffix,
            "detected_encoding": detected_encoding
        }
        
        self.logger.debug("Extracted metadata", extra=metadata)
        
        return metadata

