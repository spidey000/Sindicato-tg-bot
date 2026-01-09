import unittest
from unittest.mock import MagicMock, patch
from src.integrations.drive_client import DelegadoDriveClient
from src.integrations.docs_client import DelegadoDocsClient

class TestDriveDocsNaming(unittest.TestCase):
    
    @patch("src.integrations.drive_client.build")
    @patch("src.integrations.drive_client.get_google_creds")
    def test_drive_folder_naming(self, mock_get_creds, mock_build):
        # Setup
        mock_service = MagicMock()
        mock_build.return_value = mock_service
        mock_service.files.return_value.create.return_value.execute.return_value = {"id": "folder_id", "webViewLink": "http://link"}
        
        client = DelegadoDriveClient()
        
        # Action
        client.create_case_folder("D-2026-001", "Resumen del Caso")
        
        # Assertion
        args, kwargs = mock_service.files.return_value.create.call_args
        body = kwargs["body"]
        self.assertEqual(body["name"], "D-2026-001 - Resumen del Caso")

    @patch("src.integrations.docs_client.build")
    @patch("src.integrations.docs_client.get_google_creds")
    def test_docs_naming(self, mock_get_creds, mock_build):
        # Setup
        mock_service = MagicMock()
        # We need to distinguish between 'docs' and 'drive' services built by the same mock_build
        # But for this test, we only care that the 'docs' service receives the correct title
        # DelegadoDocsClient builds 'docs' then 'drive'.
        
        client = DelegadoDocsClient()
        # Mock the service attached to client manually if needed, or rely on mock_build returning a mock that handles both.
        # But mock_build returns a NEW mock each time it's called.
        
        # client.service is the docs service
        client.service = MagicMock()
        client.service.documents.return_value.create.return_value.execute.return_value = {"documentId": "doc_id"}
        
        # Mock drive service inside docs client for the move operation
        client.drive_service = MagicMock()
        client.drive_service.files.return_value.get.return_value.execute.return_value = {"parents": ["old_parent"]}
        
        # Action
        title = "D-2026-001 - Resumen del Caso"
        client.create_draft_document(title, "Content", "parent_id")
        
        # Assertion
        args, kwargs = client.service.documents.return_value.create.call_args
        body = kwargs["body"]
        self.assertEqual(body["title"], "D-2026-001 - Resumen del Caso")

if __name__ == "__main__":
    unittest.main()
