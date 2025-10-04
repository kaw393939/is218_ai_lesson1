"""AI Chat REPL with cost tracking and transparency."""

import json
import uuid
from pathlib import Path
from datetime import datetime
import tiktoken
from openai import OpenAI
from config import TypedConfig
from logger import get_logger, setup_logging


# Pricing per 1M tokens (as of January 2025)
# Source: OpenAI Pricing Page
MODEL_PRICING = {
    # Latest models (recommended for most use cases)
    'gpt-4o': {
        'input': 2.50,    # $2.50 per 1M tokens
        'output': 10.00,  # $10.00 per 1M tokens
        'cached_input': 1.25,  # $1.25 per 1M cached tokens
    },
    'gpt-4o-mini': {
        'input': 0.15,    # $0.15 per 1M tokens
        'output': 0.60,   # $0.60 per 1M tokens
        'cached_input': 0.075,  # $0.075 per 1M cached tokens
    },
    
    # GPT-5 series (newest, most capable)
    'gpt-5': {
        'input': 1.25,
        'output': 10.00,
        'cached_input': 0.125,
    },
    'gpt-5-mini': {
        'input': 0.25,
        'output': 2.00,
        'cached_input': 0.025,
    },
    'gpt-5-nano': {
        'input': 0.05,
        'output': 0.40,
        'cached_input': 0.005,
    },
    
    # GPT-4.1 series
    'gpt-4.1': {
        'input': 2.00,
        'output': 8.00,
        'cached_input': 0.50,
    },
    'gpt-4.1-mini': {
        'input': 0.40,
        'output': 1.60,
        'cached_input': 0.10,
    },
    'gpt-4.1-nano': {
        'input': 0.10,
        'output': 0.40,
        'cached_input': 0.025,
    },
    
    # O-series (reasoning models)
    'o3-mini': {
        'input': 1.10,
        'output': 4.40,
        'cached_input': 0.55,
    },
    'o4-mini': {
        'input': 1.10,
        'output': 4.40,
        'cached_input': 0.275,
    },
    
    # Legacy models (for comparison)
    'gpt-4-turbo': {
        'input': 10.00,
        'output': 30.00,
    },
    'gpt-3.5-turbo': {
        'input': 0.50,
        'output': 1.50,
    },
}


class ChatConfig(TypedConfig):
    """Configuration for AI chat application."""

    @property
    def model(self) -> str:
        """OpenAI model to use (e.g., gpt-3.5-turbo, gpt-4-turbo)."""
        return self.get_str('CHAT_MODEL', 'gpt-3.5-turbo')

    @property
    def max_tokens(self) -> int:
        """Maximum tokens in response."""
        return self.get_int('CHAT_MAX_TOKENS', 500)

    @property
    def temperature(self) -> float:
        """Response randomness (0.0-2.0)."""
        return self.get_float('CHAT_TEMPERATURE', 0.7)

    @property
    def session_budget(self) -> float:
        """Maximum cost per session (0 = unlimited)."""
        return self.get_float('CHAT_SESSION_BUDGET', 0.0)

    @property
    def daily_budget(self) -> float:
        """Maximum cost per day per user (0 = unlimited)."""
        return self.get_float('CHAT_DAILY_BUDGET', 0.0)

    @property
    def budget_warning_threshold(self) -> float:
        """Budget warning threshold (0.0-1.0)."""
        return self.get_float('CHAT_BUDGET_WARNING', 0.75)

    @property
    def user_id(self) -> str:
        """User identifier for cost tracking."""
        return self.get_str('CHAT_USER_ID', 'default')

    @property
    def cost_log_file(self) -> str:
        """File to log cost data."""
        return self.get_str('CHAT_COST_LOG_FILE', 'costs.json')

    @property
    def log_level(self) -> str:
        """Logging level (DEBUG, INFO, WARNING, ERROR)."""
        return self.get_str('CHAT_LOG_LEVEL', 'INFO')

    @property
    def log_file(self) -> str:
        """Path to log file."""
        return self.get_str('CHAT_LOG_FILE', 'chat.log')


def count_tokens(text: str, model: str = "gpt-3.5-turbo") -> int:
    """Count tokens in text for given model.

    Args:
        text: Text to count tokens for
        model: Model name (different models use different encodings)

    Returns:
        Number of tokens

    Note:
        Falls back to cl100k_base encoding for unknown models.
    """
    try:
        encoding = tiktoken.encoding_for_model(model)
    except KeyError:
        # Fallback for unknown models
        encoding = tiktoken.get_encoding("cl100k_base")
    return len(encoding.encode(text))


def calculate_cost(model: str, input_tokens: int, output_tokens: int) -> float:
    """Calculate cost for API call.

    Args:
        model: Model name
        input_tokens: Number of input tokens
        output_tokens: Number of output tokens

    Returns:
        Cost in dollars

    Raises:
        ValueError: If model not found in pricing
    """
    if model not in MODEL_PRICING:
        raise ValueError(f"Unknown model: {model}")

    pricing = MODEL_PRICING[model]
    input_cost = (input_tokens / 1_000_000) * pricing['input']
    output_cost = (output_tokens / 1_000_000) * pricing['output']

    return input_cost + output_cost


class CostTracker:
    """Track and persist cost data."""

    def __init__(self, cost_file: str = "costs.json"):
        """Initialize cost tracker.

        Args:
            cost_file: Path to JSON file for storing cost data
        """
        self.cost_file = Path(cost_file)
        self.costs = self._load_costs()

    def _load_costs(self) -> dict:
        """Load existing cost data from file.

        Returns:
            Dictionary of cost data by user and date
        """
        if self.cost_file.exists():
            with open(self.cost_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {}

    def _save_costs(self):
        """Save cost data to file."""
        with open(self.cost_file, 'w', encoding='utf-8') as f:
            json.dump(self.costs, f, indent=2)

    def add_session(self, session_id: str, user_id: str,
                   cost: float, messages: int):
        """Add session cost data.

        Args:
            session_id: Unique session identifier
            user_id: User identifier
            cost: Total session cost
            messages: Number of messages
        """
        date = datetime.now().strftime('%Y-%m-%d')

        if user_id not in self.costs:
            self.costs[user_id] = {}

        if date not in self.costs[user_id]:
            self.costs[user_id][date] = {
                'sessions': [],
                'total_cost': 0.0,
                'total_messages': 0
            }

        self.costs[user_id][date]['sessions'].append({
            'session_id': session_id,
            'cost': cost,
            'messages': messages,
            'timestamp': datetime.now().isoformat()
        })

        self.costs[user_id][date]['total_cost'] += cost
        self.costs[user_id][date]['total_messages'] += messages

        self._save_costs()

    def get_daily_cost(self, user_id: str, date: str | None = None) -> float:
        """Get total cost for user on given date.

        Args:
            user_id: User identifier
            date: Date in YYYY-MM-DD format (defaults to today)

        Returns:
            Total cost for the day
        """
        if date is None:
            date = datetime.now().strftime('%Y-%m-%d')

        if user_id in self.costs and date in self.costs[user_id]:
            return self.costs[user_id][date]['total_cost']
        return 0.0


class ChatREPL:
    """Interactive AI chat REPL with cost tracking and budgets."""

    def __init__(self, config: ChatConfig | None = None):
        """Initialize chat REPL.

        Args:
            config: Optional configuration object. If None, creates default config.
        """
        self.config = config or ChatConfig()
        self.client = OpenAI()

        # Setup logging
        setup_logging(
            level=self.config.log_level,
            log_file=self.config.log_file
        )
        self.logger = get_logger(__name__)

        # Session tracking
        self.session_id = str(uuid.uuid4())[:8]
        self.session_cost = 0.0
        self.message_count = 0
        self.running = False

        # Cost tracking
        self.cost_tracker = CostTracker(self.config.cost_log_file)

        # Log session start
        self.logger.info(
            "Chat session started",
            extra={
                'session_id': self.session_id,
                'user_id': self.config.user_id,
                'model': self.config.model
            }
        )

        # Check daily budget
        daily_cost = self.cost_tracker.get_daily_cost(self.config.user_id)
        if self.config.daily_budget > 0 and daily_cost >= self.config.daily_budget:
            self.logger.warning(
                "Daily budget already exceeded: $%.4f >= $%.4f",
                daily_cost,
                self.config.daily_budget,
                extra={'user_id': self.config.user_id}
            )
            print(f"⚠️  Daily budget exceeded (${daily_cost:.4f})")
            print("Contact administrator to increase budget.")
            self.running = False

    def start(self):
        """Start the chat REPL."""
        print("AI Chat REPL - Type 'exit' to quit, 'help' for commands\n")
        self.running = True

        while self.running:
            try:
                user_input = input("You: ").strip()
                if not user_input:
                    continue

                self.process_message(user_input)

            except KeyboardInterrupt:
                print("\nUse 'exit' to quit")
            except EOFError:
                print("\nGoodbye!")
                break

    def _print_help(self):
        """Print available commands and current settings."""
        print("\nAvailable commands:")
        print("  exit    - Exit the chat")
        print("  help    - Show this help message")
        print("  /cost   - Show cost report")
        print("  /budget - Show budget status")
        print("\nCurrent settings:")
        print(f"  Model: {self.config.model}")
        print(f"  Max tokens: {self.config.max_tokens}")
        print(f"  Temperature: {self.config.temperature}")
        print("\nSession stats:")
        print(f"  Messages: {self.message_count}")
        print(f"  Total cost: ${self.session_cost:.6f}")

    def _check_budget(self, estimated_cost: float) -> bool:
        """Check if estimated cost is within budget.

        Args:
            estimated_cost: Estimated cost of next API call

        Returns:
            True if within budget, False if over
        """
        if self.config.session_budget <= 0:
            return True  # No budget limit

        projected_total = self.session_cost + estimated_cost

        if projected_total > self.config.session_budget:
            self.logger.warning(
                "Budget exceeded: $%.6f + $%.6f = $%.6f > $%.6f",
                self.session_cost,
                estimated_cost,
                projected_total,
                self.config.session_budget,
                extra={
                    'session_id': self.session_id,
                    'user_id': self.config.user_id,
                    'session_cost': self.session_cost,
                    'estimated_cost': estimated_cost,
                    'budget': self.config.session_budget,
                    'over_budget': True
                }
            )

            print("\n⚠️  Budget Exceeded!")
            print(f"Session cost: ${self.session_cost:.4f}")
            print(f"Session budget: ${self.config.session_budget:.4f}")
            print(f"This message would cost: ${estimated_cost:.6f}")
            print("\nSession ended due to budget limit.")

            self.running = False
            return False

        return True

    def _check_budget_warnings(self):
        """Check budget usage and display warnings."""
        if self.config.session_budget <= 0:
            return  # No budget limit

        usage_percent = self.session_cost / self.config.session_budget

        if usage_percent >= 0.9:
            self.logger.warning(
                "Budget critical: %.0f%% used",
                usage_percent * 100,
                extra={
                    'session_id': self.session_id,
                    'user_id': self.config.user_id,
                    'budget_percent': usage_percent,
                    'session_cost': self.session_cost,
                    'budget': self.config.session_budget
                }
            )
            print(f"\n🚨 Critical: {usage_percent*100:.0f}% of budget used!")

        elif usage_percent >= self.config.budget_warning_threshold:
            self.logger.info(
                "Budget warning: %.0f%% used",
                usage_percent * 100,
                extra={
                    'session_id': self.session_id,
                    'user_id': self.config.user_id,
                    'budget_percent': usage_percent,
                    'session_cost': self.session_cost,
                    'budget': self.config.session_budget
                }
            )
            print(f"\n⚠️  Warning: {usage_percent*100:.0f}% of budget used")

    def _show_cost_report(self):
        """Display cost report for current user."""
        print("\n📊 Cost Report")
        print("=" * 50)
        print(f"Session: ${self.session_cost:.6f} ({self.message_count} messages)")

        if self.config.daily_budget > 0:
            daily_cost = self.cost_tracker.get_daily_cost(self.config.user_id)
            daily_percent = (daily_cost / self.config.daily_budget) * 100
            print(f"Today: ${daily_cost:.4f} / ${self.config.daily_budget:.2f} "
                  f"({daily_percent:.1f}%)")

        if self.session_cost > 0:
            avg_cost = self.session_cost / self.message_count
            print(f"Average per message: ${avg_cost:.6f}")

    def _show_budget_status(self):
        """Display budget status."""
        print("\n💰 Budget Status")
        print("=" * 50)

        if self.config.session_budget > 0:
            session_percent = (self.session_cost / self.config.session_budget) * 100
            print(f"Session: ${self.session_cost:.6f} / "
                  f"${self.config.session_budget:.2f} ({session_percent:.1f}%)")
        else:
            print(f"Session: ${self.session_cost:.6f} (no limit)")

        if self.config.daily_budget > 0:
            daily_cost = self.cost_tracker.get_daily_cost(self.config.user_id)
            daily_percent = (daily_cost / self.config.daily_budget) * 100
            print(f"Daily: ${daily_cost:.4f} / "
                  f"${self.config.daily_budget:.2f} ({daily_percent:.1f}%)")
        else:
            print("Daily: No limit set")

    def stop(self):
        """Stop REPL and save session data."""
        # Save session cost data
        self.cost_tracker.add_session(
            self.session_id,
            self.config.user_id,
            self.session_cost,
            self.message_count
        )

        self.logger.info(
            "Chat session ended",
            extra={
                'session_id': self.session_id,
                'user_id': self.config.user_id,
                'total_cost': self.session_cost,
                'messages': self.message_count
            }
        )

    def process_message(self, message: str):
        """Process user message with cost tracking and logging.

        Args:
            message: User's message text
        """
        # Handle exit command
        if message.lower() == 'exit':
            self.stop()
            self.running = False
            print(f"\nGoodbye! Total cost: ${self.session_cost:.6f}")
            return

        # Handle help command
        if message.lower() == 'help':
            self._print_help()
            return

        # Handle cost command
        if message.lower() == '/cost':
            self._show_cost_report()
            return

        # Handle budget command
        if message.lower() == '/budget':
            self._show_budget_status()
            return

        # Count tokens and estimate cost
        input_tokens = count_tokens(message, self.config.model)
        estimated_cost = calculate_cost(
            self.config.model,
            input_tokens,
            self.config.max_tokens  # Assume max output for estimation
        )

        print(f"\n[Estimated cost: ${estimated_cost:.6f}]")

        # Check budget BEFORE API call
        if not self._check_budget(estimated_cost):
            return

        # Make API call
        try:
            response = self.client.chat.completions.create(
                model=self.config.model,
                messages=[{"role": "user", "content": message}],
                max_tokens=self.config.max_tokens,
                temperature=self.config.temperature
            )

            # Extract response and usage
            reply = response.choices[0].message.content
            actual_input = response.usage.prompt_tokens
            actual_output = response.usage.completion_tokens
            total_tokens = response.usage.total_tokens

            # Calculate actual cost
            actual_cost = calculate_cost(
                self.config.model,
                actual_input,
                actual_output
            )

            self.session_cost += actual_cost
            self.message_count += 1

            # Log the API call with full cost details
            self.logger.info(
                "API call completed: %s tokens for $%.6f",
                total_tokens,
                actual_cost,
                extra={
                    'session_id': self.session_id,
                    'user_id': self.config.user_id,
                    'model': self.config.model,
                    'input_tokens': actual_input,
                    'output_tokens': actual_output,
                    'total_tokens': total_tokens,
                    'cost': actual_cost,
                    'session_total': self.session_cost,
                    'message_count': self.message_count,
                    'prompt_preview': message[:50]
                }
            )

            # Check if approaching budget limit
            self._check_budget_warnings()

            # Display response and cost
            print(f"\nAI: {reply}")
            print(f"\n[Tokens: {actual_input} in + {actual_output} out = "
                  f"{total_tokens} total]")
            print(f"[Cost: ${actual_cost:.6f} | Session: ${self.session_cost:.6f}]")

        except Exception as e:  # pylint: disable=broad-exception-caught
            self.logger.error(
                "API call failed: %s",
                str(e),
                extra={
                    'session_id': self.session_id,
                    'user_id': self.config.user_id,
                    'error': str(e)
                }
            )
            print(f"\nError: {e}")


def main():
    """Entry point for the chat REPL."""
    repl = ChatREPL()
    repl.start()


if __name__ == '__main__':  # pragma: no cover
    main()
