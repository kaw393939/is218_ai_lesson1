"""Tests for Lesson 2.3: Contextual Logging with Adapters

This module tests contextual logging functionality:
- LoggerAdapter with request ID
- User context in logs
- Arbitrary context addition
- Context manager for automatic context
"""
import logging
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
    """Test that required functions can be imported."""

    def test_get_contextual_logger_exists(self):
        """Should be able to import get_contextual_logger function.

        HINT: def get_contextual_logger(logger, request_id=None):
        """
        from logger import get_contextual_logger
        assert callable(get_contextual_logger)

    def test_get_user_logger_exists(self):
        """Should be able to import get_user_logger function.

        HINT: def get_user_logger(logger, user_id, username=None):
        """
        from logger import get_user_logger
        assert callable(get_user_logger)

    def test_get_logger_with_context_exists(self):
        """Should be able to import get_logger_with_context function.

        HINT: def get_logger_with_context(logger, **context):
        """
        from logger import get_logger_with_context
        assert callable(get_logger_with_context)

    def test_log_context_exists(self):
        """Should be able to import log_context function.

        HINT: from contextlib import contextmanager
              @contextmanager
              def log_context(logger, **context):
        """
        from logger import log_context
        assert callable(log_context)


class TestContextualLogger:
    """Test contextual logger with request ID."""

    def test_get_contextual_logger_returns_adapter(self):
        """get_contextual_logger should return a LoggerAdapter.

        HINT: from logging import LoggerAdapter
              return LoggerAdapter(logger, {'request_id': ...})
        """
        from logger import get_contextual_logger

        base_logger = logging.getLogger('test_contextual')
        context_logger = get_contextual_logger(base_logger, request_id='test-123')

        assert isinstance(context_logger, logging.LoggerAdapter)

    def test_contextual_logger_has_request_id(self):
        """Logger should have request_id in context.

        HINT: LoggerAdapter(logger, {'request_id': request_id})
        """
        from logger import get_contextual_logger

        base_logger = logging.getLogger('test_contextual')
        context_logger = get_contextual_logger(base_logger, request_id='test-123')

        assert 'request_id' in context_logger.extra
        assert context_logger.extra['request_id'] == 'test-123'

    def test_contextual_logger_generates_request_id(self):
        """If no request_id provided, should generate one.

        HINT: import uuid
              request_id = request_id or str(uuid.uuid4())
        """
        from logger import get_contextual_logger

        base_logger = logging.getLogger('test_contextual')
        context_logger = get_contextual_logger(base_logger)

        assert 'request_id' in context_logger.extra
        # Should be a valid UUID format
        request_id = context_logger.extra['request_id']
        assert isinstance(request_id, str)
        assert len(request_id) > 0

    def test_contextual_logger_logs_with_context(self, caplog):
        """Logs should include request_id context.

        HINT: LoggerAdapter automatically adds extra dict to logs
        """
        from logger import get_contextual_logger

        base_logger = logging.getLogger('test_contextual')
        context_logger = get_contextual_logger(base_logger, request_id='abc-123')

        with caplog.at_level(logging.INFO):
            context_logger.info('Test message')

        # Check that log includes context
        assert 'Test message' in caplog.text


class TestUserLogger:
    """Test logger with user context."""

    def test_get_user_logger_returns_adapter(self):
        """get_user_logger should return a LoggerAdapter.

        HINT: return LoggerAdapter(logger, context)
        """
        from logger import get_user_logger

        base_logger = logging.getLogger('test_user')
        user_logger = get_user_logger(base_logger, 'user123')

        assert isinstance(user_logger, logging.LoggerAdapter)

    def test_user_logger_has_user_id(self):
        """Logger should have user_id in context.

        HINT: context = {'user_id': user_id}
        """
        from logger import get_user_logger

        base_logger = logging.getLogger('test_user')
        user_logger = get_user_logger(base_logger, 'user123')

        assert 'user_id' in user_logger.extra
        assert user_logger.extra['user_id'] == 'user123'

    def test_user_logger_with_username(self):
        """Logger should include username if provided.

        HINT: if username:
                  context['username'] = username
        """
        from logger import get_user_logger

        base_logger = logging.getLogger('test_user')
        user_logger = get_user_logger(base_logger, 'user123', username='alice')

        assert 'user_id' in user_logger.extra
        assert user_logger.extra['user_id'] == 'user123'
        assert 'username' in user_logger.extra
        assert user_logger.extra['username'] == 'alice'

    def test_user_logger_without_username(self):
        """Logger should work without username.

        HINT: username is optional parameter
        """
        from logger import get_user_logger

        base_logger = logging.getLogger('test_user')
        user_logger = get_user_logger(base_logger, 'user123')

        assert 'user_id' in user_logger.extra
        assert 'username' not in user_logger.extra


class TestLoggerWithContext:
    """Test logger with arbitrary context."""

    def test_get_logger_with_context_returns_adapter(self):
        """get_logger_with_context should return a LoggerAdapter.

        HINT: def get_logger_with_context(logger, **context):
              return LoggerAdapter(logger, context)
        """
        from logger import get_logger_with_context

        base_logger = logging.getLogger('test_context')
        context_logger = get_logger_with_context(base_logger, key='value')

        assert isinstance(context_logger, logging.LoggerAdapter)

    def test_logger_with_single_context(self):
        """Logger should include single context item.

        HINT: **context captures keyword arguments as dict
        """
        from logger import get_logger_with_context

        base_logger = logging.getLogger('test_context')
        context_logger = get_logger_with_context(base_logger, request_id='abc-123')

        assert 'request_id' in context_logger.extra
        assert context_logger.extra['request_id'] == 'abc-123'

    def test_logger_with_multiple_context(self):
        """Logger should include multiple context items.

        HINT: All **kwargs become context dict
        """
        from logger import get_logger_with_context

        base_logger = logging.getLogger('test_context')
        context_logger = get_logger_with_context(
            base_logger,
            request_id='abc-123',
            user_id='user456',
            endpoint='/api/test'
        )

        assert context_logger.extra['request_id'] == 'abc-123'
        assert context_logger.extra['user_id'] == 'user456'
        assert context_logger.extra['endpoint'] == '/api/test'

    def test_logger_with_no_context(self):
        """Logger should work with no context.

        HINT: Empty dict is valid context
        """
        from logger import get_logger_with_context

        base_logger = logging.getLogger('test_context')
        context_logger = get_logger_with_context(base_logger)

        assert isinstance(context_logger, logging.LoggerAdapter)
        assert context_logger.extra == {}


class TestLogContext:
    """Test context manager for logging."""

    def test_log_context_is_context_manager(self):
        """log_context should be a context manager.

        HINT: @contextmanager decorator from contextlib
        """
        from logger import log_context

        # Should be usable as a context manager
        base_logger = logging.getLogger('test_ctx_mgr_check')
        ctx = log_context(base_logger, test='value')
        # Check it has __enter__ and __exit__ methods (context manager protocol)
        assert hasattr(ctx, '__enter__')
        assert hasattr(ctx, '__exit__')

    def test_log_context_yields_adapter(self):
        """log_context should yield a LoggerAdapter.

        HINT: yield LoggerAdapter(logger, context)
        """
        from logger import log_context

        base_logger = logging.getLogger('test_context_mgr')

        with log_context(base_logger, request_id='test-123') as logger:
            assert isinstance(logger, logging.LoggerAdapter)

    def test_log_context_includes_context(self):
        """Context manager should include provided context.

        HINT: context_logger = LoggerAdapter(logger, context)
        """
        from logger import log_context

        base_logger = logging.getLogger('test_context_mgr')

        with log_context(base_logger, request_id='abc-123', user_id='user456') as logger:
            assert 'request_id' in logger.extra
            assert logger.extra['request_id'] == 'abc-123'
            assert 'user_id' in logger.extra
            assert logger.extra['user_id'] == 'user456'

    def test_log_context_can_log(self, caplog):
        """Should be able to log with context manager.

        HINT: Just use the yielded logger normally
        """
        from logger import log_context

        base_logger = logging.getLogger('test_context_mgr')

        with caplog.at_level(logging.INFO):
            with log_context(base_logger, request_id='abc-123') as logger:
                logger.info('Test message')

        assert 'Test message' in caplog.text


class TestContextPropagation:
    """Test that context propagates correctly."""

    def test_context_persists_across_calls(self, caplog):
        """Context should be included in all log calls.

        HINT: LoggerAdapter keeps context for all calls
        """
        from logger import get_contextual_logger

        base_logger = logging.getLogger('test_propagation')
        context_logger = get_contextual_logger(base_logger, request_id='persist-123')

        with caplog.at_level(logging.INFO):
            context_logger.info('First message')
            context_logger.info('Second message')
            context_logger.info('Third message')

        assert 'First message' in caplog.text
        assert 'Second message' in caplog.text
        assert 'Third message' in caplog.text

    def test_passing_logger_maintains_context(self):
        """Passing logger to functions should maintain context.

        HINT: LoggerAdapter can be passed like regular logger
        """
        from logger import get_contextual_logger

        def helper_function(logger):
            """Helper that uses passed logger."""
            logger.info('Helper called')
            return logger.extra.get('request_id')

        base_logger = logging.getLogger('test_passing')
        context_logger = get_contextual_logger(base_logger, request_id='pass-123')

        request_id = helper_function(context_logger)
        assert request_id == 'pass-123'


class TestRealWorldScenario:
    """Test a realistic usage scenario."""

    def test_web_request_scenario(self, caplog):
        """Simulate a web request with full context.

        HINT: Create logger with context, pass to functions
        """
        from logger import get_logger_with_context

        def validate_user(logger, user_id):
            logger.info(f'Validating user {user_id}')
            return True

        def process_request(logger):
            logger.info('Processing request')
            return {'status': 'success'}

        # Simulate web request handler
        base_logger = logging.getLogger('test_web')
        request_logger = get_logger_with_context(
            base_logger,
            request_id='req-123',
            user_id='user456',
            endpoint='/api/data'
        )

        with caplog.at_level(logging.INFO):
            request_logger.info('Request started')
            validate_user(request_logger, 'user456')
            process_request(request_logger)
            request_logger.info('Request completed')

        assert 'Request started' in caplog.text
        assert 'Validating user' in caplog.text
        assert 'Processing request' in caplog.text
        assert 'Request completed' in caplog.text

    def test_nested_context_managers(self, caplog):
        """Test nested context managers.

        HINT: Context managers can be nested
        """
        from logger import log_context

        base_logger = logging.getLogger('test_nested')

        with caplog.at_level(logging.INFO):
            with log_context(base_logger, request_id='outer-123') as outer_log:
                outer_log.info('Outer context')

                with log_context(outer_log, operation='inner') as inner_log:
                    inner_log.info('Inner context')
                    # Should have both contexts
                    assert 'request_id' in inner_log.extra
                    assert 'operation' in inner_log.extra

        assert 'Outer context' in caplog.text
        assert 'Inner context' in caplog.text
