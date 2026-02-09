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

    @classmethod
    def create(cls, book_id: int, title: str, author: str) -> "Book":
        """Create a new book with specified ID and AVAILABLE status."""
        return cls(
            id=book_id,
            title=title.strip(),
            author=author.strip(),
            status=BookStatus.AVAILABLE,
            picked_by=None,
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
        )
