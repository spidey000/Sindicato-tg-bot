
import pytest
from unittest.mock import patch, ANY, AsyncMock
from src.agents.inspector import InspectorLaboralAgent
from src import config

@pytest.fixture
def agent():
    return InspectorLaboralAgent()

@pytest.mark.asyncio
async def test_agent_uses_draft_hierarchy(agent):
    """Test that agent's draft generation uses the DRAFT hierarchy."""
    with patch.object(agent.llm_client, '_make_request', new_callable=AsyncMock) as mock_request:
        mock_request.return_value = '{"summary": "Test", "content": "This is a long enough content for the validation to pass.", "thesis": "T", "specific_point": "S", "area": "A"}'
        
        await agent.generate_structured_draft_with_retry("Context")
        
        # Verify call used PRIMARY_DRAFT_MODEL
        mock_request.assert_any_call(
            ANY, 
            config.PRIMARY_DRAFT_MODEL, 
            {"type": "json_object"}
        )

@pytest.mark.asyncio
async def test_agent_uses_refinement_model(agent):
    """Test that agent's refinement uses the REFINEMENT (default) hierarchy."""
    with patch.object(agent.llm_client, '_make_request', new_callable=AsyncMock) as mock_request:
        mock_request.return_value = "Refined content"
        
        await agent.refine_draft("Old content", "New info")
        
        # Verify call used MODEL_PRIMARY (not draft models)
        mock_request.assert_any_call(
            ANY, 
            config.MODEL_PRIMARY, 
            None
        )
