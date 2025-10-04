# Lesson 3.1: Building Your First REPL - Calculator Foundation

## Story: The Command Line Revolution

Maria's team built an amazing Python library, but nobody used it. Why? Because running it required writing Python scripts, importing modules, calling functions... it was too much friction.

Then she added a REPL (Read-Eval-Print Loop) - a simple command-line interface where users could type commands and get instant results. Usage increased 500% in the first week.

"People don't want to write code to use your tool," she realized. "They want to TYPE commands and SEE results. Make it conversational, make it instant, make it feel like a dialogue."

**The lesson:** REPLs lower the barrier to entry. They make your code accessible to non-programmers and make debugging faster for everyone.

## Learning Objectives

By the end of this lesson, you will be able to:

1. Understand what a REPL is and why it's useful
2. Build a basic command loop that reads user input
3. Parse user commands into operations and arguments
4. Implement a calculator with basic operations (add, subtract, multiply, divide)
5. Handle errors gracefully with user-friendly messages
6. Exit cleanly with proper cleanup

## Concepts

### What is a REPL?

REPL stands for **Read-Eval-Print Loop**:
- **Read**: Get input from the user
- **Eval**: Parse and execute the command
- **Print**: Show the result
- **Loop**: Repeat until the user quits

**Examples of REPLs you use:**
- Python interpreter (`python` command)
- Node.js console (`node` command)
- SQL shells (`psql`, `mysql`)
- Bash/Zsh terminal

### The Basic REPL Pattern

```python
def repl():
    """Basic REPL pattern."""
    print("Welcome! Type 'exit' to quit.")
    
    while True:
        # Read
        user_input = input("> ")
        
        # Check for exit
        if user_input.lower() == 'exit':
            break
        
        # Eval
        result = process_command(user_input)
        
        # Print
        print(result)
    
    print("Goodbye!")
```

### Command Parsing

Commands typically follow a pattern:
```
command arg1 arg2 arg3
```

For a calculator:
```
add 5 3        # Result: 8
multiply 4 7   # Result: 28
divide 10 2    # Result: 5.0
```

**Parsing strategy:**
```python
parts = user_input.strip().split()
command = parts[0]
args = parts[1:]
```

### Error Handling in REPLs

REPLs should NEVER crash. They should catch errors and show helpful messages:

```python
try:
    result = execute_command(command, args)
    print(f"Result: {result}")
except ValueError as e:
    print(f"Error: {e}")
except ZeroDivisionError:
    print("Error: Cannot divide by zero")
except Exception as e:
    print(f"Unexpected error: {e}")
```

## Implementation Guide

### Step 1: Create the REPL Structure

Create `src/repl.py` with the basic REPL loop:

```python
"""REPL (Read-Eval-Print Loop) for calculator application."""


class CalculatorREPL:
    """Interactive calculator REPL."""
    
    def __init__(self):
        """Initialize the calculator REPL."""
        self.running = False
    
    def start(self):
        """Start the REPL."""
        self.running = True
        print("Calculator REPL")
        print("Available commands: add, subtract, multiply, divide, exit")
        print()
        
        while self.running:
            try:
                user_input = input("> ")
                self.process_command(user_input)
            except KeyboardInterrupt:
                # Handle Ctrl+C gracefully
                print("\nUse 'exit' to quit")
            except EOFError:
                # Handle Ctrl+D gracefully
                print("\nGoodbye!")
                break
    
    def process_command(self, user_input: str):
        """Process a user command.
        
        Args:
            user_input: Raw input from user
        """
        # Strip whitespace and split into parts
        parts = user_input.strip().split()
        
        if not parts:
            return
        
        command = parts[0].lower()
        args = parts[1:]
        
        # Handle exit
        if command == 'exit':
            print("Goodbye!")
            self.running = False
            return
        
        # Execute command
        try:
            result = self.execute_command(command, args)
            print(f"Result: {result}")
        except ValueError as e:
            print(f"Error: {e}")
        except ZeroDivisionError:
            print("Error: Cannot divide by zero")
        except Exception as e:
            print(f"Error: {e}")
    
    def execute_command(self, command: str, args: list) -> float:
        """Execute a calculator command.
        
        Args:
            command: Command name (add, subtract, multiply, divide)
            args: List of string arguments
        
        Returns:
            Result of the calculation
        
        Raises:
            ValueError: If command is invalid or args are wrong
        """
        # Validate we have exactly 2 arguments
        if len(args) != 2:
            raise ValueError(f"Command '{command}' requires exactly 2 numbers")
        
        # Convert arguments to numbers
        try:
            num1 = float(args[0])
            num2 = float(args[1])
        except ValueError:
            raise ValueError(f"Invalid numbers: {args}")
        
        # Execute the operation
        if command == 'add':
            return num1 + num2
        elif command == 'subtract':
            return num1 - num2
        elif command == 'multiply':
            return num1 * num2
        elif command == 'divide':
            if num2 == 0:
                raise ZeroDivisionError()
            return num1 / num2
        else:
            raise ValueError(f"Unknown command: {command}")


def main():
    """Entry point for the REPL."""
    repl = CalculatorREPL()
    repl.start()


if __name__ == '__main__':
    main()
```

### Step 2: Make it Runnable

You can run your REPL:

```bash
python src/repl.py
```

Or create a convenience script.

### Step 3: Test Your REPL

Try these commands:
```
> add 5 3
Result: 8.0

> multiply 4 7
Result: 28.0

> divide 10 2
Result: 5.0

> divide 10 0
Error: Cannot divide by zero

> subtract 100 42
Result: 58.0

> exit
Goodbye!
```

## Testing Your Implementation

Run the tests to see what you need to implement:

```bash
pytest tests/part3_repl/test_lesson_3_1.py -v
```

You'll see 20 failing tests. Your job is to implement `CalculatorREPL` in `src/repl.py`.

Once all tests pass, verify your coverage:

```bash
pytest tests/part3_repl/ --cov=src.repl --cov-report=term-missing
```

You should have 100% coverage on `src/repl.py`.

Finally, check code quality:

```bash
pylint src/repl.py
```

Aim for 10.00/10!

## Real-World Example: Interactive Session

Here's what a real session looks like:

```
$ python src/repl.py
Calculator REPL
Available commands: add, subtract, multiply, divide, exit

> add 15 27
Result: 42.0

> multiply 6 7
Result: 42.0

> divide 84 2
Result: 42.0

> subtract 50 8
Result: 42.0

> add 1 2 3
Error: Command 'add' requires exactly 2 numbers

> unknown 5 5
Error: Unknown command: unknown

> exit
Goodbye!
```

## Best Practices

### DO:
- ✅ Show a clear welcome message with available commands
- ✅ Use a recognizable prompt (like `>`)
- ✅ Handle Ctrl+C and Ctrl+D gracefully
- ✅ Give helpful error messages
- ✅ Never let the REPL crash - catch all exceptions
- ✅ Make exit obvious and easy

### DON'T:
- ❌ Crash on bad input
- ❌ Show Python tracebacks to users
- ❌ Require exact casing (accept 'ADD', 'add', 'Add')
- ❌ Exit without saying goodbye
- ❌ Use cryptic error messages
- ❌ Ignore Ctrl+C

## Common Pitfalls

### Pitfall 1: Not Trimming Input
```python
# BAD: Won't handle "  add  5  3  "
command = input().split()[0]

# GOOD: Strip first, then split
command = input().strip().split()[0]
```

### Pitfall 2: Crashing on Empty Input
```python
# BAD: Crashes if user just presses Enter
parts = input().split()
command = parts[0]  # IndexError if parts is empty

# GOOD: Check if empty
parts = input().strip().split()
if not parts:
    return
command = parts[0]
```

### Pitfall 3: Not Handling Keyboard Interrupts
```python
# BAD: Ugly traceback when user presses Ctrl+C
while True:
    process_input(input("> "))

# GOOD: Catch and handle gracefully
while True:
    try:
        process_input(input("> "))
    except KeyboardInterrupt:
        print("\nUse 'exit' to quit")
```

## Key Takeaways

1. **REPLs make code accessible** - Lower the barrier to entry
2. **The Read-Eval-Print Loop pattern** is simple but powerful
3. **Command parsing** is just split and validate
4. **Error handling is critical** - Never crash, always help
5. **User experience matters** - Clear messages, graceful exits
6. **REPLs are great for testing** - Quick experimentation

## What's Next?

In Lesson 3.2, we'll integrate our configuration system from Part 1, allowing users to customize the calculator's behavior through environment variables.

In Lesson 3.3, we'll add logging from Part 2 to track all calculations and debug issues.

In Lesson 3.4, we'll add advanced features like command history, command shortcuts, and a help system.

---

**Time to implement:** ~45 minutes  
**Difficulty:** ⭐⭐☆☆☆  
**Key Skill:** Building user-friendly command-line interfaces
