# Lesson 2.2: Custom Log Handlers and Formatters

**Duration:** 45 minutes  
**Prerequisites:** Lesson 2.1 (Basic Logging)

## Learning Objectives

By the end of this lesson, you will:
- Create custom log handlers for different output destinations
- Build custom formatters for specialized log formats
- Implement a rotating file handler to manage log file sizes
- Add colored console output for better readability
- Create a JSON formatter for structured logging

## The Story: When Basic Logging Isn't Enough

Your app is growing. You have logs going to a file, but now:
- **The log file is getting huge** (10GB and counting!)
- **You want different formats** for console vs. file
- **Your monitoring system** needs JSON format
- **Developers want colored output** to spot errors quickly

Basic logging works, but you need more control. That's where custom handlers and formatters come in.

## Part 1: Understanding Handlers and Formatters

### What are Handlers?

Handlers determine **where** logs go:
- `StreamHandler` → console
- `FileHandler` → single file
- `RotatingFileHandler` → multiple files (auto-rotate by size)
- `TimedRotatingFileHandler` → multiple files (auto-rotate by time)

### What are Formatters?

Formatters determine **how** logs look:
```python
# Standard format
'%(asctime)s - %(name)s - %(levelname)s - %(message)s'

# Custom format with more details
'[%(levelname)s] %(asctime)s | %(name)s:%(lineno)d | %(message)s'

# JSON format for machine parsing
'{"timestamp": "%(asctime)s", "level": "%(levelname)s", "message": "%(message)s"}'
```

## Part 2: Rotating File Handler

**Problem:** Log files grow forever and fill your disk.

**Solution:** Rotate logs when they reach a size limit.

```python
from logging.handlers import RotatingFileHandler

def setup_rotating_logger(log_file: str, max_bytes: int = 10485760, backup_count: int = 5):
    """Set up logger with rotating file handler.
    
    Args:
        log_file: Path to log file
        max_bytes: Max size before rotation (default: 10MB)
        backup_count: Number of backup files to keep
    """
    handler = RotatingFileHandler(
        log_file,
        maxBytes=max_bytes,      # 10MB
        backupCount=backup_count  # Keep 5 backups
    )
    # When app.log hits 10MB:
    # - app.log → app.log.1
    # - app.log.1 → app.log.2
    # - Start new app.log
```

## Part 3: Custom JSON Formatter

**Problem:** Your monitoring system (Datadog, ELK, etc.) needs structured data.

**Solution:** Create a JSON formatter.

```python
import json
import logging

class JsonFormatter(logging.Formatter):
    """Format log records as JSON."""
    
    def format(self, record: logging.LogRecord) -> str:
        """Convert log record to JSON string."""
        log_data = {
            'timestamp': self.formatTime(record),
            'level': record.levelname,
            'logger': record.name,
            'message': record.getMessage(),
            'module': record.module,
            'function': record.funcName,
            'line': record.lineno
        }
        
        # Add exception info if present
        if record.exc_info:
            log_data['exception'] = self.formatException(record.exc_info)
        
        return json.dumps(log_data)
```

## Part 4: Multiple Handlers

**Real-world scenario:** You want:
- Console: Colored, human-readable
- File: JSON format for parsing
- Errors: Separate error.log file

```python
def setup_multi_handler_logging(app_log: str, error_log: str):
    """Set up logging with multiple handlers."""
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)
    
    # Console handler - human readable
    console = logging.StreamHandler()
    console.setLevel(logging.INFO)
    console.setFormatter(logging.Formatter(
        '%(levelname)s: %(message)s'
    ))
    
    # File handler - JSON format
    file_handler = RotatingFileHandler(app_log, maxBytes=10485760, backupCount=5)
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(JsonFormatter())
    
    # Error handler - only errors
    error_handler = logging.FileHandler(error_log)
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    ))
    
    logger.addHandler(console)
    logger.addHandler(file_handler)
    logger.addHandler(error_handler)
```

## Part 5: Custom Formatter with Colors

**Problem:** Hard to spot errors in console output.

**Solution:** Add ANSI color codes.

```python
class ColoredFormatter(logging.Formatter):
    """Format logs with colors for console output."""
    
    COLORS = {
        'DEBUG': '\033[36m',    # Cyan
        'INFO': '\033[32m',     # Green
        'WARNING': '\033[33m',  # Yellow
        'ERROR': '\033[31m',    # Red
        'CRITICAL': '\033[35m'  # Magenta
    }
    RESET = '\033[0m'
    
    def format(self, record: logging.LogRecord) -> str:
        """Add colors to log output."""
        # Get color for this level
        color = self.COLORS.get(record.levelname, self.RESET)
        
        # Color the level name
        record.levelname = f"{color}{record.levelname}{self.RESET}"
        
        return super().format(record)
```

## Real-World Example

**Scenario:** Production app with comprehensive logging.

```python
from logger import setup_rotating_logger, JsonFormatter, ColoredFormatter
from logging.handlers import RotatingFileHandler
import logging

# Set up production logging
def setup_production_logging():
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)
    
    # 1. Console - colored, INFO and above
    console = logging.StreamHandler()
    console.setLevel(logging.INFO)
    console.setFormatter(ColoredFormatter(
        '%(levelname)s - %(message)s'
    ))
    
    # 2. Application logs - JSON, rotating, all levels
    app_handler = RotatingFileHandler(
        'logs/app.log',
        maxBytes=10485760,  # 10MB
        backupCount=10
    )
    app_handler.setFormatter(JsonFormatter())
    
    # 3. Error logs - separate file, errors only
    error_handler = logging.FileHandler('logs/error.log')
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s\n%(pathname)s:%(lineno)d'
    ))
    
    logger.addHandler(console)
    logger.addHandler(app_handler)
    logger.addHandler(error_handler)

# Use in application
setup_production_logging()
logger = logging.getLogger(__name__)

logger.debug('Database query executed')      # → app.log only
logger.info('User logged in')                # → console + app.log
logger.error('Database connection failed')   # → all three!
```

## Key Concepts

### Handler Hierarchy
```
Logger (root)
├── Handler 1 (Console, INFO+)
├── Handler 2 (File, DEBUG+)
└── Handler 3 (Error file, ERROR+)
```

Each handler can have:
- Different level filters
- Different formatters
- Different destinations

### Formatter Patterns

| Pattern | Output | Use Case |
|---------|--------|----------|
| Standard | `2024-01-01 10:00:00 - INFO - Message` | Development |
| JSON | `{"timestamp": "...", "level": "INFO"}` | Production/Monitoring |
| Minimal | `INFO: Message` | Console |
| Detailed | `[INFO] file.py:42 - Message` | Debugging |

## Testing Strategy

You'll test:
1. **RotatingFileHandler** creates and rotates files
2. **JsonFormatter** produces valid JSON
3. **Multiple handlers** each receive appropriate messages
4. **ColoredFormatter** adds ANSI codes (optional for color)
5. **Handler levels** filter correctly

## Common Pitfalls

❌ **Forgetting to create log directory**
```python
# Bad
handler = FileHandler('logs/app.log')  # Crashes if 'logs/' doesn't exist

# Good
import os
os.makedirs('logs', exist_ok=True)
handler = FileHandler('logs/app.log')
```

❌ **Not closing handlers in tests**
```python
# Handlers hold file handles - close them!
for handler in logger.handlers[:]:
    handler.close()
    logger.removeHandler(handler)
```

❌ **JSON formatter breaking on exceptions**
```python
# Bad - exception text might break JSON

# Good - properly escape and include exception
if record.exc_info:
    log_data['exception'] = self.formatException(record.exc_info)
```

## Summary

Custom handlers and formatters give you:
- ✅ **Control over destinations** (console, files, network)
- ✅ **Control over formats** (human, JSON, colored)
- ✅ **Automatic log rotation** (no more 10GB files!)
- ✅ **Level-based routing** (errors → error.log)

Next lesson: We'll add **contextual logging** (request IDs, user info, etc.)

## Your Task

Implement the functions to make the tests pass:
1. `JsonFormatter` - Custom formatter that outputs JSON
2. `get_rotating_file_handler()` - Returns a RotatingFileHandler
3. `setup_multi_handler_logging()` - Sets up multiple handlers with different formatters

Run the tests:
```bash
pytest tests/part2_logging/test_lesson_2_2.py -v
```

Good luck! 🎯
