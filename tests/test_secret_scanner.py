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
    # Test common variable names with quotes (using 16+ chars as per final regex)
    assert secret_scanner.find_secrets('API_KEY="1234567890abcdef"') == ['1234567890abcdef']
    assert secret_scanner.find_secrets("TOKEN = 'abcdefghij123456'") == ['abcdefghij123456']
    assert secret_scanner.find_secrets("SECRET_PASSWORD='super_secret_password_123'") == ['super_secret_password_123']

def test_find_secrets_none():
    """Test that safe strings or non-literal assignments are not flagged."""
    assert secret_scanner.find_secrets('my_variable = "hello"') == []
    assert secret_scanner.find_secrets('print("API_KEY")') == []
    # Test safe environment variable loading
    assert secret_scanner.find_secrets('BOT_TOKEN = os.getenv("BOT_TOKEN")') == []
    # Test short values (below 16 chars)
    assert secret_scanner.find_secrets('API_KEY="short"') == []

def test_redact_line():
    """Test that secrets are correctly redacted."""
    # Simple replacement
    assert secret_scanner.redact_line('API_KEY="1234567890abcdef"') == 'API_KEY="<REDACTED_SECRET>"'
    
    # Preserving quotes
    assert secret_scanner.redact_line("TOKEN = 'abcdefghij123456'") == "TOKEN = '<REDACTED_SECRET>'"
    
    # Safe line remains unchanged
    safe_line = 'BOT_TOKEN = os.getenv("BOT_TOKEN")'
    assert secret_scanner.redact_line(safe_line) == safe_line

def test_get_tracked_files():
    """Test that it correctly identifies tracked files."""
    files = secret_scanner.get_tracked_files()
    assert 'README.md' in files
    assert '.git/config' not in files
    # Excluded files
    assert 'node_modules/axios/README.md' not in files
    # Scripts/security/secret_scanner.py is excluded in get_tracked_files
    assert 'scripts/security/secret_scanner.py' not in files