"""
PDFLoader: extracts raw text and metadata from .pdf files using pypdf.
"""

import logging
import os
from pathlib import Path
from typing import Dict, Any, List, Optional

from .interfaces import LoaderProtocol, DocumentChunk
from ..config.models import DocumentProcessingConfig

try:
    import pypdf
except ImportError:
    pypdf = None


class PDFLoader(LoaderProtocol):
    """
    Loads text from .pdf files.
    """
    def __init__(self, config: DocumentProcessingConfig):
        """
        Initializes the PDFLoader with configuration.
        
        Args:
            config: Configuration object with file size settings.
        """
        self.logger = logging.getLogger(__name__)
        self.max_file_size_bytes = config.max_file_size_mb * 1024 * 1024
        self.logger.info(f"PDFLoader initialized. Max file size: {config.max_file_size_mb} MB")

    def supports(self, file_path: Path) -> bool:
        """Checks if the loader supports the given file extension."""
        return file_path.suffix.lower() == '.pdf'

    def load(self, file_path: Path) -> Optional[DocumentChunk]:
        """Loads a PDF file and returns its content in a DocumentChunk."""
        if not self._validate_file(file_path):
            return None

        try:
            self.logger.info(f"Loading PDF file: {file_path}", extra={"file_path": str(file_path)})
            
            with open(file_path, "rb") as f:
                reader = pypdf.PdfReader(f)
                
                # Check for encryption
                if reader.is_encrypted:
                    self.logger.warning(f"PDF is encrypted and cannot be read: {file_path}", extra={"file_path": str(file_path)})
                    return None

                text_content = "".join(page.extract_text() for page in reader.pages)
            
            metadata = {
                "file_path": str(file_path),
                "file_name": file_path.name,
                "file_extension": file_path.suffix,
                "page_count": len(reader.pages)
            }
            return DocumentChunk(text=text_content, metadata=metadata)

        except Exception as e:
            self.logger.error(f"Failed to load PDF file: {e}", extra={"file_path": str(file_path)}, exc_info=True)
            return None

    def _validate_file(self, file_path: Path) -> bool:
        """Validates file existence, type, and size."""
        if not file_path.is_file():
            self.logger.warning(f"File not found: {file_path}", extra={"file_path": str(file_path)})
            return False
        
        if not file_path.name.lower().endswith('.pdf'):
            self.logger.warning(f"File is not a PDF: {file_path}", extra={"file_path": str(file_path)})
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

    def extract_metadata(self, path: str) -> Dict[str, Any]:
        """Extract metadata from a .pdf file."""
        if not self.supports(Path(path)):
            raise ValueError(f"PDFLoader cannot handle file: {path}")
        
        file_path = Path(path)
        file_size = file_path.stat().st_size
        
        try:
            with open(path, 'rb') as file:
                pdf_reader = pypdf.PdfReader(file)
                
                # Extract PDF metadata
                pdf_info = pdf_reader.metadata or {}
                page_count = len(pdf_reader.pages)
                
                # Get detailed page information
                pages_info = []
                for page_num, page in enumerate(pdf_reader.pages, 1):
                    try:
                        page_text = page.extract_text()
                        pages_info.append({
                            "page_number": page_num,
                            "text_length": len(page_text),
                            "has_text": len(page_text.strip()) > 0
                        })
                    except Exception:
                        pages_info.append({
                            "page_number": page_num,
                            "text_length": 0,
                            "has_text": False,
                            "extraction_failed": True
                        })
                
                metadata = {
                    "file_path": str(file_path.absolute()),
                    "file_name": file_path.name,
                    "file_size_bytes": file_size,
                    "file_size_mb": round(file_size / (1024 * 1024), 2),
                    "file_extension": file_path.suffix,
                    "page_count": page_count,
                    "pages_info": pages_info,
                    "is_encrypted": pdf_reader.is_encrypted,
                    # PDF-specific metadata
                    "pdf_title": pdf_info.get("/Title", ""),
                    "pdf_author": pdf_info.get("/Author", ""),
                    "pdf_subject": pdf_info.get("/Subject", ""),
                    "pdf_creator": pdf_info.get("/Creator", ""),
                    "pdf_producer": pdf_info.get("/Producer", "")
                }
                
                self.logger.debug("Extracted PDF metadata", extra=metadata)
                
                return metadata
                
        except Exception as e:
            raise ValueError(f"Failed to extract metadata from PDF {path}: {e}")


