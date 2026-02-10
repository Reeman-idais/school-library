from __future__ import annotations

from abc import ABC, abstractmethod
from typing import List, Optional

from models.book import Book


class BookRepository(ABC):
    """Abstract base class for book repositories."""

    @abstractmethod
    def load_books(self) -> List[Book]:
        pass

    @abstractmethod
    def get_book_by_id(self, book_id: int) -> Optional[Book]:
        pass

    @abstractmethod
    def get_next_book_id(self) -> int:
        pass

    @abstractmethod
    def add_book(self, book: Book) -> bool:
        pass

    @abstractmethod
    def update_book(self, book: Book) -> bool:
        pass

    @abstractmethod
    def remove_book(self, book_id: int) -> bool:
        pass

    def search_books(self, **kwargs) -> List[Book]:
        """Optional search; default to naive filter over load_books()."""
        books = self.load_books()
        results = []
        title = kwargs.get("title")
        author = kwargs.get("author")
        status = kwargs.get("status")
        for book in books:
            if title and title.lower() not in book.title.lower():
                continue
            if author and author.lower() not in book.author.lower():
                continue
            if status and str(book.status.value) != str(status):
                continue
            results.append(book)
        return results
