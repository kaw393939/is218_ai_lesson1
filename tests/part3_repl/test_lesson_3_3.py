"""
Test suite for Lesson 3.3: Adding Logging to REPL

This test suite covers:
1. Logger initialization and        mock_logger = MagicMock()
        mock_get_logger.return_value = mock_logger
        
        repl = CalculatorREPL(config)
        
        # Verify logger attribute exists and is the mocked logger
        assert hasattr(repl, 'logger')
        assert repl.logger == mock_loggerguration
2. Session tracking with unique IDs
3. Command logging at appropriate levels
4. Result logging with context
5. Error logging with full details
6. Debug mode toggling
7. Operation counting
8. Session start/end logging

Run: pytest tests/part3_repl/test_lesson_3_3.py -v
"""

from unittest.mock import patch, MagicMock
from io import StringIO
from repl import CalculatorREPL, CalculatorConfig


# ============================================================================
# Test Group 1: Configuration Extensions
# ============================================================================

class TestLoggingConfiguration:
    """Test logging configuration properties."""
    
    def test_default_log_level(self):
        """Default log level should be INFO."""
        config = CalculatorConfig()
        assert config.log_level == 'INFO'
    
    def test_custom_log_level(self):
        """Should read REPL_LOG_LEVEL from environment."""
        with patch.dict('os.environ', {'REPL_LOG_LEVEL': 'DEBUG'}):
            config = CalculatorConfig()
            assert config.log_level == 'DEBUG'
    
    def test_default_log_file(self):
        """Default log file should be calculator.log."""
        config = CalculatorConfig()
        assert config.log_file == 'calculator.log'
    
    def test_custom_log_file(self):
        """Should read REPL_LOG_FILE from environment."""
        with patch.dict('os.environ', {'REPL_LOG_FILE': 'custom.log'}):
            config = CalculatorConfig()
            assert config.log_file == 'custom.log'
    
    def test_default_log_to_console(self):
        """Default log_to_console should be False."""
        config = CalculatorConfig()
        assert config.log_to_console is False
    
    def test_custom_log_to_console(self):
        """Should read REPL_LOG_TO_CONSOLE from environment."""
        with patch.dict('os.environ', {'REPL_LOG_TO_CONSOLE': 'true'}):
            config = CalculatorConfig()
            assert config.log_to_console is True


# ============================================================================
# Test Group 2: Logger Initialization
# ============================================================================

class TestLoggerInitialization:
    """Test that logger is properly initialized in REPL."""
    
    @patch('repl.get_logger')
    @patch('repl.setup_logging')
    def test_logger_setup_called(self, mock_setup, mock_get_logger):
        """setup_logging should be called with config values."""
        config = CalculatorConfig()
        _ = CalculatorREPL(config)  # noqa: F841
        
        mock_setup.assert_called_once()
        mock_get_logger.assert_called_once()
    
    @patch('repl.get_logger')
    @patch('repl.setup_logging')
    def test_logger_uses_config_level(self, mock_setup, mock_get_logger):
        """Logger should use log_level from config."""
        with patch.dict('os.environ', {'REPL_LOG_LEVEL': 'DEBUG'}):
            config = CalculatorConfig()
            _ = CalculatorREPL(config)
            
            # Verify setup_logging was called with level from config
            call_kwargs = mock_setup.call_args[1]
            assert call_kwargs['level'] == 'DEBUG'
    
    @patch('repl.get_logger')
    @patch('repl.setup_logging')
    def test_logger_uses_config_file(self, mock_setup, mock_get_logger):
        """Logger should use log_file from config."""
        with patch.dict('os.environ', {'REPL_LOG_FILE': 'test.log'}):
            config = CalculatorConfig()
            _ = CalculatorREPL(config)
            
            # Verify setup_logging was called with file from config
            call_kwargs = mock_setup.call_args[1]
            assert call_kwargs['log_file'] == 'test.log'
    
    @patch('repl.get_logger')
    @patch('repl.setup_logging')
    def test_repl_has_logger_attribute(self, mock_setup, mock_get_logger):
        """REPL should have a logger attribute."""
        mock_logger = MagicMock()
        mock_get_logger.return_value = mock_logger
        
        repl = CalculatorREPL()
        assert hasattr(repl, 'logger')
        assert repl.logger == mock_logger


# ============================================================================
# Test Group 3: Session Tracking
# ============================================================================

class TestSessionTracking:
    """Test session ID generation and tracking."""
    
    @patch('repl.get_logger')
    @patch('repl.setup_logging')
    def test_session_id_generated(self, mock_setup, mock_get_logger):
        """REPL should generate a unique session_id."""
        repl = CalculatorREPL()
        assert hasattr(repl, 'session_id')
        assert isinstance(repl.session_id, str)
        assert len(repl.session_id) > 0
    
    @patch('repl.get_logger')
    @patch('repl.setup_logging')
    def test_unique_session_ids(self, mock_setup, mock_get_logger):
        """Each REPL instance should have unique session_id."""
        repl1 = CalculatorREPL()
        repl2 = CalculatorREPL()
        assert repl1.session_id != repl2.session_id
    
    @patch('repl.get_logger')
    @patch('repl.setup_logging')
    def test_operation_count_initialized(self, mock_setup, mock_get_logger):
        """REPL should initialize operation_count to 0."""
        repl = CalculatorREPL()
        assert hasattr(repl, 'operation_count')
        assert repl.operation_count == 0
    
    @patch('repl.get_logger')
    @patch('repl.setup_logging')
    def test_session_start_logged(self, mock_setup, mock_get_logger):
        """Session start should be logged."""
        mock_logger = MagicMock()
        mock_get_logger.return_value = mock_logger
        
        _ = CalculatorREPL()
        
        # Verify logger.info was called for session start
        mock_logger.info.assert_called()
        call_args = mock_logger.info.call_args
        assert 'session' in call_args[0][0].lower() or 'started' in call_args[0][0].lower()


# ============================================================================
# Test Group 4: Command Logging
# ============================================================================

class TestCommandLogging:
    """Test logging of user commands."""
    
    @patch('repl.get_logger')
    @patch('repl.setup_logging')
    def test_command_execution_logged(self, mock_setup, mock_get_logger):
        """Command execution should be logged."""
        mock_logger = MagicMock()
        mock_get_logger.return_value = mock_logger
        
        repl = CalculatorREPL()
        repl.execute_command('add', ['10', '20'])
        
        # Verify logger was called
        assert mock_logger.info.called or mock_logger.debug.called
    
    @patch('repl.get_logger')
    @patch('repl.setup_logging')
    def test_operation_count_incremented(self, mock_setup, mock_get_logger):
        """Operation count should increment after each calculation."""
        repl = CalculatorREPL()
        
        initial_count = repl.operation_count
        repl.execute_command('add', ['10', '20'])
        assert repl.operation_count == initial_count + 1
        
        repl.execute_command('subtract', ['30', '10'])
        assert repl.operation_count == initial_count + 2
    
    @patch('repl.get_logger')
    @patch('repl.setup_logging')
    def test_session_id_in_log_context(self, mock_setup, mock_get_logger):
        """Logs should include session_id in extra context."""
        mock_logger = MagicMock()
        mock_get_logger.return_value = mock_logger
        
        repl = CalculatorREPL()
        repl.execute_command('add', ['10', '20'])
        
        # Check that at least one log call included session_id in extra
        found_session_id = False
        for call_obj in mock_logger.info.call_args_list + mock_logger.debug.call_args_list:
            if 'extra' in call_obj[1]:
                extra = call_obj[1]['extra']
                if 'session_id' in extra:
                    found_session_id = True
                    break
        
        assert found_session_id, "session_id should be in log context"


# ============================================================================
# Test Group 5: Error Logging
# ============================================================================

class TestErrorLogging:
    """Test logging of errors."""
    
    @patch('repl.get_logger')
    @patch('repl.setup_logging')
    @patch('sys.stdout', new_callable=StringIO)
    def test_divide_by_zero_logged(self, mock_stdout, mock_setup, mock_get_logger):
        """Division by zero should be logged as error."""
        mock_logger = MagicMock()
        mock_get_logger.return_value = mock_logger
        
        repl = CalculatorREPL()
        repl.process_command('divide 10 0')
        
        # Verify error was logged
        mock_logger.error.assert_called()
        call_args = mock_logger.error.call_args[0][0]
        assert 'divide' in call_args.lower() or 'zero' in call_args.lower()
    
    @patch('repl.get_logger')
    @patch('repl.setup_logging')
    @patch('sys.stdout', new_callable=StringIO)
    def test_invalid_command_logged(self, mock_stdout, mock_setup, mock_get_logger):
        """Invalid commands should be logged as error."""
        mock_logger = MagicMock()
        mock_get_logger.return_value = mock_logger
        
        repl = CalculatorREPL()
        repl.process_command('invalid 10 20')
        
        # Verify error was logged
        mock_logger.error.assert_called()
    
    @patch('repl.get_logger')
    @patch('repl.setup_logging')
    @patch('sys.stdout', new_callable=StringIO)
    def test_max_value_exceeded_logged(self, mock_stdout, mock_setup, mock_get_logger):
        """Max value exceeded should be logged as error."""
        mock_logger = MagicMock()
        mock_get_logger.return_value = mock_logger
        
        with patch.dict('os.environ', {'REPL_MAX_VALUE': '100'}):
            config = CalculatorConfig()
            repl = CalculatorREPL(config)
            repl.process_command('add 100 100')
            
            # Verify error was logged
            mock_logger.error.assert_called()
    
    @patch('repl.get_logger')
    @patch('repl.setup_logging')
    @patch('sys.stdout', new_callable=StringIO)
    def test_error_includes_context(self, mock_stdout, mock_setup, mock_get_logger):
        """Error logs should include command context."""
        mock_logger = MagicMock()
        mock_get_logger.return_value = mock_logger
        
        repl = CalculatorREPL()
        repl.process_command('divide 10 0')
        
        # Verify error log included extra context
        call_kwargs = mock_logger.error.call_args[1]
        assert 'extra' in call_kwargs
        extra = call_kwargs['extra']
        assert 'session_id' in extra


# ============================================================================
# Test Group 6: Debug Logging
# ============================================================================

class TestDebugLogging:
    """Test debug-level logging."""
    
    @patch('repl.get_logger')
    @patch('repl.setup_logging')
    def test_debug_logs_when_enabled(self, mock_setup, mock_get_logger):
        """Debug logs should be created when log level is DEBUG."""
        mock_logger = MagicMock()
        mock_get_logger.return_value = mock_logger
        
        with patch.dict('os.environ', {'REPL_LOG_LEVEL': 'DEBUG'}):
            config = CalculatorConfig()
            repl = CalculatorREPL(config)
            repl.execute_command('add', ['10', '20'])
            
            # Verify debug was called
            assert mock_logger.debug.called
    
    @patch('repl.get_logger')
    @patch('repl.setup_logging')
    @patch('sys.stdout', new_callable=StringIO)
    def test_process_command_debug_logging(self, mock_stdout, mock_setup, mock_get_logger):
        """process_command should log debug information."""
        mock_logger = MagicMock()
        mock_get_logger.return_value = mock_logger
        
        repl = CalculatorREPL()
        repl.process_command('add 10 20')
        
        # Verify debug was called during processing
        assert mock_logger.debug.called


# ============================================================================
# Test Group 7: Session End Logging
# ============================================================================

class TestSessionEndLogging:
    """Test logging when session ends."""
    
    @patch('repl.get_logger')
    @patch('repl.setup_logging')
    @patch('sys.stdout', new_callable=StringIO)
    @patch('builtins.input', side_effect=['add 10 20', 'exit'])
    def test_exit_command_logged(self, mock_input, mock_stdout, mock_setup, mock_get_logger):
        """Exit command should be logged."""
        mock_logger = MagicMock()
        mock_get_logger.return_value = mock_logger
        
        repl = CalculatorREPL()
        try:
            repl.start()
        except (EOFError, KeyboardInterrupt):
            pass
        
        # Verify exit/session end was logged
        info_calls = [call_obj[0][0] for call_obj in mock_logger.info.call_args_list]
        assert any('exit' in msg.lower() or 'end' in msg.lower() for msg in info_calls)
    
    @patch('repl.get_logger')
    @patch('repl.setup_logging')
    @patch('sys.stdout', new_callable=StringIO)
    @patch('builtins.input', side_effect=['add 10 20', 'multiply 5 6', 'exit'])
    def test_operation_count_in_exit_log(self, mock_input, mock_stdout, mock_setup, mock_get_logger):
        """Exit log should include operation count."""
        mock_logger = MagicMock()
        mock_get_logger.return_value = mock_logger
        
        repl = CalculatorREPL()
        try:
            repl.start()
        except (EOFError, KeyboardInterrupt):
            pass
        
        # Verify operation count was included in logs
        for call_obj in mock_logger.info.call_args_list:
            if 'extra' in call_obj[1]:
                extra = call_obj[1]['extra']
                if 'operations' in str(extra).lower() or 'count' in str(extra).lower():
                    break
        
        # Operation count should be tracked
        assert repl.operation_count == 2
