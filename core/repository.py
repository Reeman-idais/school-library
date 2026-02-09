"""Repository pattern: abstract data access for loose coupling and testability."""

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Generic, List, Optional, Protocol, TypeVar

EntityT = TypeVar("EntityT")
KeyT = TypeVar("KeyT")


class Repository(ABC, Generic[EntityT, KeyT]):
    """
    Abstract repository interface (Repository pattern).
    Services depend on this abstraction for loose coupling and testability.
    """

    @abstractmethod
    def get_by_id(self, id: KeyT) -> Optional[EntityT]:
        """Load entity by id."""
        pass

    @abstractmethod
    def load_all(self) -> List[EntityT]:
        """Load all entities."""
        pass


# Protocol interfaces so storage implementations can be swapped (e.g. JSON, DB).
# BookStorage and UserStorage satisfy these protocols.


class BookRepository(Protocol):
    """Protocol for book persistence (implemented by BookStorage)."""

    def load_books(self) -> List["Book"]:
        pass

    def get_book_by_id(self, book_id: int) -> Optional["Book"]:
        pass

    def get_next_book_id(self) -> int:
        pass

    def add_book(self, book: "Book") -> bool:
        pass

    def update_book(self, book: "Book") -> bool:
        pass

    def remove_book(self, book_id: int) -> bool:
        pass


class UserRepository(Protocol):
    """Protocol for user persistence (implemented by UserStorage)."""

    def load_users(self) -> List["User"]:
        pass

    def get_user_by_username(self, username: str) -> Optional["User"]:
        pass

    def create_user(self, username: str, role: "Role") -> Optional["User"]:
        pass

    def user_exists(self, username: str) -> bool:
        pass


if TYPE_CHECKING:
    from models.book import Book
    from models.role import Role
    from models.user import User
