"""Tests for Lesson 2.1: Basic Logging

This module tests the basic logging functionality:
- Logger creation
- Basic logging methods (info, warning, error)
- Log levels (DEBUG, INFO, WARNING, ERROR, CRITICAL)
- Log message formatting
"""
import logging
import tempfile
import os
import pytest


@pytest.fixture(autouse=True)
def reset_logging():
    """Reset logging configuration before and after each test."""
    # Before test: clear all handlers and reset level
    for handler in logging.root.handlers[:]:
        logging.root.removeHandler(handler)
        handler.close()
    logging.root.setLevel(logging.INFO)  # Changed to INFO since that's the default
    
    yield
    
    # After test: clear all handlers again
    for handler in logging.root.handlers[:]:
        logging.root.removeHandler(handler)
        handler.close()
    logging.root.setLevel(logging.INFO)


class TestImports:
    """Test that logger module can be imported."""
    
    def test_logger_module_exists(self):
        """Should be able to import logger module.
        
        HINT: Create src/logger.py file
        """
        import logger
        assert logger is not None
    
    def test_get_logger_function_exists(self):
        """Should have a get_logger() function.
        
        HINT: def get_logger(name: str) -> logging.Logger:
        """
        from logger import get_logger
        assert callable(get_logger)


class TestBasicLogging:
    """Test basic logging functionality."""
    
    def test_get_logger_returns_logger(self):
        """get_logger() should return a Logger instance.
        
        HINT: return logging.getLogger(name)
        """
        from logger import get_logger
        logger = get_logger('test')
        assert isinstance(logger, logging.Logger)
    
    def test_logger_has_name(self):
        """Logger should have the specified name.
        
        HINT: Logger name helps identify where logs come from
        """
        from logger import get_logger
        logger = get_logger('my_app')
        assert logger.name == 'my_app'
    
    def test_logger_can_log_info(self, caplog):
        """Logger should be able to log INFO messages.
        
        HINT: logger.info('message')
        """
        from logger import get_logger
        logger = get_logger('test')
        
        with caplog.at_level(logging.INFO):
            logger.info('Test info message')
        
        assert 'Test info message' in caplog.text
    
    def test_logger_can_log_warning(self, caplog):
        """Logger should be able to log WARNING messages.
        
        HINT: logger.warning('message')
        """
        from logger import get_logger
        logger = get_logger('test')
        
        with caplog.at_level(logging.WARNING):
            logger.warning('Test warning message')
        
        assert 'Test warning message' in caplog.text
    
    def test_logger_can_log_error(self, caplog):
        """Logger should be able to log ERROR messages.
        
        HINT: logger.error('message')
        """
        from logger import get_logger
        logger = get_logger('test')
        
        with caplog.at_level(logging.ERROR):
            logger.error('Test error message')
        
        assert 'Test error message' in caplog.text


class TestLogLevels:
    """Test different log levels."""
    
    def test_debug_level_lowest(self, caplog):
        """DEBUG is the lowest level - shows everything.
        
        HINT: logging.DEBUG = 10
        """
        from logger import get_logger
        logger = get_logger('test')
        logger.setLevel(logging.DEBUG)
        
        with caplog.at_level(logging.DEBUG):
            logger.debug('Debug message')
            logger.info('Info message')
            logger.warning('Warning message')
        
        assert 'Debug message' in caplog.text
        assert 'Info message' in caplog.text
        assert 'Warning message' in caplog.text
    
    def test_info_level_filters_debug(self, caplog):
        """INFO level filters out DEBUG messages.
        
        HINT: logger.setLevel(logging.INFO)
        """
        from logger import get_logger
        logger = get_logger('test')
        logger.setLevel(logging.INFO)
        
        with caplog.at_level(logging.DEBUG):
            logger.debug('Debug message')
            logger.info('Info message')
        
        assert 'Debug message' not in caplog.text
        assert 'Info message' in caplog.text
    
    def test_warning_level_filters_info_and_debug(self, caplog):
        """WARNING level shows only warnings and above.
        
        HINT: Set level to logging.WARNING
        """
        from logger import get_logger
        logger = get_logger('test')
        logger.setLevel(logging.WARNING)
        
        with caplog.at_level(logging.DEBUG):
            logger.debug('Debug message')
            logger.info('Info message')
            logger.warning('Warning message')
            logger.error('Error message')
        
        assert 'Debug message' not in caplog.text
        assert 'Info message' not in caplog.text
        assert 'Warning message' in caplog.text
        assert 'Error message' in caplog.text


class TestLoggingConfiguration:
    """Test logging configuration setup."""
    
    def test_setup_logging_function_exists(self):
        """Should have a setup_logging() function.
        
        HINT: def setup_logging(level=logging.INFO, log_file=None):
        """
        from logger import setup_logging
        assert callable(setup_logging)
    
    def test_setup_logging_configures_root_logger(self):
        """setup_logging() should configure the root logger.
        
        HINT: Use logging.basicConfig()
        """
        from logger import setup_logging
        
        # Reset logging
        logging.root.handlers = []
        
        setup_logging()
        
        # Should have at least one handler
        assert len(logging.root.handlers) > 0
    
    def test_setup_logging_sets_level(self):
        """setup_logging() should set the logging level.
        
        HINT: logging.basicConfig(level=level)
        """
        from logger import setup_logging
        
        logging.root.handlers = []
        setup_logging(level=logging.WARNING)
        
        assert logging.root.level == logging.WARNING
    
    def test_setup_logging_with_file(self):
        """setup_logging() should log to a file when specified.
        
        HINT: logging.basicConfig(filename=log_file)
        """
        from logger import setup_logging
        
        with tempfile.TemporaryDirectory() as tmpdir:
            log_file = os.path.join(tmpdir, 'test.log')
            
            # Store and remove any caplog handlers
            saved_handlers = logging.root.handlers[:]
            logging.root.handlers = []
            
            try:
                setup_logging(log_file=log_file)
                
                logger = logging.getLogger('file_test_logger')
                logger.info('Test message to file')
                
                # Close all handlers to ensure file is written
                for handler in logging.root.handlers[:]:
                    handler.close()
                    logging.root.removeHandler(handler)
                
                assert os.path.exists(log_file)
                with open(log_file, 'r') as f:
                    content = f.read()
                    assert 'Test message to file' in content
            finally:
                # Restore original handlers
                logging.root.handlers = saved_handlers


class TestLogFormat:
    """Test log message formatting."""
    
    def test_setup_logging_includes_timestamp(self):
        """Log messages should include timestamps.
        
        HINT: format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        """
        from logger import setup_logging
        
        with tempfile.TemporaryDirectory() as tmpdir:
            log_file = os.path.join(tmpdir, 'test.log')
            
            # Store and remove any caplog handlers
            saved_handlers = logging.root.handlers[:]
            logging.root.handlers = []
            
            try:
                setup_logging(log_file=log_file)
                
                logger = logging.getLogger('timestamp_test_logger')
                logger.info('Test message')
                
                # Close all handlers to ensure file is written
                for handler in logging.root.handlers[:]:
                    handler.close()
                    logging.root.removeHandler(handler)
                
                with open(log_file, 'r') as f:
                    content = f.read()
                    # Should have timestamp pattern (contains dashes and colons)
                    assert '-' in content
                    assert 'INFO' in content
                    assert 'Test message' in content
            finally:
                # Restore original handlers
                logging.root.handlers = saved_handlers
    
    def test_setup_logging_includes_level_name(self):
        """Log messages should include level name (INFO, WARNING, etc).
        
        HINT: %(levelname)s in format string
        """
        from logger import setup_logging
        
        with tempfile.TemporaryDirectory() as tmpdir:
            log_file = os.path.join(tmpdir, 'test.log')
            
            logging.root.handlers = []
            setup_logging(log_file=log_file)
            
            logger = logging.getLogger('test')
            logger.warning('Test warning')
            logger.error('Test error')
            
            for handler in logging.root.handlers:
                handler.flush()
            
            with open(log_file, 'r') as f:
                content = f.read()
                assert 'WARNING' in content
                assert 'ERROR' in content
    
    def test_setup_logging_includes_logger_name(self):
        """Log messages should include the logger name.
        
        HINT: %(name)s in format string
        """
        from logger import setup_logging
        
        with tempfile.TemporaryDirectory() as tmpdir:
            log_file = os.path.join(tmpdir, 'test.log')
            
            logging.root.handlers = []
            setup_logging(log_file=log_file)
            
            logger = logging.getLogger('my_module')
            logger.info('Test message')
            
            for handler in logging.root.handlers:
                handler.flush()
            
            with open(log_file, 'r') as f:
                content = f.read()
                assert 'my_module' in content


class TestRealWorldUsage:
    """Test real-world logging scenarios."""
    
    def test_logging_replaces_print(self, caplog):
        """Logging is better than print() for debugging.
        
        HINT: Use logger.debug() instead of print()
        """
        from logger import get_logger
        logger = get_logger('calculator')
        
        def add(a, b):
            logger.debug(f'Adding {a} + {b}')
            result = a + b
            logger.debug(f'Result: {result}')
            return result
        
        with caplog.at_level(logging.DEBUG):
            result = add(2, 3)
        
        assert result == 5
        assert 'Adding 2 + 3' in caplog.text
        assert 'Result: 5' in caplog.text
    
    def test_logging_exception_with_traceback(self, caplog):
        """Logger can capture exceptions with tracebacks.
        
        HINT: logger.exception('message') or logger.error('message', exc_info=True)
        """
        from logger import get_logger
        logger = get_logger('test')
        
        def divide(a, b):
            try:
                return a / b
            except ZeroDivisionError:
                logger.exception('Division by zero occurred')
                raise
        
        with caplog.at_level(logging.ERROR):
            with pytest.raises(ZeroDivisionError):
                divide(10, 0)
        
        assert 'Division by zero occurred' in caplog.text
        assert 'ZeroDivisionError' in caplog.text
    
    def test_logging_with_context(self, caplog):
        """Logs should include context information.
        
        HINT: Use f-strings or extra parameters to add context
        """
        from logger import get_logger
        logger = get_logger('api')
        
        user_id = 12345
        endpoint = '/api/users'
        
        with caplog.at_level(logging.INFO):
            logger.info(f'User {user_id} accessed {endpoint}')
        
        assert '12345' in caplog.text
        assert '/api/users' in caplog.text


# Cleanup function
def teardown_module():
    """Clean up logging handlers after tests."""
    logging.root.handlers = []
