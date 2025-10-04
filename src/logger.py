"""Logging utilities for the application.

This module provides functions to set up and get loggers with
consistent configuration across the application.
"""
import json
import logging
import re
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


class SensitiveDataFilter(logging.Filter):
    """Filter that redacts sensitive information from log messages."""

    # Patterns for sensitive data
    PATTERNS = {
        'credit_card': (r'\b\d{4}[- ]?\d{4}[- ]?\d{4}[- ]?\d{4}\b', '[REDACTED-CC]'),
        'ssn': (r'\b\d{3}-\d{2}-\d{4}\b', '[REDACTED-SSN]'),
        'email': (r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', '[REDACTED-EMAIL]'),
        'api_key': (r'(api[_-]?key[=:]\s*)([^\s&,}]+)', r'\1[REDACTED-KEY]'),
        'password': (r'(password[=:]\s*)([^\s&,}]+)', r'\1[REDACTED-PWD]'),
    }

    def filter(self, record):
        """Redact sensitive data from the log record.

        Args:
            record: Log record to filter

        Returns:
            Always returns True to allow the record through
        """
        record.msg = self.redact(str(record.msg))
        # Also redact from args if they exist
        if record.args:
            if isinstance(record.args, dict):  # pragma: no cover
                # Handle dict args (for %(name)s style formatting)  # pragma: no cover
                record.args = {  # pragma: no cover
                    k: self.redact(str(v)) for k, v in record.args.items()
                }
            elif isinstance(record.args, tuple):
                # Handle tuple args (for %s style formatting)
                record.args = tuple(self.redact(str(arg)) for arg in record.args)
        return True

    def redact(self, text):
        """Apply all redaction patterns to text.

        Args:
            text: Text to redact

        Returns:
            Text with sensitive data redacted
        """
        for pattern, replacement in self.PATTERNS.values():
            text = re.sub(pattern, replacement, text, flags=re.IGNORECASE)
        return text


def get_secure_logger(name, level=logging.INFO):
    """Get a logger with sensitive data filtering enabled.

    Args:
        name: Name for the logger
        level: Logging level (default: INFO)

    Returns:
        Logger with SensitiveDataFilter attached

    Example:
        logger = get_secure_logger(__name__)
        logger.info('User password=secret123')  # password is redacted
    """
    logger = logging.getLogger(name)
    logger.setLevel(level)

    # Add the filter
    sensitive_filter = SensitiveDataFilter()
    logger.addFilter(sensitive_filter)

    # Add a console handler if none exists
    if not logger.handlers:
        handler = logging.StreamHandler()
        handler.setFormatter(logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        ))
        logger.addHandler(handler)

    return logger


def sanitize_dict(data, sensitive_keys=None):
    """Sanitize a dictionary by redacting sensitive keys.

    Args:
        data: Dictionary to sanitize
        sensitive_keys: Set of keys to redact (case-insensitive)

    Returns:
        New dictionary with sensitive values redacted

    Example:
        user_data = {'username': 'alice', 'password': 'secret'}
        safe_data = sanitize_dict(user_data)
        # safe_data = {'username': 'alice', 'password': '[REDACTED]'}
    """
    if sensitive_keys is None:
        sensitive_keys = {
            'password', 'pwd', 'passwd',
            'api_key', 'apikey', 'api-key',
            'secret', 'token', 'auth',
            'credit_card', 'cc', 'card_number',
            'ssn', 'social_security',
        }

    # Convert to lowercase for comparison
    sensitive_keys_lower = {k.lower() for k in sensitive_keys}

    sanitized = {}
    for key, value in data.items():
        if key.lower() in sensitive_keys_lower:
            sanitized[key] = '[REDACTED]'
        elif isinstance(value, dict):
            # Recursively sanitize nested dicts
            sanitized[key] = sanitize_dict(value, sensitive_keys)
        else:
            sanitized[key] = value

    return sanitized


def mask_credit_card(card_number):
    """Mask all but the last 4 digits of a credit card.

    Args:
        card_number: Credit card number as string

    Returns:
        Masked credit card like '****1234'

    Example:
        masked = mask_credit_card('4532-1234-5678-9010')
        # masked = '****9010'
    """
    # Remove spaces and dashes
    digits = ''.join(c for c in str(card_number) if c.isdigit())

    if len(digits) < 4:
        return '[INVALID-CC]'

    return '****' + digits[-4:]


def mask_email(email):
    """Mask email address but preserve domain.

    Args:
        email: Email address as string

    Returns:
        Masked email like 'j***@example.com'

    Example:
        masked = mask_email('john.doe@example.com')
        # masked = 'j***@example.com'
    """
    if '@' not in email:
        return '[INVALID-EMAIL]'

    local, domain = email.split('@', 1)

    if len(local) <= 1:
        masked_local = '*'
    else:
        masked_local = local[0] + '***'

    return f"{masked_local}@{domain}"
