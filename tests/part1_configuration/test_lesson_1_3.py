"""
Tests for Lesson 1.3: Configuration Validation

This lesson teaches you to:
1. Validate configuration values (ranges, formats, patterns)
2. Provide helpful error messages
3. Use custom validators
4. Ensure configuration is safe before use

Run with: PYTHONPATH=src pytest tests/part1_configuration/test_lesson_1_3.py -v
"""
import os
import pytest
from config import ValidatedConfig


class TestImports:
    """Test that all necessary imports work."""
    
    def test_validated_config_exists(self):
        """ValidatedConfig class should exist in config module.
        
        HINT: Add a ValidatedConfig class to src/config.py
        """
        assert hasattr(ValidatedConfig, '__init__')


class TestRangeValidation:
    """Test validation of numeric ranges."""
    
    def test_max_retries_within_range(self):
        """Should accept max_retries within valid range (1-10).
        
        HINT: Check if 1 <= max_retries <= 10
        """
        os.environ.update({
            'APP_NAME': 'TestApp',
            'MAX_RETRIES': '5',
            'TIMEOUT': '30.0',
            'ALLOWED_USERS': 'admin,user',
            'API_KEY': 'sk-test123456789'
        })
        config = ValidatedConfig()
        assert config.max_retries == 5
    
    def test_max_retries_too_low(self):
        """Should raise ValueError if max_retries < 1.
        
        HINT: if not (1 <= max_retries <= 10): raise ValueError(...)
        """
        os.environ.update({
            'APP_NAME': 'TestApp',
            'MAX_RETRIES': '0',
            'TIMEOUT': '30.0',
            'ALLOWED_USERS': 'admin,user',
            'API_KEY': 'sk-test123456789'
        })
        
        with pytest.raises(ValueError) as exc_info:
            ValidatedConfig()
        
        assert 'MAX_RETRIES' in str(exc_info.value)
        assert '1' in str(exc_info.value)
    
    def test_max_retries_too_high(self):
        """Should raise ValueError if max_retries > 10.
        
        HINT: Same validation check
        """
        os.environ.update({
            'APP_NAME': 'TestApp',
            'MAX_RETRIES': '11',
            'TIMEOUT': '30.0',
            'ALLOWED_USERS': 'admin,user',
            'API_KEY': 'sk-test123456789'
        })
        
        with pytest.raises(ValueError) as exc_info:
            ValidatedConfig()
        
        assert 'MAX_RETRIES' in str(exc_info.value)
        assert '10' in str(exc_info.value)
    
    def test_timeout_positive(self):
        """Should validate timeout is positive (> 0).
        
        HINT: if timeout <= 0: raise ValueError(...)
        """
        os.environ.update({
            'APP_NAME': 'TestApp',
            'MAX_RETRIES': '3',
            'TIMEOUT': '30.5',
            'ALLOWED_USERS': 'admin,user',
            'API_KEY': 'sk-test123456789'
        })
        config = ValidatedConfig()
        assert config.timeout == 30.5
    
    def test_timeout_negative(self):
        """Should raise ValueError if timeout <= 0."""
        os.environ.update({
            'APP_NAME': 'TestApp',
            'MAX_RETRIES': '3',
            'TIMEOUT': '-5.0',
            'ALLOWED_USERS': 'admin,user',
            'API_KEY': 'sk-test123456789'
        })
        
        with pytest.raises(ValueError) as exc_info:
            ValidatedConfig()
        
        assert 'TIMEOUT' in str(exc_info.value)


class TestStringFormatValidation:
    """Test validation of string formats."""
    
    def test_api_key_valid_format(self):
        """Should accept API keys starting with 'sk-'.
        
        HINT: if not api_key.startswith('sk-'): raise ValueError(...)
        """
        os.environ.update({
            'APP_NAME': 'TestApp',
            'MAX_RETRIES': '3',
            'TIMEOUT': '30.0',
            'ALLOWED_USERS': 'admin,user',
            'API_KEY': 'sk-test123456789'
        })
        config = ValidatedConfig()
        assert config.api_key == 'sk-test123456789'
    
    def test_api_key_invalid_format(self):
        """Should raise ValueError if API key doesn't start with 'sk-'."""
        os.environ.update({
            'APP_NAME': 'TestApp',
            'MAX_RETRIES': '3',
            'TIMEOUT': '30.0',
            'ALLOWED_USERS': 'admin,user',
            'API_KEY': 'invalid-key'
        })
        
        with pytest.raises(ValueError) as exc_info:
            ValidatedConfig()
        
        assert 'API_KEY' in str(exc_info.value)
        assert 'sk-' in str(exc_info.value)
    
    def test_api_key_min_length(self):
        """Should validate API key has minimum length (at least 10 chars).
        
        HINT: if len(api_key) < 10: raise ValueError(...)
        """
        os.environ.update({
            'APP_NAME': 'TestApp',
            'MAX_RETRIES': '3',
            'TIMEOUT': '30.0',
            'ALLOWED_USERS': 'admin,user',
            'API_KEY': 'sk-abc'  # Too short
        })
        
        with pytest.raises(ValueError) as exc_info:
            ValidatedConfig()
        
        assert 'API_KEY' in str(exc_info.value)
        assert 'length' in str(exc_info.value).lower()
    
    def test_app_name_not_empty(self):
        """Should validate app_name is not empty.
        
        HINT: if not app_name or app_name.strip() == '': raise ValueError(...)
        """
        os.environ.update({
            'APP_NAME': '',
            'MAX_RETRIES': '3',
            'TIMEOUT': '30.0',
            'ALLOWED_USERS': 'admin,user',
            'API_KEY': 'sk-test123456789'
        })
        
        with pytest.raises(ValueError) as exc_info:
            ValidatedConfig()
        
        assert 'APP_NAME' in str(exc_info.value)


class TestListValidation:
    """Test validation of list values."""
    
    def test_allowed_users_not_empty(self):
        """Should validate allowed_users list is not empty.
        
        HINT: if not allowed_users: raise ValueError(...)
        """
        os.environ.update({
            'APP_NAME': 'TestApp',
            'MAX_RETRIES': '3',
            'TIMEOUT': '30.0',
            'ALLOWED_USERS': '',
            'API_KEY': 'sk-test123456789'
        })
        
        with pytest.raises(ValueError) as exc_info:
            ValidatedConfig()
        
        assert 'ALLOWED_USERS' in str(exc_info.value)
    
    def test_allowed_users_valid(self):
        """Should accept non-empty allowed_users list."""
        os.environ.update({
            'APP_NAME': 'TestApp',
            'MAX_RETRIES': '3',
            'TIMEOUT': '30.0',
            'ALLOWED_USERS': 'admin,user,guest',
            'API_KEY': 'sk-test123456789'
        })
        config = ValidatedConfig()
        assert config.allowed_users == ['admin', 'user', 'guest']


class TestValidationHelpers:
    """Test helper methods for validation."""
    
    def test_validate_range_helper(self):
        """Should have a helper method for range validation.
        
        HINT: Create @staticmethod _validate_range(value, min_val, max_val, name)
        This makes validation logic reusable
        """
        # Should not raise for valid value
        ValidatedConfig._validate_range(5, 1, 10, 'test_value')
        
        # Should raise for value too low
        with pytest.raises(ValueError) as exc_info:
            ValidatedConfig._validate_range(0, 1, 10, 'test_value')
        assert 'test_value' in str(exc_info.value)
        
        # Should raise for value too high
        with pytest.raises(ValueError) as exc_info:
            ValidatedConfig._validate_range(11, 1, 10, 'test_value')
        assert 'test_value' in str(exc_info.value)
    
    def test_validate_positive_helper(self):
        """Should have a helper method for positive number validation.
        
        HINT: Create @staticmethod _validate_positive(value, name)
        """
        # Should not raise for positive value
        ValidatedConfig._validate_positive(30.5, 'test_value')
        
        # Should raise for zero
        with pytest.raises(ValueError) as exc_info:
            ValidatedConfig._validate_positive(0, 'test_value')
        assert 'test_value' in str(exc_info.value)
        
        # Should raise for negative
        with pytest.raises(ValueError) as exc_info:
            ValidatedConfig._validate_positive(-5, 'test_value')
        assert 'test_value' in str(exc_info.value)
    
    def test_validate_non_empty_helper(self):
        """Should have a helper method for non-empty string validation.
        
        HINT: Create @staticmethod _validate_non_empty(value, name)
        """
        # Should not raise for non-empty string
        ValidatedConfig._validate_non_empty('hello', 'test_value')
        
        # Should raise for empty string
        with pytest.raises(ValueError) as exc_info:
            ValidatedConfig._validate_non_empty('', 'test_value')
        assert 'test_value' in str(exc_info.value)
        
        # Should raise for whitespace-only string
        with pytest.raises(ValueError) as exc_info:
            ValidatedConfig._validate_non_empty('   ', 'test_value')
        assert 'test_value' in str(exc_info.value)


class TestValidateMethod:
    """Test the main validate() method."""
    
    def test_validate_method_exists(self):
        """Should have a validate() method that runs all validations.
        
        HINT: Create a validate() method called after loading all values
        This separates loading from validation
        """
        os.environ.update({
            'APP_NAME': 'TestApp',
            'API_KEY': 'sk-test123456789',
            'MAX_RETRIES': '3',
            'TIMEOUT': '30.0',
            'ALLOWED_USERS': 'admin,user'
        })
        config = ValidatedConfig()
        # Should not raise if called again
        config.validate()
    
    def test_validate_all_at_once(self):
        """Validate method should check all rules.
        
        HINT: Call all validation helpers in the validate() method
        """
        os.environ.update({
            'APP_NAME': 'TestApp',
            'API_KEY': 'sk-test123456789',
            'MAX_RETRIES': '3',
            'TIMEOUT': '30.0',
            'ALLOWED_USERS': 'admin,user'
        })
        config = ValidatedConfig()
        # All validations should pass
        assert config.app_name == 'TestApp'
        assert config.api_key == 'sk-test123456789'
        assert config.max_retries == 3
        assert config.timeout == 30.0
        assert config.allowed_users == ['admin', 'user']


class TestErrorMessages:
    """Test that error messages are helpful."""
    
    def test_error_message_includes_variable_name(self):
        """Error messages should include the variable name.
        
        HINT: f"{name} must be between {min_val} and {max_val}"
        """
        os.environ['MAX_RETRIES'] = '0'
        os.environ['API_KEY'] = 'sk-test'
        
        with pytest.raises(ValueError) as exc_info:
            ValidatedConfig()
        
        error_msg = str(exc_info.value)
        assert 'MAX_RETRIES' in error_msg
    
    def test_error_message_includes_constraint(self):
        """Error messages should explain the constraint.
        
        HINT: Include the valid range or format in the message
        """
        os.environ['MAX_RETRIES'] = '0'
        os.environ['API_KEY'] = 'sk-test'
        
        with pytest.raises(ValueError) as exc_info:
            ValidatedConfig()
        
        error_msg = str(exc_info.value)
        # Should mention the valid range
        assert any(word in error_msg for word in ['between', 'range', '1', '10'])


# Cleanup after tests
def teardown_module():
    """Clean up environment variables after all tests."""
    test_vars = ['APP_NAME', 'MAX_RETRIES', 'TIMEOUT', 'DEBUG_MODE', 
                 'ALLOWED_USERS', 'API_KEY']
    for var in test_vars:
        os.environ.pop(var, None)
