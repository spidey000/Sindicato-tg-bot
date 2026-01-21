"""
Marxnager Telegram Bot - Handlers Package

This package contains all Telegram bot command handlers, organized by functionality.
The monolithic handlers.py (951 lines) has been refactored into modular components.

Module Structure:
- base: Shared utilities, client initialization, and common helper functions
- admin: Administrative commands (/log, /start, /help)
- denuncia: /denuncia command handler for ITSS labor complaints
- demanda: /demanda command handler for judicial labor demands
- email: /email command handler for corporate HR communications
- status: /status and /update commands for case management
- history: /history command for chronological event timeline
- private: Private message handlers for document refinement and file uploads
"""

from src.handlers.base import notion, drive, docs
from src.handlers.admin import metrics_command, log_command, start, help_command
from src.handlers.denuncia import denuncia_handler
from src.handlers.demanda import demanda_handler
from src.handlers.email import email_handler
from src.handlers.status import status_handler, update_handler
from src.handlers.history import history_command
from src.handlers.private import private_message_handler, stop_editing_handler

__all__ = [
    # Client instances
    'notion', 'drive', 'docs',

    # Admin commands
    'metrics_command', 'log_command', 'start', 'help_command',

    # Document generation commands
    'denuncia_handler', 'demanda_handler', 'email_handler',

    # Case management commands
    'status_handler', 'update_handler',

    # History command
    'history_command',

    # Private message handlers
    'private_message_handler', 'stop_editing_handler',
]
