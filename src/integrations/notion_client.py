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
            # Map internal values to Notion Schema options
            status_map = {
                "Borrador": "Pendiente de hacer",
                "En edición": "En progreso",
                "Listo": "En revisión",
                "Enviado": "Presentada"
            }
            notion_status = status_map.get(case_data.get("status"), "Pendiente de hacer")

            type_map = {
                "Denuncia ITSS": "ITSS",
                "Demanda Judicial": "Defensor del pueblo", # Fallback as it's not in the list
                "Email RRHH": None # No mapping in Organismo
            }
            notion_type = type_map.get(case_data.get("type"))

            # Construct Title: "ID - Context (Truncated)"
            title_text = f"{case_data.get('id')} - {case_data.get('initial_context', '')[:50]}"

            properties = {
                "Name": {"title": [{"text": {"content": title_text}}]},
                "Estado": {"status": {"name": notion_status}},
                "AI summary": {"rich_text": [{"text": {"content": case_data.get("initial_context", "")}}]}
            }

            if notion_type:
                properties["Organismo"] = {"select": {"name": notion_type}}
            
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

    def get_active_cases(self) -> list:
        """Retrieves active cases (not archived/closed)."""
        if not self.client or not self.database_id: return []
        
        try:
            response = self.client.databases.query(
                database_id=self.database_id,
                filter={
                    "or": [
                        {"property": "Estado", "status": {"equals": "Pendiente de hacer"}},
                        {"property": "Estado", "status": {"equals": "En progreso"}},
                        {"property": "Estado", "status": {"equals": "En revisión"}}
                    ]
                }
            )
            
            cases = []
            for page in response["results"]:
                title_prop = page["properties"].get("Name", {}).get("title", [])
                title = title_prop[0]["text"]["content"] if title_prop else "Sin Título"
                status = page["properties"].get("Estado", {}).get("status", {}).get("name", "Unknown")
                
                # Try to extract ID from Title (assuming "ID - Context" format)
                case_id = title.split(" - ")[0] if " - " in title else title
                
                cases.append({
                    "id": case_id,
                    "title": title,
                    "status": status
                })
            return cases
        except Exception as e:
            logger.error(f"Error fetching active cases: {e}")
            return []

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
        """Updates the Drive link for a specific page."""
        if not self.client: return

        properties = {}
        if drive_link:
            properties["Gdrive folder"] = {"url": drive_link}
        # Note: The schema doesn't have a specific 'Doc Link' field, so we only update Drive or append to body (not implemented here)
            
        if not properties: return

        try:
            self.client.pages.update(page_id=page_id, properties=properties)
            logger.info(f"Notion page {page_id} updated with links.")
        except Exception as e:
            logger.error(f"Error updating Notion page links: {e}")
