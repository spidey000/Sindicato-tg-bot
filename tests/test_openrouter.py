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
    async def test_qwen_json_fixing_passing_case(self, mock_make_request):
        """
        Test that invalid JSON is detected, triggers repair, and successfully
        returns valid JSON after repair.
        """
        print("\nTesting Qwen JSON fixing (passing case for successful repair)...")

        malformed_json = '{"name": "test", "age": 30,' # Malformed JSON from primary
        repaired_json = json.dumps({"name": "test", "age": 30, "status": "repaired"}) # Valid JSON from repair

        # Configure the mock to return malformed JSON first, then valid JSON for repair
        mock_make_request.side_effect = [
            malformed_json, # First call to _make_request for primary model
            repaired_json   # Second call for repair model
        ]

        # Use a temporary logger to capture messages
        with self.assertLogs('src.integrations.openrouter_client', level='WARNING') as cm:
            response = await self.client.completion(
                self.test_messages,
                model=os.getenv('PRIMARY_DRAFT_MODEL'),
                response_format={"type": "json_object"}
            )
            print(f"Response: {response}")
            
            # Assert that the final response is valid JSON
            self.assertIsInstance(json.loads(response), dict)
            self.assertEqual(json.loads(response), {"name": "test", "age": 30, "status": "repaired"})

            # Assert that warnings about invalid JSON and repair attempt were logged
            self.assertIn("Invalid JSON from", cm.output[0])
            self.assertIn("Attempting repair with", cm.output[0])
            # Ensure "JSON repair failed" is NOT in the logs (since repair should succeed)
            self.assertFalse(any("JSON repair failed" in s for s in cm.output))
            
        # Ensure _make_request was called twice (initial + repair)
        self.assertEqual(mock_make_request.call_count, 2)

    @patch('src.integrations.openrouter_client.OpenRouterClient._make_request', new_callable=AsyncMock)
    async def test_qwen_json_repair_response_format(self, mock_make_request):
        """
        Test that the _make_request call from _repair_json initially does NOT
        receive response_format={"type": "json_object"}. This is our failing test.
        """
        print("\nTesting Qwen JSON repair response_format (failing test)...")

        malformed_json = '{"key": "value",' # Malformed JSON to trigger repair

        # Configure the mock. The first call will trigger repair.
        # The second call is what we want to inspect for response_format.
        mock_make_request.side_effect = [
            malformed_json, # First call (primary model)
            json.dumps({"repaired_key": "repaired_value"}) # Placeholder for repair model's response
        ]

        # Call completion, which will eventually call _repair_json
        await self.client.completion(
            self.test_messages,
            model=os.getenv('PRIMARY_DRAFT_MODEL'),
            response_format={"type": "json_object"}
        )

        # Assert that _make_request was called at least twice (initial + repair)
        self.assertGreaterEqual(mock_make_request.call_count, 2)

        # Get the arguments of the second call to _make_request (the one from _repair_json)
        # The args are (messages, model, response_format)
        repair_call_args = mock_make_request.call_args_list[1]
        
        # This is the FAILING ASSERTION: Expect response_format to NOT be present in the second call
        # It's currently None because the fix for this track is not yet implemented.
        self.assertIsNone(repair_call_args.kwargs.get('response_format'))


if __name__ == '__main__':
    unittest.main()