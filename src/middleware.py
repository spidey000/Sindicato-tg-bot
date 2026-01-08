from functools import wraps
from telegram import Update
from telegram.ext import ContextTypes
from src.config import AUTHORIZED_USERS
import logging

logger = logging.getLogger(__name__)

def restricted(func):
    """
    Decorator that checks if the user is authorized to use the bot.
    If the user is not in the whitelist, the command is ignored or a rejection message is sent.
    """
    @wraps(func)
    async def wrapped(update: Update, context: ContextTypes.DEFAULT_TYPE, *args, **kwargs):
        user_id = update.effective_user.id
        user_name = update.effective_user.username or update.effective_user.first_name
        
        if user_id not in AUTHORIZED_USERS:
            logger.warning(f"Unauthorized access attempt by user {user_id} ({user_name})")
            # Option 1: Silent ignore (comment out the next line to enable)
            # return 
            
            # Option 2: Informative response
            await update.message.reply_text(
                "⛔ Acceso denegado.\n\n"
                "Este sistema es una herramienta interna de representación laboral. "
                "Si necesitas asesoramiento sindical, contacta con tu delegado en el centro de trabajo."
            )
            return

        logger.info(f"Authorized command from {user_id} ({user_name})")
        return await func(update, context, *args, **kwargs) 
    
    return wrapped
