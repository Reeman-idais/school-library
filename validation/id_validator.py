"""ID validation functions."""

import re
from typing import Tuple


def validate_id(id_str: str) -> Tuple[bool, str]:
    """
    Validate ID format (4-10 digits).

    ID format: 4 to 10 digits only

    Args:
        id_str: ID string to validate

    Returns:
        Tuple of (is_valid, error_message)
        If valid: (True, "")
        If invalid: (False, error_message)
    """
    if not id_str:
        return False, "ID cannot be empty"

    # Remove hyphens and spaces
    id_clean = re.sub(r"[-\s]", "", id_str)

    # Check if it's all digits
    if not id_clean.isdigit():
        return False, "ID must contain only digits"

    # Check length (4-10 digits)
    length = len(id_clean)
    if length < 4:
        return False, f"ID must be at least 4 digits (got {length})"
    if length > 10:
        return False, f"ID must be at most 10 digits (got {length})"

    return True, ""


def normalize_id(id_str: str) -> str:
    """
    Normalize ID by removing hyphens and spaces.

    Args:
        id_str: ID string to normalize

    Returns:
        Normalized ID string (digits only)
    """
    if not id_str:
        return ""

    # Remove hyphens and spaces, keep only digits
    normalized = re.sub(r"[-\s]", "", id_str)
    return normalized
