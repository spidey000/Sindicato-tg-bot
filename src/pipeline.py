"""
Marxnager Telegram Bot - Unified Document Generation Pipeline

This module provides a unified pipeline for all document generation workflows
(denuncia, demanda, email). It implements a 7-step pipeline that abstracts
the common pattern while allowing handler-specific configuration.

Pipeline Steps:
1. Initialization - Generate case ID and load template
2. Research - Query Perplexity AI for Spanish labor law research
3. Document Generation - Generate document via OpenRouter LLM
4. Drive Structure - Create Google Drive folder with subfolders
5. Docs Creation - Create editable Google Doc with generated content
6. Notion Entry - Create Notion database entry with links and content
7. Finalization - Send Telegram summary card with deep link

The pipeline is designed to be:
- Atomic: Either completes all steps or rolls back completely
- Observable: Real-time progress updates via Telegram
- Resilient: Automatic rollback on any step failure
- Configurable: Handler-specific behavior via configuration dict
"""

import re
import logging
from typing import Dict, List, Optional, Callable
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from datetime import datetime

from src.utils import (
    generate_case_id,
    send_progress_message,
    update_progress_message,
    RollbackManager,
    ProgressTracker
)
from src.integrations.perplexity_client import PerplexityClient
from src.integrations.openrouter_client import OpenRouterClient
from src.template_loader import get_template_for_document_type
from src.handlers.base import notion, drive, docs, logger

# Document type configurations
DOCUMENT_CONFIGS = {
    'denuncia': {
        'case_prefix': 'D',
        'notion_type': 'Denuncia ITSS',
        'case_type': 'denuncia',
        'subfolders': ['Pruebas', 'Respuestas'],
        'min_content_length': 200,
        'response_header': 'EXPEDIENTE CREADO',
        'response_icon': '📋',
        'type_emoji': '📂',
        'type_name': 'Denuncia ITSS',
        'use_deep_link': True,
        'update_links_in_finalization': False
    },
    'demanda': {
        'case_prefix': 'J',
        'notion_type': 'Demanda Judicial',
        'case_type': 'demanda',
        'subfolders': ['Pruebas', 'Procedimiento'],
        'min_content_length': 500,
        'response_header': 'EXPEDIENTE JUDICIAL CREADO',
        'response_icon': '⚖️',
        'type_emoji': '⚖️',
        'type_name': 'Demanda',
        'use_deep_link': True,
        'update_links_in_finalization': True  # Extra link update in finalization
    },
    'email': {
        'case_prefix': 'E',
        'notion_type': 'Email RRHH',
        'case_type': 'email',
        'subfolders': [],  # No subfolders for email
        'min_content_length': 100,
        'response_header': 'COMUNICACIÓN CREADA',
        'response_icon': '✉️',
        'type_emoji': '📧',
        'type_name': 'Email RRHH',
        'use_deep_link': False,  # No deep link for emails
        'update_links_in_finalization': False
    }
}


async def execute_document_pipeline(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    document_type: str,
    context_args: str
) -> None:
    """
    Execute the unified document generation pipeline.

    This function implements the complete 7-step workflow for creating
    legal documents, from case ID generation to Telegram summary.

    Args:
        update: Telegram update object containing message and user info
        context: Telegram context object for bot interactions
        document_type: Type of document ('denuncia', 'demanda', or 'email')
        context_args: User-provided context/facts for the document

    Raises:
        ValueError: If template loading fails or document generation fails
        Exception: Propagates API failures with automatic rollback

    Pipeline Flow:
        1. Initialize: Generate case ID (D/J/E-2026-XXX) and load template
        2. Research: Query Perplexity AI for legal context
        3. Generate: Fill template via OpenRouter LLM
        4. Drive: Create Google Drive folder with subfolders
        5. Docs: Create editable Google Doc
        6. Notion: Create database entry with links and content
        7. Finalize: Send Telegram summary with deep link
    """
    # Validate document type
    if document_type not in DOCUMENT_CONFIGS:
        raise ValueError(f"Unknown document type: {document_type}")

    config = DOCUMENT_CONFIGS[document_type]
    user = update.effective_user.first_name

    # Define steps for progress tracking
    steps = [
        "Initialization",
        "Research",
        "Document Generation",
        "Drive Structure",
        "Docs Creation",
        "Notion Entry",
        "Finalization"
    ]
    tracker = ProgressTracker(steps)

    # Initialize progress message
    message_id = await send_progress_message(update, steps)
    chat_id = update.effective_chat.id
    rollback = RollbackManager()

    async def refresh_progress():
        """Helper to update progress message with current status."""
        await update_progress_message(context, chat_id, message_id, tracker.get_steps_status())

    # Initialize AI clients
    pplx_client = PerplexityClient()
    openrouter_client = OpenRouterClient()

    # Pipeline state
    case_id = None
    template = None
    research = None
    draft_content = None
    safe_summary = None
    full_title = None
    drive_link = None
    folder_id = None
    doc_link = None
    notion_page_id = None

    try:
        # ========== STEP 1: INITIALIZATION ==========
        tracker.start_step("Initialization")
        await refresh_progress()
        try:
            last_id = notion.get_last_case_id(config['case_prefix'])
            case_id = generate_case_id(config['case_prefix'], last_id)

            # Load template
            template = get_template_for_document_type(document_type)
            if not template:
                raise ValueError(f"No se pudo cargar la plantilla de {document_type}")

            tracker.complete_step("Initialization")
            await refresh_progress()
        except Exception as e:
            tracker.fail_step("Initialization")
            await refresh_progress()
            rollback.trigger_failure("Initialization", e)
            raise e

        # ========== STEP 2: RESEARCH (PERPLEXITY) ==========
        tracker.start_step("Research")
        await refresh_progress()
        try:
            research = await pplx_client.research_case(context_args, document_type=document_type)
            if not research:
                raise ValueError(f"Perplexity no pudo completar la investigación para {document_type}")
            tracker.complete_step("Research")
            await refresh_progress()
        except Exception as e:
            tracker.fail_step("Research")
            await refresh_progress()
            rollback.trigger_failure("Research", e)
            raise e

        # ========== STEP 3: DOCUMENT GENERATION ==========
        tracker.start_step("Document Generation")
        await refresh_progress()
        try:
            draft_content = await openrouter_client.generate_from_template(
                template=template,
                context=context_args,
                research=research
            )
            if not draft_content or len(draft_content) < config['min_content_length']:
                raise ValueError("El documento generado es demasiado corto")

            # Generate safe summary for folder title
            summary = context_args[:80].replace('\n', ' ') + "..." if len(context_args) > 80 else context_args
            safe_summary = re.sub(r'[<>:"/\\|?*]', '', summary).strip()
            full_title = f"{case_id} - {safe_summary}"

            tracker.complete_step("Document Generation")
            await refresh_progress()
        except Exception as e:
            tracker.fail_step("Document Generation")
            await refresh_progress()
            rollback.trigger_failure("Document Generation", e)
            raise e

        # ========== STEP 4: DRIVE STRUCTURE ==========
        tracker.start_step("Drive Structure")
        await refresh_progress()
        try:
            drive_link, folder_id = None, None
            if not drive.service:
                logger.warning("Drive service not initialized. Skipping Drive creation.")
                tracker.fail_step("Drive Structure")
            else:
                drive_link, folder_id = drive.create_case_folder(
                    case_id,
                    safe_summary,
                    case_type=config['case_type']
                )
                if folder_id:
                    rollback.set_drive_folder(folder_id)
                    # Create subfolders if configured
                    for subfolder in config['subfolders']:
                        drive.create_subfolder(folder_id, subfolder)
                    tracker.complete_step("Drive Structure")
                else:
                    raise ValueError("Falló la creación de la carpeta en Drive")

            await refresh_progress()
        except Exception as e:
            tracker.fail_step("Drive Structure")
            await refresh_progress()
            rollback.trigger_failure("Drive Structure", e)
            logger.error(f"Drive step failed: {e}")

        # ========== STEP 5: DOCS CREATION ==========
        tracker.start_step("Docs Creation")
        await refresh_progress()
        try:
            doc_link = None
            if not docs.service:
                logger.warning("Docs service not initialized. Skipping Doc creation.")
                tracker.fail_step("Docs Creation")
            elif not folder_id:
                logger.warning("No Drive folder available. Skipping Doc creation.")
                tracker.fail_step("Docs Creation")
            else:
                doc_link = docs.create_draft_document(full_title, draft_content, folder_id)
                if doc_link:
                    tracker.complete_step("Docs Creation")
                else:
                    raise ValueError("Falló la creación del documento de Google")

            await refresh_progress()
        except Exception as e:
            tracker.fail_step("Docs Creation")
            await refresh_progress()
            rollback.trigger_failure("Docs Creation", e)
            logger.error(f"Docs step failed: {e}")

        # ========== STEP 6: NOTION ENTRY ==========
        tracker.start_step("Notion Entry")
        await refresh_progress()
        try:
            notion_page_id = notion.create_case_page({
                "id": case_id,
                "title": full_title,
                "type": config['notion_type'],
                "status": "Borrador",
                "created_at": datetime.now(),
                "initial_context": context_args
            })
            if not notion_page_id:
                raise ValueError("Falló la creación de la página en Notion")
            rollback.set_notion_page(notion_page_id)

            # Update links immediately
            if drive_link or doc_link:
                notion.update_page_links(notion_page_id, drive_link, doc_link)

            # Append content blocks
            try:
                if research or draft_content:
                    notion.append_content_blocks(notion_page_id, research, draft_content)
            except Exception as e:
                logger.error(f"Failed to append content blocks: {e}")

            tracker.complete_step("Notion Entry")
            await refresh_progress()
        except Exception as e:
            tracker.fail_step("Notion Entry")
            await refresh_progress()
            rollback.trigger_failure("Notion Entry", e)
            raise e

        # ========== STEP 7: FINALIZATION ==========
        tracker.start_step("Finalization")
        await refresh_progress()
        try:
            # Some document types (e.g., demanda) update links again in finalization
            if config['update_links_in_finalization'] and notion_page_id:
                if drive_link or doc_link:
                    notion.update_page_links(notion_page_id, drive_link, doc_link)

            tracker.complete_step("Finalization")
            await refresh_progress()
        except Exception as e:
            tracker.fail_step("Finalization")
            await refresh_progress()
            rollback.trigger_failure("Finalization", e)
            raise e

        # ========== FINAL RESPONSE ==========
        response = (
            f"✅ *{config['response_header']}*\n\n"
            f"📋 *ID:* `{case_id}`\n"
            f"{config['type_emoji']} *Tipo:* {config['type_name']}\n"
            f"📝 *Asunto:* {safe_summary}"
        )

        if user:
            response += f"\n👤 *Responsable:* {user}"

        response += "\n"

        if notion_page_id:
            response += f"🔗 [Ver en Notion](https://notion.so/{notion_page_id.replace('-', '')})\n"

        if drive_link:
            response += f"📁 [Carpeta Drive]({drive_link})\n"
        else:
            response += "❌ Carpeta Drive\n"

        if doc_link:
            response += f"📄 [Borrador Doc]({doc_link})\n"
        else:
            response += "❌ Borrador Doc\n"

        # Add deep link button for document types that support it
        reply_markup = None
        if config['use_deep_link']:
            bot_username = context.bot.username
            deep_link = f"https://t.me/{bot_username}?start=case_{case_id}"
            keyboard = [[InlineKeyboardButton("🔒 Continuar en Privado", url=deep_link)]]
            reply_markup = InlineKeyboardMarkup(keyboard)

        await update.message.reply_text(response, parse_mode='Markdown', reply_markup=reply_markup)

    except Exception as e:
        logger.error(f"execute_document_pipeline failed for {document_type}: {e}", exc_info=True)

        # Mark current pending step as failed
        for s in tracker.steps:
            if tracker.status[s] == "in_progress" or tracker.status[s] == "pending":
                tracker.fail_step(s)
                break
        await update_progress_message(context, chat_id, message_id, tracker.get_steps_status())

        # Execute rollback
        rollback_report = await rollback.execute_rollback()
        await update.message.reply_text(rollback_report, parse_mode='Markdown')

        raise e


__all__ = ['execute_document_pipeline', 'DOCUMENT_CONFIGS']
