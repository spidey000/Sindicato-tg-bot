from googleapiclient.discovery import build
from google.oauth2.service_account import Credentials
import os
import logging
import io
from googleapiclient.http import MediaIoBaseUpload

logger = logging.getLogger(__name__)

class DelegadoDriveClient:
    def __init__(self):
        self.creds_path = os.getenv("GOOGLE_DRIVE_CREDENTIALS_PATH")
        self.root_folder_id = os.getenv("GOOGLE_DRIVE_ROOT_FOLDER_ID")
        self.service = None
        
        if self.creds_path and os.path.exists(self.creds_path):
            try:
                creds = Credentials.from_service_account_file(self.creds_path)
                self.service = build('drive', 'v3', credentials=creds)
            except Exception as e:
                logger.error(f"Error initializing Drive client: {e}")
        else:
            logger.warning("GOOGLE_DRIVE_CREDENTIALS_PATH not found or invalid. Drive integration disabled.")

    def create_case_folder(self, case_id: str, case_name: str) -> Optional[str]:
        """Creates a folder for the case and returns its Web View Link."""
        if not self.service or not self.root_folder_id:
            return None

        try:
            folder_metadata = {
                'name': f"{case_id} - {case_name}",
                'mimeType': 'application/vnd.google-apps.folder',
                'parents': [self.root_folder_id]
            }
            
            folder = self.service.files().create(
                body=folder_metadata,
                fields='id, webViewLink'
            ).execute()
            
            logger.info(f"Drive folder created: {folder.get('id')}")
            return folder.get('webViewLink'), folder.get('id')
        except Exception as e:
            logger.error(f"Error creating Drive folder: {e}")
            return None, None
            
    def create_subfolder(self, parent_id: str, folder_name: str) -> Optional[str]:
        """Creates a subfolder inside a case folder."""
        if not self.service: return None
        try:
            metadata = {
                'name': folder_name,
                'mimeType': 'application/vnd.google-apps.folder',
                'parents': [parent_id]
            }
            folder = self.service.files().create(body=metadata, fields='id').execute()
            return folder.get('id')
        except Exception as e:
            logger.error(f"Error creating subfolder {folder_name}: {e}")
            return None
