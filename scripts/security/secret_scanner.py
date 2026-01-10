import re
import subprocess
import os

# Common patterns for secrets
# Captures: 
# 1=Variable Name
# 2=Whitespace before separator
# 3=Separator (= or :)
# 4=Whitespace after separator
# 5=Quote (optional)
# 6=Secret Value
SECRET_PATTERN = re.compile(
    r'''(?i)(API_KEY|TOKEN|PASSWORD|SECRET|CREDENTIALS?)(\s*)([=:])(\s*)(["'])?([^"'\s]+)\5?'''
)

def redact_line(line: str) -> str:
    """
    Scans a line for secrets and returns the redacted line.
    """
    def replace_match(match):
        key = match.group(1)
        ws1 = match.group(2)
        sep = match.group(3)
        ws2 = match.group(4)
        quote = match.group(5) or ''
        return f"{key}{ws1}{sep}{ws2}{quote}<REDACTED_SECRET>{quote}"
        
    return SECRET_PATTERN.sub(replace_match, line)

def find_secrets(text: str) -> list[str]:
    """
    Finds potential secrets in the text based on common patterns.
    Returns a list of the found secret values.
    """
    matches = SECRET_PATTERN.findall(text)
    # The secret value is the 6th capture group (index 5)
    return [match[5] for match in matches]

def get_tracked_files() -> list[str]:
    """
    Returns a list of files tracked by git in the current repository.
    """
    try:
        result = subprocess.run(
            ['git', 'ls-files'],
            capture_output=True,
            text=True,
            check=True
        )
        return result.stdout.splitlines()
    except subprocess.CalledProcessError:
        return []
