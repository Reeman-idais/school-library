"""Strategy pattern: pluggable validation strategies for maintainability."""

from typing import Any, Optional, Protocol, Tuple


class ValidationStrategy(Protocol):
    """
    Strategy interface for validation (Strategy pattern).
    Different validators can be plugged in without changing callers.
    """

    def validate(self, *args: Any, **kwargs: Any) -> Tuple[bool, str]:
        """
        Validate input.
        Returns (is_valid, error_message). If valid, error_message is empty.
        """
        ...


class BookValidationStrategy:
    """
    Validation strategy for book data (title, author, optional ISBN).
    Wraps existing validation functions for consistent Strategy interface.
    """

    def validate(
        self,
        title: Optional[str] = None,
        author: Optional[str] = None,
        isbn: Optional[str] = None,
    ) -> Tuple[bool, str]:
        from validation.book_validator import validate_book_data

        is_valid, msg = validate_book_data(title=title, author=author, isbn=isbn)
        return is_valid, msg


class UserValidationStrategy:
    """
    Validation strategy for user data (username, role).
    Wraps existing validation functions.
    """

    def validate_username(
        self, username: str, user_storage: Optional[Any] = None
    ) -> Tuple[bool, str]:
        from validation.user_validator import validate_username

        return validate_username(username, user_storage)

    def validate_role(self, role_string: str) -> Tuple[bool, str, Optional[Any]]:
        from validation.user_validator import validate_role

        return validate_role(role_string)
