import random
import string
from datetime import datetime


def generate_ref_id() -> str:
    """
    Generate human-friendly reference ID
    Format: ACB + 5 alphanumeric characters (uppercase)
    Example: ACB12A4D, ACBX9K2M
    """
    chars = string.ascii_uppercase + string.digits
    random_part = ''.join(random.choices(chars, k=5))
    return f"ACB{random_part}"


def generate_unique_ref_id(existing_ids: set = None) -> str:
    """
    Generate unique reference ID
    Ensures no collision with existing IDs
    """
    max_attempts = 100
    existing_ids = existing_ids or set()
    
    for _ in range(max_attempts):
        ref_id = generate_ref_id()
        if ref_id not in existing_ids:
            return ref_id
    
    # Fallback with timestamp
    timestamp = datetime.utcnow().strftime("%H%M%S")
    return f"ACB{timestamp[:5]}"