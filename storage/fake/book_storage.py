"""In-memory (fake) book storage used for unit tests and CI.

This implementation mirrors the public API of the production storages but
keeps everything in memory for deterministic, fast tests.
"""

from typing import List, Optional

from lib_logging.logger import get_logger
from models.book import Book

logger = get_logger(__name__)


class FakeBookStorage:
    """In-memory book storage used for tests."""

    def __init__(self):
        self._books: List[Book] = []
        self._next_id: int = 1

    def load_books(self) -> List[Book]:
        return list(self._books)

    def _reset(self) -> None:
        self._books = []
        self._next_id = 1

    def save_books(self, books: List[Book]) -> bool:
        self._books = list(books)
        return True

    def get_next_book_id(self) -> int:
        nid = self._next_id
        self._next_id += 1
        return nid

    def get_book_by_id(self, book_id: int) -> Optional[Book]:
        for b in self._books:
            if b.id == book_id:
                return b
        return None

    def add_book(self, book: Book) -> bool:
        if any(b.id == book.id for b in self._books):
            logger.warning("Book with ID %s already exists", book.id)
            return False
        self._books.append(book)
        return True

    def update_book(self, book: Book) -> bool:
        for i, b in enumerate(self._books):
            if b.id == book.id:
                self._books[i] = book
                return True
        logger.warning("Book with ID %s not found for update", book.id)
        return False

    def remove_book(self, book_id: int) -> bool:
        new_books = [b for b in self._books if b.id != book_id]
        if len(new_books) == len(self._books):
            logger.warning("Book with ID %s not found for removal", book_id)
            return False
        self._books = new_books
        return True
