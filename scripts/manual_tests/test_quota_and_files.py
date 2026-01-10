import os
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaInMemoryUpload
from dotenv import load_dotenv

load_dotenv()

def test_quota_and_files():
    creds_path = os.getenv("GOOGLE_DRIVE_CREDENTIALS_PATH", "google_credentials.json")
    folders = {
        "DENUNCIAS": os.getenv("DRIVE_FOLDER_DENUNCIAS"),
        "DEMANDAS": os.getenv("DRIVE_FOLDER_DEMANDAS"),
        "EMAILS": os.getenv("DRIVE_FOLDER_EMAILS")
    }
    
    creds = Credentials.from_service_account_file(
        creds_path, 
        scopes=['https://www.googleapis.com/auth/drive']
    )
    service = build('drive', 'v3', credentials=creds)

    print(f"ℹ️  Checking quota for: {creds.service_account_email}")
    try:
        about = service.about().get(fields="storageQuota, user").execute()
        quota = about.get('storageQuota', {})
        limit = int(quota.get('limit', 0)) / (1024**2)
        usage = int(quota.get('usage', 0)) / (1024**2)
        print(f"📊 Storage Limit: {limit:.2f} MB")
        print(f"📊 Storage Usage: {usage:.2f} MB")
        print(f"👤 User: {about.get('user', {}).get('emailAddress')}")
    except Exception as e:
        print(f"❌ Could not retrieve quota: {e}")

    print("\n--- Attempting to create a small TXT file in folders ---")
    for name, folder_id in folders.items():
        if not folder_id: continue
        
        try:
            file_metadata = {
                'name': f'quota_test_{name}.txt',
                'parents': [folder_id]
            }
            media = MediaInMemoryUpload(b'This is a small test file to check quota.', mimetype='text/plain')
            file = service.files().create(body=file_metadata, media_body=media, fields='id, name').execute()
            print(f"✅ Created {file.get('name')} in {name} (ID: {file.get('id')})")
            
            # Cleanup: Delete the test file
            # service.files().delete(fileId=file.get('id')).execute()
            # print(f"🧹 Deleted test file {file.get('id')}")
            
        except Exception as e:
            print(f"❌ Failed to create file in {name}: {e}")

if __name__ == "__main__":
    test_quota_and_files()
