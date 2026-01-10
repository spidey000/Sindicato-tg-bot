import sys
import os
from google_auth_oauthlib.flow import InstalledAppFlow

SCOPES = [
    'https://www.googleapis.com/auth/drive',
    'https://www.googleapis.com/auth/documents',
    'https://www.googleapis.com/auth/spreadsheets'
]

def finish_oauth():
    if len(sys.argv) < 2:
        print("❌ Usage: python3 finish_oauth.py <auth_code>")
        return

    auth_code = sys.argv[1]
    
    flow = InstalledAppFlow.from_client_secrets_file(
        'client_secret.json', SCOPES, redirect_uri='urn:ietf:wg:oauth:2.0:oob')
    
    try:
        flow.fetch_token(code=auth_code)
        creds = flow.credentials
        
        with open('token.json', 'w') as f:
            f.write(creds.to_json())
            
        print("✅ Success! Authentication token saved to 'token.json'")
    except Exception as e:
        print(f"❌ Failed to exchange code for token: {e}")

if __name__ == '__main__':
    finish_oauth()
