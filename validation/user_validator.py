"""User data validation functions."""

import re
from typing import Optional, Tuple

from models.role import Role
from storage.user_storage import UserStorage


def validate_username(
    username: str, user_storage: Optional[UserStorage] = None
) -> Tuple[bool, str]:
    """
    Validate username format and uniqueness.

    Args:
        username: Username to validate
        user_storage: Optional UserStorage instance to check uniqueness

    Returns:
        Tuple of (is_valid, error_message)
        If valid: (True, "")
        If invalid: (False, error_message)
    """
    if not username:
        return False, "Username cannot be empty"

    username = username.strip()

    if not username:
        return False, "Username cannot be empty or whitespace only"

    # Check length (reasonable limits)
    if len(username) < 3:
        return False, "Username must be at least 3 characters long"

    if len(username) > 50:
        return False, "Username must be at most 50 characters long"

    # Check format: allow letters (any language), numbers, underscore, hyphen
    # Changed from r"^[a-zA-Z0-9_-]+$" to allow Unicode letters
    if not re.match(r"^[\w\-]+$", username, re.UNICODE):
        return (
            False,
            "Username can only contain letters, numbers, underscores, and hyphens",
        )

    # Check uniqueness if storage is provided
    if user_storage is not None:
        if user_storage.user_exists(username):
            return False, f"Username '{username}' already exists"

    return True, ""


def validate_role(role_string: str) -> Tuple[bool, str, Optional[Role]]:
    """
    Validate and parse role string.

    Args:
        role_string: Role string to validate

    Returns:
        Tuple of (is_valid, error_message, role)
        If valid: (True, "", Role enum)
        If invalid: (False, error_message, None)
    """
    if not role_string:
        return False, "Role cannot be empty", None

    role_string = role_string.strip().lower()

    try:
        role = Role(role_string)
        return True, "", role
    except ValueError:
        valid_roles = [r.value for r in Role]
        return (
            False,
            f"Invalid role '{role_string}'. Valid roles are: {', '.join(valid_roles)}",
            None,
        )


def validate_password(password: str) -> Tuple[bool, str]:
    """
    Validate password format (digits only).

    Args:
        password: Password to validate

    Returns:
        Tuple of (is_valid, error_message)
        If valid: (True, "")
        If invalid: (False, error_message)
    """
    if not password:
        return False, "Password cannot be empty"

    password = password.strip()

    if not password:
        return False, "Password cannot be empty or whitespace only"

    # Check length (minimum 4 digits)
    if len(password) < 4:
        return False, "Password must be at least 4 digits long"

    if len(password) > 20:
        return False, "Password must be at most 20 digits long"

    # Check format: digits only
    if not re.match(r"^\d+$", password):
        return False, "Password must contain only digits (numbers 0-9)"

    return True, ""
