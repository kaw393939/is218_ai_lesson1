# Lesson 3.3: Adding Logging to REPL

**Course**: IS 218 - Building AI Systems  
**Part**: 3 - REPL Development  
**Lesson**: 3.3 - Logging Integration  
**Difficulty**: ⭐⭐⭐☆☆  
**Time**: 60 minutes

## Learning Objectives

By the end of this lesson, you will be able to:

1. Integrate structured logging into an interactive application
2. Log user commands and calculation results for audit trails
3. Implement debug mode for troubleshooting
4. Use contextual logging with session IDs
5. Apply log levels appropriately (INFO, DEBUG, ERROR)
6. Create logging configuration from environment variables

## The Story: Building an Audit Trail

Your calculator REPL is working great! Users love it. But then your manager asks:

- **"How do we know what calculations users are performing?"**
- **"Can we troubleshoot when users report errors?"**
- **"Do we have an audit trail for compliance?"**

You realize you need logging. Not just print statements, but **structured, searchable logs** that can:
- Track every calculation performed
- Record errors with full context
- Help debug issues in production
- Comply with audit requirements

Good news: You already built a comprehensive logging system in Part 2! Now it's time to integrate it.

## Why Logging in a REPL?

REPLs are interactive, which makes logging tricky:
- **Too much logging**: Clutters the user interface
- **Too little logging**: Can't troubleshoot issues
- **Wrong log level**: Users see debug messages or miss errors

The solution? **Contextual logging** that:
- Uses INFO for user-facing results
- Uses DEBUG for internal details
- Uses ERROR for problems
- Keeps session context to group related operations

## Logging Requirements for Calculator

Let's define what we want to log:

### 1. Session Start/End
```
INFO: Starting calculator session (session_id=abc123)
INFO: Calculator session ended (session_id=abc123, operations=15, duration=120s)
```

### 2. User Commands
```
INFO: Command executed: add 10 20 (session_id=abc123)
DEBUG: Parsed command: operation='add', args=[10.0, 20.0]
```

### 3. Calculation Results
```
INFO: Result: 30.0 (session_id=abc123)
DEBUG: Result rounded to 2 decimal places: 30.80 -> 30.8
```

### 4. Errors
```
ERROR: Command failed: divide by zero (session_id=abc123, command='divide 10 0')
ERROR: Invalid input: not a number (session_id=abc123, input='abc')
```

### 5. Configuration
```
INFO: Calculator configured (precision=2, max_value=1000000.0)
DEBUG: Configuration loaded from environment
```

## Implementation Plan

### Step 1: Extend CalculatorConfig with Logging Settings

```python
class CalculatorConfig(TypedConfig):
    """Configuration for calculator REPL with sensible defaults."""
    
    # ... existing properties ...
    
    @property
    def log_level(self) -> str:
        """Logging level (DEBUG, INFO, WARNING, ERROR)."""
        return self.get_str('REPL_LOG_LEVEL', 'INFO')
    
    @property
    def log_file(self) -> str:
        """Path to log file."""
        return self.get_str('REPL_LOG_FILE', 'calculator.log')
    
    @property
    def log_to_console(self) -> bool:
        """Whether to show logs in console."""
        return self.get_bool('REPL_LOG_TO_CONSOLE', False)
```

### Step 2: Initialize Logger in CalculatorREPL

```python
import uuid
from logger import get_logger, setup_logging

class CalculatorREPL:
    """Interactive calculator REPL with logging."""
    
    def __init__(self, config: CalculatorConfig | None = None):
        """Initialize REPL with logging."""
        self.running = False
        self.config = config or CalculatorConfig()
        
        # Setup logging
        setup_logging(
            level=self.config.log_level,
            log_file=self.config.log_file
        )
        self.logger = get_logger(__name__)
        
        # Session tracking
        self.session_id = str(uuid.uuid4())[:8]
        self.operation_count = 0
        
        self.logger.info(
            "Calculator session started",
            extra={'session_id': self.session_id}
        )
```

### Step 3: Log User Commands

```python
def process_command(self, user_input: str):
    """Process user command with logging."""
    self.logger.debug(
        f"Processing input: {user_input}",
        extra={'session_id': self.session_id}
    )
    
    # ... parse command ...
    
    if command == 'exit':
        self.logger.info(
            "Exit command received",
            extra={
                'session_id': self.session_id,
                'operations_performed': self.operation_count
            }
        )
        # ... exit logic ...
```

### Step 4: Log Calculation Results

```python
def execute_command(self, command: str, args: list) -> float:
    """Execute command with detailed logging."""
    self.logger.debug(
        f"Executing command: {command}",
        extra={
            'session_id': self.session_id,
            'command': command,
            'args': args
        }
    )
    
    # ... perform calculation ...
    
    self.logger.info(
        f"Calculation completed: {command} {args[0]} {args[1]} = {result}",
        extra={
            'session_id': self.session_id,
            'operation': command,
            'result': result
        }
    )
    
    self.operation_count += 1
    return result
```

### Step 5: Log Errors with Context

```python
def process_command(self, user_input: str):
    """Process command with error logging."""
    try:
        result = self.execute_command(command, args)
        print(f"Result: {result}")
    except ValueError as e:
        self.logger.error(
            f"Invalid command: {e}",
            extra={
                'session_id': self.session_id,
                'command': command,
                'args': args,
                'error': str(e)
            }
        )
        print(f"Error: {e}")
    except ZeroDivisionError:
        self.logger.error(
            "Division by zero attempted",
            extra={
                'session_id': self.session_id,
                'command': command,
                'args': args
            }
        )
        print("Error: Cannot divide by zero")
```

## Real-World Example

Let's see how logging helps in practice:

```bash
# Start calculator with debug logging
$ export REPL_LOG_LEVEL=DEBUG
$ export REPL_LOG_FILE=calculator.log
$ python src/repl.py
Calculator REPL v1.0

> add 10.5 20.3
Result: 30.8

> divide 100 0
Error: Cannot divide by zero

> multiply 1000000 1000000
Error: Result exceeds maximum value: 1000000.0

> exit
Goodbye!
```

**Log file (calculator.log):**
```
2025-10-03 14:30:00 INFO Calculator session started session_id=a1b2c3d4
2025-10-03 14:30:00 INFO Calculator configured precision=2 max_value=1000000.0
2025-10-03 14:30:05 DEBUG Processing input: add 10.5 20.3 session_id=a1b2c3d4
2025-10-03 14:30:05 DEBUG Executing command: add session_id=a1b2c3d4 args=['10.5', '20.3']
2025-10-03 14:30:05 INFO Calculation completed: add 10.5 20.3 = 30.8 session_id=a1b2c3d4
2025-10-03 14:30:10 DEBUG Processing input: divide 100 0 session_id=a1b2c3d4
2025-10-03 14:30:10 DEBUG Executing command: divide session_id=a1b2c3d4 args=['100', '0']
2025-10-03 14:30:10 ERROR Division by zero attempted session_id=a1b2c3d4 command=divide args=['100', '0']
2025-10-03 14:30:15 DEBUG Processing input: multiply 1000000 1000000 session_id=a1b2c3d4
2025-10-03 14:30:15 DEBUG Executing command: multiply session_id=a1b2c3d4 args=['1000000', '1000000']
2025-10-03 14:30:15 ERROR Result exceeds maximum session_id=a1b2c3d4 command=multiply result=1000000000000.0
2025-10-03 14:30:20 INFO Exit command received session_id=a1b2c3d4 operations_performed=1
2025-10-03 14:30:20 INFO Session ended session_id=a1b2c3d4 duration=20s operations=1
```

Notice how the logs provide:
- **Session tracking**: All operations grouped by session_id
- **Audit trail**: Complete record of what happened
- **Debug information**: Detailed parsing and execution steps
- **Error context**: Full information about failures

## Testing Strategy

We need tests for:

1. **Logger initialization**: Verify logger is created with correct config
2. **Session tracking**: Ensure session_id is generated and used
3. **Command logging**: Verify commands are logged at INFO level
4. **Result logging**: Verify results are logged with context
5. **Error logging**: Verify errors are logged with full details
6. **Debug mode**: Verify DEBUG logs only appear when enabled
7. **Operation counting**: Verify operation count is tracked
8. **Session end logging**: Verify session summary is logged

## Key Concepts

### 1. Contextual Logging with Session ID

```python
# Add session context to all logs
self.logger.info(
    "Message",
    extra={'session_id': self.session_id}
)
```

This allows grouping all logs from a single user session.

### 2. Appropriate Log Levels

- **DEBUG**: Internal details (parsing, rounding, config loading)
- **INFO**: User actions and results (commands, calculations)
- **ERROR**: Failures (invalid input, divide by zero, max exceeded)

### 3. Structured Logging

```python
# Good: Structured data in extra
self.logger.info(
    "Calculation completed",
    extra={
        'operation': 'add',
        'result': 30.8,
        'session_id': 'abc123'
    }
)

# Bad: Everything in message
self.logger.info(f"Calculation: add result=30.8 session=abc123")
```

Structured logs are easier to parse and search!

### 4. Logging Without Cluttering UI

```python
# Don't show debug logs to users unless configured
if self.config.log_to_console:
    # Add console handler
    console_handler = logging.StreamHandler()
    self.logger.addHandler(console_handler)
```

## Common Patterns

### Pattern 1: Log Before and After

```python
def execute_command(self, command: str, args: list) -> float:
    self.logger.debug(f"Starting: {command}", extra={'args': args})
    result = self._calculate(command, args)
    self.logger.info(f"Completed: {command}", extra={'result': result})
    return result
```

### Pattern 2: Log Exceptions with Context

```python
try:
    result = self.execute_command(command, args)
except Exception as e:
    self.logger.error(
        "Command failed",
        extra={'command': command, 'error': str(e)},
        exc_info=True  # Include stack trace
    )
    raise
```

### Pattern 3: Performance Logging

```python
import time

def execute_command(self, command: str, args: list) -> float:
    start_time = time.time()
    result = self._calculate(command, args)
    duration = time.time() - start_time
    
    self.logger.debug(
        "Performance",
        extra={
            'command': command,
            'duration_ms': round(duration * 1000, 2)
        }
    )
    return result
```

## Testing Your Understanding

### Exercise 1: Add Operation History Logging
Log the last 10 operations when the session ends:

```python
def __init__(self):
    # ...
    self.history = []

def execute_command(self, command: str, args: list) -> float:
    # ...
    self.history.append({
        'command': command,
        'args': args,
        'result': result
    })
    return result

def stop(self):
    self.logger.info(
        "Session history",
        extra={
            'session_id': self.session_id,
            'history': self.history[-10:]  # Last 10 operations
        }
    )
```

### Exercise 2: Add Slow Operation Warnings
Warn if an operation takes longer than expected:

```python
def execute_command(self, command: str, args: list) -> float:
    start = time.time()
    result = self._calculate(command, args)
    duration = time.time() - start
    
    if duration > 0.1:  # 100ms threshold
        self.logger.warning(
            "Slow operation detected",
            extra={'command': command, 'duration_ms': duration * 1000}
        )
    return result
```

### Exercise 3: Add User Context
Track which user is running the calculator:

```python
@property
def user_name(self) -> str:
    """Current user's name from environment."""
    return self.get_str('USER', 'unknown')

def __init__(self, config: CalculatorConfig | None = None):
    # ...
    self.logger.info(
        "Session started",
        extra={
            'session_id': self.session_id,
            'user': self.config.user_name
        }
    )
```

## What You Built

In this lesson, you:

1. ✅ Extended `CalculatorConfig` with logging settings
2. ✅ Integrated logger into `CalculatorREPL`
3. ✅ Added session tracking with unique IDs
4. ✅ Logged all user commands at INFO level
5. ✅ Logged calculation results with context
6. ✅ Logged errors with full details
7. ✅ Added DEBUG logging for internal operations
8. ✅ Tracked operation count per session
9. ✅ Logged session start and end with summary

## How This Helps You

**In Industry**:
- Production systems need comprehensive logging for troubleshooting
- Compliance requirements often mandate audit trails
- Performance monitoring relies on structured logs
- Security teams use logs to detect anomalies

**Common Interview Topics**:
- "How do you debug production issues?"
- "Explain log levels and when to use each"
- "How do you implement request tracing?"
- "What's the difference between logging and monitoring?"

**Real Tools That Use This**:
- **ELK Stack**: Elasticsearch, Logstash, Kibana for log analysis
- **Datadog**: Application performance monitoring with logs
- **Splunk**: Log aggregation and search
- **CloudWatch**: AWS logging and monitoring

## Next Steps

In **Lesson 3.4: Advanced REPL Features**, you'll add command history, shortcuts, tab completion, and color output to create a professional-grade calculator REPL.

## Before You Start

Run the tests and watch them fail. That's expected! You'll implement the code to make them pass:

```bash
pytest tests/part3_repl/test_lesson_3_3.py -v
```

## Success Criteria

When you're done:
- ✅ All 25 tests pass
- ✅ Coverage remains above 68%
- ✅ Pylint scores 10/10
- ✅ Calculator logs all operations
- ✅ Session tracking works correctly
- ✅ Debug mode can be toggled
- ✅ Errors are logged with full context

---

Ready? Let's add logging! 📝
