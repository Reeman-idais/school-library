"""User model for the library management system."""

from dataclasses import dataclass, field
from uuid import UUID, uuid4

from .role import Role


@dataclass
class User:
    """Represents a user in the library system."""

    id: UUID
    username: str
    role: Role
    borrowed_book_ids: list[int] = field(default_factory=list)

    @classmethod
    def create(cls, username: str, role: Role) -> "User":
        """Create a new user with generated ID."""
        return cls(id=uuid4(), username=username, role=role)

    def to_dict(self) -> dict:
        """Convert user to dictionary for JSON serialization."""
        return {"id": str(self.id), "username": self.username, "role": self.role.value}

    @classmethod
    def from_dict(cls, data: dict) -> "User":
        """Create user from dictionary (JSON deserialization)."""
        return cls(
            id=UUID(data["id"]), username=data["username"], role=Role(data["role"])
        )
