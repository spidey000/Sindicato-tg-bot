import unittest
from unittest.mock import patch, MagicMock
from src.integrations.cleanup_helper import delete_notion_page, delete_drive_object

class TestCleanupHelper(unittest.TestCase):
    
    @patch("src.integrations.cleanup_helper.DelegadoNotionClient")
    def test_delete_notion_page(self, mock_notion_cls):
        mock_notion = mock_notion_cls.return_value
        mock_notion.delete_page.return_value = True
        
        result = delete_notion_page("page_123")
        
        self.assertTrue(result)
        mock_notion.delete_page.assert_called_once_with("page_123")

    @patch("src.integrations.cleanup_helper.DelegadoDriveClient")
    def test_delete_drive_object(self, mock_drive_cls):
        mock_drive = mock_drive_cls.return_value
        mock_drive.delete_file_or_folder.return_value = True
        
        result = delete_drive_object("file_456")
        
        self.assertTrue(result)
        mock_drive.delete_file_or_folder.assert_called_once_with("file_456")

if __name__ == "__main__":
    unittest.main()
