import os
from google_auth_oauthlib.flow import InstalledAppFlow

SCOPES = [
    'https://www.googleapis.com/auth/drive',
    'https://www.googleapis.com/auth/documents',
    'https://www.googleapis.com/auth/spreadsheets'
]

def start_oauth():
    if not os.path.exists('client_secret.json'):
        print("❌ client_secret.json not found.")
        return

    flow = InstalledAppFlow.from_client_secrets_file(
        'client_secret.json', SCOPES, redirect_uri='urn:ietf:wg:oauth:2.0:oob')
    
    auth_url, _ = flow.authorization_url(prompt='consent')
    
    print("\n🔗 --- Authorization URL ---")
    print("Please open this URL in your browser, sign in, and copy the code:")
    print(auth_url)
    print("----------------------------\n")

if __name__ == '__main__':
    start_oauth()

