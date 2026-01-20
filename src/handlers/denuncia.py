"""
Marxnager Telegram Bot - Denuncia Handler

This module handles the /denuncia command for creating ITSS (Inspección de Trabajo
y Seguridad Social) labor complaints.

The handler delegates to the unified execute_document_pipeline() function which
implements a 7-step pipeline:
1. Initialization - Generate case ID and load template
2. Research - Query Perplexity AI for Spanish labor law research
3. Document Generation - Generate document via OpenRouter LLM
4. Drive Structure - Create Google Drive folder with subfolders
5. Docs Creation - Create editable Google Doc with generated content
6. Notion Entry - Create Notion database entry with links and content
7. Finalization - Send Telegram summary card with deep link

Case ID Format: D-2026-XXX (D for Denuncia)
"""

from telegram import Update
from telegram.ext import ContextTypes

from src.middleware import restricted
from src.pipeline import execute_document_pipeline


@restricted
async def denuncia_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Handler for the /denuncia command.

    Creates a complete ITSS labor complaint workflow including:
    - Legal research via Perplexity AI
    - Document generation via OpenRouter (DeepSeek R1 → Gemma 3 fallback)
    - Google Drive folder structure (Pruebas, Respuestas subfolders)
    - Google Doc creation for collaborative editing
    - Notion database entry with links and collapsible toggles
    - Telegram summary with deep link for continued editing

    Usage: /denuncia [hechos]
    Example: /denuncia Falta de EPIs en el almacén

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
            "⚠️ Por favor, describe los hechos para iniciar la denuncia.\n"
            "Ejemplo: /denuncia Falta de EPIs en el almacén"
        )
        return

    # Delegate to unified pipeline
    await execute_document_pipeline(update, context, "denuncia", context_args)


__all__ = ['denuncia_handler']
