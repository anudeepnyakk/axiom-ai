

#!/usr/bin/env python3
"""
Day 3 Smoke Test: Complete Document Ingestion Pipeline
Tests the end-to-end flow from files to DocumentChunk objects.
"""

import pytest
import tempfile
from pathlib import Path

from axiom import load_config
from axiom.core.document_processor import FileSystemDocumentProcessor
from axiom.state_tracker import StateTracker, FileStatus
from axiom.config.models import StateTrackerConfig

@pytest.fixture
def temp_test_files():
    """A pytest fixture to create a temporary directory with test files."""
    with tempfile.TemporaryDirectory() as temp_dir:
        test_dir = Path(temp_dir)
        
        # Create a valid text file
        txt_file = test_dir / "sample.txt"
        txt_file.write_text("This is a sample text document.")
        
        # Create a valid PDF file (requires pypdf to be installed)
        # Note: This is a more robust test than the original script's mock PDF.
        try:
            from pypdf import PdfWriter
            writer = PdfWriter()
            writer.add_blank_page(width=100, height=100)
            with open(test_dir / "sample.pdf", "wb") as f:
                writer.write(f)
        except ImportError:
            # If pypdf is not installed, we can't create a real PDF for the test.
            # We'll create a dummy file instead to ensure the path exists.
            (test_dir / "sample.pdf").touch()

        # Create an unsupported file type
        unsupported_file = test_dir / "document.docx"
        unsupported_file.write_text("This is a Word document.")
        
        yield {
            "txt": str(txt_file),
            "pdf": str(test_dir / "sample.pdf"),
            "docx": str(unsupported_file)
        }

@pytest.fixture
def ingestion_components():
    """A pytest fixture to set up all components needed for an ingestion test."""
    # Use an in-memory database for a clean, isolated test environment.
    test_config = StateTrackerConfig(db_path=":memory:")
    state_tracker = StateTracker(test_config)
    
    config = load_config()
    processor = FileSystemDocumentProcessor(
        config.document_processing, 
        state_tracker=state_tracker
    )
    
    yield processor, state_tracker
    
    # Teardown: close the state tracker's database connection
    state_tracker.close()

def test_successful_ingestion(ingestion_components, temp_test_files):
    """Tests that supported file types are processed and marked as COMPLETED."""
    processor, state_tracker = ingestion_components
    
    # Process supported files
    processor.process_document(temp_test_files["txt"])
    processor.process_document(temp_test_files["pdf"])
    
    # Assert final status is COMPLETED
    assert state_tracker.get_file_status(temp_test_files["txt"]) == FileStatus.COMPLETED
    assert state_tracker.get_file_status(temp_test_files["pdf"]) == FileStatus.COMPLETED
    
    # Assert statistics
    stats = state_tracker.get_processing_stats()
    assert stats.get(FileStatus.COMPLETED.value, 0) == 2

def test_unsupported_file_ingestion(ingestion_components, temp_test_files):
    """Tests that unsupported file types are gracefully rejected and marked as FAILED."""
    processor, state_tracker = ingestion_components
    
    # Processing an unsupported file should raise a ValueError
    with pytest.raises(ValueError):
        processor.process_document(temp_test_files["docx"])
        
    # Assert final status is FAILED
    # Note: The state is updated inside the process_document method before the error is raised.
    assert state_tracker.get_file_status(temp_test_files["docx"]) == FileStatus.FAILED
    
    # Assert statistics
    stats = state_tracker.get_processing_stats()
    assert stats.get(FileStatus.FAILED.value, 0) == 1
    
def test_batch_processing(ingestion_components, temp_test_files):
    """Tests the batch processing functionality."""
    processor, state_tracker = ingestion_components
    
    all_files = list(temp_test_files.values())
    
    # The batch processor should continue on failure and not raise an exception.
    processor.process_batch(all_files)
    
    # Assert final statuses are correct
    assert state_tracker.get_file_status(temp_test_files["txt"]) == FileStatus.COMPLETED
    assert state_tracker.get_file_status(temp_test_files["pdf"]) == FileStatus.COMPLETED
    assert state_tracker.get_file_status(temp_test_files["docx"]) == FileStatus.FAILED
    
    # Assert final statistics
    stats = state_tracker.get_processing_stats()
    assert stats.get(FileStatus.COMPLETED.value, 0) == 2
    assert stats.get(FileStatus.FAILED.value, 0) == 1
