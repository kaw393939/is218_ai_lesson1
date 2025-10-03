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
        self.app_name = os.getenv('APP_NAME', 'TinyTools')
        self.app_version = os.getenv('APP_VERSION', '1.0.0')
        self.debug_mode = os.getenv('DEBUG_MODE', 'false').lower() == 'true'
    
    def __repr__(self):
        """Return string representation of configuration."""
        return (f"Config(app_name='{self.app_name}', "
                f"version='{self.app_version}', "
                f"debug={self.debug_mode})")
