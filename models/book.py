"""Book model for the library management system."""

from dataclasses import dataclass
from enum import Enum
from typing import Optional


class BookStatus(Enum):
    """Book availability status."""

    AVAILABLE = "Available"
    PICKED = "Picked"
    BORROWED = "Borrowed"

    def __str__(self):
        return self.value


@dataclass
class Book:
    """Represents a book in the library system."""

    id: int
    title: str
    author: str
    status: BookStatus
    picked_by: Optional[str] = None  # Username who picked the book
    isbn: Optional[str] = None  # Optional ISBN (backwards-compatible)

    @classmethod
    def create(
        cls,
        book_id: int,
        title: str,
        author: str,
        status: "Optional[BookStatus]" = None,
        picked_by: Optional[str] = None,
        isbn: Optional[str] = None,
        **kwargs,
    ) -> "Book":
        """Create a new book.

        Args:
            book_id: numeric identifier for the book
            title: book title
            author: book author
            status: optional BookStatus (defaults to AVAILABLE)
            picked_by: optional username who picked the book
            isbn: optional ISBN string (forward-compatibility)
            **kwargs: ignore any additional fields (forward-compatibility)

        The factory is intentionally forgiving: callers (storage layers,
        deserializers or third-party code) may pass extra keys — silently
        ignore them to remain robust across data shape changes.
        """
        # Accept and ignore unexpected kwargs to be defensive against callers
        # that pass the whole document (e.g. `Book.create(**doc)`).
        return cls(
            id=book_id,
            title=title.strip(),
            author=author.strip(),
            status=status or BookStatus.AVAILABLE,
            picked_by=picked_by,
            isbn=isbn,
        )

    def to_dict(self) -> dict:
        """Convert book to dictionary for JSON serialization."""
        result = {
            "id": self.id,
            "title": self.title,
            "author": self.author,
            "status": self.status.value,
        }
        if self.picked_by:
            result["picked_by"] = self.picked_by
        if self.isbn:
            result["isbn"] = self.isbn
        return result

    @classmethod
    def from_dict(cls, data: dict) -> "Book":
        """Create book from dictionary (JSON deserialization)."""
        # ID should already be migrated to int by storage layer
        book_id = int(data["id"])

        # Handle status
        status_str = data.get("status", "Available")
        try:
            status = BookStatus(status_str)
        except ValueError:
            # Map old statuses to new ones
            if status_str == "Available":
                status = BookStatus.AVAILABLE
            elif status_str == "Borrowed":
                status = BookStatus.BORROWED
            else:
                status = BookStatus.AVAILABLE

        return cls(
            id=book_id,
            title=data["title"],
            author=data["author"],
            status=status,
            picked_by=data.get("picked_by"),
            isbn=data.get("isbn"),
        )
