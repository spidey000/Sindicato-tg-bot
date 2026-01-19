import time
from datetime import datetime
import random
import os
from telegram.error import BadRequest
import logging

logger = logging.getLogger(__name__)

class ProgressTracker:
    """
    Manages the state and timing of multiple execution steps.
    """
    def __init__(self, steps: list):
        self.steps = steps
        self.status = {step: "pending" for step in steps}
        self.start_times = {}
        self.elapsed_times = {}

    def start_step(self, step_name: str):
        if step_name in self.status:
            self.status[step_name] = "in_progress"
            self.start_times[step_name] = time.time()
            logger.info(f"⏳ Starting step: {step_name}")

    def complete_step(self, step_name: str):
        if step_name in self.status:
            self.status[step_name] = "completed"
            if step_name in self.start_times:
                elapsed = time.time() - self.start_times[step_name]
                self.elapsed_times[step_name] = f"{elapsed:.1f}s"
            logger.info(f"✅ Completed step: {step_name} in {self.elapsed_times.get(step_name, '0s')}")

    def fail_step(self, step_name: str):
        if step_name in self.status:
            self.status[step_name] = "failed"
            logger.error(f"❌ Failed step: {step_name}")

    def get_steps_status(self) -> list:
        """
        Returns a list of [step_name, status, elapsed] for all steps.
        """
        result = []
        for step in self.steps:
            status = self.status[step]
            elapsed = self.elapsed_times.get(step)
            result.append([step, status, elapsed])
        return result

def generate_case_id(type_prefix="D", last_id=None):
    """
    Generates a case ID like D-2026-001.
    If last_id is provided (e.g., 'D-2026-015'), it increments the sequence.
    Otherwise, it starts at 001.
    """
    year = datetime.now().year
    
    if last_id:
        try:
            # Parse last_id: D-2026-015
            parts = last_id.split("-")
            if len(parts) == 3:
                last_year = int(parts[1])
                last_seq = int(parts[2])
                
                if last_year == year:
                    new_seq = last_seq + 1
                    return f"{type_prefix}-{year}-{new_seq:03d}"
        except ValueError:
            pass # Fallback to 001 if parse fails

    # Default / Fallback
    return f"{type_prefix}-{year}-001"

def get_logs(file_path, max_bytes=10485760):
    """
    Retrieves the content of a log file, strictly limited to the last `max_bytes`.
    Defaults to 10MB.
    
    Args:
        file_path (str): The path to the log file.
        max_bytes (int): The maximum number of bytes to read from the end of the file.

    Returns:
        str: The log content, or None if the file does not exist.
    """
    if not os.path.exists(file_path):
        return None

    try:
        file_size = os.path.getsize(file_path)
        with open(file_path, 'rb') as f:
            if file_size > max_bytes:
                f.seek(-max_bytes, 2) # Seek from end
            content = f.read()
            return content.decode('utf-8', errors='replace')
    except Exception as e:
        print(f"Error reading log file: {e}")
        return None

async def send_progress_message(update, steps):
    """
    Sends the initial progress message with all steps pending.
    
    Args:
        update: The Telegram Update object.
        steps (list): List of step descriptions (str).
        
    Returns:
        int: The message_id of the sent message.
    """
    # Format steps as pending with white square
    formatted_steps = "\n".join([f"⬜ {step}" for step in steps])
    message_text = f"🔄 *Procesando solicitud...*\n\n{formatted_steps}"
    
    sent_message = await update.message.reply_text(message_text, parse_mode='Markdown')
    return sent_message.message_id

async def update_progress_message(context, chat_id, message_id, steps_status):
    """
    Updates the existing progress message with the current status of each step.
    
    Args:
        context: The Telegram Context object.
        chat_id (int): The ID of the chat.
        message_id (int): The ID of the message to edit.
        steps_status (list of tuples): List of (step_name, status, [optional_elapsed]).
                                       Status can be "pending", "in_progress", "completed", "failed".
    """
    formatted_steps = []
    
    for item in steps_status:
        step_name = item[0]
        status = item[1]
        elapsed = item[2] if len(item) > 2 else None

        if status == "completed":
            time_info = f" `({elapsed})`" if elapsed else ""
            formatted_steps.append(f"✅ *{step_name}*{time_info}")
        elif status == "failed":
            formatted_steps.append(f"❌ *{step_name}*")
        elif status == "in_progress":
            formatted_steps.append(f"⏳ *{step_name}*")
        else: # pending
            formatted_steps.append(f"⬜ {step_name}")
            
    message_text = f"🔄 *Procesando solicitud...*\n\n" + "\n".join(formatted_steps)
    
    try:
        await context.bot.edit_message_text(
            chat_id=chat_id,
            message_id=message_id,
            text=message_text,
            parse_mode='Markdown'
        )
    except BadRequest as e:
        if str(e).startswith("Message is not modified"):
            pass
        else:
            print(f"Error updating progress message: {e}")
    except Exception as e:
        print(f"Error updating progress message: {e}")

class RollbackManager:
    """
    Manages the lifecycle of created artifacts (Notion, Drive, etc.)
    and handles automatic cleanup if a process fails.
    """
    def __init__(self):
        self.notion_page_id = None
        self.drive_folder_id = None
        self.doc_id = None
        self.failed_step = None
        self.error_message = None

    def set_notion_page(self, page_id: str):
        self.notion_page_id = page_id

    def set_drive_folder(self, folder_id: str):
        self.drive_folder_id = folder_id

    def set_doc(self, doc_id: str):
        self.doc_id = doc_id

    def trigger_failure(self, step_name: str, error: Exception):
        """Marks the point of failure."""
        self.failed_step = step_name
        self.error_message = str(error)

    async def execute_rollback(self) -> str:
        """
        Deletes all tracked artifacts and returns a detailed status message.
        """
        from src.integrations.cleanup_helper import delete_notion_page, delete_drive_object
        
        reverted_items = []
        
        # Note: Deleting a folder in Drive also deletes the Docs inside it.
        # But we track doc_id just in case or for granular reporting.
        
        if self.drive_folder_id:
            if delete_drive_object(self.drive_folder_id):
                reverted_items.append("Carpeta en Drive eliminada")
        elif self.doc_id:
            if delete_drive_object(self.doc_id):
                reverted_items.append("Documento eliminado")
        
        if self.notion_page_id:
            if delete_notion_page(self.notion_page_id):
                reverted_items.append("Página de Notion eliminada")
        
        if not reverted_items:
            rollback_summary = "No se crearon artefactos para revertir."
        else:
            rollback_summary = "Revirtiendo cambios: " + ", ".join(reverted_items) + "."
            
        final_report = (
            f"❌ **Error Crítico en '{self.failed_step}'**\n"
            f"Causa: {self.error_message}\n\n"
            f"⚠️ {rollback_summary}"
        )
        return final_report

