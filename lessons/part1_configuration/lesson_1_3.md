# Lesson 1.3: Configuration Validation

**⏱️ Time**: 45 minutes  
**🎯 Goal**: Make all 22 tests pass!  
**📦 Builds On**: Lessons 1.1 & 1.2 (Config + TypedConfig)

---

## 🎮 Your Mission

You're going to add validation to your configuration system to catch bad values before they cause problems. By the end, you'll understand why "fail fast" is a crucial principle in software engineering.

---

## 📖 Part 1: The Story (5 minutes)

### The $10 Million Bug

In 1999, NASA's Mars Climate Orbiter burned up in the Martian atmosphere. The cause? **Invalid configuration**.

One team used **metric units** (meters), another used **imperial units** (feet). The configuration accepted both without validation. The spacecraft crashed.

**Cost**: $125 million + years of work  
**Cause**: No validation of configuration values

### Real-World Configuration Bugs

**Amazon AWS Outage (2017)**
```python
# Intended to take 10% of servers offline
servers_to_remove = '10%'  # But read as integer...
# Actually removed 10 servers (way too many!)
```

**Knight Capital Trading Loss (2012)**
```python
# Configuration had wrong flag value
power_peg = 8  # Should have been between 0-7
# Lost $440 million in 45 minutes
```

These bugs are **preventable with validation**!

---

## 💡 Part 2: What You'll Learn (10 minutes)

### Why Validate?

Environment variables come from **outside your code**:
- Typed by humans → typos happen
- Copy-pasted → wrong values
- Generated → scripts have bugs
- Changed in production → without testing

**Never trust external input!**

### Types of Validation

**1. Range Validation** (numbers within bounds)
```python
max_retries = int(os.getenv('MAX_RETRIES', '3'))

# ❌ Without validation
if max_retries == -1:  # Bug waiting to happen
    # Infinite loop!

# ✅ With validation
if not (1 <= max_retries <= 10):
    raise ValueError("MAX_RETRIES must be between 1 and 10")
```

**2. Format Validation** (strings match pattern)
```python
api_key = os.getenv('API_KEY')

# ❌ Without validation
# Accepts: "my-key", "", "12345" (all invalid!)

# ✅ With validation
if not api_key.startswith('sk-'):
    raise ValueError("API_KEY must start with 'sk-'")
if len(api_key) < 10:
    raise ValueError("API_KEY must be at least 10 characters")
```

**3. Non-Empty Validation** (required fields exist)
```python
app_name = os.getenv('APP_NAME', 'MyApp')

# ❌ Without validation
# Accepts: "", "   " (empty or whitespace)

# ✅ With validation
if not app_name or not app_name.strip():
    raise ValueError("APP_NAME cannot be empty")
```

**4. Positive Number Validation**
```python
timeout = float(os.getenv('TIMEOUT', '30.0'))

# ❌ Without validation
# Accepts: 0, -5 (makes no sense for timeout!)

# ✅ With validation
if timeout <= 0:
    raise ValueError("TIMEOUT must be positive")
```

### The "Fail Fast" Principle

```python
# ❌ BAD: Fail later (hard to debug)
class Config:
    def __init__(self):
        self.timeout = float(os.getenv('TIMEOUT', '30.0'))
    
    def connect(self):
        time.sleep(self.timeout)  # Fails here if timeout is negative!

# ✅ GOOD: Fail fast (easy to debug)
class ValidatedConfig:
    def __init__(self):
        self.timeout = float(os.getenv('TIMEOUT', '30.0'))
        if self.timeout <= 0:
            raise ValueError("TIMEOUT must be positive")
        # Now guaranteed to be valid!
```

---

## 🏗️ Part 3: Build It! (25 minutes)

### Step 1: Run the Tests (They Should Fail!)

```bash
PYTHONPATH=src pytest tests/part1_configuration/test_lesson_1_3.py -v
```

You'll see: ❌ **22 FAILED** (or import error) - Perfect! Let's make them pass.

### Step 2: Add ValidatedConfig to src/config.py

Add this class to your `config.py` file:

```python
class ValidatedConfig:
    """Configuration with validation to ensure values are safe.
    
    This class extends type-safe configuration with:
    - Range validation for numeric values
    - Format validation for strings
    - Non-empty validation for required fields
    - Helpful error messages when validation fails
    """
    
    def __init__(self):
        """Initialize validated configuration from environment variables.
        
        Raises:
            ValueError: If any configuration value fails validation
        """
        # Load string values
        # TODO: Load app_name and validate it's not empty
        # HINT:
        #   self.app_name: str = os.getenv('APP_NAME', 'TinyTools')
        #   self._validate_non_empty(self.app_name, 'APP_NAME')
        
        # Load integer values
        # TODO: Load max_retries and validate range (1-10)
        # HINT:
        #   self.max_retries: int = int(os.getenv('MAX_RETRIES', '3'))
        #   self._validate_range(self.max_retries, 1, 10, 'MAX_RETRIES')
        
        # Load float values
        # TODO: Load timeout and validate it's positive
        # HINT:
        #   self.timeout: float = float(os.getenv('TIMEOUT', '30.0'))
        #   self._validate_positive(self.timeout, 'TIMEOUT')
        
        # Load list values
        # TODO: Load allowed_users and validate it's not empty
        # HINT:
        #   self.allowed_users: List[str] = TypedConfig._str_to_list(
        #       os.getenv('ALLOWED_USERS', '')
        #   )
        #   if not self.allowed_users:
        #       raise ValueError("ALLOWED_USERS cannot be empty")
        
        # Load and validate API key
        # TODO: Load api_key with multiple validations
        # HINT:
        #   api_key = os.getenv('API_KEY')
        #   if api_key is None:
        #       raise ValueError("API_KEY is required")
        #   if not api_key.startswith('sk-'):
        #       raise ValueError("API_KEY must start with 'sk-'")
        #   if len(api_key) < 10:
        #       raise ValueError("API_KEY must be at least 10 characters")
        #   self.api_key: str = api_key
        
        pass
    
    @staticmethod
    def _validate_range(value: int, min_val: int, max_val: int, name: str) -> None:
        """Validate that a value is within a specified range.
        
        Args:
            value: The value to validate
            min_val: Minimum allowed value (inclusive)
            max_val: Maximum allowed value (inclusive)
            name: Name of the configuration variable (for error message)
            
        Raises:
            ValueError: If value is outside the range
            
        HINT: if not (min_val <= value <= max_val):
                  raise ValueError(f"{name} must be between {min_val} and {max_val}, got {value}")
        """
        # TODO: Implement range validation
        pass
    
    @staticmethod
    def _validate_positive(value: float, name: str) -> None:
        """Validate that a value is positive (> 0).
        
        Args:
            value: The value to validate
            name: Name of the configuration variable (for error message)
            
        Raises:
            ValueError: If value is not positive
            
        HINT: if value <= 0:
                  raise ValueError(f"{name} must be positive, got {value}")
        """
        # TODO: Implement positive validation
        pass
    
    @staticmethod
    def _validate_non_empty(value: str, name: str) -> None:
        """Validate that a string is not empty or whitespace-only.
        
        Args:
            value: The string to validate
            name: Name of the configuration variable (for error message)
            
        Raises:
            ValueError: If value is empty or whitespace-only
            
        HINT: if not value or not value.strip():
                  raise ValueError(f"{name} cannot be empty")
        """
        # TODO: Implement non-empty validation
        pass
    
    def validate(self) -> None:
        """Run all validations on current configuration.
        
        This method can be called to re-validate configuration after changes.
        It's also useful for testing that all validation rules are working.
        
        HINT: Call all the validation methods again
        """
        # TODO: Re-run all validations
        # This is useful if config values can change after initialization
        self._validate_non_empty(self.app_name, 'APP_NAME')
        self._validate_range(self.max_retries, 1, 10, 'MAX_RETRIES')
        self._validate_positive(self.timeout, 'TIMEOUT')
        # Add other validations...
    
    def __repr__(self):
        """Return string representation of configuration."""
        return (f"ValidatedConfig(app_name='{self.app_name}', "
                f"max_retries={self.max_retries}, "
                f"timeout={self.timeout})")
```

**Your job**: Fill in all the TODOs!

### Step 3: Run Tests Iteratively

```bash
# Run tests and watch them pass one by one
PYTHONPATH=src pytest tests/part1_configuration/test_lesson_1_3.py -v

# Run a specific test class if needed
PYTHONPATH=src pytest tests/part1_configuration/test_lesson_1_3.py::TestRangeValidation -v
```

**Pro tip**: Tests are organized by validation type:
1. `TestImports` - Make ValidatedConfig exist
2. `TestRangeValidation` - Validate numeric ranges
3. `TestStringFormatValidation` - Validate string formats
4. `TestListValidation` - Validate lists
5. `TestValidationHelpers` - Create helper methods
6. `TestValidateMethod` - Add validate() method
7. `TestErrorMessages` - Ensure helpful messages

### Step 4: Verify Quality

```bash
# All tests pass
PYTHONPATH=src pytest tests/part1_configuration/test_lesson_1_3.py -v

# Check coverage (run all Part 1 tests)
PYTHONPATH=src coverage run -m pytest tests/part1_configuration/
coverage report --include=src/config.py

# Check pylint
pylint --errors-only src/config.py
```

Target: 100% coverage, no pylint errors!

---

## ✅ Part 4: Verify Understanding (5 minutes)

Before moving on, make sure you can answer:

1. **Why validate configuration at startup?**
   - Fail fast - catch errors immediately
   - Better error messages - know exactly what's wrong
   - Prevents cascading failures later

2. **What's the difference between type conversion and validation?**
   - Type conversion: `"5"` → `5` (change format)
   - Validation: Check if `5` is in valid range (verify correctness)

3. **Why use helper methods for validation?**
   - DRY - reuse validation logic
   - Testable - can test validators independently
   - Readable - clear intent

4. **When should validation raise errors?**
   - Always! Invalid config = broken application
   - Better to crash at startup than fail mysteriously later

5. **What makes a good error message?**
   - Names the variable: "MAX_RETRIES"
   - Explains the constraint: "must be between 1 and 10"
   - Shows the actual value: "got 0"

---

## 🎉 Success Criteria

You're done when:

- ✅ All 22 tests pass
- ✅ ValidatedConfig validates all required fields
- ✅ Range validation works (1-10 for max_retries)
- ✅ Positive validation works (timeout > 0)
- ✅ Non-empty validation works (app_name, allowed_users)
- ✅ API key format validation works (starts with 'sk-', min length 10)
- ✅ Error messages are helpful
- ✅ Helper methods exist and are reusable
- ✅ Coverage is 100%
- ✅ Pylint passes with no errors

---

## 🚀 Commit Your Work

```bash
# Check what changed
git diff src/config.py

# Add and commit
git add src/config.py tests/part1_configuration/test_lesson_1_3.py
git commit -m "feature: lesson 1.3 - configuration validation"
```

---

## 🔍 Troubleshooting

### "ValueError not raised when it should be"

Check your validation logic:
```python
# ❌ Wrong - doesn't raise
if value < min_val or value > max_val:
    print("Invalid!")  # Does nothing!

# ✅ Correct - raises exception
if not (min_val <= value <= max_val):
    raise ValueError(f"{name} must be between {min_val} and {max_val}")
```

### "Error message tests fail"

Make sure your error messages include all required information:
```python
# ✅ Good error message
raise ValueError(f"MAX_RETRIES must be between 1 and 10, got {value}")
#                  ↑ variable name
#                               ↑ constraint
#                                            ↑ actual value
```

### "Tests pass individually but fail together"

You might be forgetting to set all required env vars:
```python
# Set all required vars before creating config
os.environ.update({
    'APP_NAME': 'TestApp',
    'API_KEY': 'sk-test123456789',
    'MAX_RETRIES': '3',
    'TIMEOUT': '30.0',
    'ALLOWED_USERS': 'admin'
})
```

---

## 🎯 Real-World Applications

### Where You'll Use This

1. **Web Servers**
   ```python
   # Validate port number
   port = int(os.getenv('PORT', '8000'))
   if not (1024 <= port <= 65535):
       raise ValueError("PORT must be between 1024 and 65535")
   ```

2. **Database Connections**
   ```python
   # Validate connection pool size
   pool_size = int(os.getenv('DB_POOL_SIZE', '10'))
   if not (1 <= pool_size <= 100):
       raise ValueError("DB_POOL_SIZE must be between 1 and 100")
   ```

3. **API Clients**
   ```python
   # Validate API key format
   api_key = os.getenv('STRIPE_API_KEY')
   if not api_key.startswith('sk_live_') and not api_key.startswith('sk_test_'):
       raise ValueError("Invalid Stripe API key format")
   ```

4. **Machine Learning**
   ```python
   # Validate batch size
   batch_size = int(os.getenv('BATCH_SIZE', '32'))
   if batch_size <= 0 or batch_size > 1000:
       raise ValueError("BATCH_SIZE must be between 1 and 1000")
   ```

---

## 📚 Additional Resources

- [The Twelve-Factor App: Config](https://12factor.net/config)
- [Python Exception Handling Best Practices](https://docs.python.org/3/tutorial/errors.html)
- [Defensive Programming](https://en.wikipedia.org/wiki/Defensive_programming)
- [Fail-Fast Systems](https://www.martinfowler.com/ieeeSoftware/failFast.pdf)

---

## 🎓 Key Takeaways

1. **Never trust external input** - Always validate configuration
2. **Fail fast** - Catch errors at startup, not runtime
3. **Helpful error messages** - Include variable name, constraint, and actual value
4. **Validation helpers** - Make validation logic reusable
5. **Test your validators** - They prevent bugs, so test them well!

---

## 💡 Validation Best Practices

### ✅ DO:
- Validate at initialization (fail fast)
- Provide specific error messages
- Document valid ranges/formats
- Test edge cases (min, max, zero, negative)
- Use helper methods for common validations

### ❌ DON'T:
- Accept any value and hope for the best
- Use generic error messages like "Invalid config"
- Validate too late (after values are used)
- Mix validation logic with business logic
- Forget to test your validation code

---

**Next**: [Lesson 2.1 - Why Logging Matters →](../part2_logging/lesson_2_1.md)

---

## 🎊 Congratulations!

You've completed **Part 1: Configuration**! You now know how to:
- ✅ Load configuration from environment variables
- ✅ Handle different data types safely
- ✅ Validate configuration values
- ✅ Write professional, production-ready config code

These skills will serve you throughout your career. Every application needs configuration, and you now know how to do it right! 🎯

**Part 1 Complete!** Take a break, then move on to Part 2: Logging! 🚀
