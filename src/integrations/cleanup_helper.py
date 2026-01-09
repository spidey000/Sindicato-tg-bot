import logging
from src.integrations.notion_client import DelegadoNotionClient
from src.integrations.drive_client import DelegadoDriveClient

logger = logging.getLogger(__name__)

def delete_notion_page(page_id: str) -> bool:
    """Helper to delete a Notion page."""
    client = DelegadoNotionClient()
    return client.delete_page(page_id)

def delete_drive_object(object_id: str) -> bool:
    """Helper to delete a Drive file or folder."""
    client = DelegadoDriveClient()
    return client.delete_file_or_folder(object_id)
