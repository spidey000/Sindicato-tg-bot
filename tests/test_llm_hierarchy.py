
import pytest
from unittest.mock import MagicMock, patch
from src.integrations.openrouter_client import OpenRouterClient
from src import config

@pytest.fixture
def client():
    return OpenRouterClient()

def test_draft_hierarchy_primary_success(client):
    """Test that DRAFT task uses primary draft model on first attempt."""
    with patch.object(client, '_make_request') as mock_request:
        mock_request.return_value = '{"draft": "content"}'
        
        response = client.completion(messages=[], task_type="DRAFT")
        
        # Should call _make_request with PRIMARY_DRAFT_MODEL
        mock_request.assert_called_with([], config.PRIMARY_DRAFT_MODEL, None)
        assert response == '{"draft": "content"}'

def test_draft_hierarchy_fallback_on_primary_failure(client):
    """Test that DRAFT task falls back to fallback draft model if primary fails."""
    with patch.object(client, '_make_request') as mock_request:
        # First call fails, second call succeeds
        mock_request.side_effect = [Exception("Primary Failed"), '{"draft": "fallback content"}']
        
        response = client.completion(messages=[], task_type="DRAFT")
        
        # Verify both calls
        assert mock_request.call_count == 2
        calls = mock_request.call_args_list
        assert calls[0].args == ([], config.PRIMARY_DRAFT_MODEL, None)
        assert calls[1].args == ([], config.FALLBACK_DRAFT_MODEL, None)
        assert response == '{"draft": "fallback content"}'

def test_refinement_uses_configured_primary(client):
    """Test that REFINEMENT task still uses the default MODEL_PRIMARY."""
    with patch.object(client, '_make_request') as mock_request:
        mock_request.return_value = '{"refinement": "content"}'
        
        response = client.completion(messages=[], task_type="REFINEMENT")
        
        # Should call _make_request with MODEL_PRIMARY (deepseek)
        mock_request.assert_called_with([], config.MODEL_PRIMARY, None)
