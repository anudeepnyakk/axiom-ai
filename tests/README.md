# Test files for Axiom AI

This directory contains unit tests and integration tests for the Axiom AI system.

## Test Files

- `test_api_auth.py` - Tests for API authentication
- `test_json_logging.py` - Tests for JSON logging functionality
- `test_lru_cache.py` - Tests for LRU cache implementation
- `test_pii_redaction.py` - Tests for PII redaction security feature
- `test_retry_logic.py` - Tests for retry logic with exponential backoff

## Running Tests

```bash
# Run all tests
pytest tests/

# Run specific test file
pytest tests/test_api_auth.py

# Run with verbose output
pytest tests/ -v
```

