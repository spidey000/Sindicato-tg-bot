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

def test_redact_line():
    """Test that secrets are correctly redacted."""
    # Simple replacement
    assert secret_scanner.redact_line('API_KEY="12345"') == 'API_KEY="<REDACTED_SECRET>"'
    
    # Preserving quotes
    assert secret_scanner.redact_line("TOKEN = 'abcdef'") == "TOKEN = '<REDACTED_SECRET>'"
    
    # Without quotes (if that's supported/detected) - regex handles it?
    # My regex expected quotes or not.
    assert secret_scanner.redact_line("SECRET=super_secret") == "SECRET=<REDACTED_SECRET>"
    
    # Multiple secrets on one line? (Maybe out of scope but good to know)
    # assert secret_scanner.redact_line('KEY1="a" KEY2="b"') == 'KEY1="<REDACTED_SECRET>" KEY2="<REDACTED_SECRET>"'

def test_get_tracked_files(tmp_path):
    """Test that it correctly identifies tracked files."""
    # This might need to mock subprocess.run for git ls-files
    # For now, let's just test a basic implementation if it's not using git
    # But the spec says "tracked files", so git ls-files is ideal.
    
    # Let's assume we implement a function that calls git ls-files
    # We will mock it in the actual test if needed, or just test it in the repo
    files = secret_scanner.get_tracked_files()
    assert 'README.md' in files
    assert 'scripts/security/secret_scanner.py' in files
    assert '.git/config' not in files