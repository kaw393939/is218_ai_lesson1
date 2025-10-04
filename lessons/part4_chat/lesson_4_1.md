# Lesson 4.1: Chat REPL with API Integration & Cost Fundamentals

**Course**: IS 218 - Building AI Systems  
**Part**: 4 - Cost-Aware AI Chat Application  
**Lesson**: 4.1 - Foundation & Cost Awareness  
**Difficulty**: ⭐⭐⭐☆☆  
**Time**: 60 minutes

## Learning Objectives

By the end of this lesson, you will be able to:

1. Integrate OpenAI API into a REPL application
2. Understand token-based pricing models for AI services
3. Count tokens before making API calls to estimate costs
4. Track actual token usage from API responses
5. Calculate and display costs for each interaction
6. Configure AI model selection through environment variables
7. Build cost-transparent applications that show users what they're spending

## The Story: The $1000 Surprise

Jake built his first AI chatbot and deployed it to production. It worked great! Users loved it. Then at the end of the month, he got his OpenAI bill: **$1,247.63**.

He had no idea:
- Each message cost money (he thought it was "free API calls")
- Different models have different prices (he used GPT-4 for everything)
- Both input AND output tokens cost money
- Long conversations accumulate costs quickly

**His mistake**: He built the feature first, added cost tracking later (never).

**Your approach**: Build cost awareness from day one. Every API call shows its cost. Every session tracks spending. Users see exactly what they're paying for.

## Understanding Token-Based Pricing

### What Are Tokens?

Tokens are the "units of text" that AI models process:
- **1 token ≈ 4 characters** (roughly)
- "Hello world" = ~2 tokens
- "The quick brown fox jumps" = ~6 tokens
- A typical sentence = ~15-20 tokens

**Why tokens matter**: AI services charge per token, not per word or character.

### How Pricing Works

OpenAI charges separately for input and output tokens:

```
GPT-4 Turbo (as of 2024):
- Input:  $10.00 per 1M tokens ($0.00001 per token)
- Output: $30.00 per 1M tokens ($0.00003 per token)

GPT-3.5 Turbo:
- Input:  $0.50 per 1M tokens ($0.0000005 per token)
- Output: $1.50 per 1M tokens ($0.0000015 per token)
```

**Example calculation**:
```
User sends: "Explain quantum computing" (4 tokens)
GPT-4 responds: 200 tokens of explanation

Cost = (4 × $0.00001) + (200 × $0.00003)
     = $0.00004 + $0.006
     = $0.00604
```

### Why This Matters

1. **Costs accumulate**: 1000 conversations/day = $6/day = $180/month
2. **Model choice matters**: GPT-4 costs ~20x more than GPT-3.5
3. **Long responses cost more**: Asking for detailed explanations increases output tokens
4. **Context costs**: Including conversation history in each request costs tokens

## Architecture Overview

We'll build a `ChatREPL` similar to the `CalculatorREPL`, but with:
- OpenAI API integration instead of math operations
- Token counting before API calls (estimation)
- Token tracking after API calls (actual usage)
- Cost calculation and display
- Configuration for model selection and limits

```
User Input → Token Count → API Call → Response + Tokens → Calculate Cost → Display
                ↓                                              ↓
          "This will cost ~$0.002"              "Actual cost: $0.0023"
```

## Configuration Requirements

Create a `ChatConfig` class that extends `TypedConfig`:

```python
from config import TypedConfig

class ChatConfig(TypedConfig):
    """Configuration for AI chat application."""
    
    @property
    def model(self) -> str:
        """OpenAI model to use."""
        return self.get_str('CHAT_MODEL', 'gpt-3.5-turbo')
    
    @property
    def max_tokens(self) -> int:
        """Maximum tokens in response."""
        return self.get_int('CHAT_MAX_TOKENS', 500)
    
    @property
    def temperature(self) -> float:
        """Response randomness (0.0-2.0)."""
        return self.get_float('CHAT_TEMPERATURE', 0.7)
```

### Environment Variables

```bash
# .env file
OPENAI_API_KEY=sk-...your-key-here...
CHAT_MODEL=gpt-3.5-turbo
CHAT_MAX_TOKENS=500
CHAT_TEMPERATURE=0.7
```

## Token Counting with tiktoken

OpenAI provides `tiktoken` library for accurate token counting:

```python
import tiktoken

def count_tokens(text: str, model: str = "gpt-3.5-turbo") -> int:
    """Count tokens in text for given model.
    
    Args:
        text: Text to count tokens for
        model: Model name (different models use different encodings)
        
    Returns:
        Number of tokens
    """
    encoding = tiktoken.encoding_for_model(model)
    return len(encoding.encode(text))
```

### Why Count Tokens Locally?

- **Estimate before calling API**: Show users cost before they commit
- **Prevent expensive mistakes**: Reject prompts that exceed budget
- **Validate input**: Check if prompt fits in model's context window
- **No API call needed**: tiktoken runs locally, no cost

## Cost Calculation

Create pricing constants and helper functions:

```python
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
```

## Making API Calls

Using the OpenAI library:

```python
from openai import OpenAI

client = OpenAI()  # Reads OPENAI_API_KEY from environment

response = client.chat.completions.create(
    model="gpt-3.5-turbo",
    messages=[
        {"role": "user", "content": "Hello!"}
    ],
    max_tokens=500,
    temperature=0.7
)

# Extract response
message = response.choices[0].message.content

# Get actual token usage
input_tokens = response.usage.prompt_tokens
output_tokens = response.usage.completion_tokens
total_tokens = response.usage.total_tokens
```

## ChatREPL Structure

```python
class ChatREPL:
    """Interactive AI chat REPL with cost tracking."""
    
    def __init__(self, config: ChatConfig | None = None):
        """Initialize chat REPL."""
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
                break
    
    def process_message(self, message: str):
        """Process user message."""
        if message.lower() == 'exit':
            self.running = False
            print(f"\nGoodbye! Total cost: ${self.session_cost:.4f}")
            return
        
        if message.lower() == 'help':
            self._print_help()
            return
        
        # Count tokens and estimate cost
        input_tokens = count_tokens(message, self.config.model)
        estimated_cost = calculate_cost(
            self.config.model, 
            input_tokens, 
            self.config.max_tokens  # Assume max output
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
            print(f"\n[Tokens: {actual_input} in + {actual_output} out = {actual_input + actual_output} total]")
            print(f"[Cost: ${actual_cost:.6f} | Session: ${self.session_cost:.6f}]")
            
        except Exception as e:
            print(f"\nError: {e}")
```

## Implementation Steps

### Step 1: Create ChatConfig
```python
# src/chat.py
from config import TypedConfig

class ChatConfig(TypedConfig):
    """Configuration for chat REPL."""
    
    @property
    def model(self) -> str:
        """OpenAI model name."""
        return self.get_str('CHAT_MODEL', 'gpt-3.5-turbo')
    
    @property
    def max_tokens(self) -> int:
        """Maximum response tokens."""
        return self.get_int('CHAT_MAX_TOKENS', 500)
    
    @property
    def temperature(self) -> float:
        """Response temperature (0.0-2.0)."""
        return self.get_float('CHAT_TEMPERATURE', 0.7)
```

### Step 2: Add Token Counting
```python
import tiktoken

def count_tokens(text: str, model: str = "gpt-3.5-turbo") -> int:
    """Count tokens in text."""
    try:
        encoding = tiktoken.encoding_for_model(model)
    except KeyError:
        # Fallback for unknown models
        encoding = tiktoken.get_encoding("cl100k_base")
    return len(encoding.encode(text))
```

### Step 3: Add Cost Calculation
```python
MODEL_PRICING = {
    'gpt-4-turbo': {'input': 0.01, 'output': 0.03},
    'gpt-3.5-turbo': {'input': 0.0005, 'output': 0.0015},
}

def calculate_cost(model: str, input_tokens: int, output_tokens: int) -> float:
    """Calculate API call cost."""
    if model not in MODEL_PRICING:
        raise ValueError(f"Unknown model: {model}")
    
    pricing = MODEL_PRICING[model]
    return (input_tokens / 1_000_000 * pricing['input'] + 
            output_tokens / 1_000_000 * pricing['output'])
```

### Step 4: Build ChatREPL
Implement the full REPL with:
- OpenAI client initialization
- Message processing
- Cost estimation and tracking
- Error handling
- Help command

## Testing Strategy

Use `unittest.mock` to mock OpenAI API calls:

```python
from unittest.mock import Mock, patch
import pytest
from chat import ChatREPL, ChatConfig

def test_chat_basic_interaction():
    """Test basic chat interaction."""
    # Mock OpenAI response
    mock_response = Mock()
    mock_response.choices[0].message.content = "Hello!"
    mock_response.usage.prompt_tokens = 10
    mock_response.usage.completion_tokens = 5
    mock_response.usage.total_tokens = 15
    
    with patch('chat.OpenAI') as mock_openai:
        mock_client = Mock()
        mock_client.chat.completions.create.return_value = mock_response
        mock_openai.return_value = mock_client
        
        repl = ChatREPL()
        repl.process_message("Hi")
        
        assert repl.session_cost > 0
        assert repl.message_count == 1
```

## Exercises

### Exercise 1: Add Cost Display Options
Add configuration for cost display format:
- Show cost in cents or dollars
- Show only session total (hide per-message cost)
- Show token breakdown or just cost

### Exercise 2: Add Cost Warning
If estimated cost > $0.01, ask user to confirm:
```
[Warning: This message will cost ~$0.015]
Continue? (y/n):
```

### Exercise 3: Track Average Cost
Calculate and display average cost per message:
```
[Session: 10 messages, $0.0234 total, $0.00234 avg]
```

## Real-World Applications

### Production Chatbots
- Show users what each interaction costs
- Build trust through transparency
- Help users understand pricing

### Internal Tools
- Track AI spending across teams
- Identify expensive use cases
- Optimize model selection

### Cost Optimization
- Compare GPT-4 vs GPT-3.5 costs
- Measure impact of max_tokens settings
- Find sweet spot for quality vs cost

## Common Pitfalls

❌ **Not counting tokens before API calls**
- Result: Unexpected high costs
- Solution: Always estimate first

❌ **Using wrong model for token counting**
- Result: Inaccurate estimates
- Solution: Pass model to tiktoken

❌ **Forgetting input tokens have cost**
- Result: Underestimating costs
- Solution: Count both input and output

❌ **Hardcoding pricing**
- Result: Out-of-date costs when OpenAI changes prices
- Solution: Use constants, update regularly

## Summary

In this lesson you:
- ✅ Integrated OpenAI API into a REPL
- ✅ Learned how token-based pricing works
- ✅ Counted tokens with tiktoken
- ✅ Calculated costs for API calls
- ✅ Built a cost-transparent chat application
- ✅ Tracked session costs and message counts

**Next lesson**: Session cost tracking, budget management, and comprehensive logging.

## Additional Resources

- [OpenAI Pricing](https://openai.com/pricing)
- [tiktoken Documentation](https://github.com/openai/tiktoken)
- [OpenAI API Reference](https://platform.openai.com/docs/api-reference)
- [Token Counting Best Practices](https://cookbook.openai.com/examples/how_to_count_tokens_with_tiktoken)
