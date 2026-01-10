import re

# Common patterns for secrets
# Captures: 1=Variable Name, 2=Separator, 3=Quote (optional), 4=Secret Value
SECRET_PATTERN = re.compile(
    r'(?i)(API_KEY|TOKEN|PASSWORD|SECRET|CREDENTIALS?)\s*(=|:)\s*(["\'])?([^"\s\']+)\3?'
)

def scan_line(line: str) -> str:
    """
    Scans a line for secrets and returns the redacted line.
    """
    # Placeholder for now, will be implemented in next task
    return line

def find_secrets(text: str) -> list[str]:
    """
    Finds potential secrets in the text based on common patterns.
    Returns a list of the found secret values.
    """
    matches = SECRET_PATTERN.findall(text)
    # The secret value is the 4th capture group (index 3)
    return [match[3] for match in matches]