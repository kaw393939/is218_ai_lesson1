"""
Lesson 1.1: Introduction to Configuration Management - TEST FILE

🎯 YOUR MISSION:
Make all these tests pass by creating a Config class!

📝 WHAT YOU NEED TO DO:
1. Create a file: src/config.py
2. Create a Config class
3. Make it load environment variables from .env file
4. Make these tests pass!

💡 HINTS:
- You'll need to install python-dotenv (it's already in requirements.txt)
- Use load_dotenv() to read .env file
- Use os.getenv('VARIABLE_NAME') to get values
- Remember to create a .env file with your settings!

🏃 HOW TO RUN THESE TESTS:
    PYTHONPATH=src pytest tests/part1_configuration/test_lesson_1_1.py -v

🎓 LEARNING GOALS:
- Understand why we don't hardcode configuration
- Learn how to use .env files
- Practice loading environment variables
- Write your first Config class

📚 HELPFUL DOCS:
- Python-dotenv: https://github.com/theskumar/python-dotenv
- os.getenv(): https://docs.python.org/3/library/os.html#os.getenv
"""

import os
import pytest


class TestLesson11BasicConfig:
    """
    Lesson 1.1: Basic Configuration
    
    These tests guide you through creating a simple Config class
    that loads values from environment variables.
    """
    
    def test_01_config_class_can_be_imported(self):
        """
        TEST 1: Can we import the Config class?
        
        ❌ If this fails, you need to:
           - Create a file called src/config.py
           - Create a class called Config
        
        ✅ When this passes, you have:
           - A valid Python module
           - A Config class that can be imported
        """
        try:
            from config import Config
            assert Config is not None
        except ImportError as e:
            pytest.fail(f"Cannot import Config class. Error: {e}\n"
                       f"HINT: Create src/config.py with a Config class")
    
    def test_02_config_class_can_be_instantiated(self):
        """
        TEST 2: Can we create a Config object?
        
        ❌ If this fails, you need to:
           - Add an __init__ method to your Config class
        
        ✅ When this passes, you have:
           - A Config class with a proper __init__ method
        """
        from config import Config
        try:
            config = Config()
            assert config is not None
        except Exception as e:
            pytest.fail(f"Cannot create Config object. Error: {e}\n"
                       f"HINT: Add __init__(self) method to Config class")
    
    def test_03_config_has_app_name_attribute(self):
        """
        TEST 3: Does Config have an app_name attribute?
        
        ❌ If this fails, you need to:
           - In __init__, add: self.app_name = os.getenv('APP_NAME', 'TinyTools')
        
        ✅ When this passes, you have:
           - A config object with an app_name attribute
        """
        from config import Config
        config = Config()
        assert hasattr(config, 'app_name'), \
            "Config object doesn't have 'app_name' attribute.\n" \
            "HINT: Add self.app_name = os.getenv('APP_NAME', 'TinyTools') in __init__"
    
    def test_04_config_has_app_version_attribute(self):
        """
        TEST 4: Does Config have an app_version attribute?
        
        ❌ If this fails, you need to:
           - In __init__, add: self.app_version = os.getenv('APP_VERSION', '1.0.0')
        
        ✅ When this passes, you have:
           - A config object with version tracking
        """
        from config import Config
        config = Config()
        assert hasattr(config, 'app_version'), \
            "Config object doesn't have 'app_version' attribute.\n" \
            "HINT: Add self.app_version = os.getenv('APP_VERSION', '1.0.0') in __init__"
    
    def test_05_config_has_debug_mode_attribute(self):
        """
        TEST 5: Does Config have a debug_mode attribute?
        
        ❌ If this fails, you need to:
           - In __init__, add: self.debug_mode = os.getenv('DEBUG_MODE', 'false').lower() == 'true'
        
        ✅ When this passes, you have:
           - A debug mode flag (as a boolean, not string!)
        """
        from config import Config
        config = Config()
        assert hasattr(config, 'debug_mode'), \
            "Config object doesn't have 'debug_mode' attribute.\n" \
            "HINT: Add self.debug_mode = os.getenv('DEBUG_MODE', 'false').lower() == 'true'"
    
    def test_06_config_loads_dotenv(self):
        """
        TEST 6: Does Config load from .env file?
        
        ❌ If this fails, you need to:
           1. Import load_dotenv from dotenv
           2. Call load_dotenv() at the top of your config.py file
           3. Create a .env file with APP_NAME=TinyTools Calculator
        
        ✅ When this passes, you have:
           - Successfully loaded .env file
           - Environment variables available in your code
        """
        from config import Config
        # Create a test .env file if needed
        if not os.path.exists('.env'):
            pytest.skip(".env file not found. Create one with APP_NAME=TinyTools Calculator")
        
        config = Config()
        # Check that we're getting a value (not None)
        assert config.app_name is not None, \
            "app_name is None. Make sure load_dotenv() is called!"
    
    def test_07_config_reads_app_name_from_environment(self):
        """
        TEST 7: Does Config read APP_NAME from .env?
        
        ❌ If this fails:
           - Make sure your .env file has: APP_NAME=TinyTools Calculator
           - Make sure load_dotenv() is called before reading variables
        
        ✅ When this passes, you have:
           - Proper environment variable loading
           - Your app name configured externally
        """
        from config import Config
        
        # Temporarily set the environment variable for testing
        original_value = os.environ.get('APP_NAME')
        os.environ['APP_NAME'] = 'Test App Name'
        
        try:
            config = Config()
            assert config.app_name == 'Test App Name', \
                f"Expected 'Test App Name', got '{config.app_name}'\n" \
                f"HINT: Make sure you're using os.getenv('APP_NAME')"
        finally:
            # Restore original value
            if original_value:
                os.environ['APP_NAME'] = original_value
            else:
                os.environ.pop('APP_NAME', None)
    
    def test_08_config_uses_default_values(self):
        """
        TEST 8: Does Config use defaults when env vars are missing?
        
        ❌ If this fails:
           - Make sure os.getenv() has default values
           - Example: os.getenv('APP_NAME', 'TinyTools')
        
        ✅ When this passes, you have:
           - Fallback values when .env is missing
           - Robust configuration
        """
        from config import Config
        
        # Remove environment variables temporarily
        backup = {}
        for key in ['APP_NAME', 'APP_VERSION', 'DEBUG_MODE']:
            backup[key] = os.environ.pop(key, None)
        
        try:
            config = Config()
            # Should use defaults, not crash
            assert config.app_name is not None, "Should have default app_name"
            assert config.app_version is not None, "Should have default app_version"
            assert isinstance(config.debug_mode, bool), "debug_mode should be boolean"
        finally:
            # Restore environment
            for key, value in backup.items():
                if value:
                    os.environ[key] = value
    
    def test_09_config_debug_mode_is_boolean(self):
        """
        TEST 9: Is debug_mode a boolean (not a string)?
        
        ❌ If this fails:
           - Make sure you convert the string to boolean
           - Use: .lower() == 'true'
        
        ✅ When this passes, you have:
           - Type-safe configuration
           - Proper boolean handling
        """
        from config import Config
        config = Config()
        assert isinstance(config.debug_mode, bool), \
            f"debug_mode should be bool, got {type(config.debug_mode)}\n" \
            f"HINT: Use os.getenv('DEBUG_MODE', 'false').lower() == 'true'"
    
    def test_10_config_has_docstring(self):
        """
        TEST 10: Is your Config class documented?
        
        ❌ If this fails:
           - Add a docstring to your Config class
           - Example: '''Configuration management for the application.'''
        
        ✅ When this passes, you have:
           - Professional documentation
           - Code that others can understand
        """
        from config import Config
        assert Config.__doc__ is not None, \
            "Config class needs a docstring!\n" \
            "HINT: Add '''Configuration management.''' under class definition"
        assert len(Config.__doc__.strip()) > 10, \
            "Config docstring is too short. Explain what the class does!"


class TestLesson11ConfigUsage:
    """
    These tests verify that Config works correctly in practice.
    """
    
    def test_11_config_can_be_printed(self):
        """
        TEST 11: Can we print the config?
        
        This test checks if __repr__ or __str__ is implemented.
        Not required for lesson 1.1, but nice to have!
        """
        from config import Config
        config = Config()
        # Should not crash
        config_str = str(config)
        assert len(config_str) > 0, "Config should have string representation"
    
    def test_12_multiple_config_instances_work(self):
        """
        TEST 12: Can we create multiple Config objects?
        
        ❌ If this fails:
           - Make sure __init__ doesn't have any global side effects
        
        ✅ When this passes, you have:
           - Reusable Config class
           - Clean initialization
        """
        from config import Config
        config1 = Config()
        config2 = Config()
        
        # Both should work
        assert config1.app_name is not None
        assert config2.app_name is not None
        
        # They should be independent objects
        assert config1 is not config2


# 🎉 CONGRATULATIONS!
# If all tests pass, you've completed Lesson 1.1!
# 
# ✅ You now know:
# - How to create a Config class
# - How to load .env files
# - How to read environment variables
# - How to use default values
# - How to convert string values to booleans
#
# 🚀 NEXT STEPS:
# 1. Run coverage: PYTHONPATH=src coverage run -m pytest tests/part1_configuration/test_lesson_1_1.py
# 2. Check coverage: coverage report --include=src/config.py
# 3. Run pylint: pylint --errors-only src/config.py
# 4. Commit your work: git add src/config.py tests/part1_configuration/test_lesson_1_1.py
# 5. Move to Lesson 1.2!
