"""Book data validation functions using internal ID."""

from typing import Optional, Tuple

from validation.id_validator import validate_id


def validate_book_data(
    book_id: Optional[str] = None,
    title: Optional[str] = None,
    author: Optional[str] = None,
) -> Tuple[bool, str]:
    """
    Validate book data fields.

    Args:
        book_id: Book internal ID (optional, validated if provided)
        title: Book title (optional, validated if provided)
        author: Book author (optional, validated if provided)

    Returns:
        Tuple of (is_valid, error_message)
        If valid: (True, "")
        If invalid: (False, error_message)
    """
    # Validate book ID if provided
    if book_id is not None:
        is_valid, error_msg = validate_id(book_id)
        if not is_valid:
            return False, f"Invalid book ID: {error_msg}"

    # Validate title if provided
    if title is not None:
        title = title.strip()
        if not title:
            return False, "Title cannot be empty"

    # Validate author if provided
    if author is not None:
        author = author.strip()
        if not author:
            return False, "Author cannot be empty"

    return True, ""


def validate_book_for_creation(
    book_id: Optional[str],
    title: str,
    author: str,
) -> Tuple[bool, str]:
    """
    Validate all required fields for book creation.

    Args:
        book_id: Optional book ID (if you allow client to pass)
        title: Book title
        author: Book author

    Returns:
        Tuple of (is_valid, error_message)
    """
    return validate_book_data(book_id=book_id, title=title, author=author)


def validate_book_for_update(
    book_id: Optional[str] = None,
    title: Optional[str] = None,
    author: Optional[str] = None,
) -> Tuple[bool, str]:
    """
    Validate fields for book update (all fields optional).

    Args:
        book_id: Optional book ID
        title: Book title (optional)
        author: Book author (optional)

    Returns:
        Tuple of (is_valid, error_message)
    """
    return validate_book_data(book_id=book_id, title=title, author=author)
