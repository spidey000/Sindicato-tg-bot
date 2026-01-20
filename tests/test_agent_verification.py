import unittest
from unittest.mock import MagicMock, patch, AsyncMock
from src.agents.base import AgentBase

# Create a concrete implementation for testing
class TestAgent(AgentBase):
    def get_system_prompt(self):
        return "You are a test agent."

class TestAgentVerification(unittest.IsolatedAsyncioTestCase):
    @patch("src.agents.base.PerplexityClient")
    @patch("src.agents.base.OpenRouterClient")
    @patch("src.agents.base.DelegadoNotionClient")
    async def test_generate_structured_draft_with_verification(self, mock_notion_cls, mock_router_cls, mock_pplx_cls):
        # Setup Router Mock (Initial Draft)
        mock_router = MagicMock()
        mock_router_cls.return_value = mock_router
        mock_router.completion = AsyncMock(side_effect=[
            '{"summary": "Test Summary", "content": "This is a very long initial draft that serves to pass the validation check requiring fifty characters.", "thesis": "My Thesis", "specific_point": "My Point", "area": "My Area"}', # First call: Initial
            "Refined Draft" # Second call: Refinement
        ])

        # Setup Perplexity Mock
        mock_pplx = MagicMock()
        mock_pplx_cls.return_value = mock_pplx
        mock_pplx.verify_draft = AsyncMock(return_value="Grounding Feedback")

        # Setup Notion Mock
        mock_notion = MagicMock()
        mock_notion_cls.return_value = mock_notion

        # Init Agent
        agent = TestAgent()

        # Action
        result = await agent.generate_structured_draft_verified("Context", notion_page_id="page-123")

        # Verify
        self.assertEqual(result["summary"], "Test Summary")
        self.assertEqual(result["content"], "Refined Draft")
        self.assertEqual(result["verification_status"], "Verified")

        # Verify Perplexity called with Metadata
        mock_pplx.verify_draft.assert_called_once_with(
            context="This is a very long initial draft that serves to pass the validation check requiring fifty characters.",
            thesis="My Thesis",
            specific_point="My Point",
            area="My Area"
        )

        # Verify Notion Audit Log was triggered
        mock_notion.append_verification_report.assert_called_once_with(
            "page-123",
            "Grounding Feedback"
        )

        self.assertEqual(mock_router.completion.call_count, 2) # Initial + Refine

    @patch("src.agents.base.PerplexityClient")
    @patch("src.agents.base.OpenRouterClient")
    async def test_generate_structured_draft_verification_failed(self, mock_router_cls, mock_pplx_cls):
        # Setup Router Mock
        mock_router = MagicMock()
        mock_router_cls.return_value = mock_router
        mock_router.completion = AsyncMock(return_value='{"summary": "Test Summary", "content": "This is a very long initial draft that serves to pass the validation check requiring fifty characters.", "thesis": "", "specific_point": "", "area": ""}')

        # Setup Perplexity Mock (Failure)
        mock_pplx = MagicMock()
        mock_pplx_cls.return_value = mock_pplx
        mock_pplx.verify_draft = AsyncMock(return_value=None)

        # Init Agent
        agent = TestAgent()

        # Action
        result = await agent.generate_structured_draft_verified("Context")

        # Verify
        self.assertEqual(result["content"], "This is a very long initial draft that serves to pass the validation check requiring fifty characters.")
        self.assertEqual(result["verification_status"], "Verification Failed")

        # Verify calls
        mock_pplx.verify_draft.assert_called_once()
        self.assertEqual(mock_router.completion.call_count, 1) # Only Initial

if __name__ == "__main__":
    unittest.main()