"""
Retry Utilities for Axiom AI

This module provides retry logic with exponential backoff for handling
transient failures in external API calls (e.g., OpenAI).

Features:
- Exponential backoff (1s, 2s, 4s, 8s...)
- Configurable max attempts
- Selective retry based on exception types
- Detailed logging of retry attempts

Usage:
    @retry(max_attempts=3, backoff_base=1.0, exceptions=(OpenAIError, Timeout))
    def call_external_api():
        return api.request()
"""

import time
import logging
from typing import Callable, Tuple, Type, Optional
from functools import wraps


logger = logging.getLogger(__name__)


class AllRetriesFailed(Exception):
    """
    Exception raised when all retry attempts have been exhausted.
    
    This exception wraps the original exception that caused the failure.
    """
    def __init__(self, message: str, original_exception: Exception, attempts: int):
        super().__init__(message)
        self.original_exception = original_exception
        self.attempts = attempts


def retry(
    max_attempts: int = 3,
    backoff_base: float = 1.0,
    backoff_multiplier: float = 2.0,
    exceptions: Tuple[Type[Exception], ...] = (Exception,),
    logger_instance: Optional[logging.Logger] = None
):
    """
    Decorator that adds retry logic with exponential backoff.
    
    Args:
        max_attempts: Maximum number of attempts (including first try)
        backoff_base: Base delay in seconds for first retry
        backoff_multiplier: Multiplier for exponential backoff (usually 2.0)
        exceptions: Tuple of exception types to catch and retry
        logger_instance: Optional logger for retry messages
        
    Returns:
        Decorator function
        
    Example:
        @retry(max_attempts=3, backoff_base=1.0, exceptions=(TimeoutError,))
        def unreliable_function():
            return call_external_api()
            
        # Will retry up to 3 times with delays: 1s, 2s, 4s
    """
    log = logger_instance or logger
    
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            last_exception = None
            
            for attempt in range(1, max_attempts + 1):
                try:
                    # Log attempt
                    if attempt > 1:
                        log.info(
                            f"Retry attempt {attempt}/{max_attempts} for {func.__name__}",
                            extra={"attempt": attempt, "max_attempts": max_attempts}
                        )
                    
                    # Try calling the function
                    result = func(*args, **kwargs)
                    
                    # Success!
                    if attempt > 1:
                        log.info(
                            f"Succeeded on attempt {attempt} for {func.__name__}",
                            extra={"attempt": attempt}
                        )
                    
                    return result
                    
                except exceptions as e:
                    last_exception = e
                    
                    # Log the failure
                    log.warning(
                        f"Attempt {attempt}/{max_attempts} failed for {func.__name__}: {str(e)}",
                        extra={
                            "attempt": attempt,
                            "max_attempts": max_attempts,
                            "exception_type": type(e).__name__,
                            "exception_message": str(e)
                        }
                    )
                    
                    # If this was the last attempt, don't sleep
                    if attempt >= max_attempts:
                        break
                    
                    # Calculate exponential backoff delay
                    delay = backoff_base * (backoff_multiplier ** (attempt - 1))
                    
                    log.info(
                        f"Waiting {delay:.2f}s before retry {attempt + 1}",
                        extra={"delay_seconds": delay}
                    )
                    
                    time.sleep(delay)
            
            # All retries exhausted
            error_message = (
                f"All {max_attempts} retry attempts failed for {func.__name__}. "
                f"Last error: {type(last_exception).__name__}: {str(last_exception)}"
            )
            
            log.error(
                error_message,
                extra={
                    "function": func.__name__,
                    "total_attempts": max_attempts,
                    "final_exception": type(last_exception).__name__
                }
            )
            
            raise AllRetriesFailed(
                error_message,
                original_exception=last_exception,
                attempts=max_attempts
            )
        
        return wrapper
    return decorator


def is_retryable_error(exception: Exception) -> bool:
    """
    Determine if an exception represents a transient error worth retrying.
    
    Args:
        exception: The exception to check
        
    Returns:
        bool: True if the error is likely transient and worth retrying
        
    Examples of retryable errors:
    - Network timeouts
    - Rate limiting (429)
    - Server errors (500, 502, 503, 504)
    - Connection errors
    
    Examples of non-retryable errors:
    - Authentication failures (401)
    - Invalid requests (400)
    - Not found (404)
    - Invalid API key
    """
    exception_str = str(exception).lower()
    exception_type = type(exception).__name__.lower()
    
    # Retryable indicators
    retryable_keywords = [
        'timeout',
        'rate limit',
        'too many requests',
        '429',
        'server error',
        '500',
        '502',
        '503',
        '504',
        'connection',
        'network',
        'temporary',
        'unavailable'
    ]
    
    # Non-retryable indicators
    non_retryable_keywords = [
        'authentication',
        'unauthorized',
        '401',
        'invalid api key',
        'api key',
        'bad request',
        '400',
        'not found',
        '404',
        'forbidden',
        '403'
    ]
    
    # Check non-retryable first (higher priority)
    for keyword in non_retryable_keywords:
        if keyword in exception_str or keyword in exception_type:
            return False
    
    # Check retryable
    for keyword in retryable_keywords:
        if keyword in exception_str or keyword in exception_type:
            return True
    
    # Default: retry generic errors (assume transient)
    return True


class RetryStatistics:
    """
    Track retry statistics for monitoring and debugging.
    
    Useful for understanding system reliability and API health.
    """
    def __init__(self):
        self.total_calls = 0
        self.successful_first_try = 0
        self.successful_after_retry = 0
        self.total_failures = 0
        self.retry_counts = {}  # {attempt_number: count}
    
    def record_success(self, attempts: int):
        """Record a successful call."""
        self.total_calls += 1
        if attempts == 1:
            self.successful_first_try += 1
        else:
            self.successful_after_retry += 1
            self.retry_counts[attempts] = self.retry_counts.get(attempts, 0) + 1
    
    def record_failure(self, attempts: int):
        """Record a failed call."""
        self.total_calls += 1
        self.total_failures += 1
        self.retry_counts[attempts] = self.retry_counts.get(attempts, 0) + 1
    
    def get_stats(self) -> dict:
        """Get retry statistics as a dictionary."""
        return {
            "total_calls": self.total_calls,
            "successful_first_try": self.successful_first_try,
            "successful_after_retry": self.successful_after_retry,
            "total_failures": self.total_failures,
            "success_rate": self.successful_first_try / self.total_calls if self.total_calls > 0 else 0,
            "retry_distribution": self.retry_counts
        }


# Global retry statistics
retry_stats = RetryStatistics()

