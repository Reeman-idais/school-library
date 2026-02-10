from __future__ import annotations

from typing import List, Optional

from models.book import Book
from storage.repositories.base import BookRepository


class FakeBookRepository(BookRepository):
    """In-memory fake repository for unit tests."""

    def __init__(self):
        self._books: List[Book] = []
        self._next_id = 1

    def load_books(self) -> List[Book]:
        # return a copy to avoid tests mutating internal state directly
        return [Book.from_dict(b.to_dict()) for b in self._books]

    def get_book_by_id(self, book_id: int) -> Optional[Book]:
        for book in self._books:
            if book.id == book_id:
                return Book.from_dict(book.to_dict())
        return None

    def get_next_book_id(self) -> int:
        nid = self._next_id
        self._next_id += 1
        return nid

    def add_book(self, book: Book) -> bool:
        if any(b.id == book.id for b in self._books):
            return False
        self._books.append(Book.from_dict(book.to_dict()))
        # keep next id consistent
        if book.id >= self._next_id:
            self._next_id = book.id + 1
        return True

    def update_book(self, book: Book) -> bool:
        for i, b in enumerate(self._books):
            if b.id == book.id:
                self._books[i] = Book.from_dict(book.to_dict())
                return True
        return False

    def remove_book(self, book_id: int) -> bool:
        before = len(self._books)
        self._books = [b for b in self._books if b.id != book_id]
        return len(self._books) != before
