from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import os
import logging
from typing import Optional
from src.integrations.auth_helper import get_google_creds
from src.utils.retry import sync_retry
from src.utils.monitoring import track_api_call

logger = logging.getLogger(__name__)

class DelegadoDocsClient:
    def __init__(self):
        self.service = None
        self.drive_service = None
        
        SCOPES = [
            'https://www.googleapis.com/auth/documents',
            'https://www.googleapis.com/auth/drive'
        ]
        creds = get_google_creds(SCOPES)
        
        if creds:
            try:
                self.service = build('docs', 'v1', credentials=creds)
                self.drive_service = build('drive', 'v3', credentials=creds)
            except Exception as e:
                logger.error(f"Error initializing Docs client: {e}")
        else:
            logger.warning("Docs integration disabled: No valid credentials.")

    @sync_retry(
        max_retries=3,
        initial_delay=1.0,
        backoff_factor=2.0,
        exceptions=(HttpError, ConnectionError, TimeoutError)
    )
    @track_api_call('docs')
    def create_draft_document(self, title: str, content: str, parent_folder_id: str) -> Optional[str]:
        """
        Creates a Google Doc with content and moves it to the specified folder.

        Includes retry logic for transient API failures.
        """
        if not self.service or not self.drive_service: return None

        try:
            # 1. Create Doc
            doc = self.service.documents().create(body={'title': title}).execute()
            doc_id = doc.get('documentId')

            # 2. Insert Content
            text_to_insert = content if content else "(Contenido vacío)"
            requests = [
                {
                    'insertText': {
                        'location': {'index': 1},
                        'text': text_to_insert
                    }
                }
            ]
            self.service.documents().batchUpdate(documentId=doc_id, body={'requests': requests}).execute()

            # 3. Move to Case Folder
            # Retrieve current parents to remove them
            file = self.drive_service.files().get(fileId=doc_id, fields='parents').execute()
            previous_parents = ",".join(file.get('parents'))

            self.drive_service.files().update(
                fileId=doc_id,
                addParents=parent_folder_id,
                removeParents=previous_parents,
                fields='id, webViewLink'
            ).execute()

            logger.info(f"Document created and moved: {doc_id}")
            return f"https://docs.google.com/document/d/{doc_id}/edit"

        except Exception as e:
            logger.error(f"Error creating draft document: {e}")
            return None

    def read_document_content(self, document_id: str) -> Optional[str]:
        """
        Reads the full text content of a Google Doc.

        Accepts either a Google Doc ID or a full URL. Extracts and concatenates
        all text elements from the document structure.

        Args:
            document_id (str): The Google Doc ID or URL (e.g.,
                              "https://docs.google.com/document/d/abc123/edit"
                              or just "abc123").

        Returns:
            Optional[str]: The full text content of the document, or None on error.
        """
        if not self.service: return None
        
        try:
            # Check if document_id is a URL
            if "docs.google.com" in document_id:
                import re
                match = re.search(r"/d/([a-zA-Z0-9-_]+)", document_id)
                if match:
                    document_id = match.group(1)

            doc = self.service.documents().get(documentId=document_id).execute()
            content = doc.get('body').get('content')
            
            full_text = ""
            for element in content:
                if 'paragraph' in element:
                    for run in element['paragraph']['elements']:
                        if 'textRun' in run:
                            full_text += run['textRun']['content']
            
            return full_text
        except Exception as e:
            logger.error(f"Error reading document content: {e}")
            return None

    @sync_retry(
        max_retries=3,
        initial_delay=1.0,
        backoff_factor=2.0,
        exceptions=(HttpError, ConnectionError, TimeoutError)
    )
    @track_api_call('docs')
    def update_document_content(self, document_id: str, new_content: str) -> bool:
        """
        Replaces the entire content of a Google Doc with new content.

        This method deletes all existing content and inserts the new content.
        Accepts either a Google Doc ID or a full URL.

        Args:
            document_id (str): The Google Doc ID or URL.
            new_content (str): The new text content to replace the existing content.

        Returns:
            bool: True if update succeeded, False otherwise.

        Note:
            Includes retry logic for transient API failures.
        """
        if not self.service: return False

        try:
             # Check if document_id is a URL
            if "docs.google.com" in document_id:
                import re
                match = re.search(r"/d/([a-zA-Z0-9-_]+)", document_id)
                if match:
                    document_id = match.group(1)

            # 1. Get document to find end index
            doc = self.service.documents().get(documentId=document_id).execute()
            content = doc.get('body').get('content')
            end_index = content[-1].get('endIndex') - 1

            if end_index <= 1:
                # Document is empty (except for trailing newline)
                requests = [
                    {
                        'insertText': {
                            'location': {'index': 1},
                            'text': new_content
                        }
                    }
                ]
            else:
                requests = [
                    {
                        'deleteContentRange': {
                            'range': {
                                'startIndex': 1,
                                'endIndex': end_index
                            }
                        }
                    },
                    {
                        'insertText': {
                            'location': {'index': 1},
                            'text': new_content
                        }
                    }
                ]

            self.service.documents().batchUpdate(documentId=document_id, body={'requests': requests}).execute()
            logger.info(f"Updated content of document {document_id}")
            return True
        except Exception as e:
            logger.error(f"Error updating document content: {e}")
            return False

    def append_text(self, document_id: str, text: str) -> bool:
        """
        Appends text to the end of a Google Doc with a bot signature.

        Adds the specified text to the end of the document, prefixed with a
        "[NOTA ADICIONAL - <bot_name>]" header.

        Args:
            document_id (str): The Google Doc ID or URL.
            text (str): The text to append to the document.

        Returns:
            bool: True if append succeeded, False otherwise.
        """
        if not self.service: return False
        
        try:
            # Check if document_id is a URL, if so extract ID
            if "docs.google.com" in document_id:
                # Basic extraction: .../d/DOC_ID/edit...
                import re
                match = re.search(r"/d/([a-zA-Z0-9-_]+)", document_id)
                if match:
                    document_id = match.group(1)
            
            # Get document to find end index
            doc = self.service.documents().get(documentId=document_id).execute()
            content = doc.get('body').get('content')
            end_index = content[-1].get('endIndex') - 1
            
            requests = [
                {
                    'insertText': {
                        'location': {'index': end_index},
                        'text': f"\n\n[NOTA ADICIONAL - {os.getenv('BOT_NAME', 'Marxnager')}]\n{text}\n"
                    }
                }
            ]
            
            self.service.documents().batchUpdate(documentId=document_id, body={'requests': requests}).execute()
            logger.info(f"Appended text to document {document_id}")
            return True
        except Exception as e:
            logger.error(f"Error appending text to document: {e}")
            return False
