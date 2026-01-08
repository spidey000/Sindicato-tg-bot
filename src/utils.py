from datetime import datetime
import random

def generate_case_id(type_prefix="D"):
    """Generates a case ID like D-2026-001."""
    year = datetime.now().year
    # In a real app, this would check the DB for the last sequence. 
    # For now, we use a random number to avoid collisions in this prototype.
    sequence = random.randint(100, 999) 
    return f"{type_prefix}-{year}-{sequence}"
