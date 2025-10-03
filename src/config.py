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
