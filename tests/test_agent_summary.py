import pytest
from unittest.mock import MagicMock, AsyncMock, patch
from src.agents.base import AgentBase

# Concrete implementation for testing
class TestAgent(AgentBase):
    def get_system_prompt(self) -> str:
        return "System Prompt"

class TestAgentSummary:

    @pytest.mark.asyncio
    @patch("src.agents.base.OpenRouterClient")
    async def test_generate_draft_returns_summary(self, MockOpenRouterClient):
        # Setup mock
        mock_client = MockOpenRouterClient.return_value
        # The LLM will eventually return a JSON string that the agent parses
        # For now, we mock the return value of the client to be that JSON string
        mock_client.completion = AsyncMock(return_value='{"summary": "Short Title", "content": "This content is definitely long enough to pass the validation check which requires more than fifty characters."}')

        agent = TestAgent()

        # Action
        result = await agent.generate_structured_draft("Test Context")

        # Assertion
        assert isinstance(result, dict)
        assert "summary" in result
        assert "content" in result
        assert result["summary"] == "Short Title"
        assert result["content"] == "This content is definitely long enough to pass the validation check which requires more than fifty characters."
