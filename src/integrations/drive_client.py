from googleapiclient.discovery import build
from googleapiclient.errors import HttpError, RefreshError
import os
import logging
import io
from googleapiclient.http import MediaIoBaseUpload
from typing import Optional
from src.integrations.auth_helper import get_google_creds
from src.utils.retry import sync_retry

logger = logging.getLogger(__name__)

class DelegadoDriveClient:
    def __init__(self):
        self.root_folder_id = os.getenv("GOOGLE_DRIVE_ROOT_FOLDER_ID")
        self.service = None
        
        SCOPES = ['https://www.googleapis.com/auth/drive']
        creds = get_google_creds(SCOPES)
        
        if creds:
            try:
                self.service = build('drive', 'v3', credentials=creds)
            except Exception as e:
                logger.error(f"Error initializing Drive client: {e}")
        else:
            logger.warning("Drive integration disabled: No valid credentials.")

    @sync_retry(
        max_retries=3,
        initial_delay=1.0,
        backoff_factor=2.0,
        exceptions=(HttpError, RefreshError, ConnectionError, TimeoutError)
    )
    def create_case_folder(self, case_id: str, case_name: str, case_type: str = "denuncia") -> tuple[Optional[str], Optional[str]]:
        """
        Creates a folder for the case and returns (WebViewLink, FolderID).
        Selects parent folder based on case_type: 'denuncia', 'demanda', or 'email'.

        Includes retry logic for transient API failures.
        """
        if not self.service:
            return None, None

        # Determine parent folder
        parent_id = self.root_folder_id # Default fallback
        if case_type == "denuncia":
            parent_id = os.getenv("DRIVE_FOLDER_DENUNCIAS")
        elif case_type == "demanda":
            parent_id = os.getenv("DRIVE_FOLDER_DEMANDAS")
        elif case_type == "email":
            parent_id = os.getenv("DRIVE_FOLDER_EMAILS")

        if not parent_id:
            logger.warning(f"Parent folder for type '{case_type}' not configured. using root.")
            parent_id = self.root_folder_id

        try:
            folder_metadata = {
                'name': f"{case_id} - {case_name}",
                'mimeType': 'application/vnd.google-apps.folder',
                'parents': [parent_id] if parent_id else []
            }

            folder = self.service.files().create(
                body=folder_metadata,
                fields='id, webViewLink'
            ).execute()

            logger.info(f"Drive folder created: {folder.get('id')} in parent {parent_id}")
            return folder.get('webViewLink'), folder.get('id')
        except Exception as e:
            logger.error(f"Error creating Drive folder: {e}")
            return None, None
            
    @sync_retry(
        max_retries=3,
        initial_delay=1.0,
        backoff_factor=2.0,
        exceptions=(HttpError, RefreshError, ConnectionError, TimeoutError)
    )
    def create_subfolder(self, parent_id: str, folder_name: str) -> Optional[str]:
        """
        Creates a subfolder inside a case folder.

        Includes retry logic for transient API failures.
        """
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

    @sync_retry(
        max_retries=3,
        initial_delay=1.0,
        backoff_factor=2.0,
        exceptions=(HttpError, RefreshError, ConnectionError, TimeoutError)
    )
    def upload_file(self, file_content: bytes, file_name: str, folder_id: str, mime_type: str = None) -> Optional[str]:
        """
        Uploads a file to the specified Drive folder.

        Includes retry logic for transient API failures.
        """
        if not self.service: return None

        try:
            file_metadata = {
                'name': file_name,
                'parents': [folder_id]
            }

            media = MediaIoBaseUpload(
                io.BytesIO(file_content),
                mimetype=mime_type or 'application/octet-stream',
                resumable=True
            )

            file = self.service.files().create(
                body=file_metadata,
                media_body=media,
                fields='id, webViewLink'
            ).execute()

            logger.info(f"File uploaded: {file.get('name')} ({file.get('id')})")
            return file.get('webViewLink')
        except Exception as e:
            logger.error(f"Error uploading file {file_name}: {e}")
            return None

    def find_doc_in_folder(self, folder_id: str) -> Optional[str]:
        """Finds the first Google Doc in a folder and returns its ID."""
        if not self.service: return None
        try:
            query = f"'{folder_id}' in parents and mimeType = 'application/vnd.google-apps.document'"
            results = self.service.files().list(q=query, fields="files(id)", pageSize=1).execute()
            files = results.get('files', [])
            if files:
                return files[0]['id']
            return None
        except Exception as e:
            logger.error(f"Error finding doc in folder: {e}")
            return None

    def delete_file_or_folder(self, file_id: str) -> bool:
        """
        Permanently deletes a file or folder from Drive.
        """
        if not self.service: return False
        try:
            self.service.files().delete(fileId=file_id).execute()
            logger.info(f"Drive object {file_id} deleted permanently.")
            return True
        except Exception as e:
            logger.error(f"Error deleting Drive object {file_id}: {e}")
            return False

    def share_file(self, file_id: str, email: str, role: str = "writer") -> bool:
        """Shares a file or folder with a specific email."""
        if not self.service: return False
        
        try:
            user_permission = {
                'type': 'user',
                'role': role,
                'emailAddress': email
            }
            
            self.service.permissions().create(
                fileId=file_id,
                body=user_permission,
                fields='id',
                sendNotificationEmail=False
            ).execute()
            
            logger.info(f"Shared file {file_id} with {email} as {role}")
            return True
        except Exception as e:
            logger.error(f"Error sharing file {file_id}: {e}")
            return False
