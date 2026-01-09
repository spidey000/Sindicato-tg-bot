import pytest
import os

def test_branding_in_product_docs():
    """
    Verify that PRD.md and conductor/product.md contain 'Marxnager' and do not contain 'Delegado 360'
    in the title or primary descriptions.
    """
    files_to_check = ["PRD.md", "conductor/product.md"]
    
    for filename in files_to_check:
        if os.path.exists(filename):
            with open(filename, "r") as f:
                content = f.read()
                
            assert "Marxnager" in content, f"{filename} should contain 'Marxnager'"
            
            lines = content.splitlines()
            if lines:
                first_header = next((line for line in lines if line.startswith("# ")), "")
                assert "Delegado 360" not in first_header, f"{filename} title should not be 'Delegado 360'"

if __name__ == "__main__":
    pytest.main([__file__])
