from telegram import Update
from telegram.ext import ContextTypes
from src.middleware import restricted

@restricted
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler for the /start command."""
    await update.message.reply_text(
        "👋 Hola, Delegado.\n\n"
        "Soy tu asistente jurídico-administrativo 'Delegado 360'.\n"
        "Estoy listo para gestionar expedientes.\n\n"
        "Comandos disponibles:\n"
        "/denuncia [hechos] - Iniciar denuncia ITSS\n"
        "/demanda [tipo] - Iniciar demanda judicial\n"
        "/email [asunto] - Redactar email a RRHH"
    )

@restricted
async def denuncia_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler for the /denuncia command."""
    context_args = " ".join(context.args)
    if not context_args:
        await update.message.reply_text("⚠️ Por favor, describe los hechos para iniciar la denuncia.\nEjemplo: /denuncia Falta de EPIs en el almacén")
        return

    await update.message.reply_text(f"📝 [Simulación] Iniciando expediente de DENUNCIA con contexto: '{context_args}'")

@restricted
async def demanda_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler for the /demanda command."""
    context_args = " ".join(context.args)
    if not context_args:
        await update.message.reply_text("⚠️ Por favor, especifica el tipo y hechos.\nEjemplo: /demanda despido Despido improcedente de Juan")
        return

    await update.message.reply_text(f"⚖️ [Simulación] Iniciando expediente de DEMANDA con contexto: '{context_args}'")

@restricted
async def email_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler for the /email command."""
    context_args = " ".join(context.args)
    if not context_args:
        await update.message.reply_text("⚠️ Por favor, indica el asunto y el mensaje.\nEjemplo: /email Solicitud Vacaciones Pedir el calendario anual")
        return

    await update.message.reply_text(f"📧 [Simulación] Redactando EMAIL con contexto: '{context_args}'")
