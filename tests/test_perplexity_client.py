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
        result = await client.verify_draft("Draft text")
        
        # Verify
        self.assertEqual(result, "Verified content")
        # Ensure used primary key
        call_kwargs = mock_client.post.call_args.kwargs
        headers = call_kwargs["headers"]
        self.assertEqual(headers["Authorization"], f"Bearer {self.primary_key}")

    @patch("src.integrations.perplexity_client.httpx.AsyncClient")
    async def test_verify_draft_fallback(self, mock_client_cls):
        # Setup mock
        mock_client = AsyncMock()
        mock_client_cls.return_value.__aenter__.return_value = mock_client
        
        # Primary fails (401)
        mock_response_fail = MagicMock()
        mock_response_fail.status_code = 401
        
        # Fallback succeeds (200)
        mock_response_success = MagicMock()
        mock_response_success.status_code = 200
        mock_response_success.json.return_value = {
            "choices": [{"message": {"content": "Fallback content"}}]
        }
        
        mock_client.post.side_effect = [mock_response_fail, mock_response_success]

        # Init client
        client = perplexity_client.PerplexityClient()
        
        # Action
        result = await client.verify_draft("Draft text")
        
        # Verify
        self.assertEqual(result, "Fallback content")
        self.assertEqual(mock_client.post.call_count, 2)
        
        # Check second call headers
        second_call_args = mock_client.post.call_args_list[1]
        headers = second_call_args.kwargs["headers"]
        self.assertEqual(headers["Authorization"], f"Bearer {self.fallback_key}")

    @patch("src.integrations.perplexity_client.httpx.AsyncClient")
    async def test_verify_draft_all_fail(self, mock_client_cls):
         # Setup mock
        mock_client = AsyncMock()
        mock_client_cls.return_value.__aenter__.return_value = mock_client
        
        mock_response_fail = MagicMock()
        mock_response_fail.status_code = 500
        
        mock_client.post.return_value = mock_response_fail

        # Init client
        client = perplexity_client.PerplexityClient()
        
        # Action
        result = await client.verify_draft("Draft text")
        
        # Verify
        self.assertIsNone(result)

if __name__ == "__main__":
    unittest.main()
