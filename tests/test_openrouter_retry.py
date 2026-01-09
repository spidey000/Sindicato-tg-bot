import unittest
from unittest.mock import patch, MagicMock
from src.integrations.openrouter_client import OpenRouterClient
import requests

class TestOpenRouterRetry(unittest.TestCase):
    def setUp(self):
        self.client = OpenRouterClient()

    @patch('src.integrations.openrouter_client.requests.post')
    def test_make_request_retries_on_failure(self, mock_post):
        # Setup mock to raise exception twice, then succeed
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "choices": [{"message": {"content": "Success"}}]
        }
        mock_response.raise_for_status.return_value = None
        
        mock_post.side_effect = [
            requests.exceptions.RequestException("Fail 1"),
            requests.exceptions.RequestException("Fail 2"),
            mock_response
        ]

        messages = [{"role": "user", "content": "Hello"}]
        model = "test-model"
        
        # Call the private method (or the public one if it calls the private one)
        # Testing _make_request directly as per plan focus, but ideally should be tested via public API.
        # However, _make_request is what we are modifying.
        result = self.client._make_request(messages, model)
        
        self.assertEqual(result, "Success")
        self.assertEqual(mock_post.call_count, 3)

    @patch('src.integrations.openrouter_client.requests.post')
    def test_make_request_passes_response_format(self, mock_post):
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "choices": [{"message": {"content": "{}"}}]
        }
        mock_post.return_value = mock_response

        messages = [{"role": "user", "content": "JSON please"}]
        model = "test-model"
        response_format = {"type": "json_object"}
        
        self.client._make_request(messages, model, response_format=response_format)
        
        call_args = mock_post.call_args
        self.assertIn('"response_format": {"type": "json_object"}', call_args[1]['data'])

if __name__ == '__main__':
    unittest.main()
