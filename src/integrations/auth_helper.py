import os
import json
import logging
from google.oauth2.credentials import Credentials
from google.oauth2.service_account import Credentials as ServiceAccountCredentials

logger = logging.getLogger(__name__)

def get_google_creds(scopes):
    """
    Returns valid Google Credentials.

    Priority order:
    1. GOOGLE_TOKEN_JSON environment variable (User OAuth2 token as JSON string)
    2. token.json file (User OAuth2 token)
    3. Service Account credentials (file path from GOOGLE_DRIVE_CREDENTIALS_PATH)
    """
    # 1. Try User OAuth2 Token from Environment Variable
    token_json_env = os.getenv("GOOGLE_TOKEN_JSON")
    if token_json_env:
        try:
            token_data = json.loads(token_json_env)
            creds = Credentials.from_authorized_user_info(token_data, scopes)
            logger.info("Authenticated using User OAuth2 token from environment variable.")
            return creds
        except Exception as e:
            logger.warning(f"Failed to load GOOGLE_TOKEN_JSON env var: {e}")

    # 2. Try User OAuth2 Token from File
    token_path = 'token.json'
    if os.path.exists(token_path):
        try:
            creds = Credentials.from_authorized_user_file(token_path, scopes)
            logger.info("Authenticated using User OAuth2 token from file.")
            return creds
        except Exception as e:
            logger.warning(f"Failed to load token.json: {e}")

    # 3. Fallback to Service Account
    sa_path = os.getenv("GOOGLE_DRIVE_CREDENTIALS_PATH", "google_credentials.json")
    if sa_path and os.path.exists(sa_path):
        try:
            creds = ServiceAccountCredentials.from_service_account_file(sa_path, scopes=scopes)
            logger.info("Authenticated using Service Account credentials.")
            return creds
        except Exception as e:
            logger.error(f"Failed to load Service Account credentials: {e}")

    logger.error("No valid Google credentials found.")
    return None
