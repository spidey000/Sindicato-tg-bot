from datetime import datetime
import random
import os

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
    # Format steps as strikethrough italic
    formatted_steps = "\n".join([f"~_{step}_~" for step in steps])
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
        steps_status (list of tuples): List of (step_name, status).
                                       Status can be "pending", "completed", "failed".
    """
    formatted_steps = []
    
    for step_name, status in steps_status:
        if status == "completed":
            formatted_steps.append(f"✅ **{step_name}**")
        elif status == "failed":
            formatted_steps.append(f"❌ **{step_name}**")
        else:
            formatted_steps.append(f"~_{step_name}_~")
            
    message_text = f"🔄 *Procesando solicitud...*\n\n" + "\n".join(formatted_steps)
    
    try:
        await context.bot.edit_message_text(
            chat_id=chat_id,
            message_id=message_id,
            text=message_text,
            parse_mode='Markdown'
        )
    except Exception as e:
        print(f"Error updating progress message: {e}")
