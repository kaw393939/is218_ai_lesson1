# Lesson 2.4: Secure Logging - Protecting Sensitive Data

## Story: The Data Breach That Wasn't

Sarah was doing a routine log review when she froze. There, in plain text in the application logs, were dozens of customer passwords, credit card numbers, and API keys. The logs were stored on a shared server. Dozens of developers had access. The security team had access. The operations team had access.

"How long have we been logging this?" she asked, her voice shaking.

"Since launch," her tech lead replied. "Two years."

It took three weeks to audit who had accessed the logs, notify affected customers, rotate all API keys, and implement proper log sanitization. The company was fined $50,000 for the GDPR violation. All because someone logged `user.password` during debugging and forgot to remove it.

**The lesson:** Logs are permanent records that many people can access. What you log matters as much as what you store in databases.

## Learning Objectives

By the end of this lesson, you will be able to:

1. Identify sensitive data that should never appear in logs
2. Implement filters to automatically redact sensitive information
3. Create custom formatters that sanitize log messages
4. Use logging filters to protect API keys, passwords, and PII
5. Test that sensitive data is properly redacted

## Concepts

### What Is Sensitive Data?

**Never log these in plain text:**
- **Passwords**: User passwords, database passwords, service passwords
- **API Keys/Tokens**: Authentication tokens, API keys, secrets
- **Credit Cards**: Full credit card numbers (PCI-DSS violation)
- **PII (Personally Identifiable Information)**: 
  - Social security numbers
  - Email addresses (in some jurisdictions)
  - Phone numbers
  - Physical addresses
  - Medical information

**What you CAN log:**
- User IDs (non-identifying numbers)
- Masked versions: `credit_card=****1234`, `email=j***@example.com`
- Hashed versions (for correlation, not identification)
- Request IDs, transaction IDs

### Logging Filters

Python's `logging.Filter` class lets you inspect and modify log records before they're output:

```python
class SensitiveDataFilter(logging.Filter):
    def filter(self, record):
        # Modify record.msg before it's logged
        record.msg = self.redact_sensitive_data(record.msg)
        return True  # Always return True to allow the record through
```

### Pattern-Based Redaction

Use regular expressions to find and replace sensitive patterns:

```python
import re

# Match credit card numbers (simplified)
CREDIT_CARD_PATTERN = r'\b\d{4}[- ]?\d{4}[- ]?\d{4}[- ]?\d{4}\b'

# Match API keys (example: 'api_key=sk_live_...')
API_KEY_PATTERN = r'(api[_-]?key[=:]\s*)([^\s&]+)'

def redact(text):
    text = re.sub(CREDIT_CARD_PATTERN, '[REDACTED-CC]', text)
    text = re.sub(API_KEY_PATTERN, r'\1[REDACTED-KEY]', text)
    return text
```

### Structured Logging for Safety

When logging structured data (like JSON), sanitize the dictionary before logging:

```python
def sanitize_dict(data):
    """Remove sensitive keys from a dictionary."""
    sensitive_keys = {'password', 'api_key', 'secret', 'token'}
    return {
        k: '[REDACTED]' if k.lower() in sensitive_keys else v
        for k, v in data.items()
    }

logger.info("User data: %s", sanitize_dict(user_data))
```

## Implementation Guide

### Step 1: Create SensitiveDataFilter

Create a filter that redacts multiple types of sensitive data:

```python
import re
import logging

class SensitiveDataFilter(logging.Filter):
    """Filter that redacts sensitive information from log messages."""
    
    # Patterns for sensitive data
    PATTERNS = {
        'credit_card': (r'\b\d{4}[- ]?\d{4}[- ]?\d{4}[- ]?\d{4}\b', '[REDACTED-CC]'),
        'ssn': (r'\b\d{3}-\d{2}-\d{4}\b', '[REDACTED-SSN]'),
        'email': (r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', '[REDACTED-EMAIL]'),
        'api_key': (r'(api[_-]?key[=:]\s*)([^\s&,}]+)', r'\1[REDACTED-KEY]'),
        'password': (r'(password[=:]\s*)([^\s&,}]+)', r'\1[REDACTED-PWD]'),
    }
    
    def filter(self, record):
        """Redact sensitive data from the log record."""
        record.msg = self.redact(str(record.msg))
        # Also redact from args if they exist
        if record.args:
            record.args = tuple(self.redact(str(arg)) for arg in record.args)
        return True
    
    def redact(self, text):
        """Apply all redaction patterns to text."""
        for pattern, replacement in self.PATTERNS.values():
            text = re.sub(pattern, replacement, text, flags=re.IGNORECASE)
        return text
```

### Step 2: Create Convenience Functions

Make it easy to get loggers with redaction:

```python
def get_secure_logger(name, level=logging.INFO):
    """Get a logger with sensitive data filtering enabled."""
    logger = logging.getLogger(name)
    logger.setLevel(level)
    
    # Add the filter
    sensitive_filter = SensitiveDataFilter()
    logger.addFilter(sensitive_filter)
    
    # Add a console handler if none exists
    if not logger.handlers:
        handler = logging.StreamHandler()
        handler.setFormatter(logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        ))
        logger.addHandler(handler)
    
    return logger
```

### Step 3: Dictionary Sanitization

Create a function to sanitize dictionaries before logging:

```python
def sanitize_dict(data, sensitive_keys=None):
    """
    Sanitize a dictionary by redacting sensitive keys.
    
    Args:
        data: Dictionary to sanitize
        sensitive_keys: Set of keys to redact (case-insensitive)
    
    Returns:
        New dictionary with sensitive values redacted
    """
    if sensitive_keys is None:
        sensitive_keys = {
            'password', 'pwd', 'passwd',
            'api_key', 'apikey', 'api-key',
            'secret', 'token', 'auth',
            'credit_card', 'cc', 'card_number',
            'ssn', 'social_security',
        }
    
    # Convert to lowercase for comparison
    sensitive_keys_lower = {k.lower() for k in sensitive_keys}
    
    sanitized = {}
    for key, value in data.items():
        if key.lower() in sensitive_keys_lower:
            sanitized[key] = '[REDACTED]'
        elif isinstance(value, dict):
            # Recursively sanitize nested dicts
            sanitized[key] = sanitize_dict(value, sensitive_keys)
        else:
            sanitized[key] = value
    
    return sanitized
```

### Step 4: Partial Masking

Sometimes you want to show partial information (like last 4 digits of a credit card):

```python
def mask_credit_card(card_number):
    """
    Mask all but the last 4 digits of a credit card.
    
    Args:
        card_number: Credit card number as string
    
    Returns:
        Masked credit card like '****1234'
    """
    # Remove spaces and dashes
    digits = ''.join(c for c in str(card_number) if c.isdigit())
    
    if len(digits) < 4:
        return '[INVALID-CC]'
    
    return '****' + digits[-4:]


def mask_email(email):
    """
    Mask email address but preserve domain.
    
    Args:
        email: Email address as string
    
    Returns:
        Masked email like 'j***@example.com'
    """
    if '@' not in email:
        return '[INVALID-EMAIL]'
    
    local, domain = email.split('@', 1)
    
    if len(local) <= 1:
        masked_local = '*'
    else:
        masked_local = local[0] + '***'
    
    return f"{masked_local}@{domain}"
```

## Real-World Example: User Authentication

Here's how to safely log user authentication attempts:

```python
def log_login_attempt(logger, user_data, success):
    """
    Safely log a login attempt.
    
    Args:
        logger: Logger instance (should have SensitiveDataFilter)
        user_data: Dict containing user information
        success: Whether login was successful
    """
    # Sanitize the user data
    safe_data = sanitize_dict(user_data)
    
    # Mask email if present
    if 'email' in safe_data:
        safe_data['email'] = mask_email(safe_data['email'])
    
    status = "successful" if success else "failed"
    logger.info(f"Login attempt {status}: {safe_data}")


# Example usage:
logger = get_secure_logger('auth')

user_data = {
    'username': 'john_doe',
    'email': 'john.doe@example.com',
    'password': 'super_secret_123',  # This will be redacted
    'api_key': 'sk_live_abc123xyz',  # This will be redacted
}

log_login_attempt(logger, user_data, success=True)
# Output: Login attempt successful: {'username': 'john_doe', 'email': 'j***@example.com', 
#          'password': '[REDACTED]', 'api_key': '[REDACTED]'}
```

## Testing Your Implementation

Your tests should verify:

1. **Pattern redaction works**: Credit cards, SSNs, emails are redacted
2. **Dictionary sanitization works**: Sensitive keys are replaced with '[REDACTED]'
3. **Nested dictionaries work**: Recursive sanitization of nested data
4. **Masking preserves partial info**: Last 4 digits of CC, first letter of email
5. **Logger integration works**: SensitiveDataFilter actually filters logs
6. **Args are redacted**: Both message and args are sanitized

## Best Practices

### DO:
- ✅ Use filters on all loggers that might receive user data
- ✅ Test your redaction patterns with real examples
- ✅ Sanitize data structures before logging them
- ✅ Use partial masking when you need to correlate records
- ✅ Document what data is safe to log in your team's guidelines
- ✅ Review logs regularly to catch any leaks

### DON'T:
- ❌ Log raw request/response bodies without inspection
- ❌ Log authentication headers (Authorization, Cookie, etc.)
- ❌ Trust that developers will remember to sanitize data
- ❌ Use reversible "encryption" for sensitive data in logs
- ❌ Log database connection strings with passwords
- ❌ Keep debug logs with sensitive data in production

## Exercise

Run the tests to see what functions you need to implement:

```bash
pytest tests/part2_logging/test_lesson_2_4.py -v
```

You'll see 20 failing tests. Your job is to implement:

1. `SensitiveDataFilter` class with pattern-based redaction
2. `get_secure_logger()` function
3. `sanitize_dict()` function with recursive support
4. `mask_credit_card()` function
5. `mask_email()` function

Once all tests pass, verify your coverage:

```bash
pytest tests/part2_logging/ --cov=src.logger --cov-report=term-missing
```

You should have 100% coverage on `src/logger.py`.

Finally, check code quality:

```bash
pylint src/logger.py
```

Aim for 10.00/10!

## Key Takeaways

1. **Logs are permanent**: They outlive code and are seen by many people
2. **Filters are your friend**: Automate redaction so humans don't have to remember
3. **Test redaction**: Don't assume patterns work - verify them
4. **Sanitize early**: Clean data before it reaches the logger
5. **Compliance matters**: GDPR, PCI-DSS, HIPAA all have logging requirements
6. **Partial data can help**: Masked data aids debugging without exposing secrets

## What's Next?

You've now completed Part 2: Logging! You've learned:
- Basic logging setup and configuration
- Custom handlers and formatters
- Contextual logging with adapters
- Secure logging and sensitive data protection

Next, we'll move to **Part 3: REPL Development**, where you'll build an interactive command-line interface for your applications.

---

**Time to implement:** ~45 minutes
**Difficulty:** ⭐⭐⭐☆☆
**Key Skill:** Security-conscious development - protecting user data in all contexts
