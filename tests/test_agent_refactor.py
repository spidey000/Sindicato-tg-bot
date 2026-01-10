import unittest
from unittest.mock import MagicMock, AsyncMock, patch
from src.agents.base import AgentBase

class ConcreteAgent(AgentBase):
    def get_system_prompt(self):
        return "Test Prompt"

class TestAgentRefactor(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.agent = ConcreteAgent()
        self.agent.pplx_client = MagicMock()
        self.agent.pplx_client.verify_draft = AsyncMock()
        self.agent.llm_client = MagicMock()

    async def test_verify_draft_content_method(self):
        # Expectation: Agent should expose verify_draft_content method
        # This test will fail if the method doesn't exist
        
        draft = "Draft Content"
        expected_feedback = "Feedback"
        self.agent.pplx_client.verify_draft.return_value = expected_feedback
        
        feedback = await self.agent.verify_draft_content(draft)
        
        self.assertEqual(feedback, expected_feedback)
        self.agent.pplx_client.verify_draft.assert_called_once_with(context=draft, thesis="", specific_point="", area="")

    async def test_refine_draft_with_feedback_method(self):
        # Expectation: Agent should expose refine_draft_with_feedback method
        
        content = "Old Content"
        feedback = "Needs fix"
        expected_new_content = "New Content"
        
        self.agent.llm_client.completion = AsyncMock(return_value=expected_new_content)
        
        new_content = await self.agent.refine_draft_with_feedback(content, feedback)
        
        self.assertEqual(new_content, expected_new_content)
        # Verify it calls llm_client.completion with correct prompt structure
        args, _ = self.agent.llm_client.completion.call_args
        messages = args[0]
        self.assertIn("VERIFICACIÓN LEGAL OBLIGATORIA", messages[1]['content'])

if __name__ == "__main__":
    unittest.main()
