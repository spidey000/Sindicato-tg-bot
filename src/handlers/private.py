"""
Marxnager Telegram Bot - Private Message Handlers

This module handles private chat messages for document refinement and file uploads.
It implements the "editing loop" that allows delegates to iteratively improve
generated documents.

Handlers:
- private_message_handler: Processes text and file uploads when in EDITING_CASE state
- stop_editing_handler: Exits editing mode and clears session state

Supported file types:
- Photos: Uploaded to Drive Pruebas folder
- Documents: Uploaded to Drive Pruebas folder
- Voice messages: Uploaded as audio files
- Audio files: Uploaded to Drive

Text refinement workflow:
1. User sends text feedback in private chat while in EDITING_CASE state
2. Handler identifies appropriate agent based on case ID prefix
3. Agent reads current document content from Google Docs
4. Agent refines content based on user feedback
5. Handler updates Google Doc with new content
"""

import re
from datetime import datetime
from telegram import Update
from telegram.ext import ContextTypes

from src.middleware import restricted
from src.session_manager import session_manager, SessionState
from src.agents.orchestrator import agent_orchestrator
from src.handlers.base import notion, drive, docs


@restricted
async def private_message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Handles messages in private chat based on session state.

    This handler is the core of the document refinement workflow. When a user
    is in EDITING_CASE state, it processes:

    1. File uploads (photos, documents, voice, audio) → uploads to Drive Pruebas folder
    2. Text messages → refines document using appropriate agent persona

    The workflow:
    - Gets active case ID from session
    - Extracts Drive folder ID from Notion case links
    - Routes files to Drive upload handler
    - Routes text to agent refinement handler

    Only processes messages when user is in EDITING_CASE state.
    """
    user_id = update.effective_user.id
    session = session_manager.get_session(user_id)

    if session["state"] != SessionState.EDITING_CASE:
        return

    case_id = session["active_case_id"]

    # 1. Get Folder ID from Notion
    links = notion.get_case_links(case_id)
    drive_url = links.get("drive_url")
    folder_id = None
    if drive_url:
        match = re.search(r"folders/([a-zA-Z0-9-_]+)", drive_url)
        if match:
            folder_id = match.group(1)

    if not folder_id:
        await update.message.reply_text(
            "❌ No encontré la carpeta Drive vinculada a este caso en Notion."
        )
        return

    # 2. Handle Files (Photo, Document, Voice, Audio)
    attachment = None
    if update.message.document:
        attachment = update.message.document
    elif update.message.photo:
        attachment = update.message.photo[-1]  # Highest resolution
    elif update.message.voice:
        attachment = update.message.voice
    elif update.message.audio:
        attachment = update.message.audio

    if attachment:
        try:
            await update.message.reply_text("⏳ Procesando archivo...")
            file_obj = await attachment.get_file()

            # Determine filename
            original_name = getattr(attachment, 'file_name', None)
            if not original_name:
                ext = ".jpg" if update.message.photo else ".ogg" if update.message.voice else ""
                original_name = f"upload_{datetime.now().strftime('%Y%m%d_%H%M%S')}{ext}"

            byte_array = await file_obj.download_as_bytearray()

            # Upload to Drive
            link = drive.upload_file(byte_array, original_name, folder_id)

            if link:
                await update.message.reply_text(f"✅ Archivo guardado: {link}")
            else:
                await update.message.reply_text("❌ Error al subir archivo a Drive.")
        except Exception as e:
            await update.message.reply_text(f"❌ Error procesando archivo: {e}")
        return

    # 3. Handle Text (Refinement)
    text = update.message.text
    if text:
        await update.message.reply_text("⏳ Analizando nueva información y refinando borrador...")
        doc_id = drive.find_doc_in_folder(folder_id)

        if doc_id:
            # Identify Agent based on Case ID prefix
            prefix = case_id.split("-")[0]
            command_map = {"D": "/denuncia", "J": "/demanda", "E": "/email"}
            command = command_map.get(prefix, "/denuncia")

            agent = agent_orchestrator.get_agent_for_command(command)

            # Read current content
            current_content = docs.read_document_content(doc_id)
            if not current_content:
                current_content = ""  # Should not happen if doc exists

            # Refine
            new_content = agent.refine_draft(current_content, text)

            # Update Doc
            success = docs.update_document_content(doc_id, new_content)

            if success:
                await update.message.reply_text("✅ Borrador actualizado con éxito.")
            else:
                await update.message.reply_text("❌ Error escribiendo en el documento.")
        else:
            await update.message.reply_text(
                "❌ No encontré el documento borrador en la carpeta del caso."
            )


@restricted
async def stop_editing_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Exits editing mode for the current user.

    Clears the active case from the user's session, returning them to
    the default state where commands can be used normally.

    Usage: /stop

    This command is only useful in private chat when in EDITING_CASE state.
    """
    user_id = update.effective_user.id
    session_manager.clear_session(user_id)
    await update.message.reply_text("⏹️ Has salido del modo edición.")


__all__ = ['private_message_handler', 'stop_editing_handler']
