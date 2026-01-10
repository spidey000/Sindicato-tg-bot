import asyncio
import os
import logging
from unittest.mock import MagicMock, AsyncMock
# We need to patch before importing handlers to ensure decorators pick it up? 
# No, decorators run at import time. But the logic inside restricted runs at call time.
from src.handlers import denuncia_handler
from src.config import AUTHORIZED_USERS

# Setup Logging
logging.basicConfig(level=logging.INFO)

async def run_e2e():
    print("--- Starting E2E Simulation ---")
    
    if not os.getenv("NOTION_TOKEN"):
        print("❌ NOTION_TOKEN missing")
        return

    # Mock Update object
    update = MagicMock()
    # Use a dummy ID and append to AUTHORIZED_USERS
    user_id = 999999999
    AUTHORIZED_USERS.append(user_id)
    
    update.effective_user.id = user_id
    update.effective_user.first_name = "E2E Tester"
    
    # Capture replies
    async def log_reply(text, **kwargs):
        print(f"🤖 Bot Reply:\n{text}\n")
        msg = MagicMock()
        msg.message_id = 12345
        return msg
    
    update.message.reply_text = AsyncMock(side_effect=log_reply)
    
    # Mock Context
    context = MagicMock()
    context.args = ["Test", "E2E", "Summary", "Generation", "Check"]
    context.bot.username = "test_bot"
    
    async def log_edit(chat_id, message_id, text, **kwargs):
        print(f"🔄 Bot Progress Update ({message_id}):\n{text}\n")
        
    context.bot.edit_message_text = AsyncMock(side_effect=log_edit)
    
    print(f"User ID: {user_id}")
    print(f"Context: {' '.join(context.args)}")
        
    print("Invoking denuncia_handler...")
    try:
        await denuncia_handler(update, context)
        print("✅ Handler executed successfully.")
    except Exception as e:
        print(f"❌ Handler failed: {e}")
        import traceback
        traceback.print_exc()
    
    print("--- E2E Simulation Complete ---")
    print("Please verify the artifacts in Notion and Drive.")

if __name__ == "__main__":
    asyncio.run(run_e2e())
