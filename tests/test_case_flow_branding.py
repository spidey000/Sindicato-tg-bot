import pytest
from unittest.mock import MagicMock, patch
import sys
import os

# Add src to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

from src.integrations.docs_client import DelegadoDocsClient

def test_docs_client_branding_default():
    """
    Verify that DelegadoDocsClient uses 'Marxnager' as default BOT_NAME.
    """
    # Mock credentials to allow instantiation
    with patch('src.integrations.docs_client.get_google_creds', return_value=MagicMock()):
        with patch('src.integrations.docs_client.build'):
            client = DelegadoDocsClient()
            
            # We want to check the logic inside append_text
            # But append_text builds the request internally.
            # We'll mock os.getenv to ensure it doesn't pick up a random env var
            # and verify the string construction.
            
            # Actually, we can just inspect the source code via the test?
            # Or we can run it and check the arguments passed to batchUpdate.
            
            client.service = MagicMock()
            
            with patch.dict(os.environ, {}, clear=True):
                # Remove BOT_NAME if exists
                if 'BOT_NAME' in os.environ:
                    del os.environ['BOT_NAME']
                
                client.append_text("doc_id", "Test text")
                
                # Verify batchUpdate call
                calls = client.service.documents().batchUpdate.call_args_list
                assert len(calls) == 1
                
                # Drill down to body
                body = calls[0][1]['body']
                requests = body['requests']
                insert_text = requests[0]['insertText']['text']
                
                assert "Marxnager" in insert_text
                assert "Delegado 360" not in insert_text

if __name__ == "__main__":
    pytest.main([__file__])
