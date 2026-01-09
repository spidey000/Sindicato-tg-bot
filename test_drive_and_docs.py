import os
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from dotenv import load_dotenv
import datetime

load_dotenv()

def test_drive_and_docs():
    creds_path = os.getenv("GOOGLE_DRIVE_CREDENTIALS_PATH", "google_credentials.json")
    
    # Folders to check
    folders = {
        "DENUNCIAS": os.getenv("DRIVE_FOLDER_DENUNCIAS"),
        "DEMANDAS": os.getenv("DRIVE_FOLDER_DEMANDAS"),
        "EMAILS": os.getenv("DRIVE_FOLDER_EMAILS")
    }
    
    if not os.path.exists(creds_path):
        print(f"❌ Credentials file not found: {creds_path}")
        return

    # Scopes for Drive (read/write) and Docs
    scopes = [
        'https://www.googleapis.com/auth/drive',
        'https://www.googleapis.com/auth/documents'
    ]
    
    try:
        creds = Credentials.from_service_account_file(creds_path, scopes=scopes)
        drive_service = build('drive', 'v3', credentials=creds)
        docs_service = build('docs', 'v1', credentials=creds)
        
        print(f"ℹ️  Service Account: {creds.service_account_email}\n")

        # 1. Test Read Access to Folders
        print("--- Testing Folder Access ---")
        target_folder_id = None
        
        for name, folder_id in folders.items():
            if not folder_id:
                print(f"❓ {name}: ID not configured in .env")
                continue
            
            try:
                folder = drive_service.files().get(fileId=folder_id, fields="id, name, capabilities").execute()
                can_add_children = folder.get('capabilities', {}).get('canAddChildren', False)
                status = "Writable" if can_add_children else "Read-only"
                print(f"✅ {name} ({folder.get('name')}): Accessible ({status})")
                
                if name == "DENUNCIAS" and can_add_children:
                    target_folder_id = folder_id
                    
            except Exception as e:
                print(f"❌ {name} ({folder_id}): Access DENIED or Not Found.")
                print(f"   Reason: {e}")

        # 2. Test Doc Creation
        print("\n--- Testing Google Doc Creation ---")
        if target_folder_id:
            try:
                # Create a blank doc
                file_metadata = {
                    'name': f'Gemini Test Doc {datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}',
                    'parents': [target_folder_id],
                    'mimeType': 'application/vnd.google-apps.document'
                }
                
                doc_file = drive_service.files().create(body=file_metadata, fields='id, name, webViewLink').execute()
                doc_id = doc_file.get('id')
                print(f"✅ Created Document: {doc_file.get('name')}")
                print(f"   Link: {doc_file.get('webViewLink')}")
                
                # Write to the doc
                requests = [
                    {
                        'insertText': {
                            'location': {'index': 1},
                            'text': 'Hello! This is a test document created by the Telegram Bot agent.\n'
                        }
                    }
                ]
                docs_service.documents().batchUpdate(documentId=doc_id, body={'requests': requests}).execute()
                print("✅ Successfully wrote content to the document.")
                
            except Exception as e:
                print(f"❌ Failed to create or write to document.")
                print(f"   Reason: {e}")
        else:
            print("⚠️  Skipping Doc Creation: 'DENUNCIAS' folder is not accessible or not writable.")
            print("   Please share the folder with the Service Account email listed above and give it 'Editor' permission.")

    except Exception as e:
        print(f"❌ Critical Error: {e}")

if __name__ == "__main__":
    test_drive_and_docs()
