import unittest
import os
from dotenv import load_dotenv
from src.integrations.drive_client import DelegadoDriveClient

load_dotenv()

class TestGoogleAuth(unittest.TestCase):
    def setUp(self):
        self.client = DelegadoDriveClient()

    def test_auth(self):
        """Test authentication with Google Drive."""
        print("\nTesting Google Drive Authentication...")
        if not self.client.service:
            self.fail("Failed to initialize Drive service.")
        
        # Try to list files (limit 1) just to check auth
        try:
            results = self.client.service.files().list(
                pageSize=1, fields="nextPageToken, files(id, name)").execute()
            items = results.get('files', [])
            print(f"Auth successful. Found {len(items)} files (limit 1).")
        except Exception as e:
            self.fail(f"Authentication failed: {e}")

if __name__ == '__main__':
    unittest.main()

