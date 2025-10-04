# Lesson 1.1: Introduction to Configuration Management

> **Part 1 of 4: Configuration Management** | Lesson 1 of 3

### 🧭 Navigation
🏠 [Course Index](../INDEX.md) | 📖 [README](../../README.md) | ➡️ [Next](lesson_1_2.md)

---

---

### 🧭 Navigation
🏠 [Course Index](../INDEX.md) | 📖 [README](../../README.md) | ➡️ [Next: Lesson 1.2](lesson_1_2.md)

---

## 🎮 Your Mission

You're going to create a `Config` class that loads settings from a `.env` file. By the end, you'll understand why every professional application uses this pattern.

---

## 📖 Part 1: The Story (5 minutes)

### Why This Matters

Imagine you're working at a startup. Your team builds an app that sends emails using SendGrid. Your code looks like this:

```python
def send_email(to, subject, body):
    api_key = "SG.xYz123AbC456..."  # SendGrid API key hardcoded
    # ... send email code
```

Everything works great! You commit and push to GitHub. 

**Two hours later, your company receives a $10,000 bill** because someone found your API key on GitHub and used it to send spam.

**This actually happens.** GitHub even has automated scanning to catch API keys, but often the damage is done before they're detected.

### The Solution

Professional developers use **environment variables** stored in `.env` files:

```python
# .env file (NEVER committed to git)
SENDGRID_API_KEY=SG.xYz123AbC456...

# In your code
api_key = os.getenv('SENDGRID_API_KEY')
```

Now your secrets stay secret!

---

## 💡 Part 2: What You'll Learn (5 minutes)

### Environment Variables

Environment variables are key-value pairs that exist outside your code:

```bash
# Setting an environment variable
export API_KEY="secret123"

# Python can read it
import os
api_key = os.getenv('API_KEY')  # Returns "secret123"
```

### .env Files

Instead of typing `export` for every variable, we use a `.env` file:

```
# .env
APP_NAME=TinyTools Calculator
APP_VERSION=1.0.0
DEBUG_MODE=true
```

The `python-dotenv` library loads these automatically!

### Why This Matters

Every professional application uses this pattern:
- ✅ **Security**: No secrets in code
- ✅ **Flexibility**: Different values per environment (dev/test/prod)
- ✅ **Collaboration**: Each developer has their own .env
- ✅ **Deployment**: Easy to change settings without code changes

---

## 🏗️ Part 3: Build It! (15 minutes)

### Step 1: Run the Tests (They Should Fail!)

```bash
PYTHONPATH=src pytest tests/part1_configuration/test_lesson_1_1.py -v
```

You'll see: ❌ **FAILED** - That's good! Now let's make them pass.

### Step 2: Create .env File

Create a file called `.env` in your project root:

```bash
# .env
APP_NAME=TinyTools Calculator
APP_VERSION=1.0.0
DEBUG_MODE=true
```

### Step 3: Update .gitignore

Add this to `.gitignore` so you never commit secrets:

```
# Environment variables
.env
```

### Step 4: Create .env.example (Safe Template)

Create `.env.example` (this one IS committed):

```bash
# .env.example
APP_NAME=TinyTools Calculator
APP_VERSION=1.0.0
DEBUG_MODE=false
```

### Step 5: Create src/config.py

Now create `src/config.py`:

```python
"""Configuration management using environment variables."""
import os
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
        # TODO: Load app_name from environment
        # HINT: self.app_name = os.getenv('APP_NAME', 'TinyTools')
        
        # TODO: Load app_version from environment
        # HINT: self.app_version = os.getenv('APP_VERSION', '1.0.0')
        
        # TODO: Load debug_mode from environment (as boolean!)
        # HINT: self.debug_mode = os.getenv('DEBUG_MODE', 'false').lower() == 'true'
        pass
    
    def __repr__(self):
        """Return string representation of configuration."""
        return (f"Config(app_name='{self.app_name}', "
                f"version='{self.app_version}', "
                f"debug={self.debug_mode})")
```

**Your job**: Fill in the TODOs!

### Step 6: Run Tests Again

```bash
PYTHONPATH=src pytest tests/part1_configuration/test_lesson_1_1.py -v
```

Keep running tests and fixing issues until all 12 tests pass!

### Step 7: Check Your Work

```bash
# Run tests
PYTHONPATH=src pytest tests/part1_configuration/test_lesson_1_1.py -v

# Check coverage
PYTHONPATH=src coverage run -m pytest tests/part1_configuration/test_lesson_1_1.py
coverage report --include=src/config.py

# Check pylint
pylint --errors-only src/config.py
```

All should be ✅ green!

---

## ✅ Part 4: Verify Understanding (5 minutes)

Before moving on, make sure you can answer:

1. **Why don't we hardcode API keys?**
   - Security risk - they get committed to git and exposed

2. **What's the difference between .env and .env.example?**
   - .env has real secrets (not committed)
   - .env.example is a template (committed)

3. **How do you read an environment variable?**
   - `os.getenv('VARIABLE_NAME', 'default_value')`

4. **Why do we convert DEBUG_MODE to boolean?**
   - Environment variables are always strings
   - We want `True`/`False`, not `"true"`/`"false"`

---

## 🎉 Success Criteria

You're done when:

- ✅ All 12 tests pass
- ✅ You have a `.env` file (not committed)
- ✅ You have a `.env.example` file (committed)
- ✅ `.env` is in your `.gitignore`
- ✅ Your `config.py` loads all three variables
- ✅ Coverage is 100% on config.py
- ✅ Pylint passes

---

## 🚀 Commit Your Work

```bash
git add .gitignore .env.example src/config.py tests/part1_configuration/test_lesson_1_1.py
git commit -m "feature: lesson 1.1 - basic configuration management"
```

**DO NOT** commit `.env`!

---

## 🔍 Troubleshooting

### "ModuleNotFoundError: No module named 'dotenv'"
```bash
pip install python-dotenv
```

### "All tests fail with ImportError"
Make sure you:
1. Created `src/config.py`
2. Created the `Config` class
3. Run with `PYTHONPATH=src`

### "Config has no attribute 'app_name'"
You forgot to set `self.app_name` in `__init__`!

### "debug_mode is 'true' not True"
You need to convert string to boolean:
```python
self.debug_mode = os.getenv('DEBUG_MODE', 'false').lower() == 'true'
```

---

## 📚 Additional Resources

- [Python-dotenv Documentation](https://github.com/theskumar/python-dotenv)
- [The Twelve-Factor App](https://12factor.net/config)
- [OWASP: Secrets Management](https://cheatsheetseries.owasp.org/cheatsheets/Secrets_Management_Cheat_Sheet.html)

---

## 💡 Pro Tips

1. **Never commit .env files** - Add to .gitignore immediately
2. **Always provide defaults** - Makes your code more robust
3. **Document your env vars** - Use .env.example as documentation
4. **Type conversion matters** - Environment variables are always strings
5. **Test your config** - We just did this! 

Good luck! 🎯


````

---

### 🧭 Navigation
🏠 [Course Index](../INDEX.md) | 📖 [README](../../README.md) | ➡️ [Next](lesson_1_2.md)

---

**Lesson Complete!** When all tests pass, continue to [Next Lesson →](lesson_1_2.md)
