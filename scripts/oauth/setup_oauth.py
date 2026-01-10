import os
import json
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials

# Scopes required for the bot
SCOPES = [
    'https://www.googleapis.com/auth/drive',
    'https://www.googleapis.com/auth/documents',
    'https://www.googleapis.com/auth/spreadsheets'
]

def setup_oauth():
    creds = None
    token_file = 'token.json'
    client_secrets_file = 'client_secret.json'

    # 1. Check if token already exists
    if os.path.exists(token_file):
        try:
            creds = Credentials.from_authorized_user_file(token_file, SCOPES)
        except Exception as e:
            print(f"⚠️  Existing token is invalid, refreshing... ({e})")

    # 2. Refresh or Login
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            print("🔄 Refreshing expired token...")
            creds.refresh(Request())
        else:
            if not os.path.exists(client_secrets_file):
                print(f"❌ Error: '{client_secrets_file}' not found.")
                print("   Please download the OAuth 2.0 Client ID JSON from Google Cloud Console")
                print("   and save it as 'client_secret.json' in this folder.")
                return

            print("🚀 Starting OAuth Login Flow...")
            flow = InstalledAppFlow.from_client_secrets_file(client_secrets_file, SCOPES)
            
            # Use console strategy for remote/headless environments
            creds = flow.run_console()

        # 3. Save the token
        with open(token_file, 'w') as token:
            token.write(creds.to_json())
        print(f"✅ Success! Authentication token saved to '{token_file}'")

if __name__ == '__main__':
    setup_oauth()
