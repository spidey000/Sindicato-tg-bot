import unittest
import os
from dotenv import load_dotenv
from unittest.mock import AsyncMock, patch
from src.integrations.openrouter_client import OpenRouterClient
import json

# Load env vars from the .env file we just created
load_dotenv()

class TestOpenRouter(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.client = OpenRouterClient()
        self.test_messages = [
            {"role": "user", "content": "Hola, esto es una prueba de conexión. Responde 'OK' si me lees."}
        ]

    async def test_connection_primary(self):
        """Test connection with the primary model."""
        model = os.getenv('MODEL_PRIMARY')
        print(f"\nTesting Primary Model: {model}...")
        response = await self.client.completion(self.test_messages)
        print(f"Response: {response}")
        self.assertIsNotNone(response)
        self.assertNotEqual(response, "")
        self.assertNotIn("Error", response)

    async def test_json_forcing_failure(self):
        """Test that the call now succeeds even when JSON is requested."""
        print(f"\nTesting for JSON forcing failure (expecting success now)...")
        
        response = await self.client.completion(
            self.test_messages,
            response_format={"type": "json_object"}
        )
        
        print(f"Response: {response}")
        self.assertIsNotNone(response)
        self.assertNotEqual(response, "")
        self.assertNotIn("Error", response)

    @patch('src.integrations.openrouter_client.OpenRouterClient._make_request', new_callable=AsyncMock)
    async def test_qwen_json_fixing_failing_case(self, mock_make_request):
        """
        Test that invalid JSON is detected and triggers repair,
        and that the final output is not valid JSON if repair also fails.
        This test should fail initially to confirm invalid JSON detection
        and a failed repair.
        """
        print("\nTesting Qwen JSON fixing (failing case for invalid JSON detection and failed repair)...")

        malformed_json = '{"name": "test", "age": 30,' # Malformed JSON from primary
        malformed_json_from_repair = '{"status": "error"' # Malformed JSON from repair

        # Configure the mock to return malformed JSON for both calls
        mock_make_request.side_effect = [
            malformed_json, # First call to _make_request for primary model
            Exception("Simulated repair failure") # Second call for repair model, raise an exception
        ]

        # Use a temporary logger to capture messages
        with self.assertLogs('src.integrations.openrouter_client', level='WARNING') as cm:
            response = await self.client.completion(
                self.test_messages,
                model=os.getenv('PRIMARY_DRAFT_MODEL'),
                response_format={"type": "json_object"}
            )
            print(f"Response: {response}")
            
            # Assert that the final response is NOT valid JSON
            with self.assertRaises(json.JSONDecodeError):
                json.loads(response)

            # Assert that warnings about invalid JSON and repair failure were logged
            self.assertIn("Invalid JSON from", cm.output[0])
            self.assertIn("Attempting repair with", cm.output[0])
            self.assertTrue(any("JSON repair failed" in s for s in cm.output))
            
        # Ensure _make_request was called at least twice (initial + repair)
        self.assertEqual(mock_make_request.call_count, 2)

if __name__ == '__main__':
    unittest.main()