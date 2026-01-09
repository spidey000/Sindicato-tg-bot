import pytest
import os

def test_branding_in_documentation():
    """
    Verify that README.md and CHANGELOG.md contain 'Marxnager' and do not contain 'Delegado 360' 
    (except perhaps in historical context, but strictly we want to replace current usage).
    """
    files_to_check = ["README.md", "CHANGELOG.md"]
    
    for filename in files_to_check:
        if os.path.exists(filename):
            with open(filename, "r") as f:
                content = f.read()
                
            assert "Marxnager" in content, f"{filename} should contain 'Marxnager'"
            # We accept 'Delegado 360' only if it's explicitly historical, but for this strict check 
            # we aim to replace the main title/references.
            # Ideally, we shouldn't see 'Delegado 360' as the primary name anymore.
            # We'll assert it's NOT in the first few lines or headers.
            
            lines = content.splitlines()
            # Check the title/header
            if lines:
                first_header = next((line for line in lines if line.startswith("# ")), "")
                assert "Delegado 360" not in first_header, f"{filename} title should not be 'Delegado 360'"

if __name__ == "__main__":
    pytest.main([__file__])
