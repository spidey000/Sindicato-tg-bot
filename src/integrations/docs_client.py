from googleapiclient.discovery import build
from google.oauth2.service_account import Credentials
import os
import logging

logger = logging.getLogger(__name__)

class DelegadoDocsClient:
    def __init__(self):
        self.creds_path = os.getenv("GOOGLE_DRIVE_CREDENTIALS_PATH")
        self.service = None
        self.drive_service = None
        
        if self.creds_path and os.path.exists(self.creds_path):
            try:
                creds = Credentials.from_service_account_file(self.creds_path)
                self.service = build('docs', 'v1', credentials=creds)
                self.drive_service = build('drive', 'v3', credentials=creds)
            except Exception as e:
                logger.error(f"Error initializing Docs client: {e}")
        else:
            logger.warning("GOOGLE_DRIVE_CREDENTIALS_PATH not found or invalid. Docs integration disabled.")

    def create_draft_document(self, title: str, content: str, parent_folder_id: str) -> Optional[str]:
        """Creates a Google Doc with content and moves it to the specified folder."""
        if not self.service or not self.drive_service: return None

        try:
            # 1. Create Doc
            doc = self.service.documents().create(body={'title': title}).execute()
            doc_id = doc.get('documentId')
            
            # 2. Insert Content
            requests = [
                {
                    'insertText': {
                        'location': {'index': 1},
                        'text': content
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
