import unittest
from unittest.mock import AsyncMock, MagicMock
from src.utils import send_progress_message

class TestProgressUtils(unittest.IsolatedAsyncioTestCase):
    async def test_send_progress_message(self):
        # Mock Update object
        update = MagicMock()
        update.message.reply_text = AsyncMock()
        
        # Mock return value of reply_text
        sent_message = MagicMock()
        sent_message.message_id = 12345
        update.message.reply_text.return_value = sent_message
        
        steps = [
            "Drafting",
            "Verification",
            "Refinement"
        ]
        
        # Call function
        msg_id = await send_progress_message(update, steps)
        
        # Assertions
        self.assertEqual(msg_id, 12345)
        
        # Verify call arguments
        # Expectation: Steps formatted as strikethrough italic
        expected_text = "🔄 *Procesando solicitud...*\n\n~_Drafting_~\n~_Verification_~\n~_Refinement_~"
        update.message.reply_text.assert_called_once()
        args, kwargs = update.message.reply_text.call_args
        self.assertIn("Procesando solicitud", args[0])
        self.assertIn("~_Drafting_~", args[0])
        self.assertEqual(kwargs['parse_mode'], 'Markdown')

if __name__ == "__main__":
    unittest.main()
