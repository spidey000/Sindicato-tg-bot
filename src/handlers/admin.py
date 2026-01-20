"""
Marxnager Telegram Bot - Administrative Commands

This module contains administrative commands that provide system information
and bot management functionality.

Commands:
- /log: Download system logs (admin only)
- /start: Initialize bot or handle deep linking for case editing
- /help: Display help message with all available commands
"""

import io
from telegram import Update
from telegram.ext import ContextTypes
from src.middleware import restricted
from src.utils import get_logs
from src.session_manager import session_manager
from src.middleware import logger
from src.utils.monitoring import api_metrics


@restricted
async def metrics_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Handler for the /metrics command.
    Displays API performance metrics including success rates, latency, and errors.

    Usage: /metrics [minutes]

    Args:
        minutes: Optional time window in minutes (default: 60)

    This command is restricted to authorized users only.
    """
    # Parse optional minutes argument
    minutes = 60
    if context.args and context.args[0].isdigit():
        minutes = int(context.args[0])

    await update.message.reply_text(f"📊 Recopilando métricas de los últimos {minutes} minutos...")

    # Get metrics
    metrics = api_metrics.get_all_metrics(minutes)

    # Build response
    response_lines = [f"📊 *MÉTRICAS API* (Últimos {minutes} minutos)\n"]

    if not metrics:
        response_lines.append("_No hay datos de llamadas a la API en este período._")
    else:
        for api_name, api_metrics_data in metrics.items():
            response_lines.append(f"\n🔹 *{api_name.upper()}*")

            # Success rate
            success_rate = api_metrics_data['success_rate']
            if success_rate is not None:
                emoji = "✅" if success_rate >= 90 else "⚠️" if success_rate >= 70 else "❌"
                response_lines.append(f"  {emoji} Tasa de éxito: {success_rate:.1f}%")
            else:
                response_lines.append("  ℹ️ Sin datos")

            # Latency
            avg_latency = api_metrics_data['avg_latency_ms']
            if avg_latency is not None:
                response_lines.append(f"  ⏱️ Latencia media: {avg_latency:.0f}ms")

            # Errors
            error_summary = api_metrics_data['error_summary']
            if error_summary:
                response_lines.append(f"  ❌ Errores:")
                for error_type, count in error_summary.items():
                    response_lines.append(f"     • {error_type}: {count}")

            # Rate limits
            rate_limits = api_metrics_data['rate_limit_hits']
            if rate_limits > 0:
                response_lines.append(f"  🚨 Límites de tasa: {rate_limits}")

    response = "\n".join(response_lines)

    # Also log to console for admin visibility
    api_metrics.log_summary(minutes)

    await update.message.reply_text(response, parse_mode='Markdown')


@restricted
async def log_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Handler for the /log command.
    Retrieves the system logs (last 10MB) and sends them as a file attachment.

    Usage: /log

    This command is restricted to authorized users only.
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
    """
    Handler for the /start command.

    Handles two scenarios:
    1. Deep Linking: /start case_<ID> links user to an existing case for editing
    2. Standard start: Displays welcome message with available commands

    Usage:
    - /start
    - /start case_D-2026-001 (deep link)
    """
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
    """
    Handler for the /help command.
    Displays comprehensive help message with all available commands and features.

    Usage: /help
    """
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
        "• `/metrics [minutos]` → (Admin) Métricas de rendimiento de la API.\n"
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


__all__ = ['metrics_command', 'log_command', 'start', 'help_command']
