"""
Request Context Management for Axiom AI

This module provides request ID generation and propagation across
pipeline stages using Python's contextvars for thread-safe context.

The request_id allows tracing a single user query through:
- Query Engine
- Embedding Generation
- Vector Search
- LLM Synthesis

Usage:
    from axiom.request_context import generate_request_id, set_request_id, get_request_id
    
    # At the start of query processing
    request_id = generate_request_id()
    set_request_id(request_id)
    
    # In any function later
    current_id = get_request_id()  # Returns the same request_id
"""

import uuid
from contextvars import ContextVar
from typing import Optional
from contextlib import contextmanager


# Context variable to store the current request ID
# This is thread-safe and works with async code
_request_id_var: ContextVar[Optional[str]] = ContextVar('request_id', default=None)


def generate_request_id() -> str:
    """
    Generate a new unique request ID.
    
    Returns:
        str: Unique 8-character request ID (e.g., "a7f3c2d1")
        
    Example:
        >>> request_id = generate_request_id()
        >>> print(request_id)
        'a7f3c2d1'
    """
    # Use first 8 characters of UUID for readability
    # Still astronomically unlikely to collide
    return str(uuid.uuid4())[:8]


def set_request_id(request_id: str) -> None:
    """
    Set the request ID for the current context.
    
    This makes the request_id available to all functions called
    in the current execution context.
    
    Args:
        request_id: Request ID to set
        
    Example:
        >>> set_request_id("a7f3c2d1")
    """
    _request_id_var.set(request_id)


def get_request_id() -> Optional[str]:
    """
    Get the current request ID from context.
    
    Returns:
        str: Current request ID, or None if not set
        
    Example:
        >>> request_id = get_request_id()
        >>> print(request_id)
        'a7f3c2d1'
    """
    return _request_id_var.get()


def clear_request_id() -> None:
    """
    Clear the request ID from the current context.
    
    Useful for cleanup after request processing completes.
    """
    _request_id_var.set(None)


@contextmanager
def request_context(request_id: Optional[str] = None):
    """
    Context manager for request ID handling.
    
    Automatically generates a request ID if not provided,
    sets it for the duration of the context, and clears it afterwards.
    
    Args:
        request_id: Optional request ID to use. If None, generates new one.
        
    Yields:
        str: The request ID being used
        
    Example:
        >>> with request_context() as req_id:
        ...     logger.info("Processing request")
        ...     # req_id is automatically in context
        ...     process_query(user_input)
        # req_id automatically cleared here
    """
    # Generate or use provided request ID
    req_id = request_id or generate_request_id()
    
    # Save previous request ID (for nested contexts)
    previous_id = get_request_id()
    
    try:
        # Set the request ID
        set_request_id(req_id)
        yield req_id
    finally:
        # Restore previous request ID (or clear if none)
        if previous_id:
            set_request_id(previous_id)
        else:
            clear_request_id()


def get_or_create_request_id() -> str:
    """
    Get the current request ID, or create one if it doesn't exist.
    
    Useful for ensuring there's always a request ID available.
    
    Returns:
        str: Current or newly generated request ID
        
    Example:
        >>> request_id = get_or_create_request_id()
        # If no request_id in context, creates one automatically
    """
    request_id = get_request_id()
    if request_id is None:
        request_id = generate_request_id()
        set_request_id(request_id)
    return request_id

