"""
Marxnager Telegram Bot - Demanda Handler

This module handles the /demanda command for creating judicial labor demands
(demandas judiciales) in Spain.

The handler delegates to the unified execute_document_pipeline() function which
implements a 7-step pipeline:
1. Initialization - Generate case ID and load template
2. Research - Query Perplexity AI for Spanish labor law research
3. Document Generation - Generate document via OpenRouter LLM
4. Drive Structure - Create Google Drive folder with subfolders
5. Docs Creation - Create editable Google Doc with generated content
6. Notion Entry - Create Notion database entry with links and content
7. Finalization - Send Telegram summary card with deep link

Case ID Format: J-2026-XXX (J for Judicial/Demanda)
"""

from telegram import Update
from telegram.ext import ContextTypes

from src.middleware import restricted
from src.pipeline import execute_document_pipeline


@restricted
async def demanda_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Handler for the /demanda command.

    Creates a complete judicial labor demand workflow including:
    - Legal research via Perplexity AI (sonar-pro model)
    - Document generation via OpenRouter (DeepSeek R1 → Gemma 3 fallback)
    - Google Drive folder structure (Pruebas, Procedimiento subfolders)
    - Google Doc creation for collaborative editing
    - Notion database entry with links and collapsible toggles
    - Telegram summary with deep link for continued editing

    Pipeline steps:
    1. Initialization - Generate case ID (J-2026-XXX) and load demanda template
    2. Research - Perplexity researches legal grounds (verbatim)
    3. Document Generation - OpenRouter fills template with facts + research
    4. Drive Structure - Create folder with type-specific parent folder
    5. Docs Creation - Save document to Google Docs
    6. Notion Entry - Create page & dump content
    7. Finalization - Link everything

    Usage: /demanda [tipo] [hechos]
    Example: /demanda La empresa ha modificado mi turno sin previo aviso

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
            "⚠️ Por favor, describe los hechos del caso.\n"
            "Ejemplo: /demanda La empresa ha modificado mi turno sin previo aviso"
        )
        return

    # Delegate to unified pipeline
    await execute_document_pipeline(update, context, "demanda", context_args)


__all__ = ['demanda_handler']
