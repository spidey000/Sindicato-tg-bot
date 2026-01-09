import unittest
import os
from dotenv import load_dotenv
from src.integrations.docs_client import DelegadoDocsClient

load_dotenv()

class TestDocsAPI(unittest.TestCase):
    def setUp(self):
        self.client = DelegadoDocsClient()

    def test_create_doc(self):
        """Test document creation with Google Docs."""
        print("\nTesting Google Docs Creation...")
        if not self.client.service:
            self.fail("Failed to initialize Docs service.")
        
        try:
            # Try to create a dummy document
            doc = self.client.service.documents().create(body={'title': 'Test Document'}).execute()
            doc_id = doc.get('documentId')
            print(f"Doc creation successful. ID: {doc_id}")
            
            # Clean up: delete the doc (using Drive API which is also in client)
            if self.client.drive_service:
                self.client.drive_service.files().delete(fileId=doc_id).execute()
                print(f"Doc {doc_id} deleted successfully.")
        except Exception as e:
            self.fail(f"Docs API failed: {e}")

if __name__ == '__main__':
    unittest.main()

