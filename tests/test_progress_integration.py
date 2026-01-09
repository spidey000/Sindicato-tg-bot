import unittest
from unittest.mock import AsyncMock, MagicMock, patch
from src.handlers import denuncia_handler

class TestProgressIntegration(unittest.IsolatedAsyncioTestCase):
    @patch("src.middleware.AUTHORIZED_USERS", [123])
    @patch("src.handlers.send_progress_message")
    @patch("src.handlers.update_progress_message")
    @patch("src.handlers.agent_orchestrator")
    @patch("src.handlers.notion")
    @patch("src.handlers.drive")
    @patch("src.handlers.docs")
    @patch("src.handlers.generate_case_id")
    async def test_denuncia_handler_progress_flow(self, mock_gen_id, mock_docs, mock_drive, mock_notion, mock_orch, mock_update_progress, mock_send_progress):
        # Setup mocks
        update = MagicMock()
        update.effective_chat.id = 123
        update.effective_user.id = 123
        update.effective_user.first_name = "TestUser"
        update.message.reply_text = AsyncMock()
        
        context = MagicMock()
        context.args = ["Falta", "de", "EPIs"]
        
        mock_send_progress.return_value = 456 # message_id
        
        mock_agent = MagicMock()
        mock_orch.get_agent_for_command.return_value = mock_agent
        mock_agent.generate_structured_draft_verified = AsyncMock(return_value={"summary": "Resumen", "content": "Contenido"})
        mock_agent.generate_structured_draft.return_value = {"summary": "Resumen", "content": "Contenido"}
        mock_agent.verify_draft_content = AsyncMock(return_value="Feedback")
        mock_agent.refine_draft_with_feedback.return_value = "Contenido Refinado"
        
        mock_notion.get_last_case_id.return_value = "001"
        mock_gen_id.return_value = "D-2026-002"
        mock_notion.create_case_page.return_value = "notion_id"
        
        mock_drive.service = True
        mock_drive.create_case_folder.return_value = ("drive_link", "folder_id")
        
        mock_docs.service = True
        mock_docs.create_draft_document.return_value = "doc_link"
        
        # Call handler
        await denuncia_handler(update, context)
        
        # Verify send_progress_message was called
        mock_send_progress.assert_called_once()
        
        # Verify update_progress_message was called multiple times (for each step)
        # Sequence: Drafting, Initialization, Database Entry, File Structure, Verification, Refinement, Docs Creation
        # (Total 7 steps)
        self.assertGreaterEqual(mock_update_progress.call_count, 7)
        
        # Verify final response was sent (using edit or new message as per final step)
        # The spec says "Final State: The progress message is either replaced or updated one last time"
        # In current impl it sends a NEW message. I might want to change it to EDIT the progress message.
        # But for now let's just check if it was called.
        update.message.reply_text.assert_called()

    @patch("src.middleware.AUTHORIZED_USERS", [123])
    @patch("src.handlers.send_progress_message")
    @patch("src.handlers.update_progress_message")
    @patch("src.handlers.agent_orchestrator")
    @patch("src.handlers.notion")
    @patch("src.handlers.drive")
    @patch("src.handlers.docs")
    @patch("src.handlers.generate_case_id")
    async def test_demanda_handler_progress_flow(self, mock_gen_id, mock_docs, mock_drive, mock_notion, mock_orch, mock_update_progress, mock_send_progress):
        # Setup mocks
        from src.handlers import demanda_handler
        update = MagicMock()
        update.effective_chat.id = 123
        update.effective_user.id = 123
        update.effective_user.first_name = "TestUser"
        update.message.reply_text = AsyncMock()
        
        context = MagicMock()
        context.args = ["despido", "injusto"]
        
        mock_send_progress.return_value = 456 # message_id
        
        mock_agent = MagicMock()
        mock_orch.get_agent_for_command.return_value = mock_agent
        # Ensure we expect granular calls
        mock_agent.generate_structured_draft.return_value = {"summary": "Resumen", "content": "Contenido"}
        mock_agent.verify_draft_content = AsyncMock(return_value="Feedback")
        mock_agent.refine_draft_with_feedback.return_value = "Contenido Refinado"
        
        mock_notion.get_last_case_id.return_value = "001"
        mock_gen_id.return_value = "J-2026-002"
        mock_notion.create_case_page.return_value = "notion_id"
        
        mock_drive.service = True
        mock_drive.create_case_folder.return_value = ("drive_link", "folder_id")
        
        mock_docs.service = True
        mock_docs.create_draft_document.return_value = "doc_link"
        
        # Call handler
        await demanda_handler(update, context)
        
        # Verify send_progress_message was called
        mock_send_progress.assert_called_once()
        
        # Verify update_progress_message was called multiple times (for each step)
        self.assertGreaterEqual(mock_update_progress.call_count, 7)
        
        # Verify granular agent calls
        mock_agent.generate_structured_draft.assert_called_once()
        mock_agent.verify_draft_content.assert_called_once()
        # refine_draft_with_feedback is called only if feedback exists (it does here)
        mock_agent.refine_draft_with_feedback.assert_called_once()

if __name__ == "__main__":
    unittest.main()
