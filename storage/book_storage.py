"""Book storage operations using JSON persistence."""

import json
import shutil
from pathlib import Path
from typing import List, Optional

from models.book import Book
from lib_logging.logger import get_logger

logger = get_logger(__name__)


class BookStorage:
    """Handles book data persistence in JSON format with auto-incrementing IDs."""

    def __init__(self, data_dir: Optional[Path] = None):
        if data_dir is None:
            data_dir = Path(__file__).parent.parent / "data"
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.books_file = self.data_dir / "books.json"

    def load_books(self) -> List[Book]:
        """Load all books from JSON file."""
        if not self.books_file.exists():
            logger.info("Books file not found, creating empty file")
            self._save_books_internal([])
            return []

        try:
            with open(self.books_file, "r", encoding="utf-8") as f:
                data = json.load(f)
            books = []
            for item in data:
                book_id = item.get("id")
                if isinstance(book_id, str) and book_id.isdigit():
                    item["id"] = int(book_id)
                books.append(Book.from_dict(item))
            logger.info("Loaded %d books from storage", len(books))
            return books
        except (json.JSONDecodeError, KeyError) as e:
            logger.error("Failed to parse books JSON: %s", e)
            if self.books_file.exists():
                backup = self.books_file.with_suffix(".json.bak")
                shutil.copy2(self.books_file, backup)
                logger.warning("Created backup at %s", backup)
            return []
        except Exception as e:
            logger.error("Error loading books: %s", e)
            return []

    def _save_books_internal(self, books: List[Book]) -> bool:
        """Save books to JSON with atomic write."""
        temp_file = self.books_file.with_suffix(".json.tmp")
        try:
            with open(temp_file, "w", encoding="utf-8") as f:
                data = [b.to_dict() for b in books]
                json.dump(data, f, indent=2, ensure_ascii=False)
            temp_file.replace(self.books_file)
            logger.info("Saved %d books to storage", len(books))
            return True
        except Exception as e:
            logger.error("Error writing books file: %s", e)
            if temp_file.exists():
                temp_file.unlink(missing_ok=True)
            return False

    def save_books(self, books: List[Book]) -> bool:
        """Save books to JSON file."""
        try:
            return self._save_books_internal(books)
        except Exception as e:
            logger.error("Error saving books: %s", e)
            return False

    def get_next_book_id(self) -> int:
        """Return next available integer ID (max existing + 1)."""
        books = self.load_books()
        if not books:
            return 1
        return max(b.id for b in books) + 1

    def get_book_by_id(self, book_id: int) -> Optional[Book]:
        """Get a book by integer ID."""
        books = self.load_books()
        for book in books:
            if book.id == book_id:
                return book
        return None

    def add_book(self, book: Book) -> bool:
        """Add a book to storage."""
        books = self.load_books()
        if any(b.id == book.id for b in books):
            logger.warning("Book with ID %s already exists", book.id)
            return False
        books.append(book)
        return self.save_books(books)

    def update_book(self, book: Book) -> bool:
        """Update an existing book in storage."""
        books = self.load_books()
        for i, b in enumerate(books):
            if b.id == book.id:
                books[i] = book
                return self.save_books(books)
        logger.warning("Book with ID %s not found for update", book.id)
        return False

    def remove_book(self, book_id: int) -> bool:
        """Remove a book from storage by ID."""
        books = self.load_books()
        new_books = [b for b in books if b.id != book_id]
        if len(new_books) == len(books):
            logger.warning("Book with ID %s not found for removal", book_id)
            return False
        return self.save_books(new_books)
