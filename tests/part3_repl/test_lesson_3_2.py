"""
Test suite for Lesson 3.2: Integrating Configuration System

This test suite covers:
1. CalculatorConfig class creation
2. Default configuration values
3. Custom configuration from environment
4. Configuration integration into CalculatorREPL
5. Precision formatting
6. Max value limits
7. Help command functionality
8. Welcome message customization

Run: pytest tests/part3_repl/test_lesson_3_2.py -v
"""

import pytest
from unittest.mock import patch
from io import StringIO
from repl import CalculatorREPL, CalculatorConfig


# ============================================================================
# Test Group 1: CalculatorConfig Creation
# ============================================================================

class TestCalculatorConfigImport:
    """Test that CalculatorConfig can be imported from repl module."""
    
    def test_import_calculator_config(self):
        """CalculatorConfig class should be importable from repl module."""
        assert CalculatorConfig is not None
    
    def test_calculator_config_is_class(self):
        """CalculatorConfig should be a class."""
        assert isinstance(CalculatorConfig, type)


class TestCalculatorConfigDefaults:
    """Test default configuration values when no environment variables set."""
    
    def test_default_precision(self):
        """Default precision should be 2 decimal places."""
        config = CalculatorConfig()
        assert config.precision == 2
    
    def test_default_max_value(self):
        """Default max value should be 1000000.0."""
        config = CalculatorConfig()
        assert config.max_value == 1000000.0
    
    def test_default_welcome_message(self):
        """Default welcome message should be 'Calculator REPL v1.0'."""
        config = CalculatorConfig()
        assert config.welcome_message == 'Calculator REPL v1.0'
    
    def test_default_show_help(self):
        """Default show_help should be True."""
        config = CalculatorConfig()
        assert config.show_help is True


class TestCalculatorConfigCustom:
    """Test custom configuration from environment variables."""
    
    def test_custom_precision(self):
        """Should read REPL_PRECISION from environment."""
        with patch.dict('os.environ', {'REPL_PRECISION': '4'}):
            config = CalculatorConfig()
            assert config.precision == 4
    
    def test_custom_max_value(self):
        """Should read REPL_MAX_VALUE from environment."""
        with patch.dict('os.environ', {'REPL_MAX_VALUE': '999999.99'}):
            config = CalculatorConfig()
            assert config.max_value == 999999.99
    
    def test_custom_welcome_message(self):
        """Should read REPL_WELCOME_MESSAGE from environment."""
        with patch.dict('os.environ', {'REPL_WELCOME_MESSAGE': 'Custom Calculator'}):
            config = CalculatorConfig()
            assert config.welcome_message == 'Custom Calculator'
    
    def test_custom_show_help(self):
        """Should read REPL_SHOW_HELP from environment."""
        with patch.dict('os.environ', {'REPL_SHOW_HELP': 'false'}):
            config = CalculatorConfig()
            assert config.show_help is False


# ============================================================================
# Test Group 2: REPL Configuration Integration
# ============================================================================

class TestREPLWithConfiguration:
    """Test that CalculatorREPL accepts and uses configuration."""
    
    def test_repl_accepts_config(self):
        """REPL should accept CalculatorConfig in constructor."""
        config = CalculatorConfig()
        repl = CalculatorREPL(config)
        assert repl.config is config
    
    def test_repl_creates_default_config(self):
        """REPL should create default config if none provided."""
        repl = CalculatorREPL()
        assert isinstance(repl.config, CalculatorConfig)
    
    def test_repl_uses_config_precision(self):
        """REPL should format results using configured precision."""
        with patch.dict('os.environ', {'REPL_PRECISION': '3'}):
            config = CalculatorConfig()
            repl = CalculatorREPL(config)
            result = repl.execute_command('add', ['1.23456', '2.34567'])
            assert result == 3.580


# ============================================================================
# Test Group 3: Precision Formatting
# ============================================================================

class TestPrecisionFormatting:
    """Test that results are formatted with configured precision."""
    
    def test_precision_2_decimals(self):
        """Results should be rounded to 2 decimal places."""
        with patch.dict('os.environ', {'REPL_PRECISION': '2'}):
            config = CalculatorConfig()
            repl = CalculatorREPL(config)
            result = repl.execute_command('add', ['1.23456', '2.34567'])
            assert result == 3.58
    
    def test_precision_4_decimals(self):
        """Results should be rounded to 4 decimal places."""
        with patch.dict('os.environ', {'REPL_PRECISION': '4'}):
            config = CalculatorConfig()
            repl = CalculatorREPL(config)
            result = repl.execute_command('add', ['1.23456', '2.34567'])
            assert result == 3.5802
    
    def test_precision_0_decimals(self):
        """Results should be rounded to 0 decimal places (integer)."""
        with patch.dict('os.environ', {'REPL_PRECISION': '0'}):
            config = CalculatorConfig()
            repl = CalculatorREPL(config)
            result = repl.execute_command('add', ['1.4', '2.5'])
            assert result == 4.0
    
    def test_precision_with_divide(self):
        """Division should also respect precision."""
        with patch.dict('os.environ', {'REPL_PRECISION': '3'}):
            config = CalculatorConfig()
            repl = CalculatorREPL(config)
            result = repl.execute_command('divide', ['10', '3'])
            assert result == 3.333


# ============================================================================
# Test Group 4: Max Value Limits
# ============================================================================

class TestMaxValueLimits:
    """Test that operations respect max_value configuration."""
    
    def test_result_within_max_value(self):
        """Results below max_value should succeed."""
        with patch.dict('os.environ', {'REPL_MAX_VALUE': '1000'}):
            config = CalculatorConfig()
            repl = CalculatorREPL(config)
            result = repl.execute_command('add', ['100', '200'])
            assert result == 300.0
    
    def test_result_exceeds_max_value(self):
        """Results above max_value should raise ValueError."""
        with patch.dict('os.environ', {'REPL_MAX_VALUE': '100'}):
            config = CalculatorConfig()
            repl = CalculatorREPL(config)
            with pytest.raises(ValueError, match="exceeds maximum value"):
                repl.execute_command('add', ['100', '100'])
    
    def test_negative_result_exceeds_max_value(self):
        """Negative results beyond max_value should also raise ValueError."""
        with patch.dict('os.environ', {'REPL_MAX_VALUE': '100'}):
            config = CalculatorConfig()
            repl = CalculatorREPL(config)
            with pytest.raises(ValueError, match="exceeds maximum value"):
                repl.execute_command('subtract', ['0', '200'])
    
    def test_max_value_edge_case(self):
        """Result exactly at max_value should succeed."""
        with patch.dict('os.environ', {'REPL_MAX_VALUE': '300'}):
            config = CalculatorConfig()
            repl = CalculatorREPL(config)
            result = repl.execute_command('add', ['100', '200'])
            assert result == 300.0


# ============================================================================
# Test Group 5: Help Command
# ============================================================================

class TestHelpCommand:
    """Test help command functionality."""
    
    def test_help_command_exists(self):
        """REPL should handle 'help' command."""
        repl = CalculatorREPL()
        # Should not raise an error
        result = repl.process_command('help')
        assert result is None
    
    @patch('sys.stdout', new_callable=StringIO)
    def test_help_command_output(self, mock_stdout):
        """Help command should print available commands."""
        repl = CalculatorREPL()
        repl.process_command('help')
        output = mock_stdout.getvalue()
        assert 'add' in output.lower()
        assert 'subtract' in output.lower()
        assert 'multiply' in output.lower()
        assert 'divide' in output.lower()
    
    @patch('sys.stdout', new_callable=StringIO)
    def test_help_shows_precision(self, mock_stdout):
        """Help command should show current precision setting."""
        with patch.dict('os.environ', {'REPL_PRECISION': '4'}):
            config = CalculatorConfig()
            repl = CalculatorREPL(config)
            repl.process_command('help')
            output = mock_stdout.getvalue()
            assert '4' in output
            assert 'precision' in output.lower()


# ============================================================================
# Test Group 6: Welcome Message and Startup Help
# ============================================================================

class TestWelcomeMessage:
    """Test welcome message and startup help display."""
    
    @patch('sys.stdout', new_callable=StringIO)
    @patch('builtins.input', side_effect=['exit'])
    def test_default_welcome_message(self, mock_input, mock_stdout):
        """Should display default welcome message on start."""
        repl = CalculatorREPL()
        try:
            repl.start()
        except (EOFError, KeyboardInterrupt):
            pass
        output = mock_stdout.getvalue()
        assert 'Calculator REPL v1.0' in output
    
    @patch('sys.stdout', new_callable=StringIO)
    @patch('builtins.input', side_effect=['exit'])
    def test_custom_welcome_message(self, mock_input, mock_stdout):
        """Should display custom welcome message from config."""
        with patch.dict('os.environ', {'REPL_WELCOME_MESSAGE': 'My Custom Calculator'}):
            config = CalculatorConfig()
            repl = CalculatorREPL(config)
            try:
                repl.start()
            except (EOFError, KeyboardInterrupt):
                pass
            output = mock_stdout.getvalue()
            assert 'My Custom Calculator' in output
    
    @patch('sys.stdout', new_callable=StringIO)
    @patch('builtins.input', side_effect=['exit'])
    def test_help_shown_by_default(self, mock_input, mock_stdout):
        """Help should be shown on startup by default."""
        repl = CalculatorREPL()
        try:
            repl.start()
        except (EOFError, KeyboardInterrupt):
            pass
        output = mock_stdout.getvalue()
        assert 'Available commands' in output
    
    @patch('sys.stdout', new_callable=StringIO)
    @patch('builtins.input', side_effect=['exit'])
    def test_help_can_be_hidden(self, mock_input, mock_stdout):
        """Help should not be shown if show_help is false."""
        with patch.dict('os.environ', {'REPL_SHOW_HELP': 'false'}):
            config = CalculatorConfig()
            repl = CalculatorREPL(config)
            try:
                repl.start()
            except (EOFError, KeyboardInterrupt):
                pass
            output = mock_stdout.getvalue()
            assert 'Available commands' not in output
