import re
import subprocess
import os
import sys

# Final refined pattern for secrets:
# - Targets KEY=VALUE or KEY: VALUE
# - VALUE must look like a literal (starts with quote, or is a long hex/random string)
# - Excludes safe patterns like os.getenv, or simple variable-to-variable assignments
# Captures:
# 1=Key name
# 2=Whitespace before separator
# 3=Separator (= or :)
# 4=Whitespace after separator
# 5=Opening quote (optional)
# 6=Value
# 7=Closing quote (must match opening if present)
SECRET_PATTERN = re.compile(
    r'''(?i)(API_KEY|TOKEN|PASSWORD|SECRET|CREDENTIALS?)'''      # Key
    r'''(\s*)([=:])(\s*)'''                                     # Assignment
    r'''(["'])?'''                                              # Optional opening quote
    r'''(?![^"']*(?:os\.getenv|os\.environ|env\.get))'''         # Negative lookahead for safe functions
    r'''([a-zA-Z0-9\-_]{16,})'''                                 # Value (min 16 chars, alphanumeric/dash/underscore)
    r'''\5?'''                                                  # Optional closing quote
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
    Returns a list of files tracked by git in the current repository,
    excluding common directories and the scanner itself.
    """
    try:
        result = subprocess.run(
            ['git', 'ls-files'],
            capture_output=True,
            text=True,
            check=True
        )
        all_files = result.stdout.splitlines()
        
        # Filter out unwanted paths
        excluded_prefixes = (
            'node_modules/',
            'tests/',
            'scripts/security/secret_scanner.py',
            'conductor/tracks/secret_redaction_20260110/plan.md'
        )
        
        filtered_files = [
            f for f in all_files 
            if not f.startswith(excluded_prefixes)
        ]
        
        return filtered_files
    except subprocess.CalledProcessError:
        return []

def process_file(file_path: str, dry_run: bool = True) -> int:
    """
    Processes a single file, redacting any secrets found.
    Returns the number of secrets redacted.
    """
    if not os.path.exists(file_path):
        return 0
        
    # Skip binary files
    try:
        with open(file_path, 'tr') as f:
            f.read(1024)
    except (UnicodeDecodeError, PermissionError):
        return 0

    secrets_count = 0
    new_lines = []
    
    with open(file_path, 'r') as f:
        for line_num, line in enumerate(f, 1):
            redacted = redact_line(line)
            if redacted != line:
                secrets_count += 1
                print(f"  [FOUND] {file_path}:{line_num}")
                new_lines.append(redacted)
            else:
                new_lines.append(line)
                
    if secrets_count > 0 and not dry_run:
        with open(file_path, 'w') as f:
            f.writelines(new_lines)
        print(f"  [REDACTED] {file_path}: {secrets_count} occurrences")
        
    return secrets_count

def run_scan(dry_run: bool = True):
    """
    Runs a full scan of the repository.
    """
    print(f"Starting secret scan (dry_run={dry_run})...")
    files = get_tracked_files()
    total_secrets = 0
    modified_files = 0
    
    for file_path in files:
        count = process_file(file_path, dry_run=dry_run)
        if count > 0:
            total_secrets += count
            modified_files += 1
            
    print("\nScan complete.")
    print(f"Files scanned: {len(files)}")
    print(f"Files with secrets: {modified_files}")
    print(f"Total secrets found: {total_secrets}")
    
    if dry_run and total_secrets > 0:
        print("\nRun with --apply to redact detected secrets.")

if __name__ == "__main__":
    apply_changes = "--apply" in sys.argv
    run_scan(dry_run=not apply_changes)