"""
Template Loader Utility

Provides functions to load and parse document templates for legal document generation.
Includes user profile injection to replace hardcoded data with user-specific information.
"""
import os
import re
import logging
from typing import List, Optional

logger = logging.getLogger(__name__)

# Base path for templates
TEMPLATES_DIR = os.path.join(os.path.dirname(__file__), 'data')


def load_template(template_name: str) -> Optional[str]:
    """
    Loads a template from src/data/{template_name}.
    
    Args:
        template_name: Name of the template file (e.g., 'demanda_template.md')
    
    Returns:
        Template content as string, or None if not found
    """
    template_path = os.path.join(TEMPLATES_DIR, template_name)
    logger.debug(f"Looking for template at: {template_path}")
    
    try:
        with open(template_path, 'r', encoding='utf-8') as f:
            content = f.read()
            if len(content) < 100:
                logger.error(f"Template {template_name} is too short ({len(content)} chars). Path: {template_path}")
                return None
            logger.info(f"Loaded template: {template_name} ({len(content)} chars)")
            return content
    except FileNotFoundError:
        logger.error(f"Template not found: {template_path}")
        return None
    except Exception as e:
        logger.error(f"Error loading template {template_name}: {e}")
        return None


def get_template_placeholders(template: str) -> List[str]:
    """
    Extracts all {{PLACEHOLDER}} names from a template.
    
    Args:
        template: The template content
    
    Returns:
        List of unique placeholder names (without the {{ }})
    """
    pattern = r'\{\{([A-Z_]+)\}\}'
    matches = re.findall(pattern, template)
    unique_placeholders = list(set(matches))
    logger.debug(f"Found {len(unique_placeholders)} unique placeholders in template")
    return unique_placeholders


def get_template_for_document_type(document_type: str, user_profile=None) -> Optional[str]:
    """
    Returns the appropriate template based on document type, with optional user profile injection.

    Args:
        document_type: 'demanda', 'denuncia', or 'email'
        user_profile: Optional UserProfile object to inject into template

    Returns:
        Template content with user data injected, or None if not found
    """
    template_map = {
        'demanda': 'demanda_template.md',
        'denuncia': 'itss_template.md',
        'email': 'email_template.md'
    }

    template_name = template_map.get(document_type.lower())
    if not template_name:
        logger.error(f"Unknown document type: {document_type}")
        return None

    template = load_template(template_name)
    if not template:
        return None

    # Inject user profile if provided
    if user_profile:
        from src.user_profile import inject_user_profile
        template = inject_user_profile(template, user_profile)
        logger.info(f"User profile injected into {document_type} template")

    return template
