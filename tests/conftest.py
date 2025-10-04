"""Pytest configuration for test suite."""
import sys
from pathlib import Path

# Add src directory to Python path so tests can import modules
src_path = Path(__file__).parent.parent / 'src'
sys.path.insert(0, str(src_path))
