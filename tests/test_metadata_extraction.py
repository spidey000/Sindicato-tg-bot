import unittest
from unittest.mock import MagicMock, AsyncMock
from src.agents.base import AgentBase

class TestAgentBase(AgentBase):
    def get_system_prompt(self) -> str:
        return "System prompt"

class TestMetadataExtraction(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.agent = TestAgentBase()
        self.agent.llm_client = MagicMock()

    async def test_generate_structured_draft_returns_metadata(self):
        # Mock LLM response with metadata
        # Content must be > 50 chars
        long_content = "Contenido del borrador... " * 5
        mock_response = f"""
        {{
            "summary": "Despido improcedente",
            "content": "{long_content}",
            "thesis": "Nulidad del despido por discriminación",
            "specific_point": "Inversión de la carga de la prueba",
            "area": "Despido"
        }}
        """
        self.agent.llm_client.completion = AsyncMock(return_value=mock_response)

        data = await self.agent.generate_structured_draft_with_retry("Contexto del caso")

        self.assertIn("thesis", data)
        self.assertIn("specific_point", data)
        self.assertIn("area", data)
        self.assertEqual(data["thesis"], "Nulidad del despido por discriminación")
        self.assertEqual(data["specific_point"], "Inversión de la carga de la prueba")
        self.assertEqual(data["area"], "Despido")

    async def test_generate_structured_draft_missing_metadata_defaults(self):
        # Mock LLM response without metadata
        # Content must be > 50 chars
        long_content = "Contenido del borrador... " * 5
        mock_response = f"""
        {{
            "summary": "Despido improcedente",
            "content": "{long_content}"
        }}
        """
        self.agent.llm_client.completion = AsyncMock(return_value=mock_response)

        data = await self.agent.generate_structured_draft_with_retry("Contexto del caso")

        self.assertIn("thesis", data)
        self.assertIn("specific_point", data)
        self.assertIn("area", data)
        # Verify defaults or empty strings are returned
        self.assertEqual(data["thesis"], "")
        self.assertEqual(data["specific_point"], "")
        self.assertEqual(data["area"], "")

if __name__ == '__main__':
    unittest.main()