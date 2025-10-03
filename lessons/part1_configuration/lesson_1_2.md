# Lesson 1.2: Type-Safe Configuration

**⏱️ Time**: 45 minutes  
**🎯 Goal**: Make all 18 tests pass!  
**📦 Builds On**: Lesson 1.1 (basic Config class)

---

## 🎮 Your Mission

You're going to extend your configuration system to handle different data types safely. By the end, you'll understand why type safety prevents bugs before they happen.

---

## 📖 Part 1: The Story (5 minutes)

### The Bug That Cost $250,000

In 2012, a trading firm lost $250 million in **45 minutes** because of a configuration error. One problem? A setting that should have been an integer was read as a string.

```python
# They meant to do this:
max_orders = 100  # integer

# But got this:
max_orders = "100"  # string

# Then this code broke:
if current_orders < max_orders:  # Comparing int to string!
    place_order()
```

This kind of bug is called a **type error**, and it's preventable!

### Real-World Examples

Environment variables are **always strings**:

```bash
# In .env file
MAX_RETRIES=5
TIMEOUT=30.5
DEBUG_MODE=true
```

But your code needs **actual types**:

```python
# You want these:
max_retries: int = 5
timeout: float = 30.5
debug_mode: bool = True

# Not these:
max_retries: str = "5"      # ❌ Can't do math
timeout: str = "30.5"       # ❌ Can't compare
debug_mode: str = "true"    # ❌ Always truthy!
```

---

## 💡 Part 2: What You'll Learn (10 minutes)

### Type Conversion

Environment variables need conversion:

```python
import os

# String (default)
name = os.getenv('APP_NAME', 'MyApp')  # ✅ Already a string

# Integer
max_retries = int(os.getenv('MAX_RETRIES', '3'))  # ✅ Convert to int

# Float
timeout = float(os.getenv('TIMEOUT', '30.0'))  # ✅ Convert to float

# Boolean (tricky!)
debug = os.getenv('DEBUG_MODE', 'false').lower() == 'true'  # ✅ Compare string
```

### The Boolean Problem

In Python, these are **all truthy** (evaluate to `True`):

```python
# ❌ WRONG - Everything is True!
debug = bool(os.getenv('DEBUG_MODE', 'false'))
# bool('false') = True  (non-empty string)
# bool('False') = True
# bool('0') = True
# bool('no') = True

# ✅ CORRECT - Explicit comparison
debug = os.getenv('DEBUG_MODE', 'false').lower() in ('true', '1', 'yes')
```

### Lists from Strings

Comma-separated values are common:

```bash
# In .env
ALLOWED_USERS=alice,bob,charlie
```

```python
# Parse to list
users_str = os.getenv('ALLOWED_USERS', '')
users = [u.strip() for u in users_str.split(',') if u.strip()]
# Result: ['alice', 'bob', 'charlie']
```

### Required vs Optional

Some settings are **required** (API keys), others **optional** (debug mode):

```python
# Required - raise error if missing
api_key = os.getenv('API_KEY')
if api_key is None:
    raise ValueError("API_KEY is required!")

# Optional - use default
debug = os.getenv('DEBUG_MODE', 'false').lower() == 'true'
```

---

## 🏗️ Part 3: Build It! (25 minutes)

### Step 1: Run the Tests (They Should Fail!)

```bash
PYTHONPATH=src pytest tests/part1_configuration/test_lesson_1_2.py -v
```

You'll see: ❌ **18 FAILED** - Perfect! Now let's fix them one by one.

### Step 2: Update Your .env File

Add the new variables:

```bash
# .env
APP_NAME=TinyTools Calculator
APP_VERSION=1.0.0
DEBUG_MODE=true
MAX_RETRIES=3
TIMEOUT=30.0
ALLOWED_USERS=admin,user,guest
API_KEY=sk-test-your-api-key-here
```

### Step 3: Update .env.example

```bash
# .env.example
APP_NAME=TinyTools Calculator
APP_VERSION=1.0.0
DEBUG_MODE=false
MAX_RETRIES=3
TIMEOUT=30.0
ALLOWED_USERS=admin,user
API_KEY=your-api-key-here
```

### Step 4: Create TypedConfig Class

Add this to `src/config.py`:

```python
"""Configuration management using environment variables."""
import os
from typing import List
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class Config:
    """Application configuration loaded from environment variables.
    
    This class loads configuration from environment variables, with
    support for .env files via python-dotenv.
    """
    
    def __init__(self):
        """Initialize configuration from environment variables."""
        self.app_name = os.getenv('APP_NAME', 'TinyTools')
        self.app_version = os.getenv('APP_VERSION', '1.0.0')
        self.debug_mode = os.getenv('DEBUG_MODE', 'false').lower() == 'true'
    
    def __repr__(self):
        """Return string representation of configuration."""
        return (f"Config(app_name='{self.app_name}', "
                f"version='{self.app_version}', "
                f"debug={self.debug_mode})")


class TypedConfig:
    """Type-safe configuration with support for multiple data types.
    
    This class extends basic configuration with:
    - Type conversion (int, float, bool, list)
    - Required vs optional values
    - Validation and error handling
    - Type hints for better IDE support
    """
    
    def __init__(self):
        """Initialize type-safe configuration from environment variables.
        
        Raises:
            ValueError: If required configuration values are missing
        """
        # String values (default type)
        # TODO: Load app_name as string
        # HINT: self.app_name: str = os.getenv('APP_NAME', 'TinyTools')
        
        # Integer values
        # TODO: Load max_retries as integer
        # HINT: self.max_retries: int = int(os.getenv('MAX_RETRIES', '3'))
        
        # Float values
        # TODO: Load timeout as float
        # HINT: self.timeout: float = float(os.getenv('TIMEOUT', '30.0'))
        
        # Boolean values
        # TODO: Load debug_mode as boolean
        # HINT: Use the _str_to_bool helper method
        
        # List values
        # TODO: Load allowed_users as list
        # HINT: Use the _str_to_list helper method
        
        # Required values (no default)
        # TODO: Load api_key and validate it exists
        # HINT: 
        #   api_key = os.getenv('API_KEY')
        #   if api_key is None:
        #       raise ValueError("API_KEY is required")
        #   self.api_key: str = api_key
        
        pass
    
    @staticmethod
    def _str_to_bool(value: str) -> bool:
        """Convert string to boolean.
        
        Args:
            value: String value to convert
            
        Returns:
            True if value is 'true', '1', 'yes' (case-insensitive)
            False otherwise
            
        HINT: value.lower() in ('true', '1', 'yes')
        """
        # TODO: Implement boolean conversion
        pass
    
    @staticmethod
    def _str_to_list(value: str) -> List[str]:
        """Convert comma-separated string to list.
        
        Args:
            value: Comma-separated string
            
        Returns:
            List of trimmed strings, empty list if value is empty
            
        HINT: [item.strip() for item in value.split(',') if item.strip()]
        """
        # TODO: Implement list conversion
        pass
    
    def __repr__(self):
        """Return string representation of configuration."""
        # TODO: Return a helpful string representation
        # HINT: f"TypedConfig(app_name='{self.app_name}', debug={self.debug_mode})"
        pass
```

**Your job**: Fill in all the TODOs!

### Step 5: Run Tests Iteratively

```bash
# Run tests and watch them pass one by one
PYTHONPATH=src pytest tests/part1_configuration/test_lesson_1_2.py -v

# Run with more detail if needed
PYTHONPATH=src pytest tests/part1_configuration/test_lesson_1_2.py -vv
```

**Pro tip**: Tests are organized by class. Fix one class at a time:
1. `TestImports` - Make TypedConfig exist
2. `TestBasicTypes` - Handle int, float, bool
3. `TestListValues` - Parse lists
4. `TestDefaultValues` - Provide defaults
5. `TestRequiredValues` - Validate required values
6. `TestTypeHints` - Add type hints
7. `TestRepr` - Add string representation
8. `TestHelperMethods` - Create helper methods

### Step 6: Verify Quality

```bash
# All tests pass
PYTHONPATH=src pytest tests/part1_configuration/test_lesson_1_2.py -v

# Check coverage
PYTHONPATH=src coverage run -m pytest tests/part1_configuration/test_lesson_1_2.py
coverage report --include=src/config.py

# Check pylint
pylint --errors-only src/config.py
```

Target: 100% coverage, no pylint errors!

---

## ✅ Part 4: Verify Understanding (5 minutes)

Before moving on, make sure you can answer:

1. **Why can't we just use `bool(os.getenv('DEBUG_MODE'))`?**
   - Because non-empty strings are always truthy in Python
   - `bool('false')` returns `True`!

2. **What's the difference between required and optional values?**
   - Required: No default, raise error if missing
   - Optional: Have default, safe if missing

3. **Why use helper methods like `_str_to_bool`?**
   - Reusability (DRY principle)
   - Testability (can test conversion logic separately)
   - Readability (clear intent)

4. **What are type hints and why use them?**
   - Annotations like `name: str` and `count: int`
   - Help IDEs provide better autocomplete
   - Catch type errors early

5. **How do you parse a comma-separated list?**
   - Split on comma: `value.split(',')`
   - Strip whitespace: `item.strip()`
   - Filter empty: `if item.strip()`

---

## 🎉 Success Criteria

You're done when:

- ✅ All 18 tests pass
- ✅ TypedConfig handles strings, ints, floats, bools, lists
- ✅ Required values raise errors when missing
- ✅ Optional values use defaults
- ✅ Helper methods exist and work
- ✅ Type hints are used
- ✅ Coverage is 100% on TypedConfig
- ✅ Pylint passes with no errors

---

## 🚀 Commit Your Work

```bash
# Check what changed
git diff src/config.py

# Add and commit
git add src/config.py tests/part1_configuration/test_lesson_1_2.py .env.example
git commit -m "feature: lesson 1.2 - type-safe configuration"

# DO NOT commit .env!
```

---

## 🔍 Troubleshooting

### "ValueError: invalid literal for int() with base 10"

```python
# ❌ Missing default
max_retries = int(os.getenv('MAX_RETRIES'))  # Returns None if missing!

# ✅ With default
max_retries = int(os.getenv('MAX_RETRIES', '3'))  # Always a string
```

### "All boolean tests fail"

Check your `_str_to_bool` method:

```python
# ✅ Handle multiple True values
def _str_to_bool(value: str) -> bool:
    return value.lower() in ('true', '1', 'yes')
```

### "List has whitespace in items"

Use `.strip()` on each item:

```python
# ✅ Strip whitespace
[item.strip() for item in value.split(',') if item.strip()]
```

### "test_required_value_raises_error fails"

Make sure you check if the value is `None`:

```python
api_key = os.getenv('API_KEY')  # No default!
if api_key is None:
    raise ValueError("API_KEY is required")
```

---

## 🎯 Real-World Applications

### Where You'll Use This

1. **Web Applications**
   ```python
   # Django settings
   DEBUG = TypedConfig().debug_mode
   MAX_CONNECTIONS = TypedConfig().max_connections
   ```

2. **APIs**
   ```python
   # Rate limiting
   config = TypedConfig()
   if request_count > config.rate_limit:
       raise RateLimitError()
   ```

3. **Data Processing**
   ```python
   # Batch sizes
   config = TypedConfig()
   for batch in chunks(data, config.batch_size):
       process(batch)
   ```

4. **DevOps**
   ```python
   # Different configs per environment
   # DEV: DEBUG=true, MAX_RETRIES=1
   # PROD: DEBUG=false, MAX_RETRIES=5
   ```

---

## 📚 Additional Resources

- [Python Type Hints](https://docs.python.org/3/library/typing.html)
- [The Twelve-Factor App: Config](https://12factor.net/config)
- [Python's bool() gotchas](https://docs.python.org/3/library/stdtypes.html#truth-value-testing)
- [Environment Variables Best Practices](https://12factor.net/)

---

## 🎓 Key Takeaways

1. **Environment variables are always strings** - Convert to the type you need
2. **Be explicit with booleans** - Don't rely on truthiness
3. **Validate required values** - Fail fast if config is wrong
4. **Use type hints** - They help catch errors early
5. **Helper methods = DRY code** - Reuse conversion logic

---

**Next**: [Lesson 1.3 - Configuration Validation →](lesson_1_3.md)

---

## 💡 Pro Tips

1. **Type hints don't enforce types** - They're documentation + IDE help
2. **Always provide sensible defaults** - Makes development easier
3. **Required values should fail loudly** - Better than silent bugs later
4. **Test your type conversions** - Edge cases matter ('0' vs 0)
5. **Document your .env.example** - Add comments explaining each variable

Great job! You now understand type-safe configuration! 🎯
