# 🎓 Python Production Engineering - IS218

> **Learn professional Python development through building real applications**

---

## 🎯 What You're Building

This course teaches you **production-grade Python development** by building three progressively complex applications:

1. **📱 Calculator** - Simple math operations (starter project)
2. **🖥️ Calculator REPL** - Interactive command-line interface  
3. **🤖 AI Chat Assistant** - OpenAI-powered chatbot with cost tracking

By the end, you'll have **professional skills** in:
- ✅ Configuration management (keep secrets safe!)
- ✅ Logging and debugging (find bugs fast!)
- ✅ REPL interfaces (build CLI tools!)
- ✅ AI API integration (work with OpenAI!)
- ✅ Test-driven development (write tests first!)

**279 tests | 13 lessons | ~15-20 hours**

---

## 🚀 Quick Start

### Prerequisites

- Python 3.8+ installed
- Basic Python knowledge (variables, functions, classes)
- Terminal/command line comfort
- OpenAI API key (for Part 4) - [Get one here](https://platform.openai.com/api-keys)

### Setup (5 minutes)

\`\`\`bash
# 1. Clone and enter the repository
cd 218-test-complete

# 2. Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\\Scripts\\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Copy environment template
cp .env.example .env

# 5. Verify setup - all tests should pass!
pytest
# ✅ 279 passed in 1.01s
\`\`\`

**✨ You're ready! Now start Lesson 1.1 below.**

---

## 📚 Course Structure

This course uses **Test-Driven Learning (TDL)**:

1. **📖 Read** the lesson - understand concepts
2. **❌ Run tests** - see what needs to be built
3. **💻 Write code** - make tests pass
4. **✅ Verify** - all tests green!
5. **🎯 Commit** - save your progress

### Test-Driven Learning Example

\`\`\`bash
# Step 1: Run tests for lesson 1.1
pytest tests/part1_configuration/test_lesson_1_1.py -v
# ❌ 12 failed - That's expected!

# Step 2: Read lesson and write code
# (work through lessons/part1_configuration/lesson_1_1.md)

# Step 3: Run tests again
pytest tests/part1_configuration/test_lesson_1_1.py -v
# ✅ 12 passed - You did it!

# Step 4: Commit your work
git add src/config.py
git commit -m "Complete lesson 1.1: basic configuration"
\`\`\`

---

## 🗺️ Learning Path

### Part 1: Configuration Management (3 lessons | 47 tests)
> Learn to handle environment variables, secrets, and settings safely

- **Lesson 1.1**: Basic Configuration (12 tests, 30 min)
  - Load settings from \`.env\` files
  - Keep API keys secure
  - Use \`python-dotenv\`
  - 📄 \`lessons/part1_configuration/lesson_1_1.md\`

- **Lesson 1.2**: Type-Safe Configuration (16 tests, 45 min)
  - Convert strings to int, float, bool, list
  - Set default values
  - Use type hints
  - 📄 \`lessons/part1_configuration/lesson_1_2.md\`

- **Lesson 1.3**: Configuration Validation (19 tests, 45 min)
  - Validate ranges and formats
  - Provide helpful error messages
  - Prevent invalid configurations
  - 📄 \`lessons/part1_configuration/lesson_1_3.md\`

**What you build**: \`src/config.py\` with \`Config\`, \`TypedConfig\`, and \`ValidatedConfig\` classes

---

### Part 2: Logging & Debugging (4 lessons | 97 tests)
> Master professional logging for debugging and production monitoring

- **Lesson 2.1**: Basic Logging (20 tests, 45 min)
  - Replace \`print()\` with proper logging
  - Configure log levels (DEBUG, INFO, WARNING, ERROR)
  - Format log messages with timestamps
  - Log exceptions with tracebacks
  - 📄 \`lessons/part2_logging/lesson_2_1.md\`

- **Lesson 2.2**: Advanced Logging (19 tests, 60 min)
  - JSON-formatted structured logging
  - Rotating file handlers (auto-cleanup old logs)
  - Multiple handlers (console + file)
  - Different log levels per handler
  - 📄 \`lessons/part2_logging/lesson_2_2.md\`

- **Lesson 2.3**: Contextual Logging (24 tests, 60 min)
  - Add request IDs to logs
  - Track user actions
  - Context managers for temporary context
  - Correlation across service calls
  - 📄 \`lessons/part2_logging/lesson_2_3.md\`

- **Lesson 2.4**: Security & Sensitive Data (34 tests, 60 min)
  - Redact credit cards, SSNs, emails
  - Filter sensitive data from logs
  - Sanitize dictionaries
  - Mask PII (Personally Identifiable Information)
  - 📄 \`lessons/part2_logging/lesson_2_4.md\`

**What you build**: \`src/logger.py\` with professional logging utilities

---

### Part 3: REPL (Command-Line Interface) (3 lessons | 75 tests)
> Build an interactive calculator that users can actually use

- **Lesson 3.1**: Basic REPL (22 tests, 60 min)
  - Read-Eval-Print Loop pattern
  - Parse user commands
  - Execute calculator operations (add, subtract, multiply, divide)
  - Handle errors gracefully
  - 📄 \`lessons/part3_repl/lesson_3_1.md\`

- **Lesson 3.2**: Configuration & Formatting (28 tests, 60 min)
  - Configurable precision (decimal places)
  - Max value limits
  - Custom welcome messages
  - Help command
  - 📄 \`lessons/part3_repl/lesson_3_2.md\`

- **Lesson 3.3**: REPL Logging (25 tests, 60 min)
  - Log every command
  - Track session IDs
  - Count operations performed
  - Debug mode for troubleshooting
  - 📄 \`lessons/part3_repl/lesson_3_3.md\`

**What you build**: \`src/repl.py\` - A professional calculator REPL

**Try it**:
\`\`\`bash
python src/repl.py

Calculator REPL v1.0

Available commands:
  add <num1> <num2>      - Add two numbers
  subtract <num1> <num2> - Subtract num2 from num1
  multiply <num1> <num2> - Multiply two numbers
  divide <num1> <num2>   - Divide num1 by num2
  help                   - Show this help message
  exit                   - Exit the calculator

> add 5 3
Result: 8.0

> multiply 4 7
Result: 28.0

> exit
Goodbye!
\`\`\`

---

### Part 4: AI Chat with Cost Tracking (3 lessons | 48 tests)
> Integrate with OpenAI API and build a real AI chatbot

- **Lesson 4.1**: OpenAI Integration & Cost Fundamentals (36 tests, 90 min)
  - Connect to OpenAI API
  - Count tokens with tiktoken
  - Calculate exact costs
  - Display cost transparency to users
  - Model pricing (gpt-4o-mini, gpt-4o, o1 series)
  - 📄 \`lessons/part4_chat/lesson_4_1.md\`

- **Lesson 4.2**: Budget Management (12 tests, 60 min)
  - Session budgets (cost per conversation)
  - Daily budgets (cost per user per day)
  - Budget warnings (75%, 90% thresholds)
  - Persist cost tracking to JSON
  - Block requests over budget
  - 📄 \`lessons/part4_chat/lesson_4_2.md\`

- **Lesson 4.3**: Cost Optimization Strategies (reading, 30 min)
  - Choose the right model (60-95% cost savings!)
  - Reduce max_tokens intelligently
  - Implement prompt caching
  - Batch API for 50% savings
  - System prompts best practices
  - 📄 \`lessons/part4_chat/lesson_4_3.md\`

**What you build**: \`src/chat.py\` - An AI chatbot with transparent cost tracking

**Try it** (requires OpenAI API key):
\`\`\`bash
# Set your API key
export OPENAI_API_KEY='sk-proj-...'

# Run the chat
python src/chat.py

AI Chat REPL - Type 'exit' to quit, 'help' for commands

You: Hello!

[Estimated cost: $0.000300]

AI: Hello! How can I assist you today?

[Tokens: 8 in + 9 out = 17 total]
[Cost: $0.000007 | Session: $0.000007]

You: exit

Goodbye! Total cost: $0.000007
\`\`\`

**Real 2024/2025 Pricing**:
- \`gpt-4o-mini\`: $0.15/$0.60 per 1M tokens (default - cheapest!)
- \`gpt-4o\`: $2.50/$10.00 per 1M tokens
- \`o1-mini\`: $1.10/$4.40 per 1M tokens (reasoning)
- \`o1\`: $15.00/$60.00 per 1M tokens (advanced reasoning)
- \`o1-pro\`: $150.00/$600.00 per 1M tokens (1000x more expensive!)

---

## 🧪 Testing

This course is **test-driven**. Every feature has tests.

### Run All Tests
\`\`\`bash
pytest
# ✅ 279 passed in 1.01s
\`\`\`

### Run Tests for One Lesson
\`\`\`bash
pytest tests/part1_configuration/test_lesson_1_1.py -v
\`\`\`

### Run Tests for One Part
\`\`\`bash
pytest tests/part1_configuration/ -v
\`\`\`

### Watch Mode (re-run on file changes)
\`\`\`bash
pytest-watch  # requires: pip install pytest-watch
\`\`\`

### See Test Coverage
\`\`\`bash
pytest --cov=src --cov-report=html
open htmlcov/index.html
\`\`\`

---

## 📖 How to Use This Course

### For Self-Paced Learning

1. **Work sequentially** - Each lesson builds on previous ones
2. **Read first** - Understand concepts before coding
3. **Run tests** - See what needs to be implemented
4. **Code incrementally** - Make one test pass at a time
5. **Commit often** - Save your progress after each lesson
6. **Don't copy/paste** - Type the code yourself to learn

### For Instructors

This course is designed for:
- **Undergraduate CS courses** (junior/senior level)
- **Bootcamps** (intermediate Python)
- **Corporate training** (junior developers)

**Teaching tips**:
- Lessons are 30-90 minutes each
- Can be split into shorter sessions
- Tests provide immediate feedback
- Students can work at their own pace
- Hints in test docstrings help struggling students

---

## 🎯 Learning Outcomes

After completing this course, you will be able to:

### Configuration Management
- ✅ Store secrets securely in \`.env\` files
- ✅ Load environment variables with \`python-dotenv\`
- ✅ Convert strings to proper types (int, float, bool, list)
- ✅ Validate configuration values
- ✅ Provide helpful error messages

### Logging & Debugging
- ✅ Replace print statements with proper logging
- ✅ Use appropriate log levels (DEBUG, INFO, WARNING, ERROR)
- ✅ Format logs for humans and machines (JSON)
- ✅ Add contextual information (request IDs, user IDs)
- ✅ Redact sensitive data from logs
- ✅ Rotate log files automatically

### REPL Development
- ✅ Build interactive command-line interfaces
- ✅ Parse user commands
- ✅ Handle errors gracefully
- ✅ Provide help and documentation
- ✅ Configure behavior via environment variables

### AI API Integration
- ✅ Call OpenAI API with proper authentication
- ✅ Count tokens accurately with tiktoken
- ✅ Calculate exact API costs
- ✅ Implement budget limits and warnings
- ✅ Track costs per user and per session
- ✅ Choose appropriate models for cost/performance tradeoffs

### Professional Development Practices
- ✅ Test-driven development (TDD)
- ✅ Type hints for better code clarity
- ✅ Documentation and docstrings
- ✅ Error handling and validation
- ✅ Git workflow and commits
- ✅ Code organization and modularity

---

## 🛠️ Project Structure

\`\`\`
218-test-complete/
├── src/                    # Your code goes here
│   ├── calculator.py       # Simple calculator (starter)
│   ├── config.py          # Configuration management (Part 1)
│   ├── logger.py          # Logging utilities (Part 2)
│   ├── repl.py            # Calculator REPL (Part 3)
│   └── chat.py            # AI Chat (Part 4)
│
├── tests/                  # Test suite (DO NOT MODIFY)
│   ├── part1_configuration/  # 47 tests
│   ├── part2_logging/        # 97 tests
│   ├── part3_repl/           # 75 tests
│   ├── part4_chat/           # 48 tests
│   └── test_calculator.py    # 12 tests
│
├── lessons/               # Lesson materials
│   ├── part1_configuration/
│   ├── part2_logging/
│   ├── part3_repl/
│   └── part4_chat/
│
├── .env                   # Your secrets (DO NOT COMMIT)
├── .env.example          # Template (SAFE to commit)
├── .gitignore            # Git ignore rules
├── requirements.txt      # Python dependencies
└── README.md            # This file
\`\`\`

---

## 🔑 Environment Variables

Create a \`.env\` file with these variables:

\`\`\`bash
# OpenAI Configuration (Part 4)
# Get your API key from: https://platform.openai.com/api-keys
OPENAI_API_KEY=your-openai-api-key-here

# Chat Configuration
CHAT_MODEL=gpt-4o-mini
CHAT_MAX_TOKENS=500
CHAT_TEMPERATURE=0.7
CHAT_SESSION_BUDGET=0.50
CHAT_DAILY_BUDGET=5.00
CHAT_BUDGET_WARNING=0.75
CHAT_USER_ID=default
CHAT_LOG_LEVEL=INFO
CHAT_LOG_FILE=chat.log
CHAT_COST_LOG_FILE=costs.json

# REPL Configuration (Part 3)
REPL_PRECISION=2
REPL_MAX_VALUE=1000000.0
REPL_WELCOME_MESSAGE=Calculator REPL v1.0
REPL_SHOW_HELP=true
REPL_LOG_LEVEL=INFO
REPL_LOG_FILE=calculator.log
REPL_LOG_TO_CONSOLE=false

# Basic Configuration (Part 1)
APP_NAME=TinyTools
APP_VERSION=1.0.0
DEBUG_MODE=false
MAX_RETRIES=3
TIMEOUT=30.0
ALLOWED_USERS=alice,bob,charlie
\`\`\`

**⚠️ Never commit \`.env\` to git!** Use \`.env.example\` as a template.

---

## 💡 Tips for Success

### For Struggling Students

1. **Read test hints** - Every test has a docstring with hints
2. **Run one test at a time** - Use \`-k\` flag: \`pytest -k test_name\`
3. **Use the debugger** - Add \`breakpoint()\` to pause execution
4. **Check the examples** - Lessons have working code examples
5. **Ask for help** - Instructors and classmates are resources!

### Common Pitfalls

**Problem**: Tests can't find \`src\` modules
\`\`\`bash
# Solution: Activate virtual environment
source .venv/bin/activate
pytest
\`\`\`

**Problem**: Import errors with OpenAI
\`\`\`bash
# Solution: Install dependencies
pip install -r requirements.txt
\`\`\`

**Problem**: OpenAI API errors in Part 4
\`\`\`bash
# Solution: Set your API key in .env
echo "OPENAI_API_KEY=sk-proj-..." > .env
\`\`\`

**Problem**: Can't type just \`pytest\`
\`\`\`bash
# Solution: Activate virtual environment
source .venv/bin/activate
# OR use: python -m pytest
\`\`\`

---

## 🌟 What's Next?

After completing this course, you're ready for:

1. **Build your own CLI tools** - Use the REPL pattern
2. **Integrate other APIs** - Apply the same patterns
3. **Deploy to production** - You understand config, logging, and error handling
4. **Work on real projects** - These are industry-standard practices

---

## �� Need Help?

- **Bug in tests?** Open an issue on GitHub
- **Stuck on a lesson?** Ask your instructor
- **Want to contribute?** Pull requests welcome!

---

## 📜 License

MIT License - feel free to use this for teaching or learning!

---

**Ready to start?** → Open \`lessons/part1_configuration/lesson_1_1.md\` and begin! 🚀
