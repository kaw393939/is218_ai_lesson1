# Lesson 2.1: Why Logging Matters

> **Part 2 of 4: Logging & Debugging** | Lesson 1 of 4

### 🧭 Navigation
⬅️ [Previous](../part1_configuration/lesson_1_3.md) | 🏠 [All Lessons](../../README.md#-all-lessons) | 📖 [README](../../README.md) | ➡️ [Next](lesson_2_2.md)

---

---

## 🎮 Your Mission

You're going to replace `print()` statements with professional logging. By the end, you'll understand why every production application uses logging instead of print().

---

## 📖 Part 1: The Story (5 minutes)

### The Nightmare of print() Debugging

You're on-call at 3 AM. Your app is crashing in production. You need to find out why.

```python
# Your code (using print)
def process_payment(amount, user_id):
    print("Processing payment...")
    print(f"Amount: {amount}")
    print(f"User: {user_id}")
    # ... payment processing
    print("Payment complete!")
```

**Problems:**
1. **No timestamps** - When did this happen?
2. **No levels** - Is this info, warning, or error?
3. **Goes to stdout** - Mixed with application output
4. **No persistence** - Lost when the app restarts
5. **Can't turn off** - Production is flooded with debug messages
6. **No context** - Which module printed this?

### The Power of Logging

```python
# Professional code (using logging)
import logging
logger = logging.getLogger(__name__)

def process_payment(amount, user_id):
    logger.info('Processing payment', extra={'amount': amount, 'user_id': user_id})
    # ... payment processing
    logger.info('Payment completed successfully')
```

**Benefits:**
- ✅ **Timestamps** - Know exactly when it happened
- ✅ **Levels** - DEBUG, INFO, WARNING, ERROR, CRITICAL
- ✅ **Configurable** - Turn debug off in production
- ✅ **Persistent** - Save to files
- ✅ **Searchable** - grep, analyze, alert on patterns
- ✅ **Context** - Module name, line number, thread ID

---

## 💡 Part 2: What You'll Learn (10 minutes)

### Log Levels (Severity)

```python
logger.debug('Detailed diagnostic info')      # Level 10 - Development only
logger.info('Something happened')             # Level 20 - General info
logger.warning('Something unexpected')        # Level 30 - Warning (default)
logger.error('Something failed')              # Level 40 - Error occurred
logger.critical('System is broken!')          # Level 50 - Critical failure
```

**When to use each:**
- **DEBUG**: Variable values, function calls, detailed flow
- **INFO**: User actions, business events, milestones
- **WARNING**: Deprecated features, recoverable issues
- **ERROR**: Exceptions, failures, unable to continue
- **CRITICAL**: System crash, data loss, security breach

### Basic Logging Setup

```python
import logging

# Get a logger (use __name__ to get module name)
logger = logging.getLogger(__name__)

# Use it
logger.info('Application started')
logger.warning('Low memory')
logger.error('Database connection failed')
```

### Configuring Logging

```python
import logging

# Configure logging (do this once at app startup)
logging.basicConfig(
    level=logging.INFO,  # Show INFO and above
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    filename='app.log'   # Log to file instead of console
)
```

### Format String Variables

```python
format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
#       ↑            ↑           ↑                ↑
#       timestamp    logger name level name       message
```

**Available variables:**
- `%(asctime)s` - Human-readable time: `2025-10-03 14:30:45`
- `%(name)s` - Logger name (usually module name)
- `%(levelname)s` - Level: DEBUG, INFO, WARNING, ERROR, CRITICAL
- `%(message)s` - The actual log message
- `%(filename)s` - Source filename
- `%(lineno)d` - Line number
- `%(funcName)s` - Function name

### Why NOT print()?

```python
# ❌ print() - Goes away, hard to debug
def calculate(x, y):
    print(f"Calculating {x} + {y}")
    result = x + y
    print(f"Result: {result}")
    return result

# ✅ Logging - Persistent, configurable, searchable
def calculate(x, y):
    logger.debug(f"Calculating {x} + {y}")
    result = x + y
    logger.debug(f"Result: {result}")
    return result
```

---

## 🏗️ Part 3: Build It! (25 minutes)

### Step 1: Run the Tests (They Should Fail!)

```bash
PYTHONPATH=src pytest tests/part2_logging/test_lesson_2_1.py -v
```

You'll see: ❌ **ImportError: No module named 'logger'** - Perfect!

### Step 2: Create src/logger.py

Create a new file `src/logger.py`:

```python
"""Logging utilities for the application.

This module provides functions to set up and get loggers with
consistent configuration across the application.
"""
import logging
from typing import Optional


def get_logger(name: str) -> logging.Logger:
    """Get a logger with the specified name.
    
    Args:
        name: Name for the logger (usually __name__ of calling module)
        
    Returns:
        Configured Logger instance
        
    Example:
        logger = get_logger(__name__)
        logger.info('Something happened')
        
    HINT: Just return logging.getLogger(name)
    """
    # TODO: Return a logger with the given name
    pass


def setup_logging(level: int = logging.INFO, log_file: Optional[str] = None) -> None:
    """Set up logging configuration for the application.
    
    This should be called once at application startup.
    
    Args:
        level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Optional path to log file. If None, logs to console.
        
    Example:
        # Log INFO and above to console
        setup_logging(level=logging.INFO)
        
        # Log DEBUG and above to file
        setup_logging(level=logging.DEBUG, log_file='app.log')
        
    HINT: Use logging.basicConfig() with:
        - level parameter
        - format string with timestamp, name, level, message
        - filename parameter (if log_file provided)
    """
    # TODO: Configure logging with basicConfig
    # Format should be: '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    pass
```

**Your job**: Fill in the TODOs!

### Step 3: Implement get_logger()

This one is simple:

```python
def get_logger(name: str) -> logging.Logger:
    """Get a logger with the specified name."""
    return logging.getLogger(name)
```

### Step 4: Implement setup_logging()

```python
def setup_logging(level: int = logging.INFO, log_file: Optional[str] = None) -> None:
    """Set up logging configuration for the application."""
    format_string = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    
    if log_file:
        logging.basicConfig(
            level=level,
            format=format_string,
            filename=log_file
        )
    else:
        logging.basicConfig(
            level=level,
            format=format_string
        )
```

### Step 5: Run Tests Iteratively

```bash
# Run tests and watch them pass one by one
PYTHONPATH=src pytest tests/part2_logging/test_lesson_2_1.py -v

# Run a specific test class if needed
PYTHONPATH=src pytest tests/part2_logging/test_lesson_2_1.py::TestBasicLogging -v
```

**Test order**:
1. `TestImports` - Module exists
2. `TestBasicLogging` - Get logger and log messages
3. `TestLogLevels` - Filter by severity
4. `TestLoggingConfiguration` - setup_logging() function
5. `TestLogFormat` - Message formatting
6. `TestRealWorldUsage` - Practical examples

### Step 6: Try It Out!

Create a quick test script to see logging in action:

```python
# test_logging.py
from logger import get_logger, setup_logging
import logging

# Setup logging
setup_logging(level=logging.DEBUG, log_file='test.log')

# Get logger
logger = get_logger('my_app')

# Try different levels
logger.debug('This is a debug message')
logger.info('This is an info message')
logger.warning('This is a warning message')
logger.error('This is an error message')
logger.critical('This is a critical message!')

print("Check test.log for output!")
```

Run it:
```bash
PYTHONPATH=src python test_logging.py
cat test.log
```

### Step 7: Verify Quality

```bash
# All tests pass
PYTHONPATH=src pytest tests/part2_logging/test_lesson_2_1.py -v

# Check coverage
PYTHONPATH=src coverage run -m pytest tests/part2_logging/test_lesson_2_1.py
coverage report --include=src/logger.py

# Check pylint
pylint --errors-only src/logger.py
```

Target: 100% coverage, no pylint errors!

---

## ✅ Part 4: Verify Understanding (5 minutes)

Before moving on, make sure you can answer:

1. **Why is logging better than print()?**
   - Configurable (levels, formats, destinations)
   - Persistent (save to files)
   - Searchable (grep, analyze patterns)
   - Contextual (timestamps, module names, levels)

2. **What are the 5 log levels?**
   - DEBUG (10) - Detailed diagnostic info
   - INFO (20) - General informational messages
   - WARNING (30) - Something unexpected but recoverable
   - ERROR (40) - Error occurred, function failed
   - CRITICAL (50) - Severe error, system may crash

3. **When should you use each level?**
   - DEBUG: Development debugging
   - INFO: User actions, business events
   - WARNING: Deprecated features, config issues
   - ERROR: Exceptions, failures
   - CRITICAL: System crash, data loss

4. **What does logging.basicConfig() do?**
   - Configures the root logger
   - Sets level, format, and destination
   - Should be called once at startup

5. **Why use `__name__` for logger names?**
   - Gets the module name automatically
   - Makes logs traceable to source
   - Follows Python convention

---

## 🎉 Success Criteria

You're done when:

- ✅ All 22 tests pass
- ✅ `get_logger()` returns a configured logger
- ✅ `setup_logging()` configures logging properly
- ✅ Logs include timestamps, level, name, message
- ✅ Can log to files
- ✅ Log levels filter correctly
- ✅ Coverage is 100%
- ✅ Pylint passes with no errors

---

## 🚀 Commit Your Work

```bash
# Check what changed
git diff src/logger.py

# Add and commit
git add src/logger.py tests/part2_logging/test_lesson_2_1.py
git commit -m "feature: lesson 2.1 - basic logging"
```

---

## 🔍 Troubleshooting

### "Logs not appearing"

Check your log level:
```python
# ❌ Won't show debug messages
setup_logging(level=logging.INFO)
logger.debug('Not visible!')

# ✅ Shows everything
setup_logging(level=logging.DEBUG)
logger.debug('Visible!')
```

### "Duplicate log messages"

You're calling `basicConfig()` multiple times:
```python
# ❌ Creates multiple handlers
setup_logging()
setup_logging()  # Adds another handler!

# ✅ Call once at startup
setup_logging()  # Then never again
```

### "Logs go to file AND console"

`basicConfig()` only logs to one place:
```python
# Pick one:
logging.basicConfig(filename='app.log')  # File only
# OR
logging.basicConfig()  # Console only
```

---

## 🎯 Real-World Applications

### Where You'll Use This

1. **Web APIs**
   ```python
   logger.info(f'Request received: {method} {path}')
   logger.error(f'Database query failed: {error}')
   ```

2. **Data Processing**
   ```python
   logger.debug(f'Processing record {i}/{total}')
   logger.warning(f'Invalid data in row {row_num}')
   ```

3. **Background Jobs**
   ```python
   logger.info('Starting daily backup')
   logger.error('Backup failed', exc_info=True)
   ```

4. **Production Debugging**
   ```python
   # Before: No idea what happened
   # After: Search logs for errors
   grep "ERROR" app.log
   ```

---

## 📚 Additional Resources

- [Python Logging HOWTO](https://docs.python.org/3/howto/logging.html)
- [Logging Cookbook](https://docs.python.org/3/howto/logging-cookbook.html)
- [12-Factor App: Logs](https://12factor.net/logs)
- [Logging Best Practices](https://docs.python-guide.org/writing/logging/)

---

## 🎓 Key Takeaways

1. **print() is for output, logging is for debugging**
2. **Always use log levels appropriately**
3. **Configure logging once at startup**
4. **Include context in log messages**
5. **Log to files in production**
6. **Use `__name__` for logger names**
7. **DEBUG for development, INFO+ for production**

---

## 💡 Pro Tips

### ✅ DO:
- Use `__name__` for logger names
- Set appropriate log levels
- Include context (user IDs, request IDs)
- Log exceptions with `logger.exception()`
- Configure once at startup

### ❌ DON'T:
- Use print() for debugging
- Log sensitive data (passwords, tokens)
- Log in tight loops (performance!)
- Call `basicConfig()` multiple times
- Use DEBUG level in production

---

## 🎊 Great Job!

You now understand why logging is essential! Every professional Python application uses logging. You've taken a big step toward writing production-ready code! 🎯

**Remember**: 
- print() is for showing output to users
- logging is for debugging and monitoring your application

Now you can debug production issues without SSH-ing into servers and adding print statements! 🚀

---

### 🧭 Navigation
⬅️ [Previous](../part1_configuration/lesson_1_3.md) | 🏠 [All Lessons](../../README.md#-all-lessons) | 📖 [README](../../README.md) | ➡️ [Next](lesson_2_2.md)

---

**Lesson Complete!** When all tests pass, continue to [Next Lesson →](lesson_2_2.md)
