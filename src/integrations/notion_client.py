from notion_client import Client
import os
import logging
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

class DelegadoNotionClient:
    def __init__(self):
        self.api_key = os.getenv("NOTION_TOKEN")
        self.database_id = os.getenv("NOTION_DATABASE_ID")
        self.client = None
        
        if self.api_key:
            self.client = Client(auth=self.api_key)
        else:
            logger.warning("NOTION_TOKEN not found. Notion integration disabled.")

    def create_case_page(self, case_data: Dict[str, Any]) -> Optional[str]:
        """
        Creates a new page in the Notion database for a case.
        Returns the ID of the created page.
        """
        if not self.client or not self.database_id:
            logger.error("Notion client not initialized or database ID missing.")
            return None

        try:
            properties = {
                "ID": {"title": [{"text": {"content": case_data.get("id", "Unknown")}}]},
                "Tipo": {"select": {"name": case_data.get("type", "General")}},
                "Estado": {"status": {"name": case_data.get("status", "Borrador")}},
                "Empresa": {"rich_text": [{"text": {"content": case_data.get("company", "Pendiente")}}]},
                "Fecha Apertura": {"date": {"start": case_data.get("created_at", "").isoformat()}} if case_data.get("created_at") else None,
                "Contexto Inicial": {"rich_text": [{"text": {"content": case_data.get("initial_context", "")}}]}
            }
            
            # Remove None values
            properties = {k: v for k, v in properties.items() if v is not None}

            response = self.client.pages.create(
                parent={"database_id": self.database_id},
                properties=properties
            )
            logger.info(f"Notion page created: {response['id']}")
            return response["id"]
        except Exception as e:
            logger.error(f"Error creating Notion page: {e}")
            return None

    def _get_page_id_by_case_id(self, case_id: str) -> Optional[str]:
        """Helper to find a Notion page ID by its Case ID (Title property)."""
        if not self.client or not self.database_id: return None
        try:
            response = self.client.databases.query(
                database_id=self.database_id,
                filter={
                    "property": "ID",
                    "title": {
                        "equals": case_id
                    }
                }
            )
            if response["results"]:
                return response["results"][0]["id"]
            return None
        except Exception as e:
            logger.error(f"Error searching for case {case_id}: {e}")
            return None

    def update_case_status(self, case_id: str, new_status: str) -> bool:
        """Updates the status of a case in Notion."""
        page_id = self._get_page_id_by_case_id(case_id)
        if not page_id:
            logger.warning(f"Case {case_id} not found in Notion.")
            return False

        try:
            self.client.pages.update(
                page_id=page_id,
                properties={
                    "Estado": {"status": {"name": new_status}}
                }
            )
            logger.info(f"Updated status for {case_id} to {new_status}")
            return True
        except Exception as e:
            logger.error(f"Error updating status for {case_id}: {e}")
            return False

    def update_page_links(self, page_id: str, drive_link: str = None, doc_link: str = None):
        """Updates the Drive and Doc links for a specific page."""
        if not self.client: return

        properties = {}
        if drive_link:
            properties["Enlace Drive"] = {"url": drive_link}
        if doc_link:
            properties["Enlace Doc"] = {"url": doc_link}
            
        if not properties: return

        try:
            self.client.pages.update(page_id=page_id, properties=properties)
            logger.info(f"Notion page {page_id} updated with links.")
        except Exception as e:
            logger.error(f"Error updating Notion page links: {e}")
