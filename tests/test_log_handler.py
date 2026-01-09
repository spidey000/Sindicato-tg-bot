import unittest
from unittest.mock import MagicMock, patch, AsyncMock
from src import handlers
import io

class TestLogHandler(unittest.IsolatedAsyncioTestCase):
    @patch("src.handlers.get_logs")
    @patch("src.middleware.AUTHORIZED_USERS", [12345])
    async def test_log_command_success(self, mock_get_logs):
        # Setup
        update = MagicMock()
        update.effective_user.id = 12345
        update.message.reply_document = AsyncMock()
        update.message.reply_text = AsyncMock()
        
        context = MagicMock()
        
        # Mock logs
        mock_get_logs.return_value = "Fake Log Content"
        
        # Action
        # We need to ensure log_command is importable from handlers
        # Assuming the function will be named 'log_command'
        await handlers.log_command(update, context)
        
        # Verify
        mock_get_logs.assert_called_once()
        update.message.reply_document.assert_called_once()
        
        # Verify document content
        call_args = update.message.reply_document.call_args
        document = call_args[1]['document']
        self.assertIsInstance(document, io.BytesIO)
        self.assertEqual(document.getvalue(), b"Fake Log Content")
        self.assertEqual(call_args[1]['filename'], "system.log")

    @patch("src.handlers.get_logs")
    @patch("src.middleware.AUTHORIZED_USERS", [12345])
    async def test_log_command_empty(self, mock_get_logs):
        # Setup
        update = MagicMock()
        update.effective_user.id = 12345
        update.message.reply_text = AsyncMock()
        
        context = MagicMock()
        
        # Mock empty logs
        mock_get_logs.return_value = None
        
        # Action
        await handlers.log_command(update, context)
        
        # Verify
        mock_get_logs.assert_called_once()
        update.message.reply_text.assert_called_with("No logs found or empty.")

if __name__ == "__main__":
    unittest.main()
