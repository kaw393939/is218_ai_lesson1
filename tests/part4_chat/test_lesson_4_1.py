"""Tests for Lesson 4.1: Chat REPL with API Integration & Cost Fundamentals."""

from unittest.mock import Mock, patch
import pytest
from chat import (
    ChatConfig,
    ChatREPL,
    count_tokens,
    calculate_cost,
    MODEL_PRICING
)


class TestChatConfiguration:
    """Test chat configuration from environment variables."""

    def test_default_model(self):
        """Test default model configuration."""
        config = ChatConfig()
        assert config.model == 'gpt-3.5-turbo'

    def test_custom_model(self, monkeypatch):
        """Test custom model from environment."""
        monkeypatch.setenv('CHAT_MODEL', 'gpt-4-turbo')
        config = ChatConfig()
        assert config.model == 'gpt-4-turbo'

    def test_default_max_tokens(self):
        """Test default max tokens."""
        config = ChatConfig()
        assert config.max_tokens == 500

    def test_custom_max_tokens(self, monkeypatch):
        """Test custom max tokens from environment."""
        monkeypatch.setenv('CHAT_MAX_TOKENS', '1000')
        config = ChatConfig()
        assert config.max_tokens == 1000

    def test_default_temperature(self):
        """Test default temperature."""
        config = ChatConfig()
        assert config.temperature == 0.7

    def test_custom_temperature(self, monkeypatch):
        """Test custom temperature from environment."""
        monkeypatch.setenv('CHAT_TEMPERATURE', '0.9')
        config = ChatConfig()
        assert config.temperature == 0.9

    def test_inherits_from_typed_config(self):
        """Test that ChatConfig inherits TypedConfig helper methods."""
        config = ChatConfig()
        assert hasattr(config, 'get_str')
        assert hasattr(config, 'get_int')
        assert hasattr(config, 'get_float')


class TestTokenCounting:
    """Test token counting functionality."""

    def test_count_tokens_basic(self):
        """Test counting tokens in simple text."""
        # "Hello world" should be approximately 2-3 tokens
        tokens = count_tokens("Hello world")
        assert 2 <= tokens <= 3

    def test_count_tokens_empty_string(self):
        """Test counting tokens in empty string."""
        tokens = count_tokens("")
        assert tokens == 0

    def test_count_tokens_longer_text(self):
        """Test counting tokens in longer text."""
        text = "The quick brown fox jumps over the lazy dog"
        tokens = count_tokens(text)
        # Should be roughly 10-12 tokens
        assert 8 <= tokens <= 15

    def test_count_tokens_with_model(self):
        """Test counting tokens with specific model."""
        text = "Hello"
        tokens_35 = count_tokens(text, model="gpt-3.5-turbo")
        tokens_4 = count_tokens(text, model="gpt-4-turbo")
        # Different models might have slightly different tokenization
        assert tokens_35 > 0
        assert tokens_4 > 0

    def test_count_tokens_special_characters(self):
        """Test counting tokens with special characters."""
        text = "Hello! How are you? 😊"
        tokens = count_tokens(text)
        assert tokens > 0

    def test_count_tokens_with_unknown_model(self):
        """Test that unknown models fall back to default encoding."""
        # Should not raise error, use fallback encoding
        tokens = count_tokens("Hello", model="unknown-model-xyz")
        assert tokens > 0


class TestCostCalculation:
    """Test cost calculation functionality."""

    def test_calculate_cost_gpt35(self):
        """Test cost calculation for GPT-3.5."""
        cost = calculate_cost('gpt-3.5-turbo', 100, 200)
        # 100 input tokens at $0.0005/1M = $0.00005
        # 200 output tokens at $0.0015/1M = $0.0003
        # Total = $0.00035
        expected = (100 / 1_000_000 * 0.0005) + (200 / 1_000_000 * 0.0015)
        assert abs(cost - expected) < 0.000001

    def test_calculate_cost_gpt4(self):
        """Test cost calculation for GPT-4."""
        cost = calculate_cost('gpt-4-turbo', 100, 200)
        # 100 input tokens at $0.01/1M = $0.001
        # 200 output tokens at $0.03/1M = $0.006
        # Total = $0.007
        expected = (100 / 1_000_000 * 0.01) + (200 / 1_000_000 * 0.03)
        assert abs(cost - expected) < 0.000001

    def test_calculate_cost_zero_tokens(self):
        """Test cost calculation with zero tokens."""
        cost = calculate_cost('gpt-3.5-turbo', 0, 0)
        assert cost == 0.0

    def test_calculate_cost_unknown_model(self):
        """Test that unknown model raises error."""
        with pytest.raises(ValueError, match="Unknown model"):
            calculate_cost('unknown-model', 100, 200)

    def test_model_pricing_has_required_models(self):
        """Test that MODEL_PRICING has required models."""
        assert 'gpt-3.5-turbo' in MODEL_PRICING
        assert 'gpt-4-turbo' in MODEL_PRICING

    def test_model_pricing_structure(self):
        """Test that pricing has correct structure."""
        for model_name, pricing in MODEL_PRICING.items():
            assert 'input' in pricing
            assert 'output' in pricing
            assert isinstance(pricing['input'], (int, float))
            assert isinstance(pricing['output'], (int, float))


class TestChatREPLInitialization:
    """Test ChatREPL initialization."""

    @patch('chat.OpenAI')
    def test_initialization_default_config(self, mock_openai):
        """Test REPL initializes with default config."""
        repl = ChatREPL()
        assert repl.config is not None
        assert repl.running is False
        assert repl.session_cost == 0.0
        assert repl.message_count == 0

    @patch('chat.OpenAI')
    def test_initialization_custom_config(self, mock_openai, monkeypatch):
        """Test REPL initializes with custom config."""
        monkeypatch.setenv('CHAT_MODEL', 'gpt-4-turbo')
        config = ChatConfig()
        repl = ChatREPL(config)
        assert repl.config.model == 'gpt-4-turbo'

    @patch('chat.OpenAI')
    def test_openai_client_created(self, mock_openai):
        """Test that OpenAI client is created."""
        repl = ChatREPL()
        mock_openai.assert_called_once()
        assert repl.client is not None


class TestChatREPLMessageProcessing:
    """Test message processing in ChatREPL."""

    @patch('chat.OpenAI')
    def test_exit_command(self, mock_openai, capsys):
        """Test exit command stops REPL."""
        repl = ChatREPL()
        repl.process_message('exit')
        assert repl.running is False
        captured = capsys.readouterr()
        assert 'Goodbye' in captured.out
        assert 'Total cost' in captured.out

    @patch('chat.OpenAI')
    def test_help_command(self, mock_openai, capsys):
        """Test help command displays information."""
        repl = ChatREPL()
        repl.process_message('help')
        captured = capsys.readouterr()
        assert 'commands' in captured.out.lower() or 'help' in captured.out.lower()

    @patch('chat.OpenAI')
    def test_process_message_calls_api(self, mock_openai):
        """Test that processing message calls OpenAI API."""
        # Setup mock response
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = "Hello!"
        mock_response.usage.prompt_tokens = 5
        mock_response.usage.completion_tokens = 3
        mock_response.usage.total_tokens = 8
        
        mock_client = Mock()
        mock_client.chat.completions.create.return_value = mock_response
        mock_openai.return_value = mock_client
        
        repl = ChatREPL()
        repl.process_message("Hi there")
        
        # Verify API was called
        mock_client.chat.completions.create.assert_called_once()
        call_args = mock_client.chat.completions.create.call_args
        
        # Check that message was passed
        assert call_args.kwargs['messages'][0]['content'] == "Hi there"
        assert call_args.kwargs['model'] == 'gpt-3.5-turbo'

    @patch('chat.OpenAI')
    def test_process_message_updates_session_cost(self, mock_openai):
        """Test that processing message updates session cost."""
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = "Response"
        mock_response.usage.prompt_tokens = 10
        mock_response.usage.completion_tokens = 20
        mock_response.usage.total_tokens = 30
        
        mock_client = Mock()
        mock_client.chat.completions.create.return_value = mock_response
        mock_openai.return_value = mock_client
        
        repl = ChatREPL()
        initial_cost = repl.session_cost
        
        repl.process_message("Test message")
        
        assert repl.session_cost > initial_cost
        assert repl.message_count == 1

    @patch('chat.OpenAI')
    def test_process_message_multiple_messages(self, mock_openai):
        """Test processing multiple messages accumulates costs."""
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = "Response"
        mock_response.usage.prompt_tokens = 10
        mock_response.usage.completion_tokens = 20
        mock_response.usage.total_tokens = 30
        
        mock_client = Mock()
        mock_client.chat.completions.create.return_value = mock_response
        mock_openai.return_value = mock_client
        
        repl = ChatREPL()
        
        repl.process_message("First message")
        cost_after_first = repl.session_cost
        
        repl.process_message("Second message")
        cost_after_second = repl.session_cost
        
        assert cost_after_second > cost_after_first
        assert repl.message_count == 2

    @patch('chat.OpenAI')
    def test_process_message_displays_cost(self, mock_openai, capsys):
        """Test that message processing displays cost information."""
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = "Test response"
        mock_response.usage.prompt_tokens = 5
        mock_response.usage.completion_tokens = 10
        mock_response.usage.total_tokens = 15
        
        mock_client = Mock()
        mock_client.chat.completions.create.return_value = mock_response
        mock_openai.return_value = mock_client
        
        repl = ChatREPL()
        repl.process_message("Test")
        
        captured = capsys.readouterr()
        assert 'cost' in captured.out.lower() or '$' in captured.out
        assert 'token' in captured.out.lower()

    @patch('chat.OpenAI')
    def test_process_message_api_error_handling(self, mock_openai, capsys):
        """Test that API errors are handled gracefully."""
        mock_client = Mock()
        mock_client.chat.completions.create.side_effect = Exception("API Error")
        mock_openai.return_value = mock_client
        
        repl = ChatREPL()
        repl.process_message("Test")
        
        # Should not crash, should display error
        captured = capsys.readouterr()
        assert 'error' in captured.out.lower()


class TestChatREPLConfiguration:
    """Test ChatREPL uses configuration correctly."""

    @patch('chat.OpenAI')
    def test_uses_configured_model(self, mock_openai, monkeypatch):
        """Test that REPL uses configured model."""
        monkeypatch.setenv('CHAT_MODEL', 'gpt-4-turbo')
        
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = "Response"
        mock_response.usage.prompt_tokens = 5
        mock_response.usage.completion_tokens = 5
        mock_response.usage.total_tokens = 10
        
        mock_client = Mock()
        mock_client.chat.completions.create.return_value = mock_response
        mock_openai.return_value = mock_client
        
        repl = ChatREPL()
        repl.process_message("Test")
        
        call_args = mock_client.chat.completions.create.call_args
        assert call_args.kwargs['model'] == 'gpt-4-turbo'

    @patch('chat.OpenAI')
    def test_uses_configured_max_tokens(self, mock_openai, monkeypatch):
        """Test that REPL uses configured max tokens."""
        monkeypatch.setenv('CHAT_MAX_TOKENS', '1000')
        
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = "Response"
        mock_response.usage.prompt_tokens = 5
        mock_response.usage.completion_tokens = 5
        mock_response.usage.total_tokens = 10
        
        mock_client = Mock()
        mock_client.chat.completions.create.return_value = mock_response
        mock_openai.return_value = mock_client
        
        repl = ChatREPL()
        repl.process_message("Test")
        
        call_args = mock_client.chat.completions.create.call_args
        assert call_args.kwargs['max_tokens'] == 1000

    @patch('chat.OpenAI')
    def test_uses_configured_temperature(self, mock_openai, monkeypatch):
        """Test that REPL uses configured temperature."""
        monkeypatch.setenv('CHAT_TEMPERATURE', '0.9')
        
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = "Response"
        mock_response.usage.prompt_tokens = 5
        mock_response.usage.completion_tokens = 5
        mock_response.usage.total_tokens = 10
        
        mock_client = Mock()
        mock_client.chat.completions.create.return_value = mock_response
        mock_openai.return_value = mock_client
        
        repl = ChatREPL()
        repl.process_message("Test")
        
        call_args = mock_client.chat.completions.create.call_args
        assert call_args.kwargs['temperature'] == 0.9


class TestCostTransparency:
    """Test that costs are transparent to users."""

    @patch('chat.OpenAI')
    def test_displays_estimated_cost_before_api_call(self, mock_openai, capsys):
        """Test that estimated cost is shown before API call."""
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = "Response"
        mock_response.usage.prompt_tokens = 5
        mock_response.usage.completion_tokens = 10
        mock_response.usage.total_tokens = 15
        
        mock_client = Mock()
        mock_client.chat.completions.create.return_value = mock_response
        mock_openai.return_value = mock_client
        
        repl = ChatREPL()
        repl.process_message("Test message")
        
        captured = capsys.readouterr()
        # Should show estimated cost
        assert 'estimated' in captured.out.lower() or 'cost' in captured.out.lower()

    @patch('chat.OpenAI')
    def test_displays_actual_cost_after_api_call(self, mock_openai, capsys):
        """Test that actual cost is shown after API call."""
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = "Response"
        mock_response.usage.prompt_tokens = 5
        mock_response.usage.completion_tokens = 10
        mock_response.usage.total_tokens = 15
        
        mock_client = Mock()
        mock_client.chat.completions.create.return_value = mock_response
        mock_openai.return_value = mock_client
        
        repl = ChatREPL()
        repl.process_message("Test message")
        
        captured = capsys.readouterr()
        # Should show cost and session total
        assert 'cost' in captured.out.lower() or '$' in captured.out
        assert 'session' in captured.out.lower()

    @patch('chat.OpenAI')
    def test_displays_token_breakdown(self, mock_openai, capsys):
        """Test that token breakdown is displayed."""
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = "Response"
        mock_response.usage.prompt_tokens = 5
        mock_response.usage.completion_tokens = 10
        mock_response.usage.total_tokens = 15
        
        mock_client = Mock()
        mock_client.chat.completions.create.return_value = mock_response
        mock_openai.return_value = mock_client
        
        repl = ChatREPL()
        repl.process_message("Test message")
        
        captured = capsys.readouterr()
        # Should show token information
        assert 'token' in captured.out.lower()

    @patch('chat.OpenAI')
    def test_displays_session_total_on_exit(self, mock_openai, capsys):
        """Test that session total is displayed on exit."""
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = "Response"
        mock_response.usage.prompt_tokens = 5
        mock_response.usage.completion_tokens = 10
        mock_response.usage.total_tokens = 15
        
        mock_client = Mock()
        mock_client.chat.completions.create.return_value = mock_response
        mock_openai.return_value = mock_client
        
        repl = ChatREPL()
        repl.process_message("Test message")
        repl.process_message("exit")
        
        captured = capsys.readouterr()
        assert 'total cost' in captured.out.lower()
        assert '$' in captured.out
