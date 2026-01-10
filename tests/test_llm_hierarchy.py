
import pytest
from unittest.mock import MagicMock, patch, ANY, AsyncMock
from src.integrations.openrouter_client import OpenRouterClient
from src import config

@pytest.fixture
def client():
    return OpenRouterClient()

@pytest.mark.asyncio
async def test_draft_hierarchy_primary_success(client):
    """Test that DRAFT task uses primary draft model on first attempt."""
    with patch.object(client, '_make_request', new_callable=AsyncMock) as mock_request:
        mock_request.return_value = '{"draft": "content"}'
        
        response = await client.completion(messages=[], task_type="DRAFT")
        
        # Should call _make_request with PRIMARY_DRAFT_MODEL
        mock_request.assert_called_with([], config.PRIMARY_DRAFT_MODEL, None)
        assert response == '{"draft": "content"}'

@pytest.mark.asyncio
async def test_draft_hierarchy_fallback_on_primary_failure(client):
    """Test that DRAFT task falls back to fallback draft model if primary fails."""
    with patch.object(client, '_make_request', new_callable=AsyncMock) as mock_request:
        # First call fails, second call succeeds
        mock_request.side_effect = [Exception("Primary Failed"), '{"draft": "fallback content"}']
        
        response = await client.completion(messages=[], task_type="DRAFT")
        
        # Verify both calls
        assert mock_request.call_count == 2
        calls = mock_request.call_args_list
        assert calls[0].args == ([], config.PRIMARY_DRAFT_MODEL, None)
        assert calls[1].args == ([], config.FALLBACK_DRAFT_MODEL, None)
        assert response == '{"draft": "fallback content"}'

@pytest.mark.asyncio
async def test_refinement_uses_configured_primary(client):
    """Test that REFINEMENT task still uses the default MODEL_PRIMARY."""
    with patch.object(client, '_make_request', new_callable=AsyncMock) as mock_request:
        mock_request.return_value = '{"refinement": "content"}'
        
        response = await client.completion(messages=[], task_type="REFINEMENT")
        
        # Should call _make_request with MODEL_PRIMARY (deepseek)
        mock_request.assert_called_with([], config.MODEL_PRIMARY, None)

@pytest.mark.asyncio
async def test_json_repair_triggered_on_invalid_json(client):
    """Test that JSON repair is triggered when response is not valid JSON."""
    invalid_json = "This is not JSON { incomplete: "
    valid_json = '{"fixed": "data"}'
    
    with patch.object(client, '_make_request', new_callable=AsyncMock) as mock_request:
        # First call returns invalid JSON, second (repair) returns valid JSON
        mock_request.side_effect = [invalid_json, valid_json]
        
        # We need a schema or at least a hint for the repair
        response_format = {"type": "json_object", "schema": {"type": "object"}}
        
        response = await client.completion(messages=[], response_format=response_format)
        
        # Verify repair call
        assert mock_request.call_count == 2
        calls = mock_request.call_args_list
        
        # Second call should be the repair call
        repair_messages = calls[1].args[0]
        repair_model = calls[1].args[1]
        repair_format = calls[1].args[2]
        
        assert repair_model == config.REPAIR_MODEL
        assert repair_format == {"type": "json_object"} # Spec says enable structured_outputs
        
        # Repair prompt is in the second message (index 1)
        assert "Convert this text into valid JSON" in repair_messages[1]["content"]
        assert invalid_json in repair_messages[1]["content"]
        assert response == valid_json

@pytest.mark.asyncio
async def test_json_repair_failure_falls_back(client):
    """Test that if repair also fails, it returns the error or original text."""
    invalid_json = "Invalid"
    still_invalid = "Still Invalid"
    
    with patch.object(client, '_make_request', new_callable=AsyncMock) as mock_request:
        mock_request.side_effect = [invalid_json, still_invalid]
        
        response = await client.completion(messages=[], response_format={"type": "json_object"})
        
        # Should attempt repair and then return the result (which might be the error string or original)
        # The current implementation of completion handles exceptions by returning error strings.
        # If repair fails to produce valid JSON, we might just return it or let it fail.
        assert mock_request.call_count == 2
        assert response == still_invalid
