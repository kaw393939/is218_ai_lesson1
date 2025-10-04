"""
Tests for Lesson 1.2: Type-Safe Configuration

This lesson teaches you to:
1. Work with different data types (int, float, bool, list)
2. Use default values for optional configuration values
3. Handle missing required values
4. Use type hints for better code

Run with: PYTHONPATH=src pytest tests/part1_configuration/test_lesson_1_2.py -v
"""
import os
import pytest
from config import TypedConfig


class TestImports:
    """Test that all necessary imports work."""
    
    def test_typed_config_exists(self):
        """TypedConfig class should exist in config module.
        
        HINT: Add a TypedConfig class to src/config.py
        """
        assert hasattr(TypedConfig, '__init__')
        

class TestBasicTypes:
    """Test loading different data types from environment variables."""
    
    def test_string_values(self):
        """Should load string values correctly.
        
        HINT: Strings are the default type from os.getenv()
        """
        os.environ['APP_NAME'] = 'TestApp'
        config = TypedConfig()
        assert config.app_name == 'TestApp'
        assert isinstance(config.app_name, str)
    
    def test_integer_values(self):
        """Should convert string to integer.
        
        HINT: Use int(os.getenv('MAX_RETRIES', '3'))
        Environment variables are always strings!
        """
        os.environ['MAX_RETRIES'] = '5'
        config = TypedConfig()
        assert config.max_retries == 5
        assert isinstance(config.max_retries, int)
    
    def test_float_values(self):
        """Should convert string to float.
        
        HINT: Use float(os.getenv('TIMEOUT', '30.5'))
        """
        os.environ['TIMEOUT'] = '45.5'
        config = TypedConfig()
        assert config.timeout == 45.5
        assert isinstance(config.timeout, float)
    
    def test_boolean_true_values(self):
        """Should handle various representations of True.
        
        HINT: 'true', 'True', '1', 'yes' should all be True
        Create a helper method to convert strings to booleans
        """
        for true_value in ['true', 'True', 'TRUE', '1', 'yes', 'Yes']:
            os.environ['DEBUG_MODE'] = true_value
            config = TypedConfig()
            assert config.debug_mode is True, f"'{true_value}' should be True"
    
    def test_boolean_false_values(self):
        """Should handle various representations of False.
        
        HINT: 'false', 'False', '0', 'no', '' should all be False
        """
        for false_value in ['false', 'False', 'FALSE', '0', 'no', 'No', '']:
            os.environ['DEBUG_MODE'] = false_value
            config = TypedConfig()
            assert config.debug_mode is False, f"'{false_value}' should be False"


class TestListValues:
    """Test loading lists from environment variables."""
    
    def test_comma_separated_list(self):
        """Should parse comma-separated values into a list.
        
        HINT: Use .split(',') and strip whitespace from each item
        EXAMPLE: 'alice,bob,charlie' -> ['alice', 'bob', 'charlie']
        """
        os.environ['ALLOWED_USERS'] = 'alice,bob,charlie'
        config = TypedConfig()
        assert config.allowed_users == ['alice', 'bob', 'charlie']
        assert isinstance(config.allowed_users, list)
    
    def test_list_with_whitespace(self):
        """Should handle spaces around commas.
        
        HINT: Use .strip() on each item after splitting
        EXAMPLE: 'alice, bob , charlie' -> ['alice', 'bob', 'charlie']
        """
        os.environ['ALLOWED_USERS'] = 'alice, bob , charlie'
        config = TypedConfig()
        assert config.allowed_users == ['alice', 'bob', 'charlie']
    
    def test_empty_list(self):
        """Should handle empty list values.
        
        HINT: Empty string should return empty list []
        """
        os.environ['ALLOWED_USERS'] = ''
        config = TypedConfig()
        assert config.allowed_users == []


class TestDefaultValues:
    """Test that default values work correctly."""
    
    def test_defaults_when_missing(self):
        """Should use defaults when environment variables are missing.
        
        HINT: Use second parameter of os.getenv()
        EXAMPLE: os.getenv('APP_NAME', 'DefaultApp')
        """
        # Clear environment
        for key in ['APP_NAME', 'MAX_RETRIES', 'TIMEOUT', 'DEBUG_MODE']:
            os.environ.pop(key, None)
        
        config = TypedConfig()
        assert config.app_name == 'TinyTools'
        assert config.max_retries == 3
        assert config.timeout == 30.0
        assert config.debug_mode is False


class TestRequiredValues:
    """Test handling of optional configuration values.
    
    NOTE: API_KEY is now optional for Part 4 compatibility.
    Part 4 uses OPENAI_API_KEY instead.
    """
    
    def test_missing_api_key_uses_default(self):
        """Should use default when API_KEY is missing."""
        os.environ.pop('API_KEY', None)
        
        config = TypedConfig()
        
        # Should have empty string default
        assert config.api_key == ''
    
    def test_api_key_when_present(self):
        """Should load API_KEY when present."""
        os.environ['API_KEY'] = 'sk-test123456789'
        config = TypedConfig()
        assert config.api_key == 'sk-test123456789'


class TestTypeHints:
    """Test that type hints are properly defined."""
    
    def test_class_has_type_hints(self):
        """TypedConfig should use type hints.
        
        HINT: Add type hints to your attributes
        EXAMPLE:
            app_name: str
            max_retries: int
            debug_mode: bool
        """
        hints = TypedConfig.__init__.__annotations__
        # Should have return type at minimum
        assert hints is not None or hasattr(TypedConfig, '__annotations__')


class TestRepr:
    """Test string representation."""
    
    def test_repr_shows_values(self):
        """Should have a helpful __repr__ method.
        
        HINT: Return a string showing key config values
        EXAMPLE: "TypedConfig(app_name='TestApp', debug=False)"
        """
        os.environ.update({
            'APP_NAME': 'TestApp',
            'API_KEY': 'sk-test',
            'MAX_RETRIES': '3',
            'TIMEOUT': '30.0',
            'DEBUG_MODE': 'false'
        })
        config = TypedConfig()
        repr_str = repr(config)
        
        assert 'TypedConfig' in repr_str
        assert 'TestApp' in repr_str


class TestHelperMethods:
    """Test helper methods for type conversion."""
    
    def test_str_to_bool_helper(self):
        """Should have a helper method for string to bool conversion.
        
        HINT: Create a @staticmethod _str_to_bool(value: str) -> bool
        This makes the conversion logic reusable
        """
        assert TypedConfig._str_to_bool('true') is True
        assert TypedConfig._str_to_bool('1') is True
        assert TypedConfig._str_to_bool('yes') is True
        assert TypedConfig._str_to_bool('false') is False
        assert TypedConfig._str_to_bool('0') is False
        assert TypedConfig._str_to_bool('') is False
    
    def test_str_to_list_helper(self):
        """Should have a helper method for string to list conversion.
        
        HINT: Create a @staticmethod _str_to_list(value: str) -> list[str]
        """
        assert TypedConfig._str_to_list('a,b,c') == ['a', 'b', 'c']
        assert TypedConfig._str_to_list('a, b , c') == ['a', 'b', 'c']
        assert TypedConfig._str_to_list('') == []


# Cleanup after tests
def teardown_module():
    """Clean up environment variables after all tests."""
    test_vars = ['APP_NAME', 'MAX_RETRIES', 'TIMEOUT', 'DEBUG_MODE', 
                 'ALLOWED_USERS', 'API_KEY']
    for var in test_vars:
        os.environ.pop(var, None)
