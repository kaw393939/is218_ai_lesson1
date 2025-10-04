"""Logging utilities for the application.

This module provides functions to set up and get loggers with
consistent configuration across the application.
"""
import json
import logging
import uuid
from contextlib import contextmanager
from logging import LoggerAdapter
from logging.handlers import RotatingFileHandler
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


class JsonFormatter(logging.Formatter):
    """Format log records as JSON for structured logging."""

    def format(self, record: logging.LogRecord) -> str:
        """Convert log record to JSON string.

        Args:
            record: The log record to format

        Returns:
            JSON string representation of the log record

        Example:
            formatter = JsonFormatter()
            handler.setFormatter(formatter)
        """
        log_data = {
            'timestamp': self.formatTime(record),
            'level': record.levelname,
            'logger': record.name,
            'message': record.getMessage(),
            'module': record.module,
            'function': record.funcName,
            'line': record.lineno
        }

        # Add exception info if present
        if record.exc_info:  # pragma: no cover
            log_data['exception'] = self.formatException(record.exc_info)

        return json.dumps(log_data)


def get_rotating_file_handler(
    log_file: str,
    max_bytes: int = 10485760,
    backup_count: int = 5
) -> RotatingFileHandler:
    """Get a rotating file handler that manages log file size.

    Args:
        log_file: Path to the log file
        max_bytes: Maximum size in bytes before rotation (default: 10MB)
        backup_count: Number of backup files to keep (default: 5)

    Returns:
        Configured RotatingFileHandler instance

    Example:
        handler = get_rotating_file_handler('app.log', max_bytes=5242880, backup_count=3)
        logger.addHandler(handler)
    """
    handler = RotatingFileHandler(
        log_file,
        maxBytes=max_bytes,
        backupCount=backup_count
    )
    return handler


def setup_multi_handler_logging(
    console_level: int = logging.INFO,
    file_level: int = logging.DEBUG,
    log_file: str = 'app.log'
) -> None:
    """Set up logging with multiple handlers for different outputs.

    Args:
        console_level: Logging level for console output (default: INFO)
        file_level: Logging level for file output (default: DEBUG)
        log_file: Path to log file (default: 'app.log')

    Example:
        # Console shows INFO+, file captures DEBUG+
        setup_multi_handler_logging(
            console_level=logging.INFO,
            file_level=logging.DEBUG,
            log_file='logs/app.log'
        )
    """
    # Get root logger and clear existing handlers
    root_logger = logging.getLogger()
    root_logger.handlers.clear()
    root_logger.setLevel(logging.DEBUG)  # Set to lowest level, let handlers filter

    # Console handler - human readable format
    console_handler = logging.StreamHandler()
    console_handler.setLevel(console_level)
    console_formatter = logging.Formatter('%(levelname)s - %(message)s')
    console_handler.setFormatter(console_formatter)

    # File handler - detailed format
    file_handler = logging.FileHandler(log_file, mode='a')
    file_handler.setLevel(file_level)
    file_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    file_handler.setFormatter(file_formatter)

    # Add handlers to root logger
    root_logger.addHandler(console_handler)
    root_logger.addHandler(file_handler)


def get_contextual_logger(
    logger: logging.Logger,
    request_id: Optional[str] = None
) -> LoggerAdapter:
    """Get a logger with request context.

    Args:
        logger: Base logger
        request_id: Optional request ID (generates one if not provided)

    Returns:
        LoggerAdapter with request context

    Example:
        logger = get_contextual_logger(logging.getLogger(__name__), request_id='abc-123')
        logger.info('Processing request')  # Automatically includes request_id
    """
    if request_id is None:
        request_id = str(uuid.uuid4())

    return LoggerAdapter(logger, {'request_id': request_id})


def get_user_logger(
    logger: logging.Logger,
    user_id: str,
    username: Optional[str] = None
) -> LoggerAdapter:
    """Get a logger with user context.

    Args:
        logger: Base logger
        user_id: User ID
        username: Optional username

    Returns:
        LoggerAdapter with user context

    Example:
        logger = get_user_logger(logging.getLogger(__name__), 'user123', 'alice')
        logger.info('User action')  # Includes user_id and username
    """
    context = {'user_id': user_id}
    if username:
        context['username'] = username

    return LoggerAdapter(logger, context)


def get_logger_with_context(logger: logging.Logger, **context) -> LoggerAdapter:
    """Get a logger with arbitrary context.

    Args:
        logger: Base logger
        **context: Arbitrary context key-value pairs

    Returns:
        LoggerAdapter with provided context

    Example:
        logger = get_logger_with_context(
            logging.getLogger(__name__),
            request_id='abc-123',
            user_id='user456',
            endpoint='/api/data'
        )
        logger.info('Request')  # Includes all context
    """
    return LoggerAdapter(logger, context)


@contextmanager
def log_context(logger: logging.Logger, **context):
    """Context manager that adds context to logger.

    Args:
        logger: Base logger or adapter
        **context: Context to add

    Yields:
        LoggerAdapter with context

    Example:
        with log_context(logger, request_id='abc-123') as log:
            log.info('Processing')  # Automatically includes request_id
    """
    # If logger is already an adapter, merge contexts
    if isinstance(logger, LoggerAdapter):
        merged_context = {**logger.extra, **context}
        context_logger = LoggerAdapter(logger.logger, merged_context)
    else:
        context_logger = LoggerAdapter(logger, context)

    # Log entry
    context_logger.debug('Entering context')

    try:
        yield context_logger
    finally:
        # Log exit
        context_logger.debug('Exiting context')
