from __future__ import annotations

from typing import List, Optional

from models.book import Book
from storage.book_storage import BookStorage
from storage.repositories.base import BookRepository


class JSONBookRepository(BookRepository):
    """Repository adapter that delegates to BookStorage (JSON file)."""

    def __init__(self, storage: Optional[BookStorage] = None):
        self._storage = storage or BookStorage()

    def load_books(self) -> List[Book]:
        return self._storage.load_books()

    def get_book_by_id(self, book_id: int) -> Optional[Book]:
        return self._storage.get_book_by_id(book_id)

    def get_next_book_id(self) -> int:
        return self._storage.get_next_book_id()

    def add_book(self, book: Book) -> bool:
        return self._storage.add_book(book)

    def update_book(self, book: Book) -> bool:
        return self._storage.update_book(book)

    def remove_book(self, book_id: int) -> bool:
        return self._storage.remove_book(book_id)
