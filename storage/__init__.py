"""Storage package for the Library Management System."""

from .book_storage import BookStorage
from .user_storage import UserStorage

__all__ = ["BookStorage", "UserStorage"]
