"""
Logging setup for Project Axiom.
Configures structured logging based on configuration.
"""

import logging
import logging.handlers
from pathlib import Path
from typing import Optional

from .config.models import LoggingConfig
from .json_logging import JSONFormatter, RequestIDFilter
from .request_context import get_request_id


def setup_logging(config: LoggingConfig, use_json: bool = False) -> None:
    """
    Set up structured logging based on configuration.
    
    Args:
        config: Logging configuration from Config object
        use_json: If True, use JSON formatter instead of text formatter
    """
    # Clear any existing handlers
    root_logger = logging.getLogger()
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    
    # Set log level
    log_level = getattr(logging, config.level.upper(), logging.INFO)
    root_logger.setLevel(log_level)
    
    # Create formatter (JSON or text)
    if use_json:
        formatter = JSONFormatter()
    else:
        formatter = logging.Formatter(config.log_format)
    
    # Console handler
    if config.log_to_console:
        console_handler = logging.StreamHandler()
        console_handler.setLevel(log_level)
        console_handler.setFormatter(formatter)
        root_logger.addHandler(console_handler)
    
    # File handler
    if config.log_to_file:
        # Ensure log directory exists
        log_path = Path(config.log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Create rotating file handler (10MB max, keep 5 backup files)
        file_handler = logging.handlers.RotatingFileHandler(
            config.log_file,
            maxBytes=10*1024*1024,  # 10MB
            backupCount=5
        )
        file_handler.setLevel(log_level)
        file_handler.setFormatter(formatter)
        root_logger.addHandler(file_handler)
    
    # Add request ID filter if using JSON logging
    if use_json:
        request_filter = RequestIDFilter(get_request_id)
        root_logger.addFilter(request_filter)
    
    # Log the setup
    logger = logging.getLogger(__name__)
    log_format_type = "JSON" if use_json else "text"
    logger.info("Logging system initialized", extra={
        "log_level": config.level,
        "log_format": log_format_type,
        "log_file": config.log_file if config.log_to_file else "None",
        "log_to_console": config.log_to_console
    })


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger instance for a specific module.
    
    Args:
        name: Logger name (usually __name__)
        
    Returns:
        Configured logger instance
    """
    return logging.getLogger(name)
