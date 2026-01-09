import os
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from dotenv import load_dotenv

load_dotenv()

def test_simple_create():
    creds_path = os.getenv("GOOGLE_DRIVE_CREDENTIALS_PATH", "google_credentials.json")
    
    SCOPES = ['https://www.googleapis.com/auth/documents', 'https://www.googleapis.com/auth/drive']
    
    print(f"Using credentials from: {creds_path}")
    print(f"Scopes: {SCOPES}")
    
    creds = Credentials.from_service_account_file(creds_path, scopes=SCOPES)
    service = build('docs', 'v1', credentials=creds)
    
    try:
        print("Attempting to create a document...")
        doc = service.documents().create(body={'title': 'Simple Test Doc'}).execute()
        print(f"✅ Success! Doc ID: {doc.get('documentId')}")
        
        # Cleanup
        drive_service = build('drive', 'v3', credentials=creds)
        drive_service.files().delete(fileId=doc.get('documentId')).execute()
        print("✅ Cleanup successful")
        
    except Exception as e:
        print(f"❌ Failed: {e}")

if __name__ == "__main__":
    test_simple_create()
