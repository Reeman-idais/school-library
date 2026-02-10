"""User model for the library management system."""

from dataclasses import dataclass, field
from typing import List

from .role import Role


@dataclass
class User:
    """Represents a user in the library system."""

    id: int
    username: str
    password: str
    role: Role
    borrowed_book_ids: List[int] = field(default_factory=list)

    @classmethod
    def create(cls, username: str, password: str, role: Role) -> "User":
        """Create a new user with placeholder id (storage will assign an ID)."""
        return cls(
            id=0, username=username, password=password, role=role, borrowed_book_ids=[]
        )

    def to_dict(self) -> dict:
        """Convert user to dictionary for JSON serialization."""
        return {
            "id": self.id,
            "username": self.username,
            "password": self.password,
            "role": self.role.value,
            "borrowed_book_ids": self.borrowed_book_ids,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "User":
        """Create user from dictionary (JSON deserialization)."""
        return cls(
            id=int(data["id"]),
            username=data["username"],
            password=data.get("password", ""),
            role=Role(data["role"]),
            borrowed_book_ids=data.get("borrowed_book_ids", []),
        )
