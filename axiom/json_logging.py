"""
JSON Logging for Axiom AI

This module provides structured JSON logging with request ID correlation.
All log messages are formatted as JSON for easy parsing by monitoring tools.

Features:
- JSON-formatted log messages
- Request ID correlation across pipeline stages
- Structured fields for filtering and analysis
- Compatible with ELK, Datadog, Splunk, etc.
"""

import json
import logging
from datetime import datetime
from typing import Optional


class JSONFormatter(logging.Formatter):
    """
    Custom JSON formatter for structured logging.
    
    Outputs each log record as a single line of JSON with fields:
    - timestamp: ISO 8601 timestamp
    - level: Log level (INFO, WARNING, ERROR, etc.)
    - request_id: Unique ID for request tracing
    - module: Python module name
    - function: Function name where log was called
    - message: Log message
    - extra: Any additional fields passed via extra dict
    
    Example output:
    {"timestamp":"2025-10-28T19:30:45.123","level":"INFO","request_id":"a7f3c2d1",
     "module":"query_engine","message":"Query started","query_text":"What is RAG?"}
    """
    
    def format(self, record: logging.LogRecord) -> str:
        """
        Format a log record as JSON.
        
        Args:
            record: LogRecord instance to format
            
        Returns:
            str: JSON-formatted log message
        """
        # Base log data
        log_data = {
            "timestamp": datetime.fromtimestamp(record.created).isoformat(),
            "level": record.levelname,
            "module": record.module,
            "function": record.funcName,
            "message": record.getMessage()
        }
        
        # Add request_id if available
        request_id = getattr(record, 'request_id', None)
        if request_id:
            log_data['request_id'] = request_id
        
        # Add any extra fields from the log call
        # e.g., logger.info("Message", extra={"duration_ms": 123})
        if hasattr(record, '__dict__'):
            for key, value in record.__dict__.items():
                # Skip standard logging attributes
                if key not in ['name', 'msg', 'args', 'created', 'filename', 'funcName',
                              'levelname', 'levelno', 'lineno', 'module', 'msecs',
                              'message', 'pathname', 'process', 'processName',
                              'relativeCreated', 'thread', 'threadName', 'exc_info',
                              'exc_text', 'stack_info', 'request_id']:
                    # Add custom fields
                    log_data[key] = value
        
        # Add exception info if present
        if record.exc_info:
            log_data['exception'] = self.formatException(record.exc_info)
        
        # Convert to JSON string
        return json.dumps(log_data, default=str)


class RequestIDFilter(logging.Filter):
    """
    Logging filter that adds request_id to log records.
    
    This filter checks if a request_id is available in the current context
    and adds it to the log record. This enables correlation of all logs
    for a single request across multiple pipeline stages.
    """
    
    def __init__(self, get_request_id_func):
        """
        Initialize the filter.
        
        Args:
            get_request_id_func: Function that returns current request_id or None
        """
        super().__init__()
        self.get_request_id = get_request_id_func
    
    def filter(self, record: logging.LogRecord) -> bool:
        """
        Add request_id to the log record.
        
        Args:
            record: LogRecord to modify
            
        Returns:
            bool: Always True (don't filter out any records)
        """
        # Add request_id from context if not already present
        if not hasattr(record, 'request_id'):
            request_id = self.get_request_id()
            record.request_id = request_id if request_id else 'no-request'
        
        return True


def setup_json_logging(logger: logging.Logger, get_request_id_func) -> None:
    """
    Configure a logger to use JSON formatting with request ID tracking.
    
    Args:
        logger: Logger instance to configure
        get_request_id_func: Function that returns current request_id
        
    Example:
        logger = logging.getLogger(__name__)
        setup_json_logging(logger, get_current_request_id)
    """
    # Create JSON formatter
    json_formatter = JSONFormatter()
    
    # Update all handlers to use JSON formatter
    for handler in logger.handlers:
        handler.setFormatter(json_formatter)
    
    # Add request ID filter
    request_filter = RequestIDFilter(get_request_id_func)
    logger.addFilter(request_filter)

