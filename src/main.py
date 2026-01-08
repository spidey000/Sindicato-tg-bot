import logging
from telegram.ext import ApplicationBuilder, CommandHandler
from src.config import BOT_TOKEN, LOG_LEVEL
from src.handlers import start, denuncia_handler, demanda_handler, email_handler

# Configure Logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=getattr(logging, LOG_LEVEL)
)
logger = logging.getLogger(__name__)

def main():
    if not BOT_TOKEN:
        logger.error("Error: BOT_TOKEN not found in environment variables.")
        return

    application = ApplicationBuilder().token(BOT_TOKEN).build()

    # Register Handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("denuncia", denuncia_handler))
    application.add_handler(CommandHandler("demanda", demanda_handler))
    application.add_handler(CommandHandler("email", email_handler))

    logger.info("Bot started. Listening for commands...")
    application.run_polling()

if __name__ == '__main__':
    main()
