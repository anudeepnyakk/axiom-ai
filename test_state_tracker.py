#!/usr/bin/env python3
"""
Test script for Project Axiom state tracker.
"""

import pytest
from axiom import load_config, FileStatus
from axiom.state_tracker import StateTracker
from axiom.config.models import StateTrackerConfig

@pytest.fixture
def state_tracker():
    """
    A pytest fixture that sets up and tears down a clean, in-memory StateTracker for each test.
    This is the professional way to handle test setup and cleanup.
    """
    # --- Setup ---
    # Use an in-memory SQLite database for a clean, isolated test environment.
    test_db_path = ":memory:"
    test_config = StateTrackerConfig(db_path=test_db_path)
    tracker = StateTracker(test_config)
    
    # The 'yield' keyword passes the created 'tracker' object to the test function.
    yield tracker
    
    # --- Teardown ---
    # After the test is finished, this code will run to clean up.
    tracker.close()

def test_full_lifecycle(state_tracker):
    """
    Tests the full lifecycle of file tracking: seen -> processing -> completed/failed.
    The 'state_tracker' argument here is automatically provided by the pytest fixture above.
    """
    # Initialize logging for the test context
    load_config()

    # Test file paths
    test_files = [
        "document1.pdf",
        "document2.txt", 
        "document3.pdf"
    ]
    
    # 1. Record files as seen
    for file_path in test_files:
        state_tracker.record_file_seen(file_path)
    
    # 2. Simulate processing workflow
    state_tracker.record_processing_start(test_files[0])
    state_tracker.record_processing_complete(test_files[0], {"chunks": 10})
    
    state_tracker.record_processing_start(test_files[1])
    state_tracker.record_processing_failed(test_files[1], "File corrupted")
    
    state_tracker.record_processing_start(test_files[2])
    state_tracker.record_processing_complete(test_files[2], {"chunks": 20})

    # 3. Assert final statuses are correct
    assert state_tracker.get_file_status(test_files[0]) == FileStatus.COMPLETED
    assert state_tracker.get_file_status(test_files[1]) == FileStatus.FAILED
    assert state_tracker.get_file_status(test_files[2]) == FileStatus.COMPLETED

    # 4. Assert statistics are correct
    stats = state_tracker.get_processing_stats()
    assert stats[FileStatus.COMPLETED.value] == 2
    assert stats[FileStatus.FAILED.value] == 1
    assert stats.get(FileStatus.SEEN.value, 0) == 0
    assert stats.get(FileStatus.PROCESSING.value, 0) == 0

    # 5. Assert queries by status are correct
    completed_files = state_tracker.get_files_by_status(FileStatus.COMPLETED)
    failed_files = state_tracker.get_files_by_status(FileStatus.FAILED)
    
    assert len(completed_files) == 2
    assert len(failed_files) == 1
    assert failed_files[0]['file_path'] == test_files[1]
    assert failed_files[0]['error_message'] == "File corrupted"
