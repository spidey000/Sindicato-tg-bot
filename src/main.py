import logging
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters
from src.config import BOT_TOKEN
from src.logging_config import setup_logging
from src.handlers import (
    start, 
    denuncia_handler, 
    demanda_handler, 
    email_handler,
    private_message_handler,
    stop_editing_handler,
    status_handler,
    update_handler,
    log_command
)

logger = logging.getLogger(__name__)

def main():
    # Initialize Logging System
    setup_logging()
    
    if not BOT_TOKEN:
        logger.critical("❌ Error: BOT_TOKEN not found in environment variables.")
        return

    logger.info("🤖 Initializing Marxnager Bot...")

    application = ApplicationBuilder().token(BOT_TOKEN).build()

    # Command Handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("log", log_command))
    application.add_handler(CommandHandler("denuncia", denuncia_handler))
    application.add_handler(CommandHandler("demanda", demanda_handler))
    application.add_handler(CommandHandler("email", email_handler))
    application.add_handler(CommandHandler("stop", stop_editing_handler))
    application.add_handler(CommandHandler("status", status_handler))
    application.add_handler(CommandHandler("update", update_handler))

    # Message Handlers (Private messages, Files, etc.)
    # Catch all non-command messages in private chats
    application.add_handler(MessageHandler(
        filters.ChatType.PRIVATE & ~filters.COMMAND,
        private_message_handler
    ))

    logger.info("🚀 Bot started successfully. Listening for commands...")
    application.run_polling()

if __name__ == '__main__':
    main()
