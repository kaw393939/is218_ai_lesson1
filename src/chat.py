"""AI Chat REPL with cost tracking and transparency."""

import tiktoken
from openai import OpenAI
from config import TypedConfig


# Pricing per 1M tokens (as of 2024)
MODEL_PRICING = {
    'gpt-4-turbo': {
        'input': 0.01,    # $10 per 1M tokens
        'output': 0.03,   # $30 per 1M tokens
    },
    'gpt-3.5-turbo': {
        'input': 0.0005,  # $0.50 per 1M tokens
        'output': 0.0015, # $1.50 per 1M tokens
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


class ChatREPL:
    """Interactive AI chat REPL with cost tracking."""

    def __init__(self, config: ChatConfig | None = None):
        """Initialize chat REPL.

        Args:
            config: Optional configuration object. If None, creates default config.
        """
        self.config = config or ChatConfig()
        self.client = OpenAI()
        self.running = False
        self.session_cost = 0.0
        self.message_count = 0

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
        print("  exit  - Exit the chat")
        print("  help  - Show this help message")
        print("\nCurrent settings:")
        print(f"  Model: {self.config.model}")
        print(f"  Max tokens: {self.config.max_tokens}")
        print(f"  Temperature: {self.config.temperature}")
        print("\nSession stats:")
        print(f"  Messages: {self.message_count}")
        print(f"  Total cost: ${self.session_cost:.6f}")

    def process_message(self, message: str):
        """Process user message.

        Args:
            message: User's message text
        """
        # Handle exit command
        if message.lower() == 'exit':
            self.running = False
            print(f"\nGoodbye! Total cost: ${self.session_cost:.6f}")
            return

        # Handle help command
        if message.lower() == 'help':
            self._print_help()
            return

        # Count tokens and estimate cost
        input_tokens = count_tokens(message, self.config.model)
        estimated_cost = calculate_cost(
            self.config.model,
            input_tokens,
            self.config.max_tokens  # Assume max output for estimation
        )

        print(f"\n[Estimated cost: ${estimated_cost:.6f}]")

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

            # Display response and cost
            print(f"\nAI: {reply}")
            print(f"\n[Tokens: {actual_input} in + {actual_output} out = "
                  f"{total_tokens} total]")
            print(f"[Cost: ${actual_cost:.6f} | Session: ${self.session_cost:.6f}]")

        except Exception as e:  # pylint: disable=broad-exception-caught
            print(f"\nError: {e}")


def main():
    """Entry point for the chat REPL."""
    repl = ChatREPL()
    repl.start()


if __name__ == '__main__':  # pragma: no cover
    main()
