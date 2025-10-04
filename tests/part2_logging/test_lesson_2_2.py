"""Tests for Lesson 2.2: Custom Log Handlers and Formatters

This module tests custom logging functionality:
- JSON formatter
- Rotating file handler
- Multiple handlers with different formatters
- Handler level filtering
"""
import logging
import tempfile
import os
import json
import pytest


@pytest.fixture(autouse=True)
def reset_logging():
    """Reset logging configuration before and after each test."""
    # Before test: clear all handlers and reset level
    for handler in logging.root.handlers[:]:
        logging.root.removeHandler(handler)
        handler.close()
    logging.root.setLevel(logging.INFO)

    yield

    # After test: clear all handlers again
    for handler in logging.root.handlers[:]:
        logging.root.removeHandler(handler)
        handler.close()
    logging.root.setLevel(logging.INFO)


class TestImports:
    """Test that required classes and functions can be imported."""

    def test_json_formatter_exists(self):
        """Should be able to import JsonFormatter class.

        HINT: class JsonFormatter(logging.Formatter):
        """
        from logger import JsonFormatter
        assert JsonFormatter is not None

    def test_get_rotating_file_handler_exists(self):
        """Should be able to import get_rotating_file_handler function.

        HINT: def get_rotating_file_handler(log_file, max_bytes, backup_count):
        """
        from logger import get_rotating_file_handler
        assert callable(get_rotating_file_handler)

    def test_setup_multi_handler_logging_exists(self):
        """Should be able to import setup_multi_handler_logging function.

        HINT: def setup_multi_handler_logging(console_level, file_level, log_file):
        """
        from logger import setup_multi_handler_logging
        assert callable(setup_multi_handler_logging)


class TestJsonFormatter:
    """Test JSON formatter functionality."""

    def test_json_formatter_is_formatter(self):
        """JsonFormatter should inherit from logging.Formatter.

        HINT: class JsonFormatter(logging.Formatter):
        """
        from logger import JsonFormatter
        assert issubclass(JsonFormatter, logging.Formatter)

    def test_json_formatter_produces_json(self):
        """JsonFormatter should produce valid JSON output.

        HINT: Override format() method to return json.dumps(...)
        """
        from logger import JsonFormatter

        # Create a formatter and logger
        formatter = JsonFormatter()
        handler = logging.StreamHandler()
        handler.setFormatter(formatter)

        logger = logging.getLogger('json_test_logger')
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)

        # Capture formatted output
        import io
        stream = io.StringIO()
        handler.stream = stream

        logger.info('Test message')

        output = stream.getvalue().strip()
        # Should be valid JSON
        parsed = json.loads(output)
        assert isinstance(parsed, dict)

    def test_json_formatter_includes_timestamp(self):
        """JSON output should include timestamp field.

        HINT: log_data['timestamp'] = self.formatTime(record)
        """
        from logger import JsonFormatter

        formatter = JsonFormatter()
        record = logging.LogRecord(
            name='test',
            level=logging.INFO,
            pathname='test.py',
            lineno=1,
            msg='Test',
            args=(),
            exc_info=None
        )

        output = formatter.format(record)
        parsed = json.loads(output)
        assert 'timestamp' in parsed

    def test_json_formatter_includes_level(self):
        """JSON output should include level field.

        HINT: log_data['level'] = record.levelname
        """
        from logger import JsonFormatter

        formatter = JsonFormatter()
        record = logging.LogRecord(
            name='test',
            level=logging.ERROR,
            pathname='test.py',
            lineno=1,
            msg='Test',
            args=(),
            exc_info=None
        )

        output = formatter.format(record)
        parsed = json.loads(output)
        assert 'level' in parsed
        assert parsed['level'] == 'ERROR'

    def test_json_formatter_includes_message(self):
        """JSON output should include message field.

        HINT: log_data['message'] = record.getMessage()
        """
        from logger import JsonFormatter

        formatter = JsonFormatter()
        record = logging.LogRecord(
            name='test',
            level=logging.INFO,
            pathname='test.py',
            lineno=1,
            msg='Hello %s',
            args=('World',),
            exc_info=None
        )

        output = formatter.format(record)
        parsed = json.loads(output)
        assert 'message' in parsed
        assert parsed['message'] == 'Hello World'

    def test_json_formatter_includes_logger_name(self):
        """JSON output should include logger name.

        HINT: log_data['logger'] = record.name
        """
        from logger import JsonFormatter

        formatter = JsonFormatter()
        record = logging.LogRecord(
            name='my.module.logger',
            level=logging.INFO,
            pathname='test.py',
            lineno=1,
            msg='Test',
            args=(),
            exc_info=None
        )

        output = formatter.format(record)
        parsed = json.loads(output)
        assert 'logger' in parsed
        assert parsed['logger'] == 'my.module.logger'


class TestRotatingFileHandler:
    """Test rotating file handler functionality."""

    def test_get_rotating_file_handler_returns_handler(self):
        """get_rotating_file_handler should return a RotatingFileHandler.

        HINT: from logging.handlers import RotatingFileHandler
        """
        from logger import get_rotating_file_handler
        from logging.handlers import RotatingFileHandler

        with tempfile.TemporaryDirectory() as tmpdir:
            log_file = os.path.join(tmpdir, 'test.log')
            handler = get_rotating_file_handler(log_file, max_bytes=1024, backup_count=3)

            assert isinstance(handler, RotatingFileHandler)
            handler.close()

    def test_rotating_handler_has_max_bytes(self):
        """RotatingFileHandler should respect maxBytes parameter.

        HINT: RotatingFileHandler(log_file, maxBytes=max_bytes, ...)
        """
        from logger import get_rotating_file_handler

        with tempfile.TemporaryDirectory() as tmpdir:
            log_file = os.path.join(tmpdir, 'test.log')
            handler = get_rotating_file_handler(log_file, max_bytes=2048, backup_count=3)

            assert handler.maxBytes == 2048
            handler.close()

    def test_rotating_handler_has_backup_count(self):
        """RotatingFileHandler should respect backupCount parameter.

        HINT: RotatingFileHandler(..., backupCount=backup_count)
        """
        from logger import get_rotating_file_handler

        with tempfile.TemporaryDirectory() as tmpdir:
            log_file = os.path.join(tmpdir, 'test.log')
            handler = get_rotating_file_handler(log_file, max_bytes=1024, backup_count=5)

            assert handler.backupCount == 5
            handler.close()

    def test_rotating_handler_writes_to_file(self):
        """RotatingFileHandler should write logs to file.

        HINT: Handler needs a formatter and to be added to a logger
        """
        from logger import get_rotating_file_handler

        with tempfile.TemporaryDirectory() as tmpdir:
            log_file = os.path.join(tmpdir, 'test.log')

            # Store and clear existing handlers
            saved_handlers = logging.root.handlers[:]
            logging.root.handlers = []

            try:
                handler = get_rotating_file_handler(log_file, max_bytes=1024, backup_count=3)
                handler.setFormatter(logging.Formatter('%(message)s'))

                logger = logging.getLogger('rotating_test_logger')
                logger.setLevel(logging.INFO)
                logger.addHandler(handler)

                logger.info('Test message')
                handler.close()
                logger.removeHandler(handler)

                assert os.path.exists(log_file)
                with open(log_file, 'r') as f:
                    content = f.read()
                    assert 'Test message' in content
            finally:
                logging.root.handlers = saved_handlers


class TestMultiHandlerLogging:
    """Test multiple handlers with different configurations."""

    def test_setup_multi_handler_logging_adds_handlers(self):
        """setup_multi_handler_logging should add handlers to root logger.

        HINT: logging.getLogger() to get root logger, then addHandler()
        """
        from logger import setup_multi_handler_logging

        with tempfile.TemporaryDirectory() as tmpdir:
            log_file = os.path.join(tmpdir, 'test.log')

            # Clear existing handlers
            saved_handlers = logging.root.handlers[:]
            logging.root.handlers = []

            try:
                setup_multi_handler_logging(
                    console_level=logging.INFO,
                    file_level=logging.DEBUG,
                    log_file=log_file
                )

                # Should have at least 2 handlers (console + file)
                assert len(logging.root.handlers) >= 2
            finally:
                for handler in logging.root.handlers[:]:
                    handler.close()
                    logging.root.removeHandler(handler)
                logging.root.handlers = saved_handlers

    def test_console_handler_uses_correct_level(self):
        """Console handler should use the specified level.

        HINT: StreamHandler for console, set level with setLevel()
        """
        from logger import setup_multi_handler_logging

        with tempfile.TemporaryDirectory() as tmpdir:
            log_file = os.path.join(tmpdir, 'test.log')

            saved_handlers = logging.root.handlers[:]
            logging.root.handlers = []

            try:
                setup_multi_handler_logging(
                    console_level=logging.WARNING,
                    file_level=logging.DEBUG,
                    log_file=log_file
                )

                # Find console handler (StreamHandler)
                console_handler = None
                for handler in logging.root.handlers:
                    if isinstance(handler, logging.StreamHandler) and not isinstance(handler, logging.FileHandler):
                        console_handler = handler
                        break

                assert console_handler is not None
                assert console_handler.level == logging.WARNING
            finally:
                for handler in logging.root.handlers[:]:
                    handler.close()
                    logging.root.removeHandler(handler)
                logging.root.handlers = saved_handlers

    def test_file_handler_uses_correct_level(self):
        """File handler should use the specified level.

        HINT: FileHandler or RotatingFileHandler, set level with setLevel()
        """
        from logger import setup_multi_handler_logging

        with tempfile.TemporaryDirectory() as tmpdir:
            log_file = os.path.join(tmpdir, 'test.log')

            saved_handlers = logging.root.handlers[:]
            logging.root.handlers = []

            try:
                setup_multi_handler_logging(
                    console_level=logging.WARNING,
                    file_level=logging.DEBUG,
                    log_file=log_file
                )

                # Find file handler
                file_handler = None
                for handler in logging.root.handlers:
                    if isinstance(handler, logging.FileHandler):
                        file_handler = handler
                        break

                assert file_handler is not None
                assert file_handler.level == logging.DEBUG
            finally:
                for handler in logging.root.handlers[:]:
                    handler.close()
                    logging.root.removeHandler(handler)
                logging.root.handlers = saved_handlers

    def test_multi_handler_logging_writes_to_file(self):
        """Multi-handler setup should write logs to file.

        HINT: File handler should capture messages
        """
        from logger import setup_multi_handler_logging

        with tempfile.TemporaryDirectory() as tmpdir:
            log_file = os.path.join(tmpdir, 'test.log')

            saved_handlers = logging.root.handlers[:]
            logging.root.handlers = []

            try:
                setup_multi_handler_logging(
                    console_level=logging.WARNING,
                    file_level=logging.DEBUG,
                    log_file=log_file
                )

                logger = logging.getLogger('multi_handler_test_logger')
                logger.info('Test message')

                # Close handlers to flush
                for handler in logging.root.handlers[:]:
                    handler.close()
                    logging.root.removeHandler(handler)

                assert os.path.exists(log_file)
                with open(log_file, 'r') as f:
                    content = f.read()
                    assert 'Test message' in content
            finally:
                logging.root.handlers = saved_handlers


class TestHandlerLevels:
    """Test that handler levels filter messages correctly."""

    def test_handler_level_filters_messages(self):
        """Handler with WARNING level should not log INFO messages.

        HINT: Each handler has its own level that filters independently
        """
        from logger import setup_multi_handler_logging

        with tempfile.TemporaryDirectory() as tmpdir:
            log_file = os.path.join(tmpdir, 'test.log')

            saved_handlers = logging.root.handlers[:]
            logging.root.handlers = []

            try:
                # Console: WARNING+, File: DEBUG+
                setup_multi_handler_logging(
                    console_level=logging.WARNING,
                    file_level=logging.DEBUG,
                    log_file=log_file
                )

                logger = logging.getLogger('level_filter_test_logger')
                logger.setLevel(logging.DEBUG)

                # Log at different levels
                logger.debug('Debug message')
                logger.info('Info message')
                logger.warning('Warning message')

                # Close handlers
                for handler in logging.root.handlers[:]:
                    handler.close()
                    logging.root.removeHandler(handler)

                # File should have all messages (DEBUG+)
                with open(log_file, 'r') as f:
                    content = f.read()
                    assert 'Debug message' in content
                    assert 'Info message' in content
                    assert 'Warning message' in content
            finally:
                logging.root.handlers = saved_handlers


class TestRealWorldScenario:
    """Test a real-world logging setup."""

    def test_production_like_setup(self):
        """Set up logging similar to production environment.

        HINT: Multiple handlers, different levels, different formatters
        """
        from logger import setup_multi_handler_logging

        with tempfile.TemporaryDirectory() as tmpdir:
            log_file = os.path.join(tmpdir, 'app.log')

            saved_handlers = logging.root.handlers[:]
            logging.root.handlers = []

            try:
                setup_multi_handler_logging(
                    console_level=logging.INFO,
                    file_level=logging.DEBUG,
                    log_file=log_file
                )

                logger = logging.getLogger('production_test_logger')
                logger.setLevel(logging.DEBUG)

                # Simulate application logging
                logger.debug('Database query: SELECT * FROM users')
                logger.info('User logged in: user123')
                logger.warning('API rate limit approaching')
                logger.error('Database connection failed')

                # Close handlers
                for handler in logging.root.handlers[:]:
                    handler.close()
                    logging.root.removeHandler(handler)

                # File should have all messages
                with open(log_file, 'r') as f:
                    content = f.read()
                    assert 'Database query' in content
                    assert 'User logged in' in content
                    assert 'API rate limit' in content
                    assert 'Database connection failed' in content
            finally:
                logging.root.handlers = saved_handlers
