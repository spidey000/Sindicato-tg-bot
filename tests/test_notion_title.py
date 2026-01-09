import unittest
from unittest.mock import MagicMock, patch
from src.integrations.notion_client import DelegadoNotionClient

class TestNotionTitle(unittest.TestCase):
    
    @patch("src.integrations.notion_client.Client")
    def test_create_case_page_uses_title(self, MockClient):
        # Setup
        mock_notion = MockClient.return_value
        mock_notion.pages.create.return_value = {"id": "page-id"}
        
        client = DelegadoNotionClient()
        # Mock database ID retrieval if needed, but it's loaded from env
        # Since we mock Client, the check in __init__ passes if token is set.
        # But we need to ensure NOTION_TOKEN env var is handled or mocked.
        # client.database_id is initialized from env.
        
        case_data = {
            "id": "D-2026-001",
            "title": "D-2026-001 - Falta de EPIs",
            "type": "Denuncia ITSS",
            "status": "Borrador",
            "initial_context": "Context"
        }
        
        # Action
        client.create_case_page(case_data)
        
        # Assertion
        args, kwargs = mock_notion.pages.create.call_args
        properties = kwargs["properties"]
        
        # Check that the Name property uses the provided title
        self.assertEqual(
            properties["Name"]["title"][0]["text"]["content"],
            "D-2026-001 - Falta de EPIs"
        )

if __name__ == "__main__":
    unittest.main()
