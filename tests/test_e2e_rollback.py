import unittest
from unittest.mock import MagicMock, patch, AsyncMock
from src.handlers import denuncia_handler
import datetime

class TestE2ERollback(unittest.IsolatedAsyncioTestCase):
    @patch("src.handlers.notion")
    @patch("src.handlers.drive")
    @patch("src.handlers.agent_orchestrator")
    @patch("src.middleware.AUTHORIZED_USERS", [12345])
    @patch("src.utils.send_progress_message")
    @patch("src.utils.update_progress_message")
    @patch("src.integrations.cleanup_helper.DelegadoNotionClient")
    async def test_rollback_on_drive_failure(self, mock_notion_client_cls, mock_update_prog, mock_send_prog, mock_orchestrator, mock_drive, mock_notion):
        # Setup
        mock_notion_client = mock_notion_client_cls.return_value
        mock_notion_client.delete_page.return_value = True
        
        update = MagicMock()
        update.effective_user.id = 12345
        update.effective_user.first_name = "User"
        update.effective_chat.id = 123
        update.message.reply_text = AsyncMock()
        
        context = MagicMock()
        context.args = ["Contexto"]
        
        # Mock Agent
        mock_agent = MagicMock()
        mock_agent.generate_structured_draft_with_retry = AsyncMock(return_value={
            "summary": "Summary",
            "content": "This is a long content to pass validation check > 50 chars."
        })
        mock_orchestrator.get_agent_for_command.return_value = mock_agent
        
        # Mock Notion success
        valid_uuid = "00000000-0000-0000-0000-000000000000"
        mock_notion.create_case_page.return_value = valid_uuid
        
        # Mock Drive FAILURE
        mock_drive.service = True
        mock_drive.create_case_folder.side_effect = Exception("Drive API Error")
        
        # Action
        await denuncia_handler(update, context)
        
        # VERIFY ROLLBACK
        # 1. Notion Client (cleanup helper) should have been called to delete the page
        mock_notion_client.delete_page.assert_called_once_with(valid_uuid)
        
        # 2. Final message should contain rollback report
        reply_args = update.message.reply_text.call_args_list
        last_reply = reply_args[-1].args[0]
        
        self.assertIn("Error Crítico en 'Drive Structure'", last_reply)
        self.assertIn("Drive API Error", last_reply)
        self.assertIn("Revirtiendo cambios: Página de Notion eliminada", last_reply)

if __name__ == "__main__":
    unittest.main()
