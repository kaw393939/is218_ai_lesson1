# 📚 IS218 Course Index - Python Production Engineering

> **Complete navigation for all lessons** | [← Back to README](../README.md)

---

## 🎯 Course Overview

**Total**: 13 lessons | 279 tests | 15-20 hours

This course teaches production-grade Python development through test-driven learning. Each lesson builds on previous ones, culminating in a fully functional AI chatbot with cost tracking.

---

## 📖 How to Navigate

### Course Structure
1. **Read the lesson** - Understand concepts and why they matter
2. **Run the tests** - See what needs to be built (`pytest tests/partX_*/test_lesson_X_X.py -v`)
3. **Write the code** - Make tests pass incrementally
4. **Verify completion** - All tests green = lesson complete!
5. **Commit your work** - Save progress before moving on

### Navigation Tips
- **⬅️ Previous** links go to the lesson before
- **➡️ Next** links go to the lesson after
- **🏠 Index** always brings you back here
- **📖 README** takes you to the main course page

---

## 🗺️ Complete Lesson Map

### Part 1: Configuration Management
**Goal**: Learn to handle secrets, environment variables, and settings safely  
**Duration**: ~2 hours | **Tests**: 47 tests

| # | Lesson | Tests | Time | What You'll Build |
|---|--------|-------|------|-------------------|
| 1.1 | [Introduction to Configuration Management](part1_configuration/lesson_1_1.md) | 12 | 30 min | `Config` class with `.env` file loading |
| 1.2 | [Type-Safe Configuration](part1_configuration/lesson_1_2.md) | 16 | 45 min | `TypedConfig` with int, float, bool, list conversion |
| 1.3 | [Configuration Validation](part1_configuration/lesson_1_3.md) | 19 | 45 min | `ValidatedConfig` with range/format validation |

**Output**: `src/config.py` (234 lines, 3 classes)

---

### Part 2: Logging & Debugging
**Goal**: Master professional logging for debugging and production monitoring  
**Duration**: ~4 hours | **Tests**: 97 tests

| # | Lesson | Tests | Time | What You'll Build |
|---|--------|-------|------|-------------------|
| 2.1 | [Why Logging Matters](part2_logging/lesson_2_1.md) | 20 | 45 min | Basic logging setup, log levels, formatters |
| 2.2 | [Custom Log Handlers](part2_logging/lesson_2_2.md) | 19 | 60 min | JSON formatter, rotating files, multi-handler |
| 2.3 | [Contextual Logging](part2_logging/lesson_2_3.md) | 24 | 60 min | Request IDs, user tracking, context managers |
| 2.4 | [Secure Logging](part2_logging/lesson_2_4.md) | 34 | 60 min | PII redaction, sensitive data filtering |

**Output**: `src/logger.py` (416 lines, multiple utilities)

---

### Part 3: REPL (Interactive CLI)
**Goal**: Build an interactive calculator that users can actually use  
**Duration**: ~3 hours | **Tests**: 75 tests

| # | Lesson | Tests | Time | What You'll Build |
|---|--------|-------|------|-------------------|
| 3.1 | [Building Your First REPL](part3_repl/lesson_3_1.md) | 22 | 60 min | `CalculatorREPL` with command parsing |
| 3.2 | [Configuration & Formatting](part3_repl/lesson_3_2.md) | 28 | 60 min | `CalculatorConfig`, precision, help command |
| 3.3 | [Adding Logging to REPL](part3_repl/lesson_3_3.md) | 25 | 60 min | Session tracking, operation logging |

**Output**: `src/repl.py` (254 lines, working calculator REPL)

**Try it**: `python src/repl.py` 🎮

---

### Part 4: AI Chat with Cost Tracking
**Goal**: Integrate with OpenAI API and build a real AI chatbot with transparent cost tracking  
**Duration**: ~3 hours | **Tests**: 48 tests

| # | Lesson | Tests | Time | What You'll Build |
|---|--------|-------|------|-------------------|
| 4.1 | [OpenAI Integration & Cost Fundamentals](part4_chat/lesson_4_1.md) | 36 | 90 min | `ChatREPL`, API integration, token counting, cost calculation |
| 4.2 | [Session Cost Tracking & Budget Management](part4_chat/lesson_4_2.md) | 12 | 60 min | `CostTracker`, session/daily budgets, warnings |
| 4.3 | [Cost Optimization Strategies](part4_chat/lesson_4_3.md) | 0 | 30 min | Model selection, prompt optimization, caching (reading) |

**Output**: `src/chat.py` (552 lines, AI chatbot with cost tracking)

**Try it**: `python src/chat.py` (requires OpenAI API key) 🤖

---

## 🎯 Learning Outcomes by Part

### After Part 1 - Configuration
- ✅ Load secrets from `.env` files (never commit secrets!)
- ✅ Convert environment strings to proper types
- ✅ Validate configuration values
- ✅ Provide helpful error messages

### After Part 2 - Logging
- ✅ Replace `print()` with professional logging
- ✅ Use appropriate log levels
- ✅ Format logs for humans and machines (JSON)
- ✅ Add contextual information (request IDs, user IDs)
- ✅ Redact sensitive data (credit cards, SSNs, emails)

### After Part 3 - REPL
- ✅ Build interactive command-line interfaces
- ✅ Parse user commands
- ✅ Handle errors gracefully
- ✅ Provide help and documentation
- ✅ Configure behavior via environment variables

### After Part 4 - AI Chat
- ✅ Call OpenAI API with proper authentication
- ✅ Count tokens accurately (using tiktoken)
- ✅ Calculate exact API costs
- ✅ Implement budget limits and warnings
- ✅ Track costs per user and session
- ✅ Choose appropriate models for cost/performance

---

## 🧪 Testing Commands

### Run All Tests
```bash
pytest
# ✅ 279 passed
```

### Run Tests for One Lesson
```bash
pytest tests/part1_configuration/test_lesson_1_1.py -v
```

### Run Tests for One Part
```bash
pytest tests/part1_configuration/ -v    # All Part 1 (47 tests)
pytest tests/part2_logging/ -v          # All Part 2 (97 tests)
pytest tests/part3_repl/ -v             # All Part 3 (75 tests)
pytest tests/part4_chat/ -v             # All Part 4 (48 tests)
```

### Run One Specific Test
```bash
pytest tests/part1_configuration/test_lesson_1_1.py::TestLesson11BasicConfig::test_01_config_class_can_be_imported -v
```

### Watch Mode (auto-rerun on changes)
```bash
pip install pytest-watch
pytest-watch
```

---

## 🔗 Quick Links

### Documentation
- [📖 Main README](../README.md) - Course overview and setup
- [📊 Course Summary](../COURSE_SUMMARY.md) - Complete alignment guide
- [🎉 Completion Report](../COMPLETION_REPORT.md) - Final validation

### Code Files
- [`src/calculator.py`](../src/calculator.py) - Simple calculator (starter)
- [`src/config.py`](../src/config.py) - Configuration classes (Part 1)
- [`src/logger.py`](../src/logger.py) - Logging utilities (Part 2)
- [`src/repl.py`](../src/repl.py) - Calculator REPL (Part 3)
- [`src/chat.py`](../src/chat.py) - AI Chat (Part 4)

### Test Files
- [`tests/part1_configuration/`](../tests/part1_configuration/) - 47 configuration tests
- [`tests/part2_logging/`](../tests/part2_logging/) - 97 logging tests
- [`tests/part3_repl/`](../tests/part3_repl/) - 75 REPL tests
- [`tests/part4_chat/`](../tests/part4_chat/) - 48 chat tests

---

## 💡 Tips for Success

### For All Students
1. **Work sequentially** - Each lesson builds on previous ones
2. **Read before coding** - Understanding concepts helps
3. **Run tests frequently** - Know when you're making progress
4. **One test at a time** - Use `pytest -k test_name` to focus
5. **Commit often** - Save your work after each lesson

### If You're Struggling
1. **Read test hints** - Every test has a helpful docstring
2. **Check examples** - Lessons have working code samples
3. **Use the debugger** - Add `breakpoint()` to pause execution
4. **Ask for help** - Instructors and classmates are resources!
5. **Take breaks** - Sometimes stepping away helps

### If You're Ahead
1. **Explore the code** - Read the full implementations
2. **Try extensions** - Add new features
3. **Help others** - Teaching reinforces learning
4. **Read docs** - Dive deeper into libraries used
5. **Build something new** - Apply patterns to your own project

---

## 📊 Progress Tracking

Track your progress through the course:

### Part 1: Configuration ⏳
- [ ] Lesson 1.1 (12 tests) - Basic Configuration
- [ ] Lesson 1.2 (16 tests) - Type-Safe Configuration
- [ ] Lesson 1.3 (19 tests) - Configuration Validation

### Part 2: Logging ⏳
- [ ] Lesson 2.1 (20 tests) - Basic Logging
- [ ] Lesson 2.2 (19 tests) - Advanced Logging
- [ ] Lesson 2.3 (24 tests) - Contextual Logging
- [ ] Lesson 2.4 (34 tests) - Secure Logging

### Part 3: REPL ⏳
- [ ] Lesson 3.1 (22 tests) - Basic REPL
- [ ] Lesson 3.2 (28 tests) - Configuration & Formatting
- [ ] Lesson 3.3 (25 tests) - REPL Logging

### Part 4: AI Chat ⏳
- [ ] Lesson 4.1 (36 tests) - OpenAI Integration & Costs
- [ ] Lesson 4.2 (12 tests) - Budget Management
- [ ] Lesson 4.3 (0 tests) - Cost Optimization (reading)

**Total Progress**: ____ / 279 tests passing

---

## 🌟 What's Next?

After completing all lessons, you'll have:

1. **Production-Ready Code** - 5 modules, ~2,500 lines
2. **Professional Skills** - Config, logging, CLI, AI integration
3. **Real Applications** - Working calculator REPL and AI chatbot
4. **Portfolio Projects** - Code you can show employers

### Continue Learning
- Build your own CLI tools using the REPL pattern
- Integrate other APIs (Anthropic, Cohere, etc.)
- Deploy your chatbot to production
- Add web interface (Flask/FastAPI)
- Create desktop app (PyQt/Tkinter)

---

## 📞 Need Help?

- **Bug in tests?** Open an issue on GitHub
- **Stuck on a lesson?** Ask your instructor
- **Want to contribute?** Pull requests welcome!
- **Found a typo?** We appreciate corrections!

---

**Ready to start?** → [Begin with Lesson 1.1](part1_configuration/lesson_1_1.md) 🚀
