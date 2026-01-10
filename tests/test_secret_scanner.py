import pytest
import sys
import os

# Add the project root to sys.path to ensure we can import the scripts
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

def test_module_import():
    """Test that the secret_scanner module can be imported."""
    try:
        from scripts.security import secret_scanner
        assert True
    except ImportError as e:
        pytest.fail(f"Could not import secret_scanner: {e}")
