from __future__ import annotations

from typing import List, Optional

from models.book import Book
from storage.repositories.base import BookRepository
from storage.mongodb.book_storage import MongoDBBookStorage


class MongoBookRepository(BookRepository):
    """Repository adapter that delegates to MongoDBBookStorage."""

    def __init__(self, storage: Optional[MongoDBBookStorage] = None):
        self._storage = storage or MongoDBBookStorage()

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

    def search_books(self, **kwargs):
        return self._storage.search_books(**kwargs)
