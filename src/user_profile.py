"""
User Profile Management for Marxnager

This module provides multi-user profile support to replace hardcoded delegate data.
It enables personalized document generation for each union delegate.

Features:
- UserProfile dataclass with complete personal and employment information
- UserProfileManager for CRUD operations with Supabase backend
- Template injection to replace [HARDCODED] markers with user-specific data
- Validation for Spanish DNI, email, and phone number formats
"""

import os
import logging
import re
from dataclasses import dataclass, field
from typing import Optional, Dict, Any, List
from datetime import datetime

logger = logging.getLogger(__name__)


@dataclass
class UserProfile:
    """
    Complete user profile for legal document generation.

    This class contains all personal and employment data needed to generate
    legal documents (denuncia, demanda, email) for a union delegate.

    Attributes:
        telegram_user_id: Telegram user ID (primary key)
        nombre: Full name (uppercase for documents)
        dni: Spanish DNI (format: XXXXXXXX-X)
        email: Email address
        telefono: Mobile phone number
        direccion: Street address with number
        codigo_postal: Postal code (5 digits)
        ciudad: City name (uppercase)
        provincia: Province name (uppercase)
        naf: Social Security affiliation number
        fecha_alta: Employment start date (DD/MM/YYYY)
        centro_trabajo: Workplace location
        puesto: Job title (optional)
        empresa_nombre: Company legal name
        empresa_cif: Company CIF (format: XXXXXXXXX-X)
        empresa_direccion: Company street address
        empresa_codigo_postal: Company postal code
        empresa_ciudad: Company city
        empresa_provincia: Company province
        empresa_actividad: Company activity description
        empresa_ccc: Company Social Security code
        empresa_trabajadores: Number of workers at company
        empresa_horario: Company working hours
    """

    # Telegram identification
    telegram_user_id: int
    telegram_username: Optional[str] = None
    telegram_first_name: Optional[str] = None

    # Personal identification
    nombre: str = ""
    dni: str = ""

    # Contact information
    email: str = ""
    telefono: str = ""

    # Address
    direccion: str = ""
    codigo_postal: str = ""
    ciudad: str = ""
    provincia: str = ""

    # Employment
    naf: str = ""
    fecha_alta: str = ""
    centro_trabajo: str = ""
    puesto: str = ""

    # Company data
    empresa_nombre: str = ""
    empresa_cif: str = ""
    empresa_direccion: str = ""
    empresa_codigo_postal: str = ""
    empresa_ciudad: str = ""
    empresa_provincia: str = ""
    empresa_actividad: str = ""
    empresa_ccc: str = ""
    empresa_trabajadores: int = 0
    empresa_horario: str = ""

    # Metadata
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    is_active: bool = True

    def validate(self) -> tuple[bool, List[str]]:
        """
        Validate profile data for required fields and formats.

        Returns:
            Tuple of (is_valid, list_of_errors)
        """
        errors = []

        # Required fields
        required_fields = {
            'nombre': self.nombre,
            'dni': self.dni,
            'email': self.email,
            'telefono': self.telefono,
            'direccion': self.direccion,
            'codigo_postal': self.codigo_postal,
            'ciudad': self.ciudad,
            'provincia': self.provincia,
            'naf': self.naf,
            'fecha_alta': self.fecha_alta,
            'centro_trabajo': self.centro_trabajo,
            'empresa_nombre': self.empresa_nombre,
            'empresa_cif': self.empresa_cif,
            'empresa_direccion': self.empresa_direccion,
            'empresa_codigo_postal': self.empresa_codigo_postal,
            'empresa_ciudad': self.empresa_ciudad,
            'empresa_provincia': self.empresa_provincia,
            'empresa_ccc': self.empresa_ccc,
        }

        for field_name, value in required_fields.items():
            if not value or str(value).strip() == "":
                errors.append(f"Campo requerido faltante: {field_name}")

        # DNI format (Spanish ID: 8 digits + letter)
        if self.dni and not re.match(r'^\d{8}-[A-Z]$', self.dni.upper()):
            errors.append(f"DNI con formato inválido: {self.dni} (esperado: XXXXXXXX-X)")

        # Email format
        if self.email and not re.match(r'^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}$', self.email):
            errors.append(f"Email con formato inválido: {self.email}")

        # Phone format (Spanish mobile: 9 digits starting with 6 or 7)
        if self.telefono and not re.match(r'^[67]\d{8}$', self.telefono):
            errors.append(f"Teléfono con formato inválido: {self.telefono} (esperado: 9 dígitos empezando por 6 o 7)")

        # Postal code format (5 digits)
        if self.codigo_postal and not re.match(r'^\d{5}$', self.codigo_postal):
            errors.append(f"Código postal inválido: {self.codigo_postal}")

        return (len(errors) == 0, errors)

    def to_dict(self) -> Dict[str, Any]:
        """Convert profile to dictionary for Supabase storage."""
        return {
            'telegram_user_id': self.telegram_user_id,
            'telegram_username': self.telegram_username,
            'telegram_first_name': self.telegram_first_name,
            'nombre': self.nombre,
            'dni': self.dni.upper(),
            'email': self.email,
            'telefono': self.telefono,
            'direccion': self.direccion,
            'codigo_postal': self.codigo_postal,
            'ciudad': self.ciudad.upper(),
            'provincia': self.provincia.upper(),
            'naf': self.naf,
            'fecha_alta': self.fecha_alta,
            'centro_trabajo': self.centro_trabajo,
            'puesto': self.puesto,
            'empresa_nombre': self.empresa_nombre,
            'empresa_cif': self.empresa_cif.upper(),
            'empresa_direccion': self.empresa_direccion,
            'empresa_codigo_postal': self.empresa_codigo_postal,
            'empresa_ciudad': self.empresa_ciudad.upper(),
            'empresa_provincia': self.empresa_provincia.upper(),
            'empresa_actividad': self.empresa_actividad,
            'empresa_ccc': self.empresa_ccc,
            'empresa_trabajadores': self.empresa_trabajadores,
            'empresa_horario': self.empresa_horario,
            'is_active': self.is_active,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'UserProfile':
        """Create UserProfile from Supabase record."""
        return cls(
            telegram_user_id=data.get('telegram_user_id', 0),
            telegram_username=data.get('telegram_username'),
            telegram_first_name=data.get('telegram_first_name'),
            nombre=data.get('nombre', ''),
            dni=data.get('dni', ''),
            email=data.get('email', ''),
            telefono=data.get('telefono', ''),
            direccion=data.get('direccion', ''),
            codigo_postal=data.get('codigo_postal', ''),
            ciudad=data.get('ciudad', ''),
            provincia=data.get('provincia', ''),
            naf=data.get('naf', ''),
            fecha_alta=data.get('fecha_alta', ''),
            centro_trabajo=data.get('centro_trabajo', ''),
            puesto=data.get('puesto', ''),
            empresa_nombre=data.get('empresa_nombre', ''),
            empresa_cif=data.get('empresa_cif', ''),
            empresa_direccion=data.get('empresa_direccion', ''),
            empresa_codigo_postal=data.get('empresa_codigo_postal', ''),
            empresa_ciudad=data.get('empresa_ciudad', ''),
            empresa_provincia=data.get('empresa_provincia', ''),
            empresa_actividad=data.get('empresa_actividad', ''),
            empresa_ccc=data.get('empresa_ccc', ''),
            empresa_trabajadores=data.get('empresa_trabajadores', 0),
            empresa_horario=data.get('empresa_horario', ''),
            created_at=datetime.fromisoformat(data['created_at']) if data.get('created_at') else datetime.now(),
            updated_at=datetime.fromisoformat(data['updated_at']) if data.get('updated_at') else datetime.now(),
            is_active=data.get('is_active', True),
        )

    def format_for_display(self) -> str:
        """Format profile for display in Telegram message."""
        lines = [
            "👤 *Perfil de Usuario*",
            "",
            f"*Nombre:* {self.nombre}",
            f"*DNI:* {self.dni}",
            f"*Email:* {self.email}",
            f"*Teléfono:* {self.telefono}",
            "",
            "📍 *Dirección:*",
            f"{self.direccion}",
            f"{self.codigo_postal} {self.ciudad}, {self.provincia}",
            "",
            "💼 *Empleo:*",
            f"*Empresa:* {self.empresa_nombre}",
            f"*Centro:* {self.centro_trabajo}",
            f"*Puesto:* {self.puesto or 'No especificado'}",
            f"*NAF:* {self.naf}",
            f"*Fecha de alta:* {self.fecha_alta}",
            "",
            "🏢 *Datos de la Empresa:*",
            f"*CIF:* {self.empresa_cif}",
            f"*Dirección:* {self.empresa_direccion}",
            f"*Actividad:* {self.empresa_actividad or 'No especificada'}",
            f"*Trabajadores:* {self.empresa_trabajadores}",
            f"*Horario:* {self.empresa_horario or 'No especificado'}",
        ]
        return "\n".join(lines)


class UserProfileManager:
    """
    Manager for user profile CRUD operations with Supabase backend.

    Features:
    - Load profiles by Telegram user ID
    - Create, update, delete profiles
    - In-memory caching for performance
    - Retry logic for API failures
    """

    def __init__(self, supabase_client=None):
        """
        Initialize profile manager.

        Args:
            supabase_client: Optional Supabase client instance
        """
        self.supabase = supabase_client
        self._cache: Dict[int, UserProfile] = {}
        self._cache_ttl = 3600  # 1 hour
        self._cache_timestamps: Dict[int, datetime] = {}

    def _is_cache_valid(self, user_id: int) -> bool:
        """Check if cached profile is still valid."""
        if user_id not in self._cache_timestamps:
            return False

        cache_age = (datetime.now() - self._cache_timestamps[user_id]).total_seconds()
        return cache_age < self._cache_ttl

    def _invalidate_cache(self, user_id: int) -> None:
        """Invalidate cache for specific user."""
        if user_id in self._cache:
            del self._cache[user_id]
        if user_id in self._cache_timestamps:
            del self._cache_timestamps[user_id]

    def get_profile(self, telegram_user_id: int) -> Optional[UserProfile]:
        """
        Load user profile by Telegram user ID.

        Checks cache first, then queries Supabase if needed.

        Args:
            telegram_user_id: Telegram user ID

        Returns:
            UserProfile if found, None otherwise
        """
        # Check cache
        if self._is_cache_valid(telegram_user_id):
            logger.info(f"Profile cache hit for user {telegram_user_id}")
            return self._cache[telegram_user_id]

        # Query Supabase
        if not self.supabase or not self.supabase.is_enabled():
            logger.warning("Supabase not available, cannot load profile")
            return None

        try:
            profile_dict = self.supabase.get_user_profile(telegram_user_id)

            if profile_dict:
                profile = UserProfile.from_dict(profile_dict)
                # Cache the profile
                self._cache[telegram_user_id] = profile
                self._cache_timestamps[telegram_user_id] = datetime.now()
                return profile
            else:
                logger.info(f"No profile found for user {telegram_user_id}")
                return None

        except Exception as e:
            logger.error(f"Error loading profile for user {telegram_user_id}: {e}")
            return None

    def create_profile(self, profile: UserProfile) -> tuple[bool, str]:
        """
        Create new user profile in Supabase.

        Args:
            profile: UserProfile to create

        Returns:
            Tuple of (success, message)
        """
        # Validate profile
        is_valid, errors = profile.validate()
        if not is_valid:
            return (False, "Validación fallida:\n" + "\n".join(errors))

        # Check if profile already exists
        existing = self.get_profile(profile.telegram_user_id)
        if existing:
            return (False, f"El perfil ya existe para el usuario {profile.telegram_user_id}")

        # Create in Supabase
        if not self.supabase or not self.supabase.is_enabled():
            # Fallback to in-memory cache
            self._cache[profile.telegram_user_id] = profile
            self._cache_timestamps[profile.telegram_user_id] = datetime.now()
            logger.warning("Supabase not available, profile cached in memory only")
            return (True, "Perfil creado (memoria local - Supabase no disponible)")

        try:
            profile_dict = profile.to_dict()
            success = self.supabase.create_user_profile(profile_dict)

            if success:
                # Cache the profile
                self._cache[profile.telegram_user_id] = profile
                self._cache_timestamps[profile.telegram_user_id] = datetime.now()
                logger.info(f"Profile created for user {profile.telegram_user_id}")
                return (True, "Perfil creado exitosamente")
            else:
                return (False, "Error al crear perfil en Supabase")

        except Exception as e:
            logger.error(f"Error creating profile for user {profile.telegram_user_id}: {e}")
            return (False, f"Error: {str(e)}")

    def update_profile(self, profile: UserProfile) -> tuple[bool, str]:
        """
        Update existing user profile in Supabase.

        Args:
            profile: UserProfile with updated data

        Returns:
            Tuple of (success, message)
        """
        # Validate profile
        is_valid, errors = profile.validate()
        if not is_valid:
            return (False, "Validación fallida:\n" + "\n".join(errors))

        # Check if profile exists
        existing = self.get_profile(profile.telegram_user_id)
        if not existing:
            return (False, f"El perfil no existe para el usuario {profile.telegram_user_id}")

        # Update in Supabase
        if not self.supabase or not self.supabase.is_enabled():
            # Fallback to in-memory cache
            self._cache[profile.telegram_user_id] = profile
            self._cache_timestamps[profile.telegram_user_id] = datetime.now()
            logger.warning("Supabase not available, profile updated in memory only")
            return (True, "Perfil actualizado (memoria local - Supabase no disponible)")

        try:
            profile_dict = profile.to_dict()
            success = self.supabase.update_user_profile(profile.telegram_user_id, profile_dict)

            if success:
                # Update cache
                self._cache[profile.telegram_user_id] = profile
                self._cache_timestamps[profile.telegram_user_id] = datetime.now()
                logger.info(f"Profile updated for user {profile.telegram_user_id}")
                return (True, "Perfil actualizado exitosamente")
            else:
                return (False, "Error al actualizar perfil en Supabase")

        except Exception as e:
            logger.error(f"Error updating profile for user {profile.telegram_user_id}: {e}")
            return (False, f"Error: {str(e)}")

    def delete_profile(self, telegram_user_id: int) -> tuple[bool, str]:
        """
        Delete user profile (soft delete by setting is_active=False).

        Args:
            telegram_user_id: Telegram user ID

        Returns:
            Tuple of (success, message)
        """
        # Check if profile exists
        existing = self.get_profile(telegram_user_id)
        if not existing:
            return (False, f"El perfil no existe para el usuario {telegram_user_id}")

        # Delete from Supabase
        if not self.supabase or not self.supabase.is_enabled():
            # Fallback: remove from cache
            self._invalidate_cache(telegram_user_id)
            logger.warning("Supabase not available, profile removed from cache only")
            return (True, "Perfil eliminado (memoria local - Supabase no disponible)")

        try:
            success = self.supabase.delete_user_profile(telegram_user_id)

            if success:
                # Remove from cache
                self._invalidate_cache(telegram_user_id)
                logger.info(f"Profile deleted for user {telegram_user_id}")
                return (True, "Perfil eliminado exitosamente")
            else:
                return (False, "Error al eliminar perfil en Supabase")

        except Exception as e:
            logger.error(f"Error deleting profile for user {telegram_user_id}: {e}")
            return (False, f"Error: {str(e)}")

    def list_all_profiles(self) -> List[UserProfile]:
        """
        List all active profiles (admin only).

        Returns:
            List of all active UserProfile objects
        """
        # TODO: Implement Supabase query
        # For now, return cached profiles
        return list(self._cache.values())


def inject_user_profile(template: str, profile: UserProfile) -> str:
    """
    Replace [HARDCODED] markers in template with user profile data.

    This function processes template strings and substitutes hardcoded personal
    and company data with user-specific information from the profile.

    Args:
        template: Template string with [HARDCODED] markers
        profile: UserProfile with data to inject

    Returns:
        Template string with profile data injected

    Example:
        Before: "[HARDCODED] JUAN MANUEL TORALES CHORNE"
        After:  "JUAN MANUEL TORALES CHORNE" (from profile.nombre)
    """
    # Map of template markers to profile fields
    # These match the hardcoded values in itss_template.md and demanda_template.md
    replacements = {
        # Personal data
        "[HARDCODED] JUAN MANUEL TORALES CHORNE": profile.nombre.upper(),
        "[HARDCODED] 44591820-H": profile.dni,
        "[HARDCODED] delegados.sdpmad@gmail.com": profile.email,
        "[HARDCODED] 627228904": profile.telefono,

        # Address
        "[HARDCODED] CALLE PLAYA DE ZARAUZ 18, 2C": profile.direccion.upper(),
        "[HARDCODED] 28042": profile.codigo_postal,
        "[HARDCODED] MADRID / MADRID": f"{profile.ciudad.upper()} / {profile.provincia.upper()}",

        # Employment
        "[HARDCODED] 29/10177911/13": profile.naf,
        "[HARDCODED] 17/01/2023": profile.fecha_alta,
        "[HARDCODED] AEROPUERTO ADOLFO SUÁREZ MADRID - BARAJAS": profile.centro_trabajo.upper(),

        # Company data
        "[HARDCODED] SKYWAY AIR NAVIGATION SERVICES": profile.empresa_nombre.upper(),
        "[HARDCODED] A86164894": profile.empresa_cif,
        "[HARDCODED] CALLE QUINTANAVIDES 21": profile.empresa_direccion.upper(),
        "[HARDCODED] 28050": profile.empresa_codigo_postal,
        "[HARDCODED] ACTIVIDADES ANEXAS AL TRANSPORTE AÉREO": profile.empresa_actividad.upper(),
        "[HARDCODED] 28184193088": profile.empresa_ccc,
        "[HARDCODED] 37": str(profile.empresa_trabajadores),
        "[HARDCODED] 00.00 a 23.59": profile.empresa_horario,
    }

    result = template
    for marker, value in replacements.items():
        if value:  # Only replace if value is not empty
            result = result.replace(marker, value)

    return result
