"""Logging utilities for the application.

This module provides functions to set up and get loggers with
consistent configuration across the application.
"""
import logging
from typing import Optional


def get_logger(name: str) -> logging.Logger:
    """Get a logger with the specified name.
    
    Args:
        name: Name for the logger (usually __name__ of calling module)
        
    Returns:
        Configured Logger instance
        
    Example:
        logger = get_logger(__name__)
        logger.info('Something happened')
    """
    return logging.getLogger(name)


def setup_logging(level: int = logging.INFO, log_file: Optional[str] = None) -> None:
    """Set up logging configuration for the application.
    
    This should be called once at application startup.
    
    Args:
        level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Optional path to log file. If None, logs to console.
        
    Example:
        # Log INFO and above to console
        setup_logging(level=logging.INFO)
        
        # Log DEBUG and above to file
        setup_logging(level=logging.DEBUG, log_file='app.log')
    """
    format_string = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    formatter = logging.Formatter(format_string)

    # Remove existing handlers
    root_logger = logging.getLogger()
    root_logger.handlers.clear()
    root_logger.setLevel(level)

    if log_file:
        # Create file handler
        file_handler = logging.FileHandler(log_file, mode='a')
        file_handler.setLevel(level)
        file_handler.setFormatter(formatter)
        root_logger.addHandler(file_handler)
    else:
        # Create console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(level)
        console_handler.setFormatter(formatter)
        root_logger.addHandler(console_handler)
