
import pytest
from src import config
from src.integrations.openrouter_client import OpenRouterClient
from unittest.mock import MagicMock, AsyncMock

def test_config_models_constants():
    """Test that new model constants are correctly defined in config.py."""
    assert hasattr(config, 'PRIMARY_DRAFT_MODEL')
    assert hasattr(config, 'FALLBACK_DRAFT_MODEL')
    assert hasattr(config, 'REPAIR_MODEL')
    
    assert config.PRIMARY_DRAFT_MODEL == "openai/gpt-oss-120b:free"
    assert config.FALLBACK_DRAFT_MODEL == "google/gemma-3-27b-it:free"
    assert config.REPAIR_MODEL == "qwen/qwen3-4b:free"

@pytest.mark.asyncio
async def test_completion_interface_accepts_task_type():
    """Test that completion method accepts task_type parameter."""
    client = OpenRouterClient()
    # Mock _make_request as async
    client._make_request = AsyncMock(return_value="Mock Response")
    
    # This should not raise a TypeError
    try:
        await client.completion(messages=[], task_type="DRAFT")
    except TypeError as e:
        pytest.fail(f"completion method does not accept task_type: {e}")
