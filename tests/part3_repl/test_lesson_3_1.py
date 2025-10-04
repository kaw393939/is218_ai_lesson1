"""Tests for Lesson 3.1: Building Your First REPL - Calculator Foundation

This module tests the implementation of a basic REPL (Read-Eval-Print Loop)
calculator with command parsing and error handling.
"""

import io
from unittest.mock import patch


class TestImports:
    """Test that all required components can be imported."""

    def test_import_calculator_repl(self):
        """Test that CalculatorREPL class exists."""
        from repl import CalculatorREPL
        assert CalculatorREPL is not None

    def test_import_main(self):
        """Test that main function exists."""
        from repl import main
        assert callable(main)


class TestCalculatorREPLInit:
    """Test CalculatorREPL initialization."""

    def test_repl_init(self):
        """Test that REPL can be instantiated."""
        from repl import CalculatorREPL
        repl = CalculatorREPL()
        assert repl is not None

    def test_repl_has_running_attribute(self):
        """Test that REPL has running attribute."""
        from repl import CalculatorREPL
        repl = CalculatorREPL()
        assert hasattr(repl, 'running')

    def test_repl_running_starts_false(self):
        """Test that running starts as False."""
        from repl import CalculatorREPL
        repl = CalculatorREPL()
        assert repl.running is False


class TestCommandExecution:
    """Test command execution logic."""

    def test_execute_add_command(self):
        """Test addition command."""
        from repl import CalculatorREPL
        repl = CalculatorREPL()
        result = repl.execute_command('add', ['5', '3'])
        assert result == 8.0

    def test_execute_subtract_command(self):
        """Test subtraction command."""
        from repl import CalculatorREPL
        repl = CalculatorREPL()
        result = repl.execute_command('subtract', ['10', '3'])
        assert result == 7.0

    def test_execute_multiply_command(self):
        """Test multiplication command."""
        from repl import CalculatorREPL
        repl = CalculatorREPL()
        result = repl.execute_command('multiply', ['4', '7'])
        assert result == 28.0

    def test_execute_divide_command(self):
        """Test division command."""
        from repl import CalculatorREPL
        repl = CalculatorREPL()
        result = repl.execute_command('divide', ['10', '2'])
        assert result == 5.0

    def test_execute_with_floats(self):
        """Test operations with float numbers."""
        from repl import CalculatorREPL
        repl = CalculatorREPL()
        result = repl.execute_command('add', ['5.5', '3.2'])
        assert abs(result - 8.7) < 0.0001

    def test_execute_with_negative_numbers(self):
        """Test operations with negative numbers."""
        from repl import CalculatorREPL
        repl = CalculatorREPL()
        result = repl.execute_command('add', ['-5', '3'])
        assert result == -2.0


class TestCommandErrors:
    """Test error handling in command execution."""

    def test_unknown_command_raises_error(self):
        """Test that unknown commands raise ValueError."""
        from repl import CalculatorREPL
        import pytest
        
        repl = CalculatorREPL()
        with pytest.raises(ValueError, match="Unknown command"):
            repl.execute_command('unknown', ['1', '2'])

    def test_wrong_number_of_args_raises_error(self):
        """Test that wrong number of arguments raises ValueError."""
        from repl import CalculatorREPL
        import pytest
        
        repl = CalculatorREPL()
        with pytest.raises(ValueError, match="requires exactly 2 numbers"):
            repl.execute_command('add', ['1'])

    def test_too_many_args_raises_error(self):
        """Test that too many arguments raises ValueError."""
        from repl import CalculatorREPL
        import pytest
        
        repl = CalculatorREPL()
        with pytest.raises(ValueError, match="requires exactly 2 numbers"):
            repl.execute_command('add', ['1', '2', '3'])

    def test_invalid_number_raises_error(self):
        """Test that invalid numbers raise ValueError."""
        from repl import CalculatorREPL
        import pytest
        
        repl = CalculatorREPL()
        with pytest.raises(ValueError, match="Invalid numbers"):
            repl.execute_command('add', ['abc', '2'])

    def test_divide_by_zero_raises_error(self):
        """Test that division by zero raises ZeroDivisionError."""
        from repl import CalculatorREPL
        import pytest
        
        repl = CalculatorREPL()
        with pytest.raises(ZeroDivisionError):
            repl.execute_command('divide', ['10', '0'])


class TestProcessCommand:
    """Test command processing."""

    def test_process_add_command(self):
        """Test processing add command prints result."""
        from repl import CalculatorREPL
        
        repl = CalculatorREPL()
        with patch('sys.stdout', new=io.StringIO()) as fake_stdout:
            repl.process_command('add 5 3')
            output = fake_stdout.getvalue()
            assert 'Result: 8.0' in output

    def test_process_exit_command(self):
        """Test processing exit command sets running to False."""
        from repl import CalculatorREPL
        
        repl = CalculatorREPL()
        repl.running = True
        with patch('sys.stdout', new=io.StringIO()):
            repl.process_command('exit')
        assert repl.running is False

    def test_process_empty_input(self):
        """Test that empty input is handled gracefully."""
        from repl import CalculatorREPL
        
        repl = CalculatorREPL()
        # Should not raise any exception
        with patch('sys.stdout', new=io.StringIO()):
            repl.process_command('')
            repl.process_command('   ')

    def test_process_handles_error(self):
        """Test that process_command catches and prints errors."""
        from repl import CalculatorREPL
        
        repl = CalculatorREPL()
        with patch('sys.stdout', new=io.StringIO()) as fake_stdout:
            repl.process_command('unknown 1 2')
            output = fake_stdout.getvalue()
            assert 'Error' in output


class TestREPLIntegration:
    """Integration tests for the REPL."""

    def test_case_insensitive_commands(self):
        """Test that commands are case-insensitive."""
        from repl import CalculatorREPL
        
        repl = CalculatorREPL()
        result1 = repl.execute_command('ADD', ['5', '3'])
        result2 = repl.execute_command('Add', ['5', '3'])
        result3 = repl.execute_command('add', ['5', '3'])
        assert result1 == result2 == result3 == 8.0

    def test_handles_extra_whitespace(self):
        """Test that extra whitespace is handled."""
        from repl import CalculatorREPL
        
        repl = CalculatorREPL()
        with patch('sys.stdout', new=io.StringIO()) as fake_stdout:
            repl.process_command('  add   5   3  ')
            output = fake_stdout.getvalue()
            assert 'Result: 8.0' in output
