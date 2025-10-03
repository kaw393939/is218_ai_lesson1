"""Configuration management using environment variables."""
import os
from typing import List
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
        self.app_name = os.getenv('APP_NAME', 'TinyTools')
        self.app_version = os.getenv('APP_VERSION', '1.0.0')
        self.debug_mode = os.getenv('DEBUG_MODE', 'false').lower() == 'true'
    
    def __repr__(self):
        """Return string representation of configuration."""
        return (f"Config(app_name='{self.app_name}', "
                f"version='{self.app_version}', "
                f"debug={self.debug_mode})")


class TypedConfig:
    """Type-safe configuration with support for multiple data types.
    
    This class extends basic configuration with:
    - Type conversion (int, float, bool, list)
    - Required vs optional values
    - Validation and error handling
    - Type hints for better IDE support
    """
    
    def __init__(self):
        """Initialize type-safe configuration from environment variables.
        
        Raises:
            ValueError: If required configuration values are missing
        """
        # String values (default type)
        self.app_name: str = os.getenv('APP_NAME', 'TinyTools')
        
        # Integer values
        self.max_retries: int = int(os.getenv('MAX_RETRIES', '3'))
        
        # Float values
        self.timeout: float = float(os.getenv('TIMEOUT', '30.0'))
        
        # Boolean values
        self.debug_mode: bool = self._str_to_bool(os.getenv('DEBUG_MODE', 'false'))
        
        # List values
        self.allowed_users: List[str] = self._str_to_list(os.getenv('ALLOWED_USERS', ''))
        
        # Required values (no default)
        api_key = os.getenv('API_KEY')
        if api_key is None:
            raise ValueError("API_KEY is required")
        self.api_key: str = api_key
    
    @staticmethod
    def _str_to_bool(value: str) -> bool:
        """Convert string to boolean.
        
        Args:
            value: String value to convert
            
        Returns:
            True if value is 'true', '1', 'yes' (case-insensitive)
            False otherwise
        """
        return value.lower() in ('true', '1', 'yes')
    
    @staticmethod
    def _str_to_list(value: str) -> List[str]:
        """Convert comma-separated string to list.
        
        Args:
            value: Comma-separated string
            
        Returns:
            List of trimmed strings, empty list if value is empty
        """
        if not value:
            return []
        return [item.strip() for item in value.split(',') if item.strip()]
    
    def __repr__(self):
        """Return string representation of configuration."""
        return (f"TypedConfig(app_name='{self.app_name}', "
                f"debug={self.debug_mode})")


class ValidatedConfig:
    """Configuration with validation to ensure values are safe.
    
    This class extends type-safe configuration with:
    - Range validation for numeric values
    - Format validation for strings
    - Non-empty validation for required fields
    - Helpful error messages when validation fails
    """
    
    def __init__(self):
        """Initialize validated configuration from environment variables.
        
        Raises:
            ValueError: If any configuration value fails validation
        """
        # Load and validate app_name
        self.app_name: str = os.getenv('APP_NAME', 'TinyTools')
        self._validate_non_empty(self.app_name, 'APP_NAME')
        
        # Load and validate max_retries
        self.max_retries: int = int(os.getenv('MAX_RETRIES', '3'))
        self._validate_range(self.max_retries, 1, 10, 'MAX_RETRIES')
        
        # Load and validate timeout
        self.timeout: float = float(os.getenv('TIMEOUT', '30.0'))
        self._validate_positive(self.timeout, 'TIMEOUT')
        
        # Load and validate allowed_users
        self.allowed_users: List[str] = TypedConfig._str_to_list(
            os.getenv('ALLOWED_USERS', '')
        )
        if not self.allowed_users:
            raise ValueError("ALLOWED_USERS cannot be empty")
        
        # Load and validate API key
        api_key = os.getenv('API_KEY')
        if api_key is None:
            raise ValueError("API_KEY is required")
        if not api_key.startswith('sk-'):
            raise ValueError("API_KEY must start with 'sk-'")
        if len(api_key) < 10:
            raise ValueError("API_KEY must be at least 10 characters in length")
        self.api_key: str = api_key
    
    @staticmethod
    def _validate_range(value: int, min_val: int, max_val: int, name: str) -> None:
        """Validate that a value is within a specified range.
        
        Args:
            value: The value to validate
            min_val: Minimum allowed value (inclusive)
            max_val: Maximum allowed value (inclusive)
            name: Name of the configuration variable (for error message)
            
        Raises:
            ValueError: If value is outside the range
        """
        if not (min_val <= value <= max_val):
            raise ValueError(
                f"{name} must be between {min_val} and {max_val}, got {value}"
            )
    
    @staticmethod
    def _validate_positive(value: float, name: str) -> None:
        """Validate that a value is positive (> 0).
        
        Args:
            value: The value to validate
            name: Name of the configuration variable (for error message)
            
        Raises:
            ValueError: If value is not positive
        """
        if value <= 0:
            raise ValueError(f"{name} must be positive, got {value}")
    
    @staticmethod
    def _validate_non_empty(value: str, name: str) -> None:
        """Validate that a string is not empty or whitespace-only.
        
        Args:
            value: The string to validate
            name: Name of the configuration variable (for error message)
            
        Raises:
            ValueError: If value is empty or whitespace-only
        """
        if not value or not value.strip():
            raise ValueError(f"{name} cannot be empty")
    
    def validate(self) -> None:
        """Run all validations on current configuration.
        
        This method can be called to re-validate configuration after changes.
        It's also useful for testing that all validation rules are working.
        """
        self._validate_non_empty(self.app_name, 'APP_NAME')
        self._validate_range(self.max_retries, 1, 10, 'MAX_RETRIES')
        self._validate_positive(self.timeout, 'TIMEOUT')
        if not self.allowed_users:
            raise ValueError("ALLOWED_USERS cannot be empty")
        if not self.api_key.startswith('sk-'):
            raise ValueError("API_KEY must start with 'sk-'")
        if len(self.api_key) < 10:
            raise ValueError("API_KEY must be at least 10 characters in length")
    
    def __repr__(self):
        """Return string representation of configuration."""
        return (f"ValidatedConfig(app_name='{self.app_name}', "
                f"max_retries={self.max_retries}, "
                f"timeout={self.timeout})")
