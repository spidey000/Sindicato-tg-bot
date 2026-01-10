import os
import importlib
from unittest import mock
import src.config

def test_env_variable_loading():
    """Verify that config loads variables from the actual environment."""
    # We need to reload the module to pick up the new environment mock
    with mock.patch.dict(os.environ, {
        "BOT_TOKEN": "test_token",
        "OPENROUTER_API_KEY": "test_key",
        "AUTHORIZED_USER_IDS": "123,456"
    }):
        # Force reload of config module
        importlib.reload(src.config)
        
        assert src.config.BOT_TOKEN == "test_token"
        assert src.config.OPENROUTER_API_KEY == "test_key"
        assert 123 in src.config.AUTHORIZED_USERS
        assert 456 in src.config.AUTHORIZED_USERS

def test_missing_env_file_graceful():
    """Verify that if .env is missing, os.getenv still works."""
    # load_dotenv() being called in config.py shouldn't break anything if file is missing
    # We just ensure it doesn't raise an exception
    with mock.patch("dotenv.load_dotenv", return_value=False):
        importlib.reload(src.config)
        # Should still load from os.environ
        with mock.patch.dict(os.environ, {"BOT_TOKEN": "from_env"}):
             importlib.reload(src.config)
             assert src.config.BOT_TOKEN == "from_env"
