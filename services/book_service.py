"""Book service with business logic for book operations."""

from typing import List, Optional, Tuple

from lib_logging.logger import get_logger
from models.book import Book, BookStatus
from storage.repositories.base import BookRepository
from storage.factory import StorageFactory
from validation.book_validator import (
    validate_book_for_creation,
    validate_book_for_update,
)

logger = get_logger(__name__)


class BookService:
    """Service for book-related operations.

    Uses a `BookRepository` abstraction for data access.
    """

    def __init__(self, storage: Optional[BookRepository] = None):
        """
        Initialize book service.

        Args:
            storage: BookRepository instance (creates new if not provided)
        """
        self.storage = storage or StorageFactory().create_book_storage()

    def add_book(
        self, book_id: int, title: str, author: str
    ) -> Tuple[Optional[Book], str]:
        """
        Add a new book to the library with user-provided ID.

        Args:
            book_id: Book ID (provided by user)
            title: Book title
            author: Book author

        Returns:
            Tuple of (book, error_message)
            If successful: (Book object, "")
            If failed: (None, error_message)
        """
        # Validate input
        title = title.strip()
        author = author.strip()

        # Check if book ID already exists
        if self.storage.get_book_by_id(book_id):
            error_msg = f"Book with ID {book_id} already exists"
            logger.warning(error_msg)
            return None, error_msg

        # Validate title/author and ID (convert ID to string for validation)
        is_valid, error_msg = validate_book_for_creation(
            book_id=str(book_id), title=title, author=author
        )
        if not is_valid:
            logger.warning(f"Book validation failed: {error_msg}")
            return None, error_msg

        # Create book with user-provided ID
        book = Book.create(book_id, title, author)

        # Save to storage
        if self.storage.add_book(book):
            logger.info(f"Added book: '{book.title}' by {book.author} (ID: {book.id})")
            return book, ""
        else:
            error_msg = "Failed to save book to storage"
            logger.error(error_msg)
            return None, error_msg

    def delete_book(self, book_id: int) -> Tuple[bool, str]:
        """
        Delete a book from the library.

        Args:
            book_id: Integer ID of the book to delete

        Returns:
            Tuple of (success, error_message)
            If successful: (True, "")
            If failed: (False, error_message)
        """
        # Check if book exists
        book = self.storage.get_book_by_id(book_id)
        if not book:
            error_msg = f"Book with ID '{book_id}' not found"
            logger.warning(error_msg)
            return False, error_msg

        # Check if book is borrowed
        if book.status == BookStatus.BORROWED:
            error_msg = f"Cannot delete book '{book.title}' - it is currently borrowed"
            logger.warning(error_msg)
            return False, error_msg

        # Delete book
        if self.storage.remove_book(book_id):
            logger.info(f"Deleted book: '{book.title}' (ID: {book_id})")
            return True, ""
        else:
            error_msg = "Failed to delete book from storage"
            logger.error(error_msg)
            return False, error_msg

    def update_book_info(
        self, book_id: int, title: Optional[str] = None, author: Optional[str] = None
    ) -> Tuple[Optional[Book], str]:
        """
        Update book information (title and/or author).

        Args:
            book_id: Integer ID of the book to update
            title: New title (optional)
            author: New author (optional)

        Returns:
            Tuple of (book, error_message)
            If successful: (Updated Book object, "")
            If failed: (None, error_message)
        """
        # Check if book exists
        book = self.storage.get_book_by_id(book_id)
        if not book:
            error_msg = f"Book with ID '{book_id}' not found"
            logger.warning(error_msg)
            return None, error_msg

        # Trim inputs
        if title is not None:
            title = title.strip()

        if author is not None:
            author = author.strip()

        if title is None and author is None:
            error_msg = "No fields to update"
            logger.warning(error_msg)
            return None, error_msg

        # Validate fields (title/author only); ID is provided as an integer and assumed valid
        is_valid, error_msg = validate_book_for_update(title=title, author=author)
        if not is_valid:
            logger.warning(f"Book update validation failed: {error_msg}")
            return None, error_msg

        # Update fields
        updated = False
        if title is not None:
            book.title = title
            updated = True

        if author is not None:
            book.author = author
            updated = True

        if not updated:
            error_msg = "No fields to update"
            logger.warning(error_msg)
            return None, error_msg

        # Save to storage
        if self.storage.update_book(book):
            logger.info(f"Updated book info: '{book.title}' (ID: {book_id})")
            return book, ""
        else:
            error_msg = "Failed to update book in storage"
            logger.error(error_msg)
            return None, error_msg

    def update_book_status(
        self, book_id: int, status: BookStatus
    ) -> Tuple[Optional[Book], str]:
        """
        Update book status (librarian only).

        Args:
            book_id: Integer ID of the book
            status: New status (Available, Picked, or Borrowed)

        Returns:
            Tuple of (book, error_message)
            If successful: (Updated Book object, "")
            If failed: (None, error_message)
        """
        # Check if book exists
        book = self.storage.get_book_by_id(book_id)
        if not book:
            error_msg = f"Book with ID '{book_id}' not found"
            logger.warning(error_msg)
            return None, error_msg

        # Update status
        book.status = status

        # Clear picked_by if status is not Picked
        if status != BookStatus.PICKED:
            book.picked_by = None

        # Save to storage
        if self.storage.update_book(book):
            logger.info(
                f"Updated book status: '{book.title}' (ID: {book_id}) to {status.value}"
            )
            return book, ""
        else:
            error_msg = "Failed to update book status in storage"
            logger.error(error_msg)
            return None, error_msg

    def pick_book(self, book_id: int, username: str) -> Tuple[Optional[Book], str]:
        """
        User picks a book for borrowing (requires librarian approval).

        Args:
            book_id: Integer ID of the book to pick
            username: Username of the user picking the book

        Returns:
            Tuple of (book, error_message)
            If successful: (Book object, "")
            If failed: (None, error_message)
        """
        # Check if book exists
        book = self.storage.get_book_by_id(book_id)
        if not book:
            error_msg = f"Book with ID '{book_id}' not found"
            logger.warning(error_msg)
            return None, error_msg

        # Check if book is available
        if book.status != BookStatus.AVAILABLE:
            error_msg = (
                f"Book '{book.title}' is not available (status: {book.status.value})"
            )
            logger.warning(error_msg)
            return None, error_msg

        # Set status to Picked and record username
        book.status = BookStatus.PICKED
        book.picked_by = username

        # Save to storage
        if self.storage.update_book(book):
            logger.info(f"User '{username}' picked book '{book.title}' (ID: {book_id})")
            return book, ""
        else:
            error_msg = "Failed to update book in storage"
            logger.error(error_msg)
            return None, error_msg

    def approve_borrow(self, book_id: int) -> Tuple[Optional[Book], str]:
        """
        Librarian approves a picked book and changes status to Borrowed.

        Args:
            book_id: Integer ID of the book to approve

        Returns:
            Tuple of (book, error_message)
            If successful: (Book object, "")
            If failed: (None, error_message)
        """
        # Check if book exists
        book = self.storage.get_book_by_id(book_id)
        if not book:
            error_msg = f"Book with ID '{book_id}' not found"
            logger.warning(error_msg)
            return None, error_msg

        # Check if book is picked
        if book.status != BookStatus.PICKED:
            error_msg = f"Book '{book.title}' is not in Picked status (current: {book.status.value})"
            logger.warning(error_msg)
            return None, error_msg

        # Change status to Borrowed (keep picked_by for reference)
        book.status = BookStatus.BORROWED

        # Save to storage
        if self.storage.update_book(book):
            logger.info(
                f"Librarian approved borrow for book '{book.title}' (ID: {book_id}) by '{book.picked_by}'"
            )
            return book, ""
        else:
            error_msg = "Failed to update book in storage"
            logger.error(error_msg)
            return None, error_msg

    def return_book(self, book_id: int) -> Tuple[Optional[Book], str]:
        """
        Librarian returns a borrowed book to Available status.

        Args:
            book_id: Integer ID of the book to return

        Returns:
            Tuple of (book, error_message)
            If successful: (Book object, "")
            If failed: (None, error_message)
        """
        # Check if book exists
        book = self.storage.get_book_by_id(book_id)
        if not book:
            error_msg = f"Book with ID '{book_id}' not found"
            logger.warning(error_msg)
            return None, error_msg

        # Check if book is borrowed
        if book.status != BookStatus.BORROWED:
            error_msg = f"Book '{book.title}' is not currently borrowed (status: {book.status.value})"
            logger.warning(error_msg)
            return None, error_msg

        # Change status to Available and clear picked_by
        book.status = BookStatus.AVAILABLE
        book.picked_by = None

        # Save to storage
        if self.storage.update_book(book):
            logger.info(
                f"Librarian returned book '{book.title}' (ID: {book_id}) to Available"
            )
            return book, ""
        else:
            error_msg = "Failed to update book in storage"
            logger.error(error_msg)
            return None, error_msg

    def get_book(self, book_id: int) -> Optional[Book]:
        """
        Get a book by ID.

        Args:
            book_id: Integer ID of the book

        Returns:
            Book object if found, None otherwise
        """
        return self.storage.get_book_by_id(book_id)

    def list_all_books(self) -> List[Book]:
        """
        Get all books.

        Returns:
            List of all Book objects
        """
        return self.storage.load_books()

    def list_picked_books(self) -> List[Book]:
        """
        Get all picked books (for librarian to see pending requests).

        Returns:
            List of Book objects with Picked status
        """
        books = self.storage.load_books()
        picked_books = [book for book in books if book.status == BookStatus.PICKED]
        logger.info(f"Listed {len(picked_books)} picked books")
        return picked_books
