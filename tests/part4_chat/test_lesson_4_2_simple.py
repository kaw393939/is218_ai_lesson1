"""Simplified tests for Lesson 4.2 using real objects instead of mocks."""

import json
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch
from chat import ChatConfig, ChatREPL, CostTracker


class TestBudgetConfiguration:
    """Test budget configuration - uses real config objects."""

    def test_default_session_budget(self, monkeypatch):
        """Test default session budget."""
        monkeypatch.delenv('CHAT_SESSION_BUDGET', raising=False)
        config = ChatConfig()
        assert config.session_budget == 0.0

    def test_custom_session_budget(self, monkeypatch):
        """Test custom session budget."""
        monkeypatch.setenv('CHAT_SESSION_BUDGET', '0.50')
        config = ChatConfig()
        assert config.session_budget == 0.50

    def test_budget_config_properties(self, monkeypatch):
        """Test all budget-related config properties."""
        monkeypatch.setenv('CHAT_SESSION_BUDGET', '1.00')
        monkeypatch.setenv('CHAT_DAILY_BUDGET', '10.00')
        monkeypatch.setenv('CHAT_BUDGET_WARNING', '0.80')
        monkeypatch.setenv('CHAT_USER_ID', 'testuser')
        monkeypatch.setenv('CHAT_COST_LOG_FILE', 'test_costs.json')
        
        config = ChatConfig()
        assert config.session_budget == 1.00
        assert config.daily_budget == 10.00
        assert config.budget_warning_threshold == 0.80
        assert config.user_id == 'testuser'
        assert config.cost_log_file == 'test_costs.json'


class TestCostTracker:
    """Test CostTracker - uses real file I/O with temp files."""

    def test_cost_tracker_with_temp_file(self):
        """Test cost tracker creates and uses real files."""
        with tempfile.TemporaryDirectory() as tmpdir:
            cost_file = Path(tmpdir) / "costs.json"
            tracker = CostTracker(str(cost_file))
            
            # Add a session
            tracker.add_session('session123', 'user1', 0.05, 5)
            
            # File should exist
            assert cost_file.exists()
            
            # Should be able to retrieve cost
            cost = tracker.get_daily_cost('user1')
            assert abs(cost - 0.05) < 0.0001

    def test_multiple_sessions_same_day(self):
        """Test multiple sessions accumulate correctly."""
        with tempfile.TemporaryDirectory() as tmpdir:
            cost_file = Path(tmpdir) / "costs.json"
            tracker = CostTracker(str(cost_file))
            
            tracker.add_session('session1', 'user1', 0.05, 3)
            tracker.add_session('session2', 'user1', 0.03, 2)
            tracker.add_session('session3', 'user1', 0.02, 1)
            
            daily_cost = tracker.get_daily_cost('user1')
            assert abs(daily_cost - 0.10) < 0.0001

    def test_load_existing_cost_data(self):
        """Test loading existing cost data from file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            cost_file = Path(tmpdir) / "costs.json"
            
            # Create initial data
            initial_data = {
                'user1': {
                    '2024-01-01': {
                        'sessions': [],
                        'total_cost': 0.05,
                        'total_messages': 3
                    }
                }
            }
            
            with open(cost_file, 'w', encoding='utf-8') as f:
                json.dump(initial_data, f)
            
            # Load it
            tracker = CostTracker(str(cost_file))
            cost = tracker.get_daily_cost('user1', '2024-01-01')
            assert abs(cost - 0.05) < 0.0001

    def test_multiple_users_separate_tracking(self):
        """Test that different users are tracked separately."""
        with tempfile.TemporaryDirectory() as tmpdir:
            cost_file = Path(tmpdir) / "costs.json"
            tracker = CostTracker(str(cost_file))
            
            tracker.add_session('s1', 'user1', 0.05, 3)
            tracker.add_session('s2', 'user2', 0.10, 5)
            tracker.add_session('s3', 'user1', 0.03, 2)
            
            cost1 = tracker.get_daily_cost('user1')
            cost2 = tracker.get_daily_cost('user2')
            
            assert abs(cost1 - 0.08) < 0.0001
            assert abs(cost2 - 0.10) < 0.0001


class TestChatREPLWithBudgets:
    """Test ChatREPL with budget features - mocks only OpenAI API."""

    @patch('chat.OpenAI')
    def test_budget_check_blocks_over_limit(self, mock_openai_class, monkeypatch):
        """Test that budget checking blocks requests that would exceed limit."""
        with tempfile.TemporaryDirectory() as tmpdir:
            cost_file = Path(tmpdir) / "costs.json"
            
            monkeypatch.setenv('CHAT_SESSION_BUDGET', '0.001')
            monkeypatch.setenv('CHAT_COST_LOG_FILE', str(cost_file))
            monkeypatch.setenv('OPENAI_API_KEY', 'test-key')
            
            # Mock only the OpenAI client
            mock_client = Mock()
            mock_openai_class.return_value = mock_client
            
            config = ChatConfig()
            repl = ChatREPL(config)
            
            # Set session cost near limit
            repl.session_cost = 0.00095
            
            # Try to send a message - should be blocked
            repl.process_message("x" * 100)
            
            # API should NOT have been called
            assert mock_client.chat.completions.create.call_count == 0

    @patch('chat.OpenAI')
    def test_successful_message_updates_costs(self, mock_openai_class, monkeypatch, capsys):
        """Test that successful API calls update session costs."""
        with tempfile.TemporaryDirectory() as tmpdir:
            cost_file = Path(tmpdir) / "costs.json"
            
            monkeypatch.setenv('CHAT_COST_LOG_FILE', str(cost_file))
            monkeypatch.setenv('OPENAI_API_KEY', 'test-key')
            
            # Mock OpenAI response
            mock_response = Mock()
            mock_response.choices = [Mock()]
            mock_response.choices[0].message.content = "Test response"
            mock_response.usage.prompt_tokens = 10
            mock_response.usage.completion_tokens = 20
            mock_response.usage.total_tokens = 30
            
            mock_client = Mock()
            mock_client.chat.completions.create.return_value = mock_response
            mock_openai_class.return_value = mock_client
            
            config = ChatConfig()
            repl = ChatREPL(config)
            
            initial_cost = repl.session_cost
            
            # Send a message
            repl.process_message("Hello")
            
            # Cost should have increased
            assert repl.session_cost > initial_cost
            assert repl.message_count == 1
            
            # Should display cost info
            captured = capsys.readouterr()
            assert 'cost' in captured.out.lower() or '$' in captured.out

    @patch('chat.OpenAI')
    def test_cost_persists_on_stop(self, mock_openai_class, monkeypatch):
        """Test that costs are saved to file when session stops."""
        with tempfile.TemporaryDirectory() as tmpdir:
            cost_file = Path(tmpdir) / "costs.json"
            
            monkeypatch.setenv('CHAT_COST_LOG_FILE', str(cost_file))
            monkeypatch.setenv('CHAT_USER_ID', 'testuser')
            monkeypatch.setenv('OPENAI_API_KEY', 'test-key')
            
            mock_client = Mock()
            mock_openai_class.return_value = mock_client
            
            config = ChatConfig()
            repl = ChatREPL(config)
            repl.session_cost = 0.05
            repl.message_count = 3
            
            # Stop the REPL
            repl.stop()
            
            # Cost file should exist and contain data
            assert cost_file.exists()
            
            # Load and verify
            tracker = CostTracker(str(cost_file))
            assert 'testuser' in tracker.costs

    @patch('chat.OpenAI')
    def test_budget_warnings_display(self, mock_openai_class, monkeypatch, capsys):
        """Test that budget warnings are displayed to user."""
        with tempfile.TemporaryDirectory() as tmpdir:
            cost_file = Path(tmpdir) / "costs.json"
            
            monkeypatch.setenv('CHAT_SESSION_BUDGET', '1.00')
            monkeypatch.setenv('CHAT_BUDGET_WARNING', '0.75')
            monkeypatch.setenv('CHAT_COST_LOG_FILE', str(cost_file))
            monkeypatch.setenv('OPENAI_API_KEY', 'test-key')
            
            mock_client = Mock()
            mock_openai_class.return_value = mock_client
            
            config = ChatConfig()
            repl = ChatREPL(config)
            repl.session_cost = 0.76  # 76% of budget
            
            # Check for warnings
            repl._check_budget_warnings()
            
            captured = capsys.readouterr()
            assert 'warning' in captured.out.lower()

    @patch('chat.OpenAI')  
    def test_cost_and_budget_commands(self, mock_openai_class, monkeypatch, capsys):
        """Test /cost and /budget commands work."""
        with tempfile.TemporaryDirectory() as tmpdir:
            cost_file = Path(tmpdir) / "costs.json"
            
            monkeypatch.setenv('CHAT_SESSION_BUDGET', '1.00')
            monkeypatch.setenv('CHAT_COST_LOG_FILE', str(cost_file))
            monkeypatch.setenv('OPENAI_API_KEY', 'test-key')
            
            mock_client = Mock()
            mock_openai_class.return_value = mock_client
            
            config = ChatConfig()
            repl = ChatREPL(config)
            repl.session_cost = 0.05
            repl.message_count = 3
            
            # Test /cost command
            repl.process_message('/cost')
            captured = capsys.readouterr()
            assert 'cost' in captured.out.lower()
            assert '0.05' in captured.out or '.05' in captured.out
            
            # Test /budget command
            repl.process_message('/budget')
            captured = capsys.readouterr()
            assert 'budget' in captured.out.lower()


print("✅ All tests use real objects (Config, CostTracker)")
print("✅ Only OpenAI API client is mocked (to avoid real API costs)")
print("✅ Tests use temporary files for file I/O")
print("✅ No hidden behavior - tests verify actual functionality")
