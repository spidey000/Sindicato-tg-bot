import unittest
from unittest.mock import AsyncMock, MagicMock, patch
from src.handlers import denuncia_handler

class TestProgressUpdates(unittest.IsolatedAsyncioTestCase):
    @patch("src.middleware.AUTHORIZED_USERS", [123])
    @patch("src.utils.send_progress_message")
    @patch("src.utils.update_progress_message")
    @patch("src.handlers.agent_orchestrator")
    @patch("src.handlers.notion")
    @patch("src.handlers.drive")
    @patch("src.handlers.docs")
    @patch("src.utils.generate_case_id")
    async def test_progress_status_transitions(self, mock_gen_id, mock_docs, mock_drive, mock_notion, mock_orch, mock_update_progress, mock_send_progress):
        # Setup mocks
        update = MagicMock()
        update.effective_chat.id = 123
        update.effective_user.id = 123
        update.message.reply_text = AsyncMock()
        context = MagicMock()
        context.args = ["Test"]
        
        mock_send_progress.return_value = 456
        
        mock_agent = MagicMock()
        mock_orch.get_agent_for_command.return_value = mock_agent
        mock_agent.generate_structured_draft_with_retry = AsyncMock(return_value={"summary": "S", "content": "This content is definitely long enough to pass the validation check which requires more than fifty characters."})
        mock_agent.verify_draft_content = AsyncMock(return_value=None)
        
        # Ensure external services are mocked as active
        mock_drive.service = True
        mock_docs.service = True
        mock_drive.create_case_folder.return_value = ("link", "folder_id")
        mock_notion.create_case_page.return_value = "00000000-0000-0000-0000-000000000000"
        
        # Action
        await denuncia_handler(update, context)
        
        # Verify update_progress_message calls
        # We expect 16 calls (8 steps * 2 updates each: pending + completed)
        self.assertEqual(mock_update_progress.call_count, 16)
        
        # Verify the content of some calls to ensure status changes from pending to completed
        # Call 1: Initialization -> in_progress
        args1 = mock_update_progress.call_args_list[0][0]
        steps_status1 = args1[3]
        self.assertEqual(steps_status1[0][:2], ["Initialization", "in_progress"])

        # Call 2: Initialization -> completed
        args2 = mock_update_progress.call_args_list[1][0]
        steps_status2 = args2[3]
        self.assertEqual(steps_status2[0][:2], ["Initialization", "completed"])
        
        # Call 3: Drafting -> in_progress
        args3 = mock_update_progress.call_args_list[2][0]
        steps_status3 = args3[3]
        self.assertEqual(steps_status3[1][:2], ["Drafting", "in_progress"])

        # Call 4: Drafting -> completed
        args4 = mock_update_progress.call_args_list[3][0]
        steps_status4 = args4[3]
        self.assertEqual(steps_status4[1][:2], ["Drafting", "completed"])
        
        # Call 14: Docs Creation -> completed
        args14 = mock_update_progress.call_args_list[13][0]
        steps_status14 = args14[3]
        self.assertEqual(steps_status14[6][:2], ["Docs Creation", "completed"])

    @patch("src.middleware.AUTHORIZED_USERS", [123])
    @patch("src.utils.send_progress_message")
    @patch("src.utils.update_progress_message")
    @patch("src.handlers.agent_orchestrator")
    async def test_progress_failure_marking(self, mock_orch, mock_update_progress, mock_send_progress):
        # Setup mocks for failure
        update = MagicMock()
        update.effective_chat.id = 123
        update.effective_user.id = 123
        update.message.reply_text = AsyncMock()
        context = MagicMock()
        context.args = ["Test"]
        
        mock_send_progress.return_value = 456
        
        mock_orch.get_agent_for_command.side_effect = Exception("AI Error")
        
        # Action
        await denuncia_handler(update, context)
        
        # Check if update_progress_message was called with failed status
        # Since it failed at the very beginning (agent retrieval/drafting), 
        # the first step "Drafting" should be marked as failed in the catch block.
        
        last_call_args = mock_update_progress.call_args[0]
        last_steps_status = last_call_args[3]
        
        # In the exception handler:
        # for item in steps_status:
        #     if item[1] == "pending":
        #         item[1] = "failed"
        #         break
        
        self.assertEqual(last_steps_status[1], ["Drafting", "failed", None])

if __name__ == "__main__":
    unittest.main()
