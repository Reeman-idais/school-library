"""Borrow service with business logic for borrow/return operations."""

from typing import List, Optional, Tuple

from models.book import Book, BookStatus
from storage.book_storage import BookStorage
from lib_logging.logger import get_logger

logger = get_logger(__name__)


class BorrowService:
    """Service for borrow and return operations."""

    def __init__(self, storage: BookStorage = None):
        """
        Initialize borrow service.

        Args:
            storage: BookStorage instance (creates new if not provided)
        """
        self.storage = storage or BookStorage()

    def borrow_book(self, book_id: int, username: str) -> Tuple[Optional[Book], str]:
        """
        Borrow a book (change status to BORROWED).

        Args:
            book_id: Integer ID of the book to borrow
            username: Username of the borrower

        Returns:
            Tuple of (book, error_message)
        """
        book = self.storage.get_book_by_id(book_id)
        if not book:
            error_msg = f"Book with ID '{book_id}' not found"
            logger.warning(error_msg)
            return None, error_msg

        if book.status != BookStatus.AVAILABLE:
            error_msg = (
                f"Book '{book.title}' is not available (status: {book.status.value})"
            )
            logger.warning(error_msg)
            return None, error_msg

        book.status = BookStatus.BORROWED

        if self.storage.update_book(book):
            logger.info(
                f"User '{username}' borrowed book '{book.title}' (ID: {book_id})"
            )
            return book, ""
        else:
            error_msg = "Failed to update book status in storage"
            logger.error(error_msg)
            return None, error_msg

    def return_book(self, book_id: int) -> Tuple[Optional[Book], str]:
        """
        Return a book (change status to AVAILABLE).

        Args:
            book_id: Integer ID of the book to return

        Returns:
            Tuple of (book, error_message)
        """
        book = self.storage.get_book_by_id(book_id)
        if not book:
            error_msg = f"Book with ID '{book_id}' not found"
            logger.warning(error_msg)
            return None, error_msg

        if book.status != BookStatus.BORROWED:
            error_msg = f"Book '{book.title}' is not currently borrowed (status: {book.status.value})"
            logger.warning(error_msg)
            return None, error_msg

        book.status = BookStatus.AVAILABLE

        if self.storage.update_book(book):
            logger.info(f"Book '{book.title}' returned (ID: {book_id})")
            return book, ""
        else:
            error_msg = "Failed to update book status in storage"
            logger.error(error_msg)
            return None, error_msg

    def list_available_books(self) -> List[Book]:
        """
        List all available books.

        Returns:
            List of Book objects with AVAILABLE status
        """
        books = self.storage.load_books()
        available = [book for book in books if book.status == BookStatus.AVAILABLE]
        logger.info(f"Listed {len(available)} available books")
        return available

    def search_books(self, query: str) -> List[Book]:
        """
        Search books by title or author.

        Args:
            query: Search query string

        Returns:
            List of matching Book objects
        """
        if not query:
            return []

        query_lower = query.lower().strip()
        books = self.storage.load_books()
        matches = []

        for book in books:
            if query_lower in book.title.lower() or query_lower in book.author.lower():
                matches.append(book)

        logger.info(f"Search for '{query}' found {len(matches)} books")
        return matches
