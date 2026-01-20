"""
Marxnager Telegram Bot - Email Handler

This module handles the /email command for creating corporate HR communications
(emails to RRHH - Recursos Humanos).

The handler delegates to the unified execute_document_pipeline() function which
implements a 7-step pipeline:
1. Initialization - Generate case ID and load template
2. Research - Query Perplexity AI for context
3. Document Generation - Generate document via OpenRouter LLM
4. Drive Structure - Create Google Drive folder
5. Docs Creation - Create editable Google Doc with generated content
6. Notion Entry - Create Notion database entry with links and content
7. Finalization - Send Telegram summary card

Case ID Format: E-2026-XXX (E for Email)
"""

from telegram import Update
from telegram.ext import ContextTypes

from src.middleware import restricted
from src.pipeline import execute_document_pipeline


@restricted
async def email_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Handler for the /email command.

    Creates a corporate HR communication workflow including:
    - Context research via Perplexity AI
    - Email generation via OpenRouter (DeepSeek R1 → Gemma 3 fallback)
    - Google Drive folder creation
    - Google Doc creation for collaborative editing
    - Notion database entry with links and content
    - Telegram summary

    Usage: /email [asunto] [mensaje]
    Example: /email Solicitud Vacaciones Pedir el calendario anual

    Args:
        update: Telegram update object
        context: Telegram context object

    Raises:
        ValueError: If template loading fails or document generation fails
        Exception: Propagates API failures with automatic rollback
    """
    context_args = " ".join(context.args)
    if not context_args:
        await update.message.reply_text(
            "⚠️ Por favor, indica el asunto y el mensaje.\n"
            "Ejemplo: /email Solicitud Vacaciones Pedir el calendario anual"
        )
        return

    # Delegate to unified pipeline
    await execute_document_pipeline(update, context, "email", context_args)


__all__ = ['email_handler']
