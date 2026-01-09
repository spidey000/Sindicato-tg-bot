import unittest
from unittest.mock import MagicMock, patch
from src.agents.base import AgentBase

# Concrete implementation for testing
class TestAgent(AgentBase):
    def get_system_prompt(self) -> str:
        return "System Prompt"

class TestAgentSummary(unittest.TestCase):
    
    @patch("src.agents.base.OpenRouterClient")
    def test_generate_draft_returns_summary(self, MockOpenRouterClient):
        # Setup mock
        mock_client = MockOpenRouterClient.return_value
        # The LLM will eventually return a JSON string that the agent parses
        # For now, we mock the return value of the client to be that JSON string
        mock_client.completion.return_value = '{"summary": "Short Title", "content": "This content is definitely long enough to pass the validation check which requires more than fifty characters."}'
        
        agent = TestAgent()
        
        # Action
        result = agent.generate_structured_draft("Test Context")
        
        # Assertion
        self.assertIsInstance(result, dict)
        self.assertIn("summary", result)
        self.assertIn("content", result)
        self.assertEqual(result["summary"], "Short Title")
        self.assertEqual(result["content"], "This content is definitely long enough to pass the validation check which requires more than fifty characters.")

if __name__ == "__main__":
    unittest.main()
