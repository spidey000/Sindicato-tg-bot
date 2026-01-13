import re
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, MessageHandler, filters
from src.middleware import restricted
from src.utils import generate_case_id, get_logs, send_progress_message, update_progress_message, RollbackManager, ProgressTracker
from src.integrations.notion_client import DelegadoNotionClient
from src.integrations.drive_client import DelegadoDriveClient
from src.integrations.docs_client import DelegadoDocsClient
from src.session_manager import session_manager, SessionState
from src.agents.orchestrator import agent_orchestrator
from datetime import datetime
import io

# Initialize clients
notion = DelegadoNotionClient()
drive = DelegadoDriveClient()
docs = DelegadoDocsClient()

@restricted
async def log_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Handler for the /log command.
    Retrieves the system logs (last 10MB) and sends them as a file attachment.
    """
    await update.message.reply_text("⏳ Recuperando registros del sistema...")
    
    # Path to the log file (as defined in logging_config.py)
    log_path = "logs/bot.log"
    
    logs = get_logs(log_path)
    
    if not logs:
        await update.message.reply_text("No logs found or empty.")
        return

    # Create a file-like object in memory
    log_file = io.BytesIO(logs.encode('utf-8'))
    log_file.name = "system.log"
    
    await update.message.reply_document(
        document=log_file,
        filename="system.log",
        caption="📋 Aquí tienes los últimos registros del sistema."
    )

@restricted
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler for the /start command. Handles Deep Linking."""
    user_id = update.effective_user.id
    args = context.args

    # Check for Deep Linking (e.g., /start case_D-2026-001)
    if args and args[0].startswith("case_"):
        case_id = args[0].replace("case_", "")
        session_manager.set_active_case(user_id, case_id)
        
        await update.message.reply_text(
            f"🎯 *MODO EDICIÓN ACTIVO*\n"
            f"Te has vinculado al expediente `{case_id}`.\n\n"
            "Todo lo que envíes aquí (texto, fotos, audios) se procesará para este caso.\n"
            "Usa /stop para salir del modo edición.",
            parse_mode='Markdown'
        )
        return

    await update.message.reply_text(
        "👋 Hola, Delegado.\n\n"
        "Soy tu asistente jurídico-administrativo 'Marxnager'.\n"
        "Estoy listo para gestionar expedientes.\n\n"
        "Comandos disponibles:\n"
        "/denuncia [hechos] - Iniciar denuncia ITSS\n"
        "/demanda [tipo] - Iniciar demanda judicial\n"
        "/email [asunto] - Redactar email a RRHH"
    )

@restricted
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler for the /help command."""
    await update.message.reply_text(
        "🛠️ *CENTRO DE AYUDA MARXNAGER*\n\n"
        "Soy tu asistente sindical automatizado. Gestiono expedientes, redacto documentos y organizo pruebas.\n\n"
        "📋 *COMANDOS DISPONIBLES*\n"
        "• `/denuncia [hechos]` → Inicia denuncia ante la ITSS.\n"
        "• `/demanda [tipo] [hechos]` → Redacta demandas (despido, cantidad...).\n"
        "• `/email [asunto] [mensaje]` → Crea correos formales para RRHH.\n"
        "• `/status [ID] [estado]` → Actualiza el estado en Notion.\n"
        "• `/update` → (Privado) Lista casos activos para editar.\n"
        "• `/stop` → (Privado) Sale del modo edición.\n"
        "• `/log` → (Admin) Descarga logs del sistema.\n\n"
        "🔒 *MODO PRIVADO (EDICIÓN)*\n"
        "Cuando inicias un caso o usas `/update` en privado, entras en 'Modo Edición'.\n"
        "• Envíame *audios* con explicaciones extra.\n"
        "• Envíame *fotos* de pruebas o documentos.\n"
        "• Escribe *texto* para corregir el borrador.\n"
        "Todo se guardará automáticamente en la carpeta Drive del caso.\n\n"
        "✅ *QUÉ PUEDO HACER*\n"
        "• Redactar borradores jurídicos con IA.\n"
        "• Crear estructuras de carpetas en Drive.\n"
        "• Registrar y organizar casos en Notion.\n"
        "• Subir pruebas (fotos/audios) a la nube.\n\n"
        "❌ *QUÉ NO PUEDO HACER*\n"
        "• No presento denuncias ni demandas por ti (solo borradores).\n"
        "• No tengo firma digital ni validez legal directa.\n"
        "• No puedo ver mensajes de grupos a menos que me mencionen o usen comandos.",
        parse_mode='Markdown'
    )

@restricted
async def denuncia_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler for the /denuncia command."""
    context_args = " ".join(context.args)
    if not context_args:
        await update.message.reply_text("⚠️ Por favor, describe los hechos para iniciar la denuncia.\nEjemplo: /denuncia Falta de EPIs en el almacén")
        return

    user = update.effective_user.first_name
    
    # Define steps for progress tracking according to SPEC
    steps = [
        "Initialization",
        "Drafting",
        "Notion Entry",
        "Drive Structure",
        "Perplexity Check",
        "Refinement",
        "Docs Creation",
        "Finalization"
    ]
    tracker = ProgressTracker(steps)
    
    # Initialize progress message
    message_id = await send_progress_message(update, steps)
    chat_id = update.effective_chat.id
    rollback = RollbackManager()

    async def refresh_progress():
        await update_progress_message(context, chat_id, message_id, tracker.get_steps_status())

    try:
        # 1. Initialization (Generate ID & Title)
        tracker.start_step("Initialization")
        await refresh_progress()
        try:
            last_id = notion.get_last_case_id("D")
            case_id = generate_case_id("D", last_id)
            # We'll update the title once we have the AI summary, but we need an ID now.
            tracker.complete_step("Initialization")
            await refresh_progress()
        except Exception as e:
            tracker.fail_step("Initialization")
            await refresh_progress()
            rollback.trigger_failure("Initialization", e)
            raise e

        # 2. Drafting (AI Analysis & Draft)
        tracker.start_step("Drafting")
        await refresh_progress()
        agent = agent_orchestrator.get_agent_for_command("/denuncia")
        try:
            ai_result = await agent.generate_structured_draft_with_retry(context_args)
            summary = ai_result.get("summary", "Sin Título")
            draft_content = ai_result.get("content", "")
            
            safe_summary = re.sub(r'[<>:"/\\|?*]', '', summary).strip()
            full_title = f"{case_id} - {safe_summary}"
            
            tracker.complete_step("Drafting")
            await refresh_progress()
        except Exception as e:
            tracker.fail_step("Drafting")
            await refresh_progress()
            rollback.trigger_failure("Drafting", e)
            raise e

        # 3. Notion Entry
        tracker.start_step("Notion Entry")
        await refresh_progress()
        try:
            notion_page_id = notion.create_case_page({
                "id": case_id,
                "title": full_title,
                "type": "Denuncia ITSS",
                "status": "Borrador",
                "company": "Detectar o Pendiente",
                "created_at": datetime.now(),
                "initial_context": context_args
            })
            if not notion_page_id:
                raise ValueError("Falló la creación de la página en Notion")
            rollback.set_notion_page(notion_page_id)
            tracker.complete_step("Notion Entry")
            await refresh_progress()
        except Exception as e:
            tracker.fail_step("Notion Entry")
            await refresh_progress()
            rollback.trigger_failure("Notion Entry", e)
            raise e

        # 4. Drive Structure (Drive Folder)
        tracker.start_step("Drive Structure")
        await refresh_progress()
        try:
            drive_link, folder_id = None, None
            if drive.service:
                drive_link, folder_id = drive.create_case_folder(case_id, safe_summary, case_type="denuncia")
                if folder_id:
                    rollback.set_drive_folder(folder_id)
                    drive.create_subfolder(folder_id, "Pruebas")
                    drive.create_subfolder(folder_id, "Respuestas")
                else:
                    raise ValueError("Falló la creación de la carpeta en Drive")
            tracker.complete_step("Drive Structure")
            await refresh_progress()
        except Exception as e:
            tracker.fail_step("Drive Structure")
            await refresh_progress()
            rollback.trigger_failure("Drive Structure", e)
            raise e

        # 5. Perplexity Check
        tracker.start_step("Perplexity Check")
        await refresh_progress()
        try:
            verification_feedback = await agent.verify_draft_content(draft_content)
            tracker.complete_step("Perplexity Check")
            await refresh_progress()
        except Exception as e:
            tracker.fail_step("Perplexity Check")
            await refresh_progress()
            rollback.trigger_failure("Perplexity Check", e)
            raise e

        # 6. Refinement (Final AI polishing)
        tracker.start_step("Refinement")
        await refresh_progress()
        try:
            if verification_feedback:
                draft_content = await agent.refine_draft_with_feedback(draft_content, verification_feedback)
            tracker.complete_step("Refinement")
            await refresh_progress()
        except Exception as e:
            tracker.fail_step("Refinement")
            await refresh_progress()
            rollback.trigger_failure("Refinement", e)
            raise e

        # 7. Docs Creation (Google Doc)
        tracker.start_step("Docs Creation")
        await refresh_progress()
        try:
            doc_link = None
            if folder_id and docs.service:
                doc_link = docs.create_draft_document(full_title, draft_content, folder_id)
                if not doc_link:
                    raise ValueError("Falló la creación del documento de Google")
            tracker.complete_step("Docs Creation")
            await refresh_progress()
        except Exception as e:
            tracker.fail_step("Docs Creation")
            await refresh_progress()
            rollback.trigger_failure("Docs Creation", e)
            raise e

        # 8. Finalization
        tracker.start_step("Finalization")
        await refresh_progress()
        try:
            if notion_page_id and (drive_link or doc_link):
                notion.update_page_links(notion_page_id, drive_link, doc_link)
            tracker.complete_step("Finalization")
            await refresh_progress()
        except Exception as e:
            tracker.fail_step("Finalization")
            await refresh_progress()
            rollback.trigger_failure("Finalization", e)
            raise e

        # Final Response
        response = f"✅ *EXPEDIENTE CREADO*\n\n📋 *ID:* `{case_id}`\n📂 *Tipo:* Denuncia ITSS\n📝 *Asunto:* {safe_summary}\n👤 *Responsable:* {user}\n\n"
        
        if notion_page_id: response += f"🔗 [Ver en Notion](https://notion.so/{notion_page_id.replace('-', '')})\n"
        if drive_link: response += f"📁 [Carpeta Drive]({drive_link})\n"
        if doc_link: response += f"📄 [Borrador Doc]({doc_link})\n"

        bot_username = context.bot.username
        deep_link = f"https://t.me/{bot_username}?start=case_{case_id}"
        keyboard = [[InlineKeyboardButton("🔒 Continuar en Privado", url=deep_link)]]
        reply_markup = InlineKeyboardMarkup(keyboard)

        # Replace or follow-up with final card
        await update.message.reply_text(response, parse_mode='Markdown', reply_markup=reply_markup)

    except Exception as e:
        # Mark current pending step as failed
        tracker.fail_step(tracker.steps[0]) # Fallback if no step in progress
        for s in tracker.steps:
            if tracker.status[s] == "in_progress" or tracker.status[s] == "pending":
                tracker.fail_step(s)
                break
        await update_progress_message(context, chat_id, message_id, tracker.get_steps_status())
        
        # ROLLBACK
        rollback_report = await rollback.execute_rollback()
        await update.message.reply_text(rollback_report, parse_mode='Markdown')

@restricted
async def update_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler for /update command. Lists active cases for editing."""
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
    
    for case in cases[:10]:
        message_text += f"🔹 `{case['id']}` - {case['status']}\n"
        deep_link = f"https://t.me/{bot_username}?start=case_{case['id']}"
        keyboard.append([InlineKeyboardButton(f"✏️ Editar {case['id']}", url=deep_link)])

    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(message_text, parse_mode='Markdown', reply_markup=reply_markup)

@restricted
async def status_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler for /status command. Updates Notion status."""
    args = context.args
    if len(args) < 2:
        await update.message.reply_text("⚠️ Uso: /status [ID_CASO] [NUEVO_ESTADO]\nEjemplo: /status D-2026-001 Enviado")
        return

    case_id = args[0]
    new_status = " ".join(args[1:])

    await update.message.reply_text(f"🔄 Actualizando {case_id} a '{new_status}'...")
    
    if notion.client:
        success = notion.update_case_status(case_id, new_status)
        if success:
            await update.message.reply_text(f"✅ Estado actualizado correctamente en Notion.")
        else:
            await update.message.reply_text(f"❌ Error actualizando Notion (¿El caso existe?).")
    else:
        await update.message.reply_text(f"⚠️ No se pudo conectar con Notion.")

@restricted
async def private_message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handles messages in private chat based on session state."""
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
        if match: folder_id = match.group(1)
    
    if not folder_id:
        await update.message.reply_text("❌ No encontré la carpeta Drive vinculada a este caso en Notion.")
        return

    # 2. Handle Files (Photo, Document, Voice, Audio)
    attachment = None
    if update.message.document: attachment = update.message.document
    elif update.message.photo: attachment = update.message.photo[-1] # Highest res
    elif update.message.voice: attachment = update.message.voice
    elif update.message.audio: attachment = update.message.audio

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
                 current_content = "" # Should not happen if doc exists
                 
             # Refine
             new_content = await agent.refine_draft(current_content, text)
             
             # Update Doc
             success = docs.update_document_content(doc_id, new_content)
             
             if success:
                 await update.message.reply_text("✅ Borrador actualizado con éxito.")
             else:
                 await update.message.reply_text("❌ Error escribiendo en el documento.")
        else:
             await update.message.reply_text("❌ No encontré el documento borrador en la carpeta del caso.")

@restricted
async def stop_editing_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Exits editing mode."""
    user_id = update.effective_user.id
    session_manager.clear_session(user_id)
    await update.message.reply_text("⏹️ Has salido del modo edición.")

@restricted
async def demanda_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler for the /demanda command."""
    context_args = " ".join(context.args)
    if not context_args:
        await update.message.reply_text("⚠️ Por favor, especifica el tipo y hechos.\nEjemplo: /demanda despido Despido improcedente de Juan")
        return

    user = update.effective_user.first_name
    
    # Define steps for progress tracking
    steps = [
        "Initialization",
        "Drafting",
        "Notion Entry",
        "Drive Structure",
        "Perplexity Check",
        "Refinement",
        "Docs Creation",
        "Finalization"
    ]
    tracker = ProgressTracker(steps)
    
    # Initialize progress message
    message_id = await send_progress_message(update, steps)
    chat_id = update.effective_chat.id
    rollback = RollbackManager()

    async def refresh_progress():
        await update_progress_message(context, chat_id, message_id, tracker.get_steps_status())

    try:
        # 1. Initialization (Generate ID & Title)
        tracker.start_step("Initialization")
        await refresh_progress()
        try:
            last_id = notion.get_last_case_id("J")
            case_id = generate_case_id("J", last_id)
            tracker.complete_step("Initialization")
            await refresh_progress()
        except Exception as e:
            tracker.fail_step("Initialization")
            await refresh_progress()
            rollback.trigger_failure("Initialization", e)
            raise e

        # 2. Drafting (AI Analysis & Draft)
        tracker.start_step("Drafting")
        await refresh_progress()
        agent = agent_orchestrator.get_agent_for_command("/demanda")
        try:
            ai_result = await agent.generate_structured_draft_with_retry(context_args)
            summary = ai_result.get("summary", "Sin Título")
            draft_content = ai_result.get("content", "")
            
            safe_summary = re.sub(r'[<>:"/\\|?*]', '', summary).strip()
            full_title = f"{case_id} - {safe_summary}"
            
            tracker.complete_step("Drafting")
            await refresh_progress()
        except Exception as e:
            tracker.fail_step("Drafting")
            await refresh_progress()
            rollback.trigger_failure("Drafting", e)
            raise e

        # 3. Notion Entry
        tracker.start_step("Notion Entry")
        await refresh_progress()
        try:
            notion_page_id = notion.create_case_page({
                "id": case_id,
                "title": full_title,
                "type": "Demanda Judicial",
                "status": "Borrador",
                "created_at": datetime.now(),
                "initial_context": context_args
            })
            if not notion_page_id:
                raise ValueError("Falló la creación de la página en Notion")
            rollback.set_notion_page(notion_page_id)
            tracker.complete_step("Notion Entry")
            await refresh_progress()
        except Exception as e:
            tracker.fail_step("Notion Entry")
            await refresh_progress()
            rollback.trigger_failure("Notion Entry", e)
            raise e

        # 4. Drive Structure (Drive)
        tracker.start_step("Drive Structure")
        await refresh_progress()
        try:
            drive_link, folder_id = None, None
            if drive.service:
                drive_link, folder_id = drive.create_case_folder(case_id, safe_summary, case_type="demanda")
                if folder_id:
                    rollback.set_drive_folder(folder_id)
                    drive.create_subfolder(folder_id, "Pruebas")
                    drive.create_subfolder(folder_id, "Procedimiento")
                else:
                    raise ValueError("Falló la creación de la carpeta en Drive")
            tracker.complete_step("Drive Structure")
            await refresh_progress()
        except Exception as e:
            tracker.fail_step("Drive Structure")
            await refresh_progress()
            rollback.trigger_failure("Drive Structure", e)
            raise e

        # 5. Perplexity Check
        tracker.start_step("Perplexity Check")
        await refresh_progress()
        try:
            verification_feedback = await agent.verify_draft_content(draft_content)
            tracker.complete_step("Perplexity Check")
            await refresh_progress()
        except Exception as e:
            tracker.fail_step("Perplexity Check")
            await refresh_progress()
            rollback.trigger_failure("Perplexity Check", e)
            raise e

        # 6. Refinement
        tracker.start_step("Refinement")
        await refresh_progress()
        try:
            if verification_feedback:
                draft_content = await agent.refine_draft_with_feedback(draft_content, verification_feedback)
            tracker.complete_step("Refinement")
            await refresh_progress()
        except Exception as e:
            tracker.fail_step("Refinement")
            await refresh_progress()
            rollback.trigger_failure("Refinement", e)
            raise e

        # 7. Docs Creation
        tracker.start_step("Docs Creation")
        await refresh_progress()
        try:
            doc_link = None
            if folder_id and docs.service:
                doc_link = docs.create_draft_document(full_title, draft_content, folder_id)
                if not doc_link:
                    raise ValueError("Falló la creación del documento de Google")
            tracker.complete_step("Docs Creation")
            await refresh_progress()
        except Exception as e:
            tracker.fail_step("Docs Creation")
            await refresh_progress()
            rollback.trigger_failure("Docs Creation", e)
            raise e

        # 8. Finalization
        tracker.start_step("Finalization")
        await refresh_progress()
        try:
            if notion_page_id and (drive_link or doc_link):
                notion.update_page_links(notion_page_id, drive_link, doc_link)
            tracker.complete_step("Finalization")
            await refresh_progress()
        except Exception as e:
            tracker.fail_step("Finalization")
            await refresh_progress()
            rollback.trigger_failure("Finalization", e)
            raise e

        # Final Response
        response = f"✅ *EXPEDIENTE JUDICIAL CREADO*\n\n📋 *ID:* `{case_id}`\n⚖️ *Tipo:* Demanda\n📝 *Asunto:* {safe_summary}\n"
        
        if notion_page_id: response += f"🔗 [Ver en Notion](https://notion.so/{notion_page_id.replace('-', '')})\n"
        if drive_link: response += f"📁 [Carpeta Drive]({drive_link})\n"
        if doc_link: response += f"📄 [Borrador Doc]({doc_link})\n"

        bot_username = context.bot.username
        deep_link = f"https://t.me/{bot_username}?start=case_{case_id}"
        keyboard = [[InlineKeyboardButton("🔒 Continuar en Privado", url=deep_link)]]
        reply_markup = InlineKeyboardMarkup(keyboard)

        # Replace or follow-up with final card
        await update.message.reply_text(response, parse_mode='Markdown', reply_markup=reply_markup)

    except Exception as e:
         # Mark current pending step as failed
        for s in tracker.steps:
            if tracker.status[s] == "in_progress" or tracker.status[s] == "pending":
                tracker.fail_step(s)
                break
        await update_progress_message(context, chat_id, message_id, tracker.get_steps_status())
        
        # ROLLBACK
        rollback_report = await rollback.execute_rollback()
        await update.message.reply_text(rollback_report, parse_mode='Markdown')

@restricted
async def email_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler for the /email command."""
    context_args = " ".join(context.args)
    if not context_args:
        await update.message.reply_text("⚠️ Por favor, indica el asunto y el mensaje.\nEjemplo: /email Solicitud Vacaciones Pedir el calendario anual")
        return

    user = update.effective_user.first_name
    
    # Define steps for progress tracking
    steps = [
        "Initialization",
        "Drafting",
        "Notion Entry",
        "Drive Structure",
        "Perplexity Check",
        "Refinement",
        "Docs Creation",
        "Finalization"
    ]
    tracker = ProgressTracker(steps)
    
    # Initialize progress message
    message_id = await send_progress_message(update, steps)
    chat_id = update.effective_chat.id
    rollback = RollbackManager()

    async def refresh_progress():
        await update_progress_message(context, chat_id, message_id, tracker.get_steps_status())

    try:
        # 1. Initialization
        tracker.start_step("Initialization")
        await refresh_progress()
        try:
            last_id = notion.get_last_case_id("E")
            case_id = generate_case_id("E", last_id)
            tracker.complete_step("Initialization")
            await refresh_progress()
        except Exception as e:
            tracker.fail_step("Initialization")
            await refresh_progress()
            rollback.trigger_failure("Initialization", e)
            raise e

        # 2. Drafting (AI Analysis & Draft)
        tracker.start_step("Drafting")
        await refresh_progress()
        agent = agent_orchestrator.get_agent_for_command("/email")
        try:
            ai_result = await agent.generate_structured_draft_with_retry(context_args)
            summary = ai_result.get("summary", "Sin Título")
            draft_content = ai_result.get("content", "")
            
            safe_summary = re.sub(r'[<>:"/\\|?*]', '', summary).strip()
            full_title = f"{case_id} - {safe_summary}"
            
            tracker.complete_step("Drafting")
            await refresh_progress()
        except Exception as e:
            tracker.fail_step("Drafting")
            await refresh_progress()
            rollback.trigger_failure("Drafting", e)
            raise e

        # 3. Notion Entry
        tracker.start_step("Notion Entry")
        await refresh_progress()
        try:
            notion_page_id = notion.create_case_page({
                "id": case_id,
                "title": full_title,
                "type": "Email RRHH",
                "status": "Borrador",
                "created_at": datetime.now(),
                "initial_context": context_args
            })
            if not notion_page_id:
                raise ValueError("Falló la creación de la página en Notion")
            rollback.set_notion_page(notion_page_id)
            tracker.complete_step("Notion Entry")
            await refresh_progress()
        except Exception as e:
            tracker.fail_step("Notion Entry")
            await refresh_progress()
            rollback.trigger_failure("Notion Entry", e)
            raise e

        # 4. Drive Structure
        tracker.start_step("Drive Structure")
        await refresh_progress()
        try:
            drive_link, folder_id = None, None
            if drive.service:
                drive_link, folder_id = drive.create_case_folder(case_id, safe_summary, case_type="email")
                if folder_id:
                    rollback.set_drive_folder(folder_id)
                else:
                    raise ValueError("Falló la creación de la carpeta en Drive")
            tracker.complete_step("Drive Structure")
            await refresh_progress()
        except Exception as e:
            tracker.fail_step("Drive Structure")
            await refresh_progress()
            rollback.trigger_failure("Drive Structure", e)
            raise e

        # 5. Perplexity Check
        tracker.start_step("Perplexity Check")
        await refresh_progress()
        try:
            verification_feedback = await agent.verify_draft_content(draft_content)
            tracker.complete_step("Perplexity Check")
            await refresh_progress()
        except Exception as e:
            tracker.fail_step("Perplexity Check")
            await refresh_progress()
            rollback.trigger_failure("Perplexity Check", e)
            raise e

        # 6. Refinement
        tracker.start_step("Refinement")
        await refresh_progress()
        try:
            if verification_feedback:
                draft_content = await agent.refine_draft_with_feedback(draft_content, verification_feedback)
            tracker.complete_step("Refinement")
            await refresh_progress()
        except Exception as e:
            tracker.fail_step("Refinement")
            await refresh_progress()
            rollback.trigger_failure("Refinement", e)
            raise e

        # 7. Docs Creation
        tracker.start_step("Docs Creation")
        await refresh_progress()
        try:
            doc_link = None
            if folder_id and docs.service:
                doc_link = docs.create_draft_document(full_title, draft_content, folder_id)
                if not doc_link:
                    raise ValueError("Falló la creación del documento de Google")
            tracker.complete_step("Docs Creation")
            await refresh_progress()
        except Exception as e:
            tracker.fail_step("Docs Creation")
            await refresh_progress()
            rollback.trigger_failure("Docs Creation", e)
            raise e

        # 8. Finalization
        tracker.start_step("Finalization")
        await refresh_progress()
        try:
            if notion_page_id and (drive_link or doc_link):
                notion.update_page_links(notion_page_id, drive_link, doc_link)
            tracker.complete_step("Finalization")
            await refresh_progress()
        except Exception as e:
            tracker.fail_step("Finalization")
            await refresh_progress()
            rollback.trigger_failure("Finalization", e)
            raise e

        response = f"✅ *COMUNICACIÓN CREADA*\n\n📋 *ID:* `{case_id}`\n📧 *Tipo:* Email RRHH\n📝 *Asunto:* {safe_summary}\n"
        
        if notion_page_id: response += f"🔗 [Ver en Notion](https://notion.so/{notion_page_id.replace('-', '')})\n"
        if drive_link: response += f"📁 [Carpeta Drive]({drive_link})\n"
        if doc_link: response += f"📄 [Borrador]({doc_link})\n"

        await update.message.reply_text(response, parse_mode='Markdown')

    except Exception as e:
        for s in tracker.steps:
            if tracker.status[s] == "in_progress" or tracker.status[s] == "pending":
                tracker.fail_step(s)
                break
        await update_progress_message(context, chat_id, message_id, tracker.get_steps_status())
        
        # ROLLBACK
        rollback_report = await rollback.execute_rollback()
        await update.message.reply_text(rollback_report, parse_mode='Markdown')
    
    