# Lesson 2.3: Contextual Logging with Adapters

> **Part 2 of 4: Logging & Debugging** | Lesson 3 of 4

**⏱️ Time**: 60 minutes  
**🎯 Goal**: Make all 24 tests pass!  
**📁 File**: `src/logger.py` (add contextual logging)  
**📦 Builds On**: Lessons 2.1-2.2 (Basic Logging + Custom Handlers)

---

### 🧭 Navigation
⬅️ [Previous: Lesson 2.2](lesson_2_2.md) | 🏠 [Course Index](../INDEX.md) | 📖 [README](../../README.md) | ➡️ [Next: Lesson 2.4](lesson_2_4.md)

---

## Learning Objectives

By the end of this lesson, you will:
- Understand why context matters in logs
- Use LoggerAdapter to add context to all log messages
- Implement request ID tracking across function calls
- Add user context to logs for debugging
- Create custom context managers for automatic context injection

## The Story: The Mystery Bug

**Production nightmare:**
```
ERROR: Database connection failed
ERROR: Invalid user credentials
ERROR: Database connection failed
ERROR: Payment processing error
ERROR: Database connection failed
```

**Questions you can't answer:**
- Which user had the error?
- Was it the same request or different requests?
- What was the sequence of events?
- How do you trace one request through the system?

**Without context, logs are nearly useless in production.**

## Part 1: Understanding Contextual Logging

### The Problem

**Bad logging:**
```python
logger.info('User logged in')
logger.info('Checking permissions')
logger.error('Permission denied')
```

When 1000 users are online simultaneously, which user had the permission error?

**Good logging:**
```python
logger.info('User logged in', extra={'user_id': 'user123', 'request_id': 'abc-def'})
logger.info('Checking permissions', extra={'user_id': 'user123', 'request_id': 'abc-def'})
logger.error('Permission denied', extra={'user_id': 'user123', 'request_id': 'abc-def'})
```

Now you can grep logs for `request_id: abc-def` and see the entire request flow!

### The Solution: LoggerAdapter

Python's `LoggerAdapter` automatically adds context to every log message:

```python
from logging import LoggerAdapter

# Create adapter with context
logger = logging.getLogger(__name__)
context_logger = LoggerAdapter(logger, {'user_id': 'user123', 'request_id': 'abc-def'})

# All logs automatically include context
context_logger.info('User logged in')  
# Output: INFO - User logged in - {'user_id': 'user123', 'request_id': 'abc-def'}
```

## Part 2: Request ID Tracking

**Real-world pattern:** Track a single request through your entire system.

```python
import uuid
from logging import LoggerAdapter

def get_contextual_logger(logger, request_id=None):
    """Get a logger with request context.
    
    Args:
        logger: Base logger
        request_id: Optional request ID (generates one if not provided)
        
    Returns:
        LoggerAdapter with request context
    """
    if request_id is None:
        request_id = str(uuid.uuid4())
    
    return LoggerAdapter(logger, {'request_id': request_id})


# Usage in web application
def handle_api_request(request):
    request_id = request.headers.get('X-Request-ID') or str(uuid.uuid4())
    logger = get_contextual_logger(logging.getLogger(__name__), request_id)
    
    logger.info('Received API request')
    result = process_data(logger)  # Pass logger down
    logger.info('Completed API request')
    
    return result

def process_data(logger):
    logger.info('Processing data')  # Still has request_id!
    # Do work...
    logger.info('Data processing complete')
```

**Output:**
```
INFO - Received API request - {'request_id': 'abc-123'}
INFO - Processing data - {'request_id': 'abc-123'}
INFO - Data processing complete - {'request_id': 'abc-123'}
INFO - Completed API request - {'request_id': 'abc-123'}
```

## Part 3: User Context

**Add user information to every log:**

```python
def get_user_logger(logger, user_id, username=None):
    """Get a logger with user context.
    
    Args:
        logger: Base logger
        user_id: User ID
        username: Optional username
        
    Returns:
        LoggerAdapter with user context
    """
    context = {'user_id': user_id}
    if username:
        context['username'] = username
    
    return LoggerAdapter(logger, context)


# Usage
logger = get_user_logger(logging.getLogger(__name__), 'user123', 'alice')
logger.info('Updating profile')
# Output: INFO - Updating profile - {'user_id': 'user123', 'username': 'alice'}
```

## Part 4: Combined Context

**Multiple context pieces:**

```python
def get_logger_with_context(logger, **context):
    """Get a logger with arbitrary context.
    
    Args:
        logger: Base logger
        **context: Arbitrary context key-value pairs
        
    Returns:
        LoggerAdapter with provided context
    """
    return LoggerAdapter(logger, context)


# Usage
logger = get_logger_with_context(
    logging.getLogger(__name__),
    user_id='user123',
    request_id='abc-def',
    ip_address='192.168.1.1',
    endpoint='/api/users'
)

logger.info('Processing request')
# Output: INFO - Processing request - {'user_id': 'user123', 'request_id': 'abc-def', ...}
```

## Part 5: Context Manager for Automatic Context

**Problem:** Remembering to add context everywhere is error-prone.

**Solution:** Context manager that automatically adds context:

```python
from contextlib import contextmanager
import logging
from logging import LoggerAdapter

@contextmanager
def log_context(logger, **context):
    """Context manager that adds context to logger.
    
    Args:
        logger: Base logger or adapter
        **context: Context to add
        
    Yields:
        LoggerAdapter with context
        
    Example:
        with log_context(logger, request_id='abc') as log:
            log.info('Processing')
    """
    # Create adapter with context
    context_logger = LoggerAdapter(logger, context)
    
    # Log entry
    context_logger.debug('Entering context')
    
    try:
        yield context_logger
    finally:
        # Log exit
        context_logger.debug('Exiting context')


# Usage
logger = logging.getLogger(__name__)

with log_context(logger, request_id='abc-123', user_id='user456') as log:
    log.info('Processing request')
    log.info('Calling database')
    # All logs automatically have context
```

## Part 6: Custom LoggerAdapter

**For advanced use cases, create a custom adapter:**

```python
class ContextLoggerAdapter(LoggerAdapter):
    """Logger adapter with enhanced context handling."""
    
    def process(self, msg, kwargs):
        """Process log message and inject context.
        
        Args:
            msg: Log message
            kwargs: Log kwargs
            
        Returns:
            Tuple of (msg, kwargs) with context injected
        """
        # Add context to the message or extra
        if 'extra' not in kwargs:
            kwargs['extra'] = {}
        
        # Merge adapter context with call-specific extra
        kwargs['extra'].update(self.extra)
        
        return msg, kwargs


# Usage
logger = logging.getLogger(__name__)
adapter = ContextLoggerAdapter(logger, {'service': 'api', 'version': '1.0'})

adapter.info('Request received')
# Context automatically added to 'extra' dict
```

## Real-World Example: Web Application

**Complete production logging setup:**

```python
import uuid
import logging
from logging import LoggerAdapter
from contextlib import contextmanager

class WebApp:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def handle_request(self, user_id, endpoint):
        """Handle a web request with full context."""
        request_id = str(uuid.uuid4())
        
        # Create logger with all context
        logger = LoggerAdapter(self.logger, {
            'request_id': request_id,
            'user_id': user_id,
            'endpoint': endpoint
        })
        
        logger.info('Request started')
        
        try:
            # Simulate request processing
            self._validate_user(logger, user_id)
            result = self._process_business_logic(logger)
            self._save_to_database(logger, result)
            
            logger.info('Request completed successfully')
            return result
            
        except Exception as e:
            logger.error(f'Request failed: {e}')
            raise
    
    def _validate_user(self, logger, user_id):
        logger.debug('Validating user')
        # All logs still have request_id, user_id, endpoint!
        
    def _process_business_logic(self, logger):
        logger.info('Processing business logic')
        return {'status': 'success'}
    
    def _save_to_database(self, logger, data):
        logger.debug('Saving to database')


# Usage
app = WebApp()
app.handle_request('user123', '/api/orders')
```

**Output:**
```
INFO - Request started - {'request_id': 'abc-123', 'user_id': 'user123', 'endpoint': '/api/orders'}
DEBUG - Validating user - {'request_id': 'abc-123', 'user_id': 'user123', 'endpoint': '/api/orders'}
INFO - Processing business logic - {'request_id': 'abc-123', 'user_id': 'user123', 'endpoint': '/api/orders'}
DEBUG - Saving to database - {'request_id': 'abc-123', 'user_id': 'user123', 'endpoint': '/api/orders'}
INFO - Request completed successfully - {'request_id': 'abc-123', 'user_id': 'user123', 'endpoint': '/api/orders'}
```

Now you can search logs for `request_id: abc-123` and see the entire request flow!

## Key Concepts

### Why Context Matters

| Without Context | With Context |
|----------------|--------------|
| ERROR: Payment failed | ERROR: Payment failed - {'user_id': 'user123', 'order_id': 'ord-456'} |
| Impossible to debug | Can find all logs for this user/order |
| Can't trace request flow | Can grep by request_id |

### LoggerAdapter vs Extra

**Option 1: LoggerAdapter (Recommended)**
```python
logger = LoggerAdapter(base_logger, {'user_id': 'user123'})
logger.info('Message')  # Context automatic
```

**Option 2: Extra (Manual)**
```python
logger.info('Message', extra={'user_id': 'user123'})  # Must add every time
```

LoggerAdapter wins because context is automatic!

### Context Best Practices

✅ **DO:**
- Add request IDs to trace requests
- Include user IDs for debugging user issues
- Add service/module names in microservices
- Use timestamps for duration tracking

❌ **DON'T:**
- Log passwords or secrets in context
- Add huge objects (just IDs)
- Add context that changes every log (defeats the purpose)

## Testing Strategy

You'll test:
1. **get_contextual_logger()** adds request ID
2. **get_user_logger()** adds user context
3. **get_logger_with_context()** adds arbitrary context
4. **log_context()** context manager works
5. **Context propagates** through nested calls

## Common Pitfalls

❌ **Creating new adapter every log call**
```python
# Bad - creates new adapter each time
def process():
    LoggerAdapter(logger, {...}).info('Message 1')
    LoggerAdapter(logger, {...}).info('Message 2')

# Good - create once, reuse
def process():
    log = LoggerAdapter(logger, {...})
    log.info('Message 1')
    log.info('Message 2')
```

❌ **Forgetting to pass logger down**
```python
# Bad - loses context
def handler():
    log = LoggerAdapter(logger, {'request_id': '123'})
    log.info('Started')
    helper()  # helper() doesn't have context!

# Good - pass logger
def handler():
    log = LoggerAdapter(logger, {'request_id': '123'})
    log.info('Started')
    helper(log)  # Pass it down
```

❌ **Mixing context styles**
```python
# Bad - confusing
log = LoggerAdapter(logger, {'request_id': '123'})
log.info('Message', extra={'user_id': '456'})  # Now has BOTH extra dicts

# Good - use one approach
log = LoggerAdapter(logger, {'request_id': '123', 'user_id': '456'})
log.info('Message')
```

## Summary

Contextual logging with LoggerAdapter gives you:
- ✅ **Automatic context** on every log message
- ✅ **Request tracing** through entire system
- ✅ **User debugging** - find all logs for a user
- ✅ **Cleaner code** - no manual extra={'...'} everywhere

**Before:**
```
ERROR: Payment failed
```
*Which user? Which request? Good luck debugging!*

**After:**
```
ERROR: Payment failed - {'request_id': 'abc-123', 'user_id': 'user456', 'order_id': 'ord-789'}
```
*Perfect! Now I can trace this request and debug.*

Next lesson: We'll add **secure logging** (redacting sensitive data like passwords, API keys, credit cards).

## Your Task

Implement the functions to make the tests pass:
1. `get_contextual_logger()` - Returns LoggerAdapter with request_id
2. `get_user_logger()` - Returns LoggerAdapter with user context

---

### 🧭 Navigation
⬅️ [Previous: Lesson 2.2](lesson_2_2.md) | 🏠 [Course Index](../INDEX.md) | 📖 [README](../../README.md) | ➡️ [Next: Lesson 2.4](lesson_2_4.md)

---

**Lesson 2.3 Complete!** When all tests pass, continue to [Lesson 2.4: Secure Logging →](lesson_2_4.md)
3. `get_logger_with_context()` - Returns LoggerAdapter with arbitrary context
4. `log_context()` - Context manager that yields LoggerAdapter

Run the tests:
```bash
pytest tests/part2_logging/test_lesson_2_3.py -v
```

Good luck! 🎯
