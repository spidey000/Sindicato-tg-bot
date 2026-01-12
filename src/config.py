import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# App Identity
APP_NAME = "Marxnager"

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

# OpenRouter Configuration
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"
MODEL_PRIMARY = os.getenv("MODEL_PRIMARY", "deepseek/deepseek-r1-0528:free")
MODEL_FALLBACK = os.getenv("MODEL_FALLBACK", "moonshotai/moonlight-2:free")

# Drafting & Repair Models
# Drafting & Repair Models
PRIMARY_DRAFT_MODEL = os.getenv("PRIMARY_DRAFT_MODEL", "deepseek/deepseek-r1-0528:free")
FALLBACK_DRAFT_MODEL = os.getenv("FALLBACK_DRAFT_MODEL", "google/gemma-3-27b-it:free")
REPAIR_MODEL = os.getenv("REPAIR_MODEL", "qwen/qwen3-4b:free")

# Debugging
SAVE_RAW_LLM_RESPONSES = os.getenv("SAVE_RAW_LLM_RESPONSES", "False").lower() in ('true', '1', 't')


# Perplexity Configuration
PERPLEXITY_API_KEY_PRIMARY = os.getenv("PERPLEXITY_API_KEY_PRIMARY")
PERPLEXITY_API_KEY_FALLBACK = os.getenv("PERPLEXITY_API_KEY_FALLBACK")

# Drive Configuration
DRIVE_FOLDER_DENUNCIAS = os.getenv("DRIVE_FOLDER_DENUNCIAS")
DRIVE_FOLDER_DEMANDAS = os.getenv("DRIVE_FOLDER_DEMANDAS")
DRIVE_FOLDER_EMAILS = os.getenv("DRIVE_FOLDER_EMAILS")
ADMIN_EMAIL = os.getenv("ADMIN_EMAIL")