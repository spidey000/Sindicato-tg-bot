import unittest
from unittest.mock import patch, MagicMock, AsyncMock
from src.integrations.perplexity_client import PerplexityClient
import httpx

class TestPerplexityRetry(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.client = PerplexityClient()
        self.client.primary_key = "test_key"

    @patch('src.integrations.perplexity_client.httpx.AsyncClient')
    async def test_make_request_retries_on_failure(self, mock_client_cls):
        # Setup mock client
        mock_client = AsyncMock()
        mock_client_cls.return_value.__aenter__.return_value = mock_client
        
        # Mock responses: 2 failures, 1 success
        fail_response = MagicMock()
        fail_response.status_code = 500
        fail_response.text = "Error"
        
        success_response = MagicMock()
        success_response.status_code = 200
        success_response.json.return_value = {
            "choices": [{"message": {"content": "Verified Content"}}]
        }
        
        mock_client.post.side_effect = [
            fail_response,
            fail_response,
            success_response
        ]

        payload = {"test": "data"}
        
        # Call the method
        result = await self.client._make_request("test_key", payload)
        
        self.assertEqual(result, "Verified Content")
        self.assertEqual(mock_client.post.call_count, 3)

    @patch('src.integrations.perplexity_client.httpx.AsyncClient')
    async def test_make_request_fails_after_retries(self, mock_client_cls):
         # Setup mock client
        mock_client = AsyncMock()
        mock_client_cls.return_value.__aenter__.return_value = mock_client
        
        # Mock responses: 3 failures
        fail_response = MagicMock()
        fail_response.status_code = 500
        fail_response.text = "Error"
        
        mock_client.post.return_value = fail_response # Always returns fail

        payload = {"test": "data"}
        
        result = await self.client._make_request("test_key", payload)
        
        self.assertIsNone(result)
        # Should be called 3 times (max retries)
        self.assertEqual(mock_client.post.call_count, 3)

if __name__ == '__main__':
    unittest.main()
