import unittest
from unittest.mock import MagicMock, patch, AsyncMock
from src.handlers import denuncia_handler

class TestProgressIntegration(unittest.IsolatedAsyncioTestCase):
    @patch("src.handlers.notion")
    @patch("src.handlers.drive")
    @patch("src.handlers.docs")
    @patch("src.handlers.agent_orchestrator")
    @patch("src.middleware.AUTHORIZED_USERS", [12345])
    @patch("src.handlers.send_progress_message", new_callable=AsyncMock)
    @patch("src.handlers.update_progress_message", new_callable=AsyncMock)
    @patch("src.handlers.generate_case_id")
    async def test_denuncia_handler_progress_flow(self, mock_gen_id, mock_update_prog, mock_send_prog, mock_orchestrator, mock_docs, mock_drive, mock_notion):
        # Setup
        update = MagicMock()
        update.effective_user.id = 12345
        update.message.reply_text = AsyncMock()
        context = MagicMock()
        context.args = ["test"]
        
        mock_gen_id.return_value = "D-2026-001"
        mock_send_prog.return_value = 999
        
        mock_agent = MagicMock()
        mock_agent.generate_structured_draft_with_retry.return_value = {"summary": "Test", "content": "Content"}
        mock_agent.verify_draft_content = AsyncMock(return_value=None)
        mock_orchestrator.get_agent_for_command.return_value = mock_agent
        
        # Mock IDs
        mock_notion.get_last_case_id.return_value = None
        mock_notion.create_case_page.return_value = "000-page-id"
        mock_drive.service = True
        mock_drive.create_case_folder.return_value = ("https://drive.com/folder", "folder-id")
        mock_docs.service = True
        mock_docs.create_draft_document.return_value = "https://docs.com/doc"
        
        # Action
        await denuncia_handler(update, context)
        
        # Verify progress was updated multiple times
        # Initialization, Drafting, Notion Entry, Drive Structure, Perplexity Check, Refinement, Docs Creation, Finalization
        # Each step has start and complete. So around 16 calls to update_progress_message + initial send.
        self.assertGreater(mock_update_prog.call_count, 10)
        
        # Verify the last call contains all steps completed
        last_call_args = mock_update_prog.call_args[0]
        steps_status = last_call_args[3]
        
        step_names = [s[0] for s in steps_status]
        self.assertIn("Perplexity Check", step_names)
        self.assertIn("Finalization", step_names)
        
        # All steps should be completed in a successful run
        for s in steps_status:
            self.assertEqual(s[1], "completed", f"Step {s[0]} should be completed")

if __name__ == "__main__":
    unittest.main()