import pytest
from unittest.mock import MagicMock
import sys
import os

# Add src to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

def test_branding_in_handlers():
    """
    Check if handlers return 'Marxnager' instead of 'Delegado 360'.
    We'll test this by checking if the strings in src/handlers.py have been updated.
    Since we can't easily execute Telegram handlers without complex mocks, 
    we'll read the file and check for the presence of 'Marxnager' in expected places.
    """
    with open("src/handlers.py", "r") as f:
        content = f.read()
    
    assert "Marxnager" in content
    assert "Delegado 360" not in content

def test_branding_in_main_logs():
    """
    Check if main.py initialization logs use 'Marxnager'.
    """
    with open("src/main.py", "r") as f:
        content = f.read()
    
    assert "Marxnager" in content
    assert "Delegado 360" not in content

def test_branding_in_integrations():
    """
    Check if integrations (like OpenRouter or Docs) use 'Marxnager'.
    """
    files_to_check = [
        "src/integrations/openrouter_client.py",
        "src/integrations/docs_client.py"
    ]
    
    for filename in files_to_check:
        if os.path.exists(filename):
            with open(filename, "r") as f:
                content = f.read()
            assert "Marxnager" in content
            assert "Delegado 360" not in content
            assert "Sindicato" not in content or "X-Title" not in content # X-Title should be updated

if __name__ == "__main__":
    pytest.main([__file__])
