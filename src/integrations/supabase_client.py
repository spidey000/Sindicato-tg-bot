"""
Supabase Client for Marxnager Event Logging and User Profiles

This module provides integration with Supabase for:
1. Chronological event logging (history_events table)
2. User profile management (user_profiles table)

It complements Notion (active case management) with historical event tracking
and multi-user support.

Purpose:
- Log all case-related events with timestamps
- Query events by date range for /history command
- Maintain chronological timeline of labor incidents
- Enable time-series analysis of delegate activity
- Store and retrieve user profiles for multi-user support

Schema - Event Logging:
CREATE TABLE history_events (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id BIGINT NOT NULL,
    event_date DATE NOT NULL,
    event_text TEXT NOT NULL,
    case_id TEXT,
    event_type TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

Schema - User Profiles:
CREATE TABLE user_profiles (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    telegram_user_id BIGINT UNIQUE NOT NULL,
    telegram_username TEXT,
    telegram_first_name TEXT,
    nombre TEXT NOT NULL,
    dni TEXT NOT NULL UNIQUE,
    email TEXT NOT NULL,
    telefono TEXT NOT NULL,
    direccion TEXT NOT NULL,
    codigo_postal TEXT NOT NULL,
    ciudad TEXT NOT NULL,
    provincia TEXT NOT NULL,
    naf TEXT NOT NULL,
    fecha_alta TEXT NOT NULL,
    centro_trabajo TEXT NOT NULL,
    puesto TEXT,
    empresa_nombre TEXT NOT NULL,
    empresa_cif TEXT NOT NULL,
    empresa_direccion TEXT NOT NULL,
    empresa_codigo_postal TEXT NOT NULL,
    empresa_ciudad TEXT NOT NULL,
    empresa_provincia TEXT NOT NULL,
    empresa_actividad TEXT,
    empresa_ccc TEXT NOT NULL,
    empresa_trabajadores INTEGER DEFAULT 0,
    empresa_horario TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    is_active BOOLEAN DEFAULT TRUE
);
"""

import os
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime, date
from src.utils.retry import sync_retry

logger = logging.getLogger(__name__)

try:
    from supabase import create_client, Client as SupabaseClient
    SUPABASE_AVAILABLE = True
except ImportError:
    SUPABASE_AVAILABLE = False
    logger.warning("supabase-py not installed. Supabase integration disabled.")


class DelegadoSupabaseClient:
    """
    Supabase client for event logging and historical timeline queries.

    Features:
    - Event logging with timestamps
    - Time-series queries by date range
    - User-specific event filtering
    - Retry logic for API failures
    """

    def __init__(self):
        """Initialize Supabase client from environment variables."""
        self.supabase_url = os.getenv("SUPABASE_URL")
        self.supabase_key = os.getenv("SUPABASE_KEY")
        self.client: Optional[SupabaseClient] = None

        if not SUPABASE_AVAILABLE:
            logger.warning("supabase-py package not available. Install with: pip install supabase")
            return

        if self.supabase_url and self.supabase_key:
            try:
                self.client = create_client(self.supabase_url, self.supabase_key)
                logger.info("Supabase client initialized successfully")
            except Exception as e:
                logger.error(f"Failed to initialize Supabase client: {e}")
                self.client = None
        else:
            logger.warning("SUPABASE_URL or SUPABASE_KEY not found. Supabase integration disabled.")

    def is_enabled(self) -> bool:
        """Check if Supabase integration is enabled and client is initialized."""
        return self.client is not None

    @sync_retry(
        max_retries=3,
        initial_delay=1.0,
        backoff_factor=2.0,
        exceptions=(Exception, ConnectionError, TimeoutError)
    )
    def log_event(
        self,
        user_id: int,
        event_text: str,
        case_id: Optional[str] = None,
        event_type: Optional[str] = None,
        event_date: Optional[date] = None
    ) -> bool:
        """
        Log an event to the history_events table.

        Args:
            user_id: Telegram user ID
            event_text: Description of the event
            case_id: Optional case ID (e.g., "D-2026-001")
            event_type: Optional event type (e.g., "denuncia", "demanda", "status_update")
            event_date: Optional date (defaults to today)

        Returns:
            True if event was logged successfully, False otherwise
        """
        if not self.client:
            logger.warning("Supabase client not initialized. Event not logged.")
            return False

        try:
            event_data = {
                "user_id": user_id,
                "event_date": (event_date or datetime.now().date()).isoformat(),
                "event_text": event_text,
            }

            if case_id:
                event_data["case_id"] = case_id
            if event_type:
                event_data["event_type"] = event_type

            response = self.client.table("history_events").insert(event_data).execute()

            if response.data:
                logger.info(f"Event logged for user {user_id}: {event_text[:50]}...")
                return True
            else:
                logger.error(f"Failed to log event: No data returned from Supabase")
                return False

        except Exception as e:
            logger.error(f"Error logging event to Supabase: {e}")
            return False

    @sync_retry(
        max_retries=3,
        initial_delay=1.0,
        backoff_factor=2.0,
        exceptions=(Exception, ConnectionError, TimeoutError)
    )
    def get_events(
        self,
        user_id: Optional[int] = None,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        case_id: Optional[str] = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """
        Query events from the history_events table.

        Args:
            user_id: Optional filter by Telegram user ID
            start_date: Optional filter events from this date onwards
            end_date: Optional filter events up to this date
            case_id: Optional filter by specific case ID
            limit: Maximum number of events to return (default: 100)

        Returns:
            List of event dictionaries sorted by date descending (newest first)
        """
        if not self.client:
            logger.warning("Supabase client not initialized. Returning empty list.")
            return []

        try:
            query = self.client.table("history_events").select("*")

            # Apply filters
            if user_id:
                query = query.eq("user_id", user_id)
            if case_id:
                query = query.eq("case_id", case_id)
            if start_date:
                query = query.gte("event_date", start_date.isoformat())
            if end_date:
                query = query.lte("event_date", end_date.isoformat())

            # Order by date descending and limit
            response = query.order("event_date", desc=True).order("created_at", desc=True).limit(limit).execute()

            events = response.data if response.data else []
            logger.info(f"Retrieved {len(events)} events from Supabase")
            return events

        except Exception as e:
            logger.error(f"Error querying events from Supabase: {e}")
            return []

    @sync_retry(
        max_retries=3,
        initial_delay=1.0,
        backoff_factor=2.0,
        exceptions=(Exception, ConnectionError, TimeoutError)
    )
    def get_events_by_date_range(
        self,
        start_date: date,
        end_date: date,
        user_id: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        Query events within a specific date range (inclusive).

        Args:
            start_date: Start date (inclusive)
            end_date: End date (inclusive)
            user_id: Optional filter by Telegram user ID

        Returns:
            List of event dictionaries sorted by date ascending
        """
        if not self.client:
            return []

        try:
            query = self.client.table("history_events").select("*")

            query = query.gte("event_date", start_date.isoformat()).lte("event_date", end_date.isoformat())

            if user_id:
                query = query.eq("user_id", user_id)

            # Order by date ascending for chronological view
            response = query.order("event_date", desc=False).order("created_at", desc=False).execute()

            return response.data if response.data else []

        except Exception as e:
            logger.error(f"Error querying events by date range: {e}")
            return []

    @sync_retry(
        max_retries=3,
        initial_delay=1.0,
        backoff_factor=2.0,
        exceptions=(Exception, ConnectionError, TimeoutError)
    )
    def get_recent_events(self, user_id: int, days: int = 30) -> List[Dict[str, Any]]:
        """
        Query events from the last N days for a specific user.

        Args:
            user_id: Telegram user ID
            days: Number of days to look back (default: 30)

        Returns:
            List of event dictionaries sorted by date descending
        """
        from datetime import timedelta

        end_date = datetime.now().date()
        start_date = end_date - timedelta(days=days)

        return self.get_events_by_date_range(start_date, end_date, user_id)

    def format_event_for_display(self, event: Dict[str, Any]) -> str:
        """
        Format an event dictionary for display in Telegram.

        Args:
            event: Event dictionary from Supabase

        Returns:
            Formatted string with event details
        """
        event_date = event.get("event_date", "Unknown date")
        event_text = event.get("event_text", "No description")
        case_id = event.get("case_id")
        event_type = event.get("event_type")

        # Build formatted string
        lines = [f"📅 {event_date}"]

        if case_id:
            lines.append(f"🆔 {case_id}")

        if event_type:
            lines.append(f"🏷️ {event_type}")

        lines.append(f"📝 {event_text}")

        return "\n".join(lines)

    def test_connection(self) -> bool:
        """
        Test the Supabase connection by attempting to query the table.

        Returns:
            True if connection successful, False otherwise
        """
        if not self.client:
            logger.warning("Supabase client not initialized")
            return False

        try:
            # Try to fetch a single record
            response = self.client.table("history_events").select("*").limit(1).execute()
            logger.info("Supabase connection test successful")
            return True
        except Exception as e:
            logger.error(f"Supabase connection test failed: {e}")
            return False

    # ========== User Profile Management ==========

    @sync_retry(
        max_retries=3,
        initial_delay=1.0,
        backoff_factor=2.0,
        exceptions=(Exception, ConnectionError, TimeoutError)
    )
    def get_user_profile(self, telegram_user_id: int) -> Optional[Dict[str, Any]]:
        """
        Retrieve user profile by Telegram user ID.

        Args:
            telegram_user_id: Telegram user ID

        Returns:
            Profile dictionary if found, None otherwise
        """
        if not self.client:
            logger.warning("Supabase client not initialized")
            return None

        try:
            response = self.client.table("user_profiles").select("*").eq("telegram_user_id", telegram_user_id).execute()

            if response.data and len(response.data) > 0:
                profile = response.data[0]
                logger.info(f"Profile retrieved for user {telegram_user_id}")
                return profile
            else:
                logger.info(f"No profile found for user {telegram_user_id}")
                return None

        except Exception as e:
            logger.error(f"Error retrieving profile for user {telegram_user_id}: {e}")
            return None

    @sync_retry(
        max_retries=3,
        initial_delay=1.0,
        backoff_factor=2.0,
        exceptions=(Exception, ConnectionError, TimeoutError)
    )
    def create_user_profile(self, profile_data: Dict[str, Any]) -> bool:
        """
        Create new user profile.

        Args:
            profile_data: Dictionary with profile fields

        Returns:
            True if created successfully, False otherwise
        """
        if not self.client:
            logger.warning("Supabase client not initialized")
            return False

        try:
            response = self.client.table("user_profiles").insert(profile_data).execute()

            if response.data:
                logger.info(f"Profile created for user {profile_data.get('telegram_user_id')}")
                return True
            else:
                logger.error("Failed to create profile: No data returned")
                return False

        except Exception as e:
            logger.error(f"Error creating user profile: {e}")
            return False

    @sync_retry(
        max_retries=3,
        initial_delay=1.0,
        backoff_factor=2.0,
        exceptions=(Exception, ConnectionError, TimeoutError)
    )
    def update_user_profile(self, telegram_user_id: int, profile_data: Dict[str, Any]) -> bool:
        """
        Update existing user profile.

        Args:
            telegram_user_id: Telegram user ID
            profile_data: Dictionary with updated profile fields

        Returns:
            True if updated successfully, False otherwise
        """
        if not self.client:
            logger.warning("Supabase client not initialized")
            return False

        try:
            response = self.client.table("user_profiles").update(profile_data).eq("telegram_user_id", telegram_user_id).execute()

            if response.data:
                logger.info(f"Profile updated for user {telegram_user_id}")
                return True
            else:
                logger.error("Failed to update profile: No data returned")
                return False

        except Exception as e:
            logger.error(f"Error updating user profile: {e}")
            return False

    @sync_retry(
        max_retries=3,
        initial_delay=1.0,
        backoff_factor=2.0,
        exceptions=(Exception, ConnectionError, TimeoutError)
    )
    def delete_user_profile(self, telegram_user_id: int) -> bool:
        """
        Delete user profile (soft delete by setting is_active=False).

        Args:
            telegram_user_id: Telegram user ID

        Returns:
            True if deleted successfully, False otherwise
        """
        if not self.client:
            logger.warning("Supabase client not initialized")
            return False

        try:
            response = self.client.table("user_profiles").update({"is_active": False}).eq("telegram_user_id", telegram_user_id).execute()

            if response.data:
                logger.info(f"Profile soft-deleted for user {telegram_user_id}")
                return True
            else:
                logger.error("Failed to delete profile: No data returned")
                return False

        except Exception as e:
            logger.error(f"Error deleting user profile: {e}")
            return False

    @sync_retry(
        max_retries=3,
        initial_delay=1.0,
        backoff_factor=2.0,
        exceptions=(Exception, ConnectionError, TimeoutError)
    )
    def list_all_user_profiles(self) -> List[Dict[str, Any]]:
        """
        List all active user profiles (admin function).

        Returns:
            List of profile dictionaries
        """
        if not self.client:
            logger.warning("Supabase client not initialized")
            return []

        try:
            response = self.client.table("user_profiles").select("*").eq("is_active", True).execute()
            profiles = response.data if response.data else []
            logger.info(f"Retrieved {len(profiles)} active profiles")
            return profiles

        except Exception as e:
            logger.error(f"Error listing user profiles: {e}")
            return []
