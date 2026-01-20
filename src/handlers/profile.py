"""
Profile Command Handler

Provides /profile command for user profile management in Marxnager.
This enables multi-user support by allowing each delegate to maintain
their own personal and employment information.

Usage:
    /profile - View your profile
    /profile set <field> <value> - Update a profile field
    /profile create - Create new profile (interactive wizard)
    /profile delete - Delete your profile
"""

import logging
from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler
from telegram.constants import ParseMode

from src.integrations.supabase_client import DelegadoSupabaseClient
from src.user_profile import UserProfile, UserProfileManager
from src.middleware import restricted

logger = logging.getLogger(__name__)

# Initialize Supabase client
supabase = DelegadoSupabaseClient()
profile_manager = UserProfileManager(supabase_client=supabase)

# Conversation states for profile creation wizard
(
    NOMBRE,
    DNI,
    EMAIL,
    TELEFONO,
    DIRECCION,
    CODIGO_POSTAL,
    CIUDAD,
    PROVINCIA,
    NAF,
    FECHA_ALTA,
    CENTRO_TRABAJO,
    PUESTO,
    EMPRESA_NOMBRE,
    EMPRESA_CIF,
    EMPRESA_DIRECCION,
    EMPRESA_CODIGO_POSTAL,
    EMPRESA_CIUDAD,
    EMPRESA_PROVINCIA,
    EMPRESA_ACTIVIDAD,
    EMPRESA_CCC,
    EMPRESA_TRABAJADORES,
    EMPRESA_HORARIO,
) = range(21)

# Field mappings for wizard
PROFILE_FIELDS = [
    ("nombre", "Nombre completo"),
    ("dni", "DNI"),
    ("email", "Email"),
    ("telefono", "Teléfono"),
    ("direccion", "Dirección"),
    ("codigo_postal", "Código Postal"),
    ("ciudad", "Ciudad"),
    ("provincia", "Provincia"),
    ("naf", "NAF (número de afiliación SS)"),
    ("fecha_alta", "Fecha de alta en la empresa (DD/MM/YYYY)"),
    ("centro_trabajo", "Centro de trabajo"),
    ("puesto", "Puesto (opcional)"),
    ("empresa_nombre", "Nombre de la empresa"),
    ("empresa_cif", "CIF de la empresa"),
    ("empresa_direccion", "Dirección de la empresa"),
    ("empresa_codigo_postal", "Código Postal de la empresa"),
    ("empresa_ciudad", "Ciudad de la empresa"),
    ("empresa_provincia", "Provincia de la empresa"),
    ("empresa_actividad", "Actividad de la empresa (opcional)"),
    ("empresa_ccc", "CCC de la empresa"),
    ("empresa_trabajadores", "Número de trabajadores"),
    ("empresa_horario", "Horario de la empresa"),
]


@restricted
async def profile_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Handle /profile command to view user profile.

    Usage:
        /profile - View current profile
        /profile set <field> <value> - Update field
        /profile create - Create new profile
        /profile delete - Delete profile

    Args:
        update: Telegram update object
        context: Telegram context object
    """
    user_id = update.effective_user.id

    # Check if Supabase is enabled
    if not supabase.is_enabled():
        await update.message.reply_text(
            "❌ *Sistema de perfiles no disponible*\n\n"
            "La función de perfiles requiere configuración de Supabase. "
            "Contacta al administrador para habilitar esta funcionalidad.",
            parse_mode=ParseMode.MARKDOWN
        )
        logger.warning(f"User {user_id} attempted to use /profile but Supabase is not configured")
        return

    # Parse arguments
    args = context.args

    if not args:
        # No arguments: show profile
        await _show_profile(update, user_id)
    elif len(args) >= 1:
        action = args[0].lower()

        if action == "set" and len(args) >= 3:
            # /profile set <field> <value>
            field = args[1].lower()
            value = " ".join(args[2:])
            await _update_profile_field(update, user_id, field, value)
        elif action == "create":
            # /profile create - Start wizard
            await _start_profile_creation(update, context)
        elif action == "delete":
            # /profile delete
            await _delete_profile(update, user_id)
        else:
            await _show_profile_help(update)


async def _show_profile(update: Update, user_id: int) -> None:
    """Display user's current profile."""
    profile = profile_manager.get_profile(user_id)

    if not profile:
        await update.message.reply_text(
            "❌ *Perfil no encontrado*\n\n"
            "No tienes un perfil configurado. Crea uno con:\n"
            "`/profile create`",
            parse_mode=ParseMode.MARKDOWN
        )
        return

    # Format profile for display
    message = profile.format_for_display()
    await update.message.reply_text(message, parse_mode=ParseMode.MARKDOWN)
    logger.info(f"User {user_id} viewed their profile")


async def _update_profile_field(update: Update, user_id: int, field: str, value: str) -> None:
    """Update a single field in user's profile."""
    # Get existing profile
    profile = profile_manager.get_profile(user_id)

    if not profile:
        await update.message.reply_text(
            "❌ *Perfil no encontrado*\n\n"
            "No tienes un perfil configurado. Crea uno con:\n"
            "`/profile create`",
            parse_mode=ParseMode.MARKDOWN
        )
        return

    # Map field name to UserProfile attribute
    field_map = {
        "nombre": "nombre",
        "dni": "dni",
        "email": "email",
        "telefono": "telefono",
        "direccion": "direccion",
        "codigo_postal": "codigo_postal",
        "cp": "codigo_postal",
        "ciudad": "ciudad",
        "provincia": "provincia",
        "naf": "naf",
        "fecha_alta": "fecha_alta",
        "centro_trabajo": "centro_trabajo",
        "puesto": "puesto",
        "empresa_nombre": "empresa_nombre",
        "empresa_cif": "empresa_cif",
        "cif": "empresa_cif",
        "empresa_direccion": "empresa_direccion",
        "empresa_codigo_postal": "empresa_codigo_postal",
        "empresa_cp": "empresa_codigo_postal",
        "empresa_ciudad": "empresa_ciudad",
        "empresa_provincia": "empresa_provincia",
        "empresa_actividad": "empresa_actividad",
        "empresa_ccc": "empresa_ccc",
        "ccc": "empresa_ccc",
        "empresa_trabajadores": "empresa_trabajadores",
        "empresa_horario": "empresa_horario",
    }

    if field not in field_map:
        await update.message.reply_text(
            f"❌ *Campo desconocido*\n\n"
            f"El campo '{field}' no existe. "
            f"Usa `/profile` para ver tu perfil y los campos disponibles.",
            parse_mode=ParseMode.MARKDOWN
        )
        return

    attr_name = field_map[field]

    # Handle numeric fields
    if attr_name == "empresa_trabajadores":
        try:
            value = int(value)
        except ValueError:
            await update.message.reply_text(
                "❌ *Valor inválido*\n\n"
                "El número de trabajadores debe ser un número entero.",
                parse_mode=ParseMode.MARKDOWN
            )
            return

    # Update the field
    setattr(profile, attr_name, value)

    # Validate and save
    is_valid, errors = profile.validate()
    if not is_valid:
        await update.message.reply_text(
            f"❌ *Validación fallida*\n\n"
            f"Los cambios causan errores de validación:\n"
            f"{chr(10).join(errors)}",
            parse_mode=ParseMode.MARKDOWN
        )
        return

    success, message = profile_manager.update_profile(profile)

    if success:
        await update.message.reply_text(
            f"✅ *Perfil actualizado*\n\n"
            f"Campo '{field}' actualizado a: {value}",
            parse_mode=ParseMode.MARKDOWN
        )
        logger.info(f"User {user_id} updated profile field {field}")
    else:
        await update.message.reply_text(
            f"❌ *Error al actualizar perfil*\n\n"
            f"{message}",
            parse_mode=ParseMode.MARKDOWN
        )


async def _start_profile_creation(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Start the profile creation wizard."""
    user_id = update.effective_user.id

    # Check if profile already exists
    existing = profile_manager.get_profile(user_id)
    if existing:
        await update.message.reply_text(
            "⚠️ *Perfil ya existe*\n\n"
            "Ya tienes un perfil configurado. Si quieres actualizarlo, usa:\n"
            "`/profile set <campo> <valor>`",
            parse_mode=ParseMode.MARKDOWN
        )
        return

    # Initialize profile data in context
    context.user_data['profile_data'] = {}

    # Send welcome message and start wizard
    await update.message.reply_text(
        "🔧 *Configuración de Perfil*\n\n"
        "Vamos a crear tu perfil. Por favor, responde a las siguientes preguntas.\n\n"
        "Puedes cancelar en cualquier momento enviando `/cancel`.\n\n"
        f"1️⃣ {PROFILE_FIELDS[0][1]}:",
        parse_mode=ParseMode.MARKDOWN
    )

    logger.info(f"User {user_id} started profile creation wizard")
    return NOMBRE


async def profile_creation_step(field_name: str, next_state: int):
    """
    Factory function to create step handlers for profile creation wizard.

    Args:
        field_name: Name of the profile field to set
        next_state: Next conversation state

    Returns:
        Async handler function
    """
    async def step_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        user_input = update.message.text.strip()

        # Store the input
        context.user_data['profile_data'][field_name] = user_input

        # Get current step index
        current_step = next_state - NOMBRE
        total_steps = len(PROFILE_FIELDS)

        if current_step < total_steps:
            # Ask next question
            field_label = PROFILE_FIELDS[current_step][1]
            await update.message.reply_text(
                f"{current_step + 1}️⃣ {field_label}:",
                parse_mode=ParseMode.MARKDOWN
            )
            return next_state
        else:
            # All fields collected, create profile
            return await _finalize_profile_creation(update, context)

    return step_handler


async def _finalize_profile_creation(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Finalize profile creation and save to Supabase."""
    user_id = update.effective_user.id
    profile_data = context.user_data.get('profile_data', {})

    # Create UserProfile object
    profile = UserProfile(
        telegram_user_id=user_id,
        telegram_username=update.effective_user.username,
        telegram_first_name=update.effective_user.first_name,
        **profile_data
    )

    # Validate
    is_valid, errors = profile.validate()
    if not is_valid:
        await update.message.reply_text(
            "❌ *Validación fallida*\n\n"
            "El perfil tiene errores:\n"
            f"{chr(10).join(errors)}\n\n"
            "Por favor, usa `/profile create` para empezar de nuevo.",
            parse_mode=ParseMode.MARKDOWN
        )
        return ConversationHandler.END

    # Save profile
    success, message = profile_manager.create_profile(profile)

    if success:
        await update.message.reply_text(
            "✅ *Perfil creado exitosamente*\n\n"
            "Tu perfil ha sido guardado. Ahora puedes generar documentos "
            "con tu información personal.\n\n"
            "Usa `/profile` para ver tu perfil.",
            parse_mode=ParseMode.MARKDOWN
        )
        logger.info(f"User {user_id} successfully created profile")
    else:
        await update.message.reply_text(
            f"❌ *Error al crear perfil*\n\n"
            f"{message}",
            parse_mode=ParseMode.MARKDOWN
        )

    # Clear user data
    context.user_data.pop('profile_data', None)
    return ConversationHandler.END


async def _delete_profile(update: Update, user_id: int) -> None:
    """Delete user's profile."""
    profile = profile_manager.get_profile(user_id)

    if not profile:
        await update.message.reply_text(
            "❌ *Perfil no encontrado*\n\n"
            "No tienes un perfil configurado.",
            parse_mode=ParseMode.MARKDOWN
        )
        return

    success, message = profile_manager.delete_profile(user_id)

    if success:
        await update.message.reply_text(
            "✅ *Perfil eliminado*\n\n"
            "Tu perfil ha sido eliminado. Si generas documentos, "
            "se usarán los datos del sistema.",
            parse_mode=ParseMode.MARKDOWN
        )
        logger.info(f"User {user_id} deleted their profile")
    else:
        await update.message.reply_text(
            f"❌ *Error al eliminar perfil*\n\n"
            f"{message}",
            parse_mode=ParseMode.MARKDOWN
        )


async def _show_profile_help(update: Update) -> None:
    """Display help message for /profile command."""
    help_text = (
        "👤 *Comando de Perfil*\n\n"
        "*Uso:*\n"
        "• `/profile` - Ver tu perfil\n"
        "• `/profile set <campo> <valor>` - Actualizar un campo\n"
        "• `/profile create` - Crear nuevo perfil (asistente)\n"
        "• `/profile delete` - Eliminar tu perfil\n\n"
        "*Campos disponibles:*\n"
        "• nombre, dni, email, telefono\n"
        "• direccion, codigo_postal, ciudad, provincia\n"
        "• naf, fecha_alta, centro_trabajo, puesto\n"
        "• empresa_nombre, empresa_cif, empresa_direccion\n"
        "• empresa_codigo_postal, empresa_ciudad, empresa_provincia\n"
        "• empresa_actividad, empresa_ccc, empresa_trabajadores, empresa_horario\n\n"
        "*Ejemplos:*\n"
        "`/profile set email nuevo@email.com`\n"
        "`/profile set telefono 612345678`\n"
        "`/profile set empresa_horario 08.00 a 17.00`"
    )
    await update.message.reply_text(help_text, parse_mode=ParseMode.MARKDOWN)


async def cancel_profile_creation(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Cancel the profile creation conversation."""
    user_id = update.effective_user.id

    await update.message.reply_text(
        "❌ *Creación de perfil cancelada*\n\n"
        "No se ha guardado ningún perfil.",
        parse_mode=ParseMode.MARKDOWN
    )

    # Clear user data
    context.user_data.pop('profile_data', None)

    logger.info(f"User {user_id} cancelled profile creation")
    return ConversationHandler.END
