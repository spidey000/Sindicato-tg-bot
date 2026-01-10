import os
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from dotenv import load_dotenv

load_dotenv()

def check_enabled_apis():
    creds_path = os.getenv("GOOGLE_DRIVE_CREDENTIALS_PATH", "google_credentials.json")
    
    if not os.path.exists(creds_path):
        print(f"Credentials file not found at: {creds_path}")
        return

    try:
        # We need the 'https://www.googleapis.com/auth/cloud-platform.read-only' or similar scope
        # providing a broad scope to try and catch it.
        creds = Credentials.from_service_account_file(
            creds_path, 
            scopes=['https://www.googleapis.com/auth/cloud-platform.read-only']
        )
        
        # Get project ID from the credentials file (it's usually in the JSON)
        # We can also get it from the creds object after refreshing, or just load the json text.
        import json
        with open(creds_path, 'r') as f:
            data = json.load(f)
            project_id = data.get('project_id')
            
        print(f"Checking enabled APIs for project: {project_id}...")

        service = build('serviceusage', 'v1', credentials=creds)
        
        # Request to list enabled services
        request = service.services().list(
            parent=f'projects/{project_id}',
            filter='state:ENABLED'
        )
        response = request.execute()
        
        services = response.get('services', [])
        
        found_docs = False
        found_drive = False
        
        print("\nEnabled APIs (partial list):")
        for s in services:
            name = s.get('config', {}).get('name', '')
            title = s.get('config', {}).get('title', '')
            
            if 'docs.googleapis.com' in name:
                found_docs = True
                print(f"✅ {title} ({name})")
            elif 'drive.googleapis.com' in name:
                found_drive = True
                print(f"✅ {title} ({name})")
            elif 'sheets' in name or 'script' in name:
                 print(f"ℹ️ {title} ({name})")

        print("-" * 30)
        if not found_docs:
            print("❌ Google Docs API (docs.googleapis.com) is NOT found in the enabled list.")
        if not found_drive:
            print("❌ Google Drive API (drive.googleapis.com) is NOT found in the enabled list.")

    except Exception as e:
        print(f"\nError querying Service Usage API: {e}")
        print("Note: The Service Account might not have 'Service Usage Consumer' role.")

if __name__ == "__main__":
    check_enabled_apis()
