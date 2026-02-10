"""Repository interfaces (Protocols) for storage layer.

Define the repository contracts that services depend upon. This enforces
Dependency Inversion and enables different implementations (JSON, MongoDB,
in-memory/fake) to be substituted without changing business logic.
"""

from typing import List, Optional, Protocol

from models.book import Book
from models.role import Role
from models.user import User


class BookRepository(Protocol):
    def load_books(self) -> List[Book]: ...

    def get_book_by_id(self, book_id: int) -> Optional[Book]: ...

    def add_book(self, book: Book) -> bool: ...

    def update_book(self, book: Book) -> bool: ...

    def remove_book(self, book_id: int) -> bool: ...


class UserRepository(Protocol):
    def load_users(self) -> List[User]: ...

    def get_user_by_id(self, user_id: int) -> Optional[User]: ...

    def get_user_by_username(self, username: str) -> Optional[User]: ...

    def create_user(
        self, username: str, password: str, role: Role
    ) -> Optional[User]: ...

    def update_user(self, user: User) -> bool: ...

    def remove_user(self, user_id: int) -> bool: ...

    def user_exists(self, username: str) -> bool: ...
