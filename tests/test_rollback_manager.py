import unittest
from unittest.mock import patch, MagicMock, AsyncMock
from src.utils import RollbackManager

class TestRollbackManager(unittest.IsolatedAsyncioTestCase):
    
    @patch("src.integrations.cleanup_helper.delete_notion_page")
    @patch("src.integrations.cleanup_helper.delete_drive_object")
    async def test_execute_rollback_full(self, mock_delete_drive, mock_delete_notion):
        mock_delete_drive.return_value = True
        mock_delete_notion.return_value = True
        
        rm = RollbackManager()
        rm.set_notion_page("p1")
        rm.set_drive_folder("f1")
        rm.set_doc("d1")
        rm.trigger_failure("Step X", Exception("API Error"))
        
        report = await rm.execute_rollback()
        
        self.assertIn("Error Crítico en 'Step X'", report)
        self.assertIn("API Error", report)
        self.assertIn("Carpeta en Drive eliminada", report)
        self.assertIn("Página de Notion eliminada", report)
        
        mock_delete_drive.assert_called_once_with("f1")
        mock_delete_notion.assert_called_once_with("p1")

    @patch("src.integrations.cleanup_helper.delete_notion_page")
    @patch("src.integrations.cleanup_helper.delete_drive_object")
    async def test_execute_rollback_partial(self, mock_delete_drive, mock_delete_notion):
        mock_delete_notion.return_value = True
        
        rm = RollbackManager()
        rm.set_notion_page("p1")
        rm.trigger_failure("Step Y", Exception("Timeout"))
        
        report = await rm.execute_rollback()
        
        self.assertIn("Página de Notion eliminada", report)
        self.assertNotIn("Carpeta en Drive eliminada", report)
        
        mock_delete_drive.assert_not_called()
        mock_delete_notion.assert_called_once_with("p1")

if __name__ == "__main__":
    unittest.main()
