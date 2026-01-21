"""
History Command Handler

Provides /history command for chronological event timeline using Supabase.
This complements Notion's active case management with historical event logging.

Usage:
    /history - Show your events from last 30 days
    /history <days> - Show events from last N days
    /history <start_date> <end_date> - Show events in date range (DD/MM/YYYY)
"""

import logging
from datetime import datetime, timedelta
from telegram import Update
from telegram.ext import ContextTypes

from src.integrations.supabase_client import DelegadoSupabaseClient
from src.middleware import restricted

logger = logging.getLogger(__name__)

# Initialize Supabase client
supabase = DelegadoSupabaseClient()


@restricted
async def history_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Handle /history command to display chronological event timeline.

    Usage:
        /history - Last 30 days
        /history 7 - Last 7 days
        /history 01/01/2026 31/01/2026 - Date range

    Args:
        update: Telegram update object
        context: Telegram context object
    """
    user_id = update.effective_user.id

    # Check if Supabase is enabled
    if not supabase.is_enabled():
        await update.message.reply_text(
            "❌ *Sistema de historial no disponible*\n\n"
            "La función de historial requiere configuración de Supabase. "
            "Contacta al administrador para habilitar esta funcionalidad.",
            parse_mode="Markdown"
        )
        logger.warning(f"User {user_id} attempted to use /history but Supabase is not configured")
        return

    # Parse arguments
    args = context.args
    events = []

    try:
        if not args:
            # No arguments: show last 30 days
            events = supabase.get_recent_events(user_id, days=30)
            date_range_text = "últimos 30 días"

        elif len(args) == 1:
            # Single argument: number of days
            try:
                days = int(args[0])
                if days <= 0:
                    raise ValueError("Days must be positive")

                events = supabase.get_recent_events(user_id, days=days)
                date_range_text = f"últimos {days} días"

            except ValueError:
                await update.message.reply_text(
                    "❌ *Formato inválido*\n\n"
                    "Uso:\n"
                    "• `/history` - Últimos 30 días\n"
                    "• `/history 7` - Últimos 7 días\n"
                    "• `/history 01/01/2026 31/01/2026` - Rango de fechas\n\n"
                    "El número de días debe ser positivo.",
                    parse_mode="Markdown"
                )
                return

        elif len(args) == 2:
            # Two arguments: date range
            try:
                start_date = datetime.strptime(args[0], "%d/%m/%Y").date()
                end_date = datetime.strptime(args[1], "%d/%m/%Y").date()

                if start_date > end_date:
                    raise ValueError("Start date must be before end date")

                events = supabase.get_events_by_date_range(start_date, end_date, user_id)

                # Format date range
                start_str = start_date.strftime("%d/%m/%Y")
                end_str = end_date.strftime("%d/%m/%Y")
                date_range_text = f"{start_str} a {end_str}"

            except ValueError as e:
                await update.message.reply_text(
                    f"❌ *Formato de fecha inválido*\n\n"
                    f"Error: {str(e)}\n\n"
                    "Uso correcto: `/history 01/01/2026 31/01/2026`\n"
                    "Formato: DD/MM/YYYY",
                    parse_mode="Markdown"
                )
                return

        else:
            # Too many arguments
            await update.message.reply_text(
                "❌ *Demasiados argumentos*\n\n"
                "Uso:\n"
                "• `/history` - Últimos 30 días\n"
                "• `/history 7` - Últimos 7 días\n"
                "• `/history 01/01/2026 31/01/2026` - Rango de fechas",
                parse_mode="Markdown"
            )
            return

        # Display events
        if not events:
            await update.message.reply_text(
                f"📋 *Historial de Eventos*\n\n"
                f"Periodo: {date_range_text}\n\n"
                f"No se encontraron eventos en este periodo.",
                parse_mode="Markdown"
            )
            return

        # Format events
        message_lines = [
            f"📋 *Historial de Eventos*",
            f"Periodo: {date_range_text}",
            f"Total: {len(events)} eventos\n"
        ]

        for event in events:
            formatted = supabase.format_event_for_display(event)
            message_lines.append(formatted)
            message_lines.append("─" * 40)  # Separator

        # Join and send
        full_message = "\n".join(message_lines)

        # Telegram message length limit is 4096 characters
        if len(full_message) > 4000:
            # Truncate and add note
            full_message = full_message[:3900] + "\n\n... (historial truncado por límite de caracteres)"

        await update.message.reply_text(full_message, parse_mode="Markdown")

        logger.info(f"User {user_id} requested history: {len(events)} events for {date_range_text}")

    except Exception as e:
        logger.error(f"Error processing /history command for user {user_id}: {e}")
        await update.message.reply_text(
            "❌ *Error al recuperar historial*\n\n"
            "Ha ocurrido un error inesperado. Por favor, intenta nuevamente "
            "o contacta al administrador.",
            parse_mode="Markdown"
        )
