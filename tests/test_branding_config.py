import pytest
import importlib
import sys
import os

# Add src to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

def test_config_app_name():
    """
    Verify that APP_NAME or equivalent in config.py is 'Marxnager'.
    """
    import config
    importlib.reload(config)
    
    # We expect an APP_NAME constant or similar
    if hasattr(config, 'APP_NAME'):
        assert config.APP_NAME == 'Marxnager', f"APP_NAME should be 'Marxnager', found {config.APP_NAME}"
    else:
        # If no explicit APP_NAME, we check if there are other strings defining the app name
        # For now, we'll fail if we can't find it, prompting us to add it.
        pytest.fail("APP_NAME constant not found in config.py")

if __name__ == "__main__":
    pytest.main([__file__])
