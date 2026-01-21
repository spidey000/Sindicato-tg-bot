"""
Marxnager Telegram Bot - Status and Update Handlers

This module contains handlers for case management commands:
- /status: Update Notion case status
- /update: List active cases for editing (private chat only)
"""

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

from src.middleware import restricted
from src.handlers.base import notion
from src.integrations.supabase_client import DelegadoSupabaseClient
import logging

logger = logging.getLogger(__name__)
supabase = DelegadoSupabaseClient()


@restricted
async def update_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Handler for /update command. Lists active cases for editing.

    This command is only available in private chat. It displays all cases
    that are not in "Presentada" status, allowing delegates to quickly
    access them for editing via deep links.

    Usage: /update

    The handler:
    1. Validates chat is private (returns error if in group)
    2. Queries Notion for active cases (status != "Presentada")
    3. Displays list with inline keyboard deep links
    4. Each link uses /start case_<ID> format for reconnection
    """
    if update.effective_chat.type != "private":
        await update.message.reply_text("⚠️ Este comando solo está disponible en chat privado.")
        return

    await update.message.reply_text("🔄 Consultando expedientes activos...")

    cases = notion.get_active_cases()

    if not cases:
        await update.message.reply_text("📂 No tienes expedientes activos para editar.")
        return

    keyboard = []
    message_text = "📂 *TUS CASOS ACTIVOS*\nSelecciona uno para editar:\n\n"

    bot_username = context.bot.username

    for case in cases[:10]:  # Limit to first 10 cases
        message_text += f"🔹 `{case['id']}` - {case['status']}\n"
        deep_link = f"https://t.me/{bot_username}?start=case_{case['id']}"
        keyboard.append([InlineKeyboardButton(f"✏️ Editar {case['id']}", url=deep_link)])

    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(message_text, parse_mode='Markdown', reply_markup=reply_markup)


@restricted
async def status_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Handler for /status command. Updates Notion case status.

    Allows delegates to manually update the status of a case in Notion.

    Usage: /status [ID_CASO] [NUEVO_ESTADO]
    Example: /status D-2026-001 Enviado

    Args:
        update: Telegram update object
        context: Telegram context object with args [case_id, new_status]

    The handler:
    1. Validates command has at least 2 arguments (ID + status)
    2. Extracts case_id and new_status from args
    3. Calls Notion API to update the case
    4. Returns success or error message
    """
    args = context.args
    if len(args) < 2:
        await update.message.reply_text(
            "⚠️ Uso: /status [ID_CASO] [NUEVO_ESTADO]\n"
            "Ejemplo: /status D-2026-001 Enviado"
        )
        return

    case_id = args[0]
    new_status = " ".join(args[1:])

    await update.message.reply_text(f"🔄 Actualizando {case_id} a '{new_status}'...")

    if notion.client:
        success = notion.update_case_status(case_id, new_status)
        if success:
            await update.message.reply_text("✅ Estado actualizado correctamente en Notion.")

            # Log status update event to Supabase
            if supabase.is_enabled():
                try:
                    user_id = update.effective_user.id
                    event_text = f"Estado de caso {case_id} actualizado a '{new_status}'"
                    supabase.log_event(
                        user_id=user_id,
                        event_text=event_text,
                        case_id=case_id,
                        event_type="status_update"
                    )
                    logger.info(f"Logged status update event to Supabase for case {case_id}")
                except Exception as e:
                    logger.error(f"Failed to log status update to Supabase: {e}")
        else:
            await update.message.reply_text("❌ Error actualizando Notion (¿El caso existe?).")
    else:
        await update.message.reply_text("⚠️ No se pudo conectar con Notion.")


__all__ = ['status_handler', 'update_handler']
