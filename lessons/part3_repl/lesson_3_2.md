# Lesson 3.2: Integrating Configuration System

**Course**: IS 218 - Building AI Systems  
**Part**: 3 - REPL Development  
**Lesson**: 3.2 - Configuration Integration  
**Difficulty**: ⭐⭐⭐☆☆  
**Time**: 60 minutes

## Learning Objectives

By the end of this lesson, you will be able to:

1. Integrate environment-based configuration into an interactive application
2. Use TypedConfig to validate calculator settings
3. Implement configurable precision and operation limits
4. Provide customizable welcome messages through environment variables
5. Balance flexibility with sensible defaults

## The Story: Making It Your Own

You built a calculator REPL in Lesson 3.1. It works great! But then you show it to your team, and everyone has different needs:

- **Financial analyst**: "I need 4 decimal places for currency calculations"
- **Scientist**: "I need 10 decimal places for precise measurements"
- **Teacher**: "I want a custom welcome message for my students"
- **DevOps**: "I need operation limits to prevent abuse in production"

Instead of creating different versions of the calculator for each person, you'll use the configuration system from Part 1 to make it customizable through environment variables. One codebase, infinite configurations!

## Configuration-Driven Design

Remember the three config types from Part 1?

1. **BasicConfig**: Read any environment variable
2. **TypedConfig**: Type-safe access with defaults
3. **ValidatedConfig**: Type-safe + validation rules

For the calculator REPL, we'll use **TypedConfig** because:
- We need specific types (int, float, str)
- We want sensible defaults (users shouldn't need to configure everything)
- We don't need complex validation rules (yet)

## Calculator Configuration Requirements

Let's define what we want to configure:

```python
# .env file for a financial calculator
REPL_PRECISION=4
REPL_MAX_VALUE=999999.99
REPL_WELCOME_MESSAGE="Financial Calculator v1.0"
REPL_SHOW_HELP=true
```

```python
# .env file for a scientific calculator
REPL_PRECISION=10
REPL_MAX_VALUE=1e308
REPL_WELCOME_MESSAGE="Scientific Calculator - High Precision Mode"
REPL_SHOW_HELP=false
```

Same calculator code, different behavior based on environment!

## Implementation Plan

### Step 1: Extend TypedConfig for Calculator

We'll create a new class that inherits from `TypedConfig` and adds calculator-specific settings:

```python
from config import TypedConfig

class CalculatorConfig(TypedConfig):
    """Configuration for calculator REPL with sensible defaults."""
    
    @property
    def precision(self) -> int:
        """Number of decimal places to display."""
        return self.get_int('REPL_PRECISION', 2)
    
    @property
    def max_value(self) -> float:
        """Maximum allowed value for operations."""
        return self.get_float('REPL_MAX_VALUE', 1000000.0)
    
    @property
    def welcome_message(self) -> str:
        """Welcome message shown on startup."""
        return self.get_str('REPL_WELCOME_MESSAGE', 'Calculator REPL v1.0')
    
    @property
    def show_help(self) -> bool:
        """Whether to show help on startup."""
        return self.get_bool('REPL_SHOW_HELP', True)
```

Notice how we use:
- `get_int()` for numeric settings
- `get_float()` for decimal values
- `get_str()` for text
- `get_bool()` for flags

Each method has a sensible default, so the calculator works even without a `.env` file!

### Step 2: Integrate Config into CalculatorREPL

Now we'll modify the `CalculatorREPL` class to use configuration:

```python
class CalculatorREPL:
    """Interactive calculator with configurable behavior."""
    
    def __init__(self, config: CalculatorConfig | None = None):
        """Initialize REPL with optional configuration."""
        self.running = False
        self.config = config or CalculatorConfig()
    
    def start(self):
        """Start the REPL loop with configured welcome message."""
        print(self.config.welcome_message)
        if self.config.show_help:
            self._print_help()
        # ... rest of REPL loop
    
    def execute_command(self, command: str, args: list) -> float:
        """Execute command and format result with configured precision."""
        # ... calculate result
        
        # Check max value limit
        if abs(result) > self.config.max_value:
            raise ValueError(f"Result exceeds maximum value: {self.config.max_value}")
        
        # Format with configured precision
        return round(result, self.config.precision)
```

### Step 3: Add Help Command

Let's also add a `help` command that shows available operations:

```python
def _print_help(self):
    """Print available commands."""
    print("\nAvailable commands:")
    print("  add <num1> <num2>      - Add two numbers")
    print("  subtract <num1> <num2> - Subtract num2 from num1")
    print("  multiply <num1> <num2> - Multiply two numbers")
    print("  divide <num1> <num2>   - Divide num1 by num2")
    print("  help                   - Show this help message")
    print("  exit                   - Exit the calculator")
    print(f"\nPrecision: {self.config.precision} decimal places")
    print(f"Max value: {self.config.max_value}\n")
```

## Real-World Example

Let's see how this works with different configurations:

```bash
# Default configuration (no .env file)
$ python src/repl.py
Calculator REPL v1.0

Available commands:
  add <num1> <num2>      - Add two numbers
  ...
Precision: 2 decimal places
Max value: 1000000.0

> add 10.12345 20.67890
Result: 30.80
```

```bash
# Custom configuration for finance
$ cat > .env << EOF
REPL_PRECISION=4
REPL_MAX_VALUE=999999.99
REPL_WELCOME_MESSAGE="Financial Calculator v1.0"
EOF

$ python src/repl.py
Financial Calculator v1.0
...
Precision: 4 decimal places
Max value: 999999.99

> add 10.12345 20.67890
Result: 30.8024
```

```bash
# Scientific configuration with no help
$ cat > .env << EOF
REPL_PRECISION=10
REPL_SHOW_HELP=false
REPL_WELCOME_MESSAGE="Scientific Calculator"
EOF

$ python src/repl.py
Scientific Calculator

> add 10.12345 20.67890
Result: 30.8023500000
```

## Testing Strategy

We need tests for:

1. **Default configuration**: Calculator works without .env
2. **Custom precision**: Results rounded correctly
3. **Max value limits**: Exceeding max raises error
4. **Welcome message**: Custom message displayed
5. **Help display**: Can be shown or hidden
6. **Help command**: User can request help anytime

## Key Concepts

### 1. Dependency Injection

```python
def __init__(self, config: CalculatorConfig | None = None):
    self.config = config or CalculatorConfig()
```

This pattern allows:
- Easy testing (inject mock configs)
- Flexible initialization (use custom or default)
- No hidden dependencies (config is explicit)

### 2. Configuration Inheritance

```python
class CalculatorConfig(TypedConfig):
    # Inherits all TypedConfig functionality
    # Adds calculator-specific properties
```

We're building on Part 1's foundation, not reinventing it!

### 3. Progressive Enhancement

The calculator works with defaults, but can be enhanced through configuration:
- **Level 1**: Works out of the box (no .env)
- **Level 2**: Basic customization (precision, welcome)
- **Level 3**: Advanced features (limits, help toggle)

## Common Patterns

### Pattern 1: Config-First Testing

```python
def test_custom_precision():
    # Arrange: Create test config
    config = CalculatorConfig()
    config._env_vars = {'REPL_PRECISION': '4'}  # Inject for testing
    
    # Act: Use config
    repl = CalculatorREPL(config)
    result = repl.execute_command('add', ['1.23456', '2.34567'])
    
    # Assert: Check precision
    assert result == 3.5802
```

### Pattern 2: Graceful Degradation

```python
@property
def precision(self) -> int:
    """Number of decimal places to display."""
    try:
        value = self.get_int('REPL_PRECISION', 2)
        # Validate range
        if value < 0 or value > 15:
            print(f"Warning: Invalid precision {value}, using default 2")
            return 2
        return value
    except Exception:
        return 2  # Always fall back to sensible default
```

### Pattern 3: Configuration Validation

```python
def validate_config(self) -> bool:
    """Check if configuration is valid."""
    if self.precision < 0:
        return False
    if self.max_value <= 0:
        return False
    return True
```

## Testing Your Understanding

### Exercise 1: Add Min Value Config
Add a `min_value` configuration that prevents operations from going below a minimum:

```python
@property
def min_value(self) -> float:
    """Minimum allowed value for operations."""
    return self.get_float('REPL_MIN_VALUE', -1000000.0)
```

### Exercise 2: Add Timeout Config
Add a `timeout` configuration to limit how long operations can take:

```python
@property
def timeout_seconds(self) -> int:
    """Maximum seconds for a single operation."""
    return self.get_int('REPL_TIMEOUT', 5)
```

### Exercise 3: Custom Number Format
Add support for different number formats (US vs European):

```python
@property
def decimal_separator(self) -> str:
    """Decimal separator ('.' or ',')."""
    return self.get_str('REPL_DECIMAL_SEPARATOR', '.')
```

## What You Built

In this lesson, you:

1. ✅ Created `CalculatorConfig` extending `TypedConfig`
2. ✅ Added configurable precision, limits, and messages
3. ✅ Integrated configuration into `CalculatorREPL`
4. ✅ Implemented help command and startup help
5. ✅ Added max value validation
6. ✅ Formatted results with configured precision
7. ✅ Wrote comprehensive tests for all config scenarios

## How This Helps You

**In Industry**:
- SaaS applications need per-customer configuration
- Microservices need environment-specific settings
- Dev/staging/prod environments need different limits

**Common Interview Topics**:
- "How do you handle configuration in your applications?"
- "Explain dependency injection and why it's useful"
- "How would you make an application configurable?"

**Real Tools That Use This**:
- **Django**: Settings for different environments
- **Flask**: Application configuration from environment
- **FastAPI**: Environment-based configuration

## Next Steps

In **Lesson 3.3: Adding Logging to REPL**, you'll integrate the logging system from Part 2 to track all calculator operations, debug user input, and create an audit trail.

## Before You Start

Run the tests and watch them fail. That's expected! You'll implement the code to make them pass:

```bash
pytest tests/part3_repl/test_lesson_3_2.py -v
```

## Success Criteria

When you're done:
- ✅ All 28 tests pass
- ✅ Coverage remains above 68%
- ✅ Pylint scores 10/10
- ✅ Calculator works with and without .env file
- ✅ Results formatted with configured precision
- ✅ Max value limits enforced

---

Ready? Let's run those tests! 🧪
