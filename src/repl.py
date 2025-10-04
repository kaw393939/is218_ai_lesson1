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
        except Exception as e:  # pylint: disable=broad-exception-caught
            # Catch all to prevent REPL from crashing
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
        # Normalize command to lowercase
        command = command.lower()

        # Validate we have exactly 2 arguments
        if len(args) != 2:
            raise ValueError(f"Command '{command}' requires exactly 2 numbers")

        # Convert arguments to numbers
        try:
            num1 = float(args[0])
            num2 = float(args[1])
        except ValueError as exc:
            raise ValueError(f"Invalid numbers: {args}") from exc

        # Execute the operation
        if command == 'add':
            return num1 + num2
        if command == 'subtract':
            return num1 - num2
        if command == 'multiply':
            return num1 * num2
        if command == 'divide':
            if num2 == 0:
                raise ZeroDivisionError()
            return num1 / num2

        raise ValueError(f"Unknown command: {command}")


def main():
    """Entry point for the REPL."""
    repl = CalculatorREPL()
    repl.start()


if __name__ == '__main__':  # pragma: no cover
    main()
