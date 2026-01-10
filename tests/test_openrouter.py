import unittest
import os
from dotenv import load_dotenv
from src.integrations.openrouter_client import OpenRouterClient

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

if __name__ == '__main__':
    unittest.main()