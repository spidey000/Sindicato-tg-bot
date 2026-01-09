from datetime import datetime
import random

def generate_case_id(type_prefix="D", last_id=None):
    """
    Generates a case ID like D-2026-001.
    If last_id is provided (e.g., 'D-2026-015'), it increments the sequence.
    Otherwise, it starts at 001.
    """
    year = datetime.now().year
    
    if last_id:
        try:
            # Parse last_id: D-2026-015
            parts = last_id.split("-")
            if len(parts) == 3:
                last_year = int(parts[1])
                last_seq = int(parts[2])
                
                if last_year == year:
                    new_seq = last_seq + 1
                    return f"{type_prefix}-{year}-{new_seq:03d}"
        except ValueError:
            pass # Fallback to 001 if parse fails

    # Default / Fallback
    return f"{type_prefix}-{year}-001"
