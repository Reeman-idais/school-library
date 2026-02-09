"""Role enumeration for user roles in the library system."""

from enum import Enum


class Role(Enum):
    """User roles in the library management system."""

    LIBRARIAN = "librarian"
    USER = "user"

    def __str__(self):
        return self.value
