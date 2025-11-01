#!/usr/bin/env python3
"""
Test script for Project Axiom logging system.
"""

import os
from axiom import load_config, get_axiom_logger

def test_logging_system():
    """Test the logging system with different scenarios."""
    
    # Load configuration (this will set up logging)
    print("Loading configuration...")
    config = load_config()
    
    # Get logger for this module
    logger = get_axiom_logger(__name__)
    
    # Test different log levels
    logger.debug("This is a debug message - only visible if level is DEBUG")
    logger.info("This is an info message - configuration loaded successfully")
    logger.warning("This is a warning message - something to watch out for")
    logger.error("This is an error message - something went wrong")
    
    # Test structured logging with extra data
    logger.info("Processing document", extra={
        "file_path": "test_document.pdf",
        "file_size": "2.5MB",
        "status": "started"
    })
    
    logger.info("Document processing completed", extra={
        "file_path": "test_document.pdf",
        "chunks_created": 15,
        "processing_time": "2.3s",
        "status": "completed"
    })
    
    print("\nLogging test completed!")
    print(f"Check the log file: {config.logging.log_file}")
    print(f"Log level: {config.logging.level}")

if __name__ == "__main__":
    test_logging_system()
