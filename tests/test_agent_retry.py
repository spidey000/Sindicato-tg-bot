import unittest
from unittest.mock import MagicMock, AsyncMock
from src.agents.base import AgentBase

class TestAgent(AgentBase):
    def get_system_prompt(self) -> str:
        return "You are a test agent."

class TestAgentRetry(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.agent = TestAgent()
        self.agent.llm_client = MagicMock()

    async def test_retry_on_short_content(self):
        # Mock responses: 
        # 1. Valid JSON but short content
        # 2. Valid JSON but short content
        # 3. Valid JSON and valid content
        self.agent.llm_client.completion = AsyncMock(side_effect=[
            '{"summary": "Short", "content": "Too short"}', 
            '{"summary": "Short", "content": "Still too short"}',
            '{"summary": "Good", "content": "This content is definitely longer than fifty characters to pass the validation check."}'
        ])

        # I will implement/update generate_structured_draft_with_retry
        # For now, I'll call the method I intend to create/update
        result = await self.agent.generate_structured_draft_with_retry("test context")

        self.assertEqual(result["summary"], "Good")
        self.assertEqual(self.agent.llm_client.completion.call_count, 3)

    async def test_retry_on_invalid_json(self):
        # Mock responses:
        # 1. Invalid JSON
        # 2. Valid JSON/Content
        self.agent.llm_client.completion = AsyncMock(side_effect=[
            'Invalid JSON',
            '{"summary": "Good", "content": "This content is definitely longer than fifty characters to pass the validation check."}'
        ])

        result = await self.agent.generate_structured_draft_with_retry("test context")

        self.assertEqual(result["summary"], "Good")
        self.assertEqual(self.agent.llm_client.completion.call_count, 2)
        
    async def test_fail_after_max_retries(self):
        # Mock responses: 3 failures
        self.agent.llm_client.completion = AsyncMock(side_effect=[
            '{"content": "Short"}',
            '{"content": "Short"}',
            '{"content": "Short"}'
        ])
        
        # It should raise an error or return a specific failure state. 
        # The spec says: "Exhaustion: If all 3 attempts fail, the entire document generation flow is aborted and triggers the rollback"
        # So raising an exception is probably best here to trigger the rollback logic in the handler.
        
        with self.assertRaises(ValueError):
             await self.agent.generate_structured_draft_with_retry("test context")

if __name__ == '__main__':
    unittest.main()
