import pytest
import sys
import os

# Add the project root to sys.path to ensure we can import the scripts
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from scripts.security import secret_scanner

def test_module_import():
    """Test that the secret_scanner module can be imported."""
    try:
        from scripts.security import secret_scanner
        assert True
    except ImportError as e:
        pytest.fail(f"Could not import secret_scanner: {e}")

def test_find_secrets_detected():
    """Test that secrets are detected in strings."""
    # Test common variable names
    assert secret_scanner.find_secrets('API_KEY="123456"') == ['123456']
    assert secret_scanner.find_secrets("TOKEN = 'abcdef'") == ['abcdef']
    assert secret_scanner.find_secrets("SECRET_PASSWORD=super_secret") == ['super_secret']

def test_find_secrets_none():
    """Test that safe strings are not flagged."""
    assert secret_scanner.find_secrets('my_variable = "hello"') == []
    assert secret_scanner.find_secrets('print("API_KEY")') == [] # It's just a string, not assignment