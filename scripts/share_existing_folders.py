import os
import logging
from dotenv import load_dotenv
from src.integrations.drive_client import DelegadoDriveClient

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()

def share_folders():
    admin_email = os.getenv("ADMIN_EMAIL")
    if not admin_email:
        print("ADMIN_EMAIL not set in .env")
        return

    drive = DelegadoDriveClient()
    if not drive.service:
        print("Drive service not initialized.")
        return

    folders = {
        "DENUNCIAS": os.getenv("DRIVE_FOLDER_DENUNCIAS"),
        "DEMANDAS": os.getenv("DRIVE_FOLDER_DEMANDAS"),
        "EMAILS": os.getenv("DRIVE_FOLDER_EMAILS")
    }

    print(f"Sharing folders with {admin_email}...")

    for name, folder_id in folders.items():
        if folder_id:
            print(f"Sharing {name} ({folder_id})...")
            success = drive.share_file(folder_id, admin_email, role="writer")
            if success:
                print(f"✅ Shared {name}")
            else:
                print(f"❌ Failed to share {name}")
        else:
            print(f"⚠️ {name} ID not found in env")

if __name__ == "__main__":
    share_folders()
