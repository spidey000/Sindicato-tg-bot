import pytest
import os
import sys

# Add src to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

def test_help_command_exists():
    """
    Verify that help_command is defined in handlers.py and registered in main.py.
    """
    with open("src/handlers.py", "r") as f:
        content = f.read()
    assert "async def help_command" in content
    assert "CENTRO DE AYUDA MARXNAGER" in content

    with open("src/main.py", "r") as f:
        content = f.read()
    assert "help_command" in content
    assert 'CommandHandler("help", help_command)' in content

if __name__ == "__main__":
    pytest.main([__file__])
