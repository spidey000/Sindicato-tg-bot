from notion_client import Client, APIResponseError
import os
import logging
from typing import Dict, Any, Optional
from src.utils.retry import sync_retry
from src.utils.monitoring import track_api_call

logger = logging.getLogger(__name__)

class DelegadoNotionClient:
    def __init__(self):
        """
        Initialize Notion API client with authentication.

        Creates a Notion client instance using the integration token.
        Requires NOTION_TOKEN and NOTION_DATABASE_ID environment variables.

        Attributes:
            api_key: Notion integration token for API authentication.
            database_id: ID of the Notion database used for case management.
            client: Notion API client instance for database operations.

        Note:
            Integration is disabled if NOTION_TOKEN is not set.
            The database_id is required for most query operations.
        """
        self.api_key = os.getenv("NOTION_TOKEN")
        self.database_id = os.getenv("NOTION_DATABASE_ID")
        self.client = None

        if self.api_key:
            self.client = Client(auth=self.api_key)
        else:
            logger.warning("NOTION_TOKEN not found. Notion integration disabled.")

    def _get_data_source_id(self) -> Optional[str]:
        """
        Retrieves the Data Source ID associated with the current Notion Database.

        This helper method is used as a fallback when the standard databases.query
        endpoint is not available for managed Notion databases.

        Returns:
            Optional[str]: The Data Source ID if found, None otherwise.
        """
        if not self.client or not self.database_id: return None
        try:
            db_info = self.client.databases.retrieve(database_id=self.database_id)
            ds_list = db_info.get("data_sources", [])
            if ds_list:
                return ds_list[0]["id"]
            return None
        except Exception as e:
            logger.error(f"Error retrieving data source ID: {e}")
            return None

    def _query_notion(self, **kwargs) -> Dict[str, Any]:
        """
        Wrapper to query Notion database with fallback to data_sources endpoint.

        For managed Notion databases, the standard databases.query endpoint may not
        be available. This method attempts to use databases.query first, then falls
        back to data_sources.query if needed.

        Args:
            **kwargs: Query parameters to pass to the Notion API (typically database_id,
                     filter, sorts, page_size, etc.)

        Returns:
            Dict[str, Any]: The API response from Notion.

        Raises:
            AttributeError: If neither databases.query nor data_sources.query is available.
        """
        if hasattr(self.client.databases, "query"):
            return self.client.databases.query(**kwargs)
        
        # Fallback to data_sources.query if this is a managed database
        ds_id = self._get_data_source_id()
        if ds_id and hasattr(self.client, "data_sources"):
            # Map database_id to data_source_id for the fallback call
            if "database_id" in kwargs:
                kwargs["data_source_id"] = ds_id
                del kwargs["database_id"]
            return self.client.data_sources.query(**kwargs)
        
        raise AttributeError("'DatabasesEndpoint' object has no attribute 'query' and no Data Source fallback found.")

    @sync_retry(
        max_retries=3,
        initial_delay=1.0,
        backoff_factor=2.0,
        exceptions=(APIResponseError, ConnectionError, TimeoutError)
    )
    @track_api_call('notion')
    def create_case_page(self, case_data: Dict[str, Any]) -> Optional[str]:
        """
        Creates a new page in the Notion database for a case.
        Returns the ID of the created page.

        Includes retry logic for transient API failures.
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

            # Construct Title: Use passed title or "ID - Context (Truncated)"
            if case_data.get("title"):
                title_text = case_data["title"]
            else:
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
        """
        Helper method to find a Notion page ID by searching for its Case ID in the Title.

        The Case ID is expected to be at the start of the page title (e.g., "D-2026-001").

        Args:
            case_id (str): The Case ID to search for (e.g., "D-2026-001").

        Returns:
            Optional[str]: The Notion page ID if found, None otherwise.
        """
        if not self.client or not self.database_id: return None
        try:
            response = self._query_notion(
                database_id=self.database_id,
                filter={
                    "property": "Name",
                    "title": {
                        "starts_with": case_id
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
        """
        Retrieves all active cases from Notion (excluding "Presentada" status).

        Active cases are those with status: "Pendiente de hacer", "En progreso",
        or "En revisión". Cases marked as "Presentada" (file/submitted) are excluded.

        Returns:
            list: A list of dictionaries containing case information. Each dictionary
                  has keys: 'id' (extracted from title prefix), 'title', and 'status'.
                  Returns empty list on error or if no active cases exist.
        """
        if not self.client or not self.database_id: return []
        
        try:
            response = self._query_notion(
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

    @sync_retry(
        max_retries=3,
        initial_delay=1.0,
        backoff_factor=2.0,
        exceptions=(APIResponseError, ConnectionError, TimeoutError)
    )
    @track_api_call('notion')
    def update_case_status(self, case_id: str, new_status: str) -> bool:
        """
        Updates the status of a case in Notion.

        Includes retry logic for transient API failures.
        """
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

    @sync_retry(
        max_retries=3,
        initial_delay=1.0,
        backoff_factor=2.0,
        exceptions=(APIResponseError, ConnectionError, TimeoutError)
    )
    @track_api_call('notion')
    def update_page_links(self, page_id: str, drive_link: str = None, doc_link: str = None):
        """
        Updates the Drive and Doc links for a specific page.

        Includes retry logic for transient API failures.
        """
        if not self.client: return

        properties = {}
        if drive_link:
            properties["Gdrive folder"] = {"url": drive_link}
        if doc_link:
            # Note: Using 'Perplexity' property as fallback for doc link based on schema discovery
            properties["Perplexity"] = {"url": doc_link}

        if not properties: return

        try:
            self.client.pages.update(page_id=page_id, properties=properties)
            logger.info(f"Notion page {page_id} updated with links.")
        except Exception as e:
            logger.error(f"Error updating Notion page links: {e}")

    def get_case_links(self, case_id: str) -> dict:
        """
        Retrieves Google Drive and Google Doc links for a specific case from Notion.

        Queries the Notion page for the given case_id and extracts the URLs from
        the "Gdrive folder" and "Perplexity" (used as Doc link) properties.

        Args:
            case_id (str): The Case ID to retrieve links for (e.g., "D-2026-001").

        Returns:
            dict: A dictionary with keys 'drive_url' and 'doc_url'. Values are None
                  if the links are not found. Returns empty dict on error.
        """
        page_id = self._get_page_id_by_case_id(case_id)
        if not page_id: return {}
        
        try:
            page = self.client.pages.retrieve(page_id=page_id)
            props = page.get("properties", {})
            
            drive_url = props.get("Gdrive folder", {}).get("url")
            doc_url = props.get("Perplexity", {}).get("url")
            
            return {"drive_url": drive_url, "doc_url": doc_url}
        except Exception as e:
            logger.error(f"Error retrieving case links: {e}")
            return {}

    def delete_page(self, page_id: str) -> bool:
        """
        Hard deletes (archives) a Notion page.
        """
        if not self.client: return False
        try:
            self.client.pages.update(page_id=page_id, archived=True)
            logger.info(f"Notion page {page_id} archived (deleted).")
            return True
        except Exception as e:
            logger.error(f"Error archiving Notion page {page_id}: {e}")
            return False

    def append_verification_report(self, page_id: str, report_content: str) -> bool:
        """
        Appends the Perplexity verification report as a toggle block to the Notion page.
        """
        if not self.client:
            return False

        try:
            # Construct the toggle block with the report as a child paragraph
            # Truncate content if it's too long for a single paragraph (Notion limit is 2000 chars per block)
            # For simplicity, we'll just send it and let the client handle it, 
            # but ideally we'd split it if needed.
            
            # Split content into chunks of 2000 chars if necessary
            chunks = [report_content[i:i+2000] for i in range(0, len(report_content), 2000)]
            child_blocks = [
                {
                    "type": "paragraph",
                    "paragraph": {
                        "rich_text": [{"type": "text", "text": {"content": chunk}}]
                    }
                } for chunk in chunks
            ]

            children = [
                {
                    "type": "toggle",
                    "toggle": {
                        "rich_text": [
                            {
                                "type": "text",
                                "text": {"content": "🔍 Auditoría de Verificación Legal (Perplexity)"}
                            }
                        ],
                        "children": child_blocks
                    }
                }
            ]

            self.client.blocks.children.append(
                block_id=page_id,
                children=children
            )
            logger.info(f"Verification report appended to Notion page {page_id}")
            return True
        except Exception as e:
            logger.error(f"Error appending verification report to Notion: {e}")
            return False

    def append_raw_llm_response(self, page_id: str, raw_response: str) -> bool:
        """
        Appends the raw LLM JSON response as a collapsible code block for debugging.
        """
        if not self.client:
            return False

        try:
            # Notion's code block also has a 2000 character limit per block.
            chunks = [raw_response[i:i+2000] for i in range(0, len(raw_response), 2000)]
            
            # Create a code block for each chunk.
            child_blocks = [
                {
                    "type": "code",
                    "code": {
                        "rich_text": [{"type": "text", "text": {"content": chunk}}],
                        "language": "json"
                    }
                } for chunk in chunks
            ]

            children = [
                {
                    "type": "toggle",
                    "toggle": {
                        "rich_text": [
                            {
                                "type": "text",
                                "text": {"content": "🐞 Raw LLM Response (Debug)"}
                            }
                        ],
                        "children": child_blocks
                    }
                }
            ]

            self.client.blocks.children.append(
                block_id=page_id,
                children=children
            )
            logger.info(f"Raw LLM response appended to Notion page {page_id}")
            return True
        except Exception as e:
            logger.error(f"Error appending raw LLM response to Notion: {e}")
            return False


    @sync_retry(
        max_retries=3,
        initial_delay=1.0,
        backoff_factor=2.0,
        exceptions=(APIResponseError, ConnectionError, TimeoutError)
    )
    @track_api_call('notion')
    def append_content_blocks(self, page_id: str, research: str, draft: str) -> bool:
        """
        Appends Research and Draft content as toggle blocks to the Notion page.

        Includes retry logic for transient API failures.
        """
        if not self.client:
            return False

        children = []

        # Helper to create text blocks (chunked)
        def create_chunks(text):
            return [text[i:i+2000] for i in range(0, len(text), 2000)]

        # 1. Research Toggle
        if research:
            research_chunks = create_chunks(research)
            research_children = [
                {
                    "type": "paragraph",
                    "paragraph": {
                        "rich_text": [{"type": "text", "text": {"content": chunk}}]
                    }
                } for chunk in research_chunks
            ]
            children.append({
                "type": "toggle",
                "toggle": {
                    "rich_text": [{"type": "text", "text": {"content": "🧠 Investigación Perplexity"}}],
                    "children": research_children
                }
            })

        # 2. Draft Toggle
        if draft:
            draft_chunks = create_chunks(draft)
            draft_children = [
                {
                    "type": "paragraph",
                    "paragraph": {
                        "rich_text": [{"type": "text", "text": {"content": chunk}}]
                    }
                } for chunk in draft_chunks
            ]
            children.append({
                "type": "toggle",
                "toggle": {
                    "rich_text": [{"type": "text", "text": {"content": "📄 Borrador Generado"}}],
                    "children": draft_children
                }
            })

        if not children:
            return True

        try:
            self.client.blocks.children.append(
                block_id=page_id,
                children=children
            )
            logger.info(f"Appended content blocks to Notion page {page_id}")
            return True
        except Exception as e:
            logger.error(f"Error appending content blocks to Notion: {e}")
            return False

    def get_last_case_id(self, type_prefix: str) -> Optional[str]:
        """
        Retrieves the last used Case ID for a given prefix (e.g., 'D', 'J') in the current year.
        """
        if not self.client or not self.database_id: return None
        
        import datetime
        current_year = datetime.datetime.now().year
        search_prefix = f"{type_prefix}-{current_year}"

        try:
            # Filter by Title starts with "PREFIX-YEAR" and sort descending
            response = self._query_notion(
                database_id=self.database_id,
                filter={
                    "property": "Name",
                    "title": {
                        "starts_with": search_prefix
                    }
                },
                sorts=[
                    {
                        "property": "Name",
                        "direction": "descending"
                    }
                ],
                page_size=1
            )
            
            if response["results"]:
                title_prop = response["results"][0]["properties"].get("Name", {}).get("title", [])
                if title_prop:
                    full_title = title_prop[0]["text"]["content"]
                    # Extract ID: "D-2026-001 - Context" -> "D-2026-001"
                    if " - " in full_title:
                        return full_title.split(" - ")[0]
                    return full_title
            return None
        except Exception as e:
            logger.error(f"Error fetching last case ID: {e}")
            return None

