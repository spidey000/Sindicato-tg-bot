import unittest
from unittest.mock import MagicMock, patch, AsyncMock
from src.handlers import denuncia_handler
import datetime

class TestHandlerWiring(unittest.IsolatedAsyncioTestCase):
    @patch("src.handlers.notion")
    @patch("src.handlers.drive")
    @patch("src.handlers.docs")
    @patch("src.handlers.agent_orchestrator")
    @patch("src.middleware.AUTHORIZED_USERS", [12345])
    async def test_denuncia_handler_uses_summary(self, mock_orchestrator, mock_docs, mock_drive, mock_notion):
        # Setup
        update = MagicMock()
        update.effective_user.id = 12345
        update.effective_user.first_name = "User"
        update.message.reply_text = AsyncMock()
        
        context = MagicMock()
        context.args = ["Contexto", "del", "caso"]
        context.bot.username = "bot"
        
        # Mock Agent
        mock_agent = MagicMock()
        # Mock async verified draft generation
        mock_agent.generate_structured_draft_verified = AsyncMock(return_value={
            "summary": "Resumen IA",
            "content": "Contenido IA",
            "verification_status": "Verified"
        })
        # Fallback for old method if called
        mock_agent.generate_draft.return_value = "Old Content"
        
        mock_orchestrator.get_agent_for_command.return_value = mock_agent
        
        # Mock IDs
        mock_notion.get_last_case_id.return_value = None # Start fresh
        mock_notion.create_case_page.return_value = "page_id"
        mock_drive.service = True
        mock_drive.create_case_folder.return_value = ("link", "folder_id")
        mock_docs.service = True
        
        # Action
        await denuncia_handler(update, context)
        
        # Verify Agent called with generate_structured_draft_verified
        mock_agent.generate_structured_draft_verified.assert_called_once()
        
        # Verify Notion called with title containing summary
        args, kwargs = mock_notion.create_case_page.call_args
        case_data = args[0]
        self.assertIn("Resumen IA", case_data["title"])
        
        # Verify Drive called with summary
        mock_drive.create_case_folder.assert_called_once()
        drive_args = mock_drive.create_case_folder.call_args[0]
        self.assertIn("Resumen IA", drive_args[1]) # case_name
        
        # Verify Docs called with summary
        mock_docs.create_draft_document.assert_called_once()
        doc_args = mock_docs.create_draft_document.call_args[0]
        self.assertIn("Resumen IA", doc_args[0]) # title

if __name__ == "__main__":
    unittest.main()
