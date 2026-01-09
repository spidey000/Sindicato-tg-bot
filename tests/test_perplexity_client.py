import unittest
from unittest.mock import MagicMock, patch, AsyncMock
import os
from src.integrations import perplexity_client

class TestPerplexityClient(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.primary_key = "pplx-primary"
        self.fallback_key = "pplx-fallback"
        os.environ["PERPLEXITY_API_KEY_PRIMARY"] = self.primary_key
        os.environ["PERPLEXITY_API_KEY_FALLBACK"] = self.fallback_key

    @patch("src.integrations.perplexity_client.httpx.AsyncClient")
    async def test_verify_draft_success_primary(self, mock_client_cls):
        # Setup mock
        mock_client = AsyncMock()
        mock_client_cls.return_value.__aenter__.return_value = mock_client
        
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "choices": [{"message": {"content": "Verified content"}}]
        }
        mock_client.post.return_value = mock_response

        # Init client
        client = perplexity_client.PerplexityClient()
        
        # Action
        result = await client.verify_draft(
            context="Draft text",
            thesis="My Thesis",
            specific_point="My Point",
            area="My Area"
        )
        
        # Verify
        self.assertEqual(result, "Verified content")
        
        # Verify Prompt Construction
        call_kwargs = mock_client.post.call_args.kwargs
        json_payload = call_kwargs["json"]
        messages = json_payload["messages"]
        
        system_msg = messages[0]["content"]
        user_msg = messages[1]["content"]

        # Check system prompt template injection
        self.assertIn("Actúa como abogado laboralista especializado en derecho laboral español", system_msg)
        self.assertIn("Draft text", system_msg)
        self.assertIn("My Thesis", system_msg)
        self.assertIn("My Point", system_msg)
        self.assertIn("My Area", system_msg)
        
        # User message usually is simpler now, or empty if everything is in system, 
        # but the spec says "CONTEXTO DEL CASO: {context}" inside the prompt template. 
        # The spec implies the whole structure is the prompt. 
        # Typically one would put the persona in system and the specific task in user, 
        # but the spec template is one big block. 
        # I will assume the `AgentBase` implementation will put the *entire* filled template 
        # into the `system` or `user` message. 
        # Let's check `src/integrations/perplexity_client.py` original implementation.
        # It used: system="You are...", user="Please verify... {draft}"
        
        # The spec says:
        # Update verify_draft to use the following prompt template:
        # "Actúa como... CONTEXTO: {context} ..."
        
        # So I will assert that this constructed string is present.

    @patch("src.integrations.perplexity_client.httpx.AsyncClient")
    async def test_verify_draft_fallback(self, mock_client_cls):
        # Setup mock
        mock_client = AsyncMock()
        mock_client_cls.return_value.__aenter__.return_value = mock_client
        
        # Primary fails (401) - Needs to fail 3 times to trigger fallback
        mock_response_fail = MagicMock()
        mock_response_fail.status_code = 401
        mock_response_fail.text = "Unauthorized"
        
        # Fallback succeeds (200)
        mock_response_success = MagicMock()
        mock_response_success.status_code = 200
        mock_response_success.json.return_value = {
            "choices": [{"message": {"content": "Fallback content"}}]
        }
        
        mock_client.post.side_effect = [
            mock_response_fail, mock_response_fail, mock_response_fail, 
            mock_response_success
        ]

        # Init client
        client = perplexity_client.PerplexityClient()
        
        # Action
        result = await client.verify_draft(
            context="Draft text",
            thesis="Thesis",
            specific_point="Point",
            area="Area"
        )
        
        # Verify
        self.assertEqual(result, "Fallback content")
        self.assertEqual(mock_client.post.call_count, 4)
        
        # Check 4th call headers (First call of fallback key)
        fourth_call_args = mock_client.post.call_args_list[3]
        headers = fourth_call_args.kwargs["headers"]
        self.assertEqual(headers["Authorization"], f"Bearer {self.fallback_key}")

if __name__ == "__main__":
    unittest.main()