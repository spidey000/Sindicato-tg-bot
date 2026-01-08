import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Bot Configuration
BOT_TOKEN = os.getenv("BOT_TOKEN")
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

# Authorization
def get_authorized_users():
    """Retrieves the list of authorized user IDs from environment variables."""
    auth_users_str = os.getenv("AUTHORIZED_USER_IDS", "")
    if not auth_users_str:
        return []
    try:
        return [int(uid.strip()) for uid in auth_users_str.split(",") if uid.strip()]
    except ValueError:
        print("Error parsing AUTHORIZED_USER_IDS. Ensure it is a comma-separated list of integers.")
        return []

AUTHORIZED_USERS = get_authorized_users()
