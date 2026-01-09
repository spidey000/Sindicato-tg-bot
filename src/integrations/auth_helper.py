import os
import logging
from google.oauth2.credentials import Credentials
from google.oauth2.service_account import Credentials as ServiceAccountCredentials

logger = logging.getLogger(__name__)

def get_google_creds(scopes):
    """
    Returns valid Google Credentials, prioritizing token.json (User OAuth2)
    over Service Account credentials.
    """
    token_path = 'token.json'
    sa_path = os.getenv("GOOGLE_DRIVE_CREDENTIALS_PATH", "google_credentials.json")

    # 1. Try User OAuth2 Token
    if os.path.exists(token_path):
        try:
            creds = Credentials.from_authorized_user_file(token_path, scopes)
            logger.info("Authenticated using User OAuth2 token.")
            return creds
        except Exception as e:
            logger.warning(f"Failed to load token.json: {e}")

    # 2. Fallback to Service Account
    if sa_path and os.path.exists(sa_path):
        try:
            creds = ServiceAccountCredentials.from_service_account_file(sa_path, scopes=scopes)
            logger.info("Authenticated using Service Account credentials.")
            return creds
        except Exception as e:
            logger.error(f"Failed to load Service Account credentials: {e}")
            
    logger.error("No valid Google credentials found.")
    return None
