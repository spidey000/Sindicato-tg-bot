import os
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from dotenv import load_dotenv
import datetime

load_dotenv()

def test_oauth_access():
    token_path = 'token.json'
    
    if not os.path.exists(token_path):
        print(f"❌ token.json not found.")
        return

    folders = {
        "DENUNCIAS": os.getenv("DRIVE_FOLDER_DENUNCIAS"),
        "DEMANDAS": os.getenv("DRIVE_FOLDER_DEMANDAS"),
        "EMAILS": os.getenv("DRIVE_FOLDER_EMAILS")
    }
    
    try:
        creds = Credentials.from_authorized_user_file(token_path)
        drive_service = build('drive', 'v3', credentials=creds)
        docs_service = build('docs', 'v1', credentials=creds)
        
        # 1. Check Quota
        print("--- Checking Quota ---")
        about = drive_service.about().get(fields="storageQuota, user").execute()
        quota = about.get('storageQuota', {})
        limit = int(quota.get('limit', 0)) / (1024**3) # GB
        usage = int(quota.get('usage', 0)) / (1024**3) # GB
        print(f"👤 User: {about.get('user', {}).get('emailAddress')}")
        print(f"📊 Storage: {usage:.2f} GB / {limit:.2f} GB")

        # 2. Test Folder Access
        print("\n--- Testing Folder Access ---")
        target_folder_id = None
        for name, folder_id in folders.items():
            if not folder_id: continue
            try:
                folder = drive_service.files().get(fileId=folder_id, fields="id, name").execute()
                print(f"✅ {name}: Accessible ('{folder.get('name')}')")
                if name == "DENUNCIAS":
                    target_folder_id = folder_id
            except Exception as e:
                print(f"❌ {name} ({folder_id}): Access DENIED. {e}")

        # 3. Test Doc Creation
        print("\n--- Testing Google Doc Creation ---")
        if target_folder_id:
            try:
                file_metadata = {
                    'name': f'OAuth Test Doc {datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}',
                    'parents': [target_folder_id],
                    'mimeType': 'application/vnd.google-apps.document'
                }
                doc_file = drive_service.files().create(body=file_metadata, fields='id, name, webViewLink').execute()
                doc_id = doc_file.get('id')
                print(f"✅ Created Document: {doc_file.get('name')}")
                print(f"🔗 Link: {doc_file.get('webViewLink')}")
                
                # Write content
                requests = [{'insertText': {'location': {'index': 1}, 'text': 'Success! This was created using User OAuth2.\n'}}]
                docs_service.documents().batchUpdate(documentId=doc_id, body={'requests': requests}).execute()
                print("✅ Successfully wrote content.")
                
            except Exception as e:
                print(f"❌ Failed to create/write doc: {e}")
        else:
            print("⚠️ Skipping Doc Creation: No valid target folder.")

    except Exception as e:
        print(f"❌ Critical Error: {e}")

if __name__ == "__main__":
    test_oauth_access()
