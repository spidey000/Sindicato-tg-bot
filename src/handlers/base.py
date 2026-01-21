"""
Marxnager Telegram Bot - Base Handler Module

This module contains shared utilities and client initialization used across all handlers.
It provides a centralized location for common imports and setup.

Client Instances:
- notion: DelegadoNotionClient - Notion database integration for case management
- drive: DelegadoDriveClient - Google Drive integration for file storage
- docs: DelegadoDocsClient - Google Docs integration for document editing
"""

import logging

from src.integrations.notion_client import DelegadoNotionClient
from src.integrations.drive_client import DelegadoDriveClient
from src.integrations.docs_client import DelegadoDocsClient

logger = logging.getLogger(__name__)

# Initialize clients
# These are singleton instances shared across all handlers
notion = DelegadoNotionClient()
drive = DelegadoDriveClient()
docs = DelegadoDocsClient()

__all__ = ['notion', 'drive', 'docs', 'logger']
