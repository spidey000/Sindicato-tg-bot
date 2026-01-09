import unittest
from unittest.mock import MagicMock, patch
from src.integrations.notion_client import DelegadoNotionClient

class TestNotionAuditLog(unittest.TestCase):
    def setUp(self):
        # Prevent actual API initialization
        with patch.dict('os.environ', {'NOTION_TOKEN': 'fake-token', 'NOTION_DATABASE_ID': 'fake-db'}):
            self.client = DelegadoNotionClient()
            self.client.client = MagicMock()

    def test_append_verification_report(self):
        # Mock successful append
        self.client.client.blocks.children.append.return_value = {"id": "new-block-id"}
        
        page_id = "test-page-id"
        report_text = "This is a legal verification report from Perplexity."
        
        result = self.client.append_verification_report(page_id, report_text)
        
        self.assertTrue(result)
        
        # Verify block structure
        self.client.client.blocks.children.append.assert_called_once()
        call_args = self.client.client.blocks.children.append.call_args
        self.assertEqual(call_args.kwargs["block_id"], page_id)
        
        children = call_args.kwargs["children"]
        self.assertEqual(len(children), 1)
        
        block = children[0]
        self.assertEqual(block["type"], "toggle")
        self.assertEqual(block["toggle"]["rich_text"][0]["text"]["content"], "🔍 Auditoría de Verificación Legal (Perplexity)")
        
        # Check children of toggle (the actual report content)
        # Notion toggle blocks can have children
        self.assertEqual(block["toggle"]["children"][0]["type"], "paragraph")
        self.assertEqual(block["toggle"]["children"][0]["paragraph"]["rich_text"][0]["text"]["content"], report_text)

    def test_append_verification_report_failure(self):
        self.client.client.blocks.children.append.side_effect = Exception("API Error")
        
        result = self.client.append_verification_report("page-id", "report")
        
        self.assertFalse(result)

if __name__ == "__main__":
    unittest.main()
