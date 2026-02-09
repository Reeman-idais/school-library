"""Integration tests for MongoDB book storage."""

import pytest

from models.book import Book, BookStatus


@pytest.mark.integration
class TestMongoDBBookStorage:
    """Integration tests for MongoDBBookStorage."""

    def test_initialization(self, mongodb_book_storage):
        """Test storage initialization."""
        assert mongodb_book_storage.collection is not None
        assert mongodb_book_storage.id_counter is not None

    def test_get_next_id_increments(self, mongodb_book_storage):
        """Test that ID counter increments properly."""
        id1 = mongodb_book_storage.get_next_book_id()
        id2 = mongodb_book_storage.get_next_book_id()
        id3 = mongodb_book_storage.get_next_book_id()

        assert id1 == 1
        assert id2 == 2
        assert id3 == 3

    def test_add_and_retrieve_book(self, mongodb_book_storage):
        """Test adding and retrieving a book."""
        book = Book.create(1, "Python Guide", "Guido van Rossum")

        result = mongodb_book_storage.add_book(book)
        assert result is True

        retrieved = mongodb_book_storage.get_book_by_id(1)
        assert retrieved is not None
        assert retrieved.title == "Python Guide"
        assert retrieved.author == "Guido van Rossum"
        assert retrieved.status == BookStatus.AVAILABLE

    def test_load_all_books(self, mongodb_book_storage):
        """Test loading all books."""
        books = [
            Book.create(1, "Book 1", "Author 1"),
            Book.create(2, "Book 2", "Author 2"),
            Book.create(3, "Book 3", "Author 3"),
        ]

        for book in books:
            mongodb_book_storage.add_book(book)

        loaded = mongodb_book_storage.load_books()
        assert len(loaded) == 3
        assert loaded[0].id == 1
        assert loaded[1].id == 2
        assert loaded[2].id == 3

    def test_update_book(self, mongodb_book_storage):
        """Test updating a book."""
        book = Book.create(1, "Original Title", "Author")
        mongodb_book_storage.add_book(book)

        book.title = "Updated Title"
        book.status = BookStatus.BORROWED
        book.picked_by = "alice"

        result = mongodb_book_storage.update_book(book)
        assert result is True

        updated = mongodb_book_storage.get_book_by_id(1)
        assert updated.title == "Updated Title"
        assert updated.status == BookStatus.BORROWED
        assert updated.picked_by == "alice"

    def test_remove_book(self, mongodb_book_storage):
        """Test removing a book."""
        book = Book.create(1, "Book to Remove", "Author")
        mongodb_book_storage.add_book(book)

        result = mongodb_book_storage.remove_book(1)
        assert result is True

        retrieved = mongodb_book_storage.get_book_by_id(1)
        assert retrieved is None

    def test_search_books_by_title(self, mongodb_book_storage):
        """Test searching books by title."""
        books = [
            Book.create(1, "Python Guide", "Author 1"),
            Book.create(2, "Java Guide", "Author 2"),
            Book.create(3, "Python Advanced", "Author 3"),
        ]

        for book in books:
            mongodb_book_storage.add_book(book)

        results = mongodb_book_storage.search_books(title="Python")
        assert len(results) == 2
        assert all("Python" in b.title for b in results)

    def test_search_books_by_author(self, mongodb_book_storage):
        """Test searching books by author."""
        books = [
            Book.create(1, "Book 1", "John Doe"),
            Book.create(2, "Book 2", "Jane Smith"),
            Book.create(3, "Book 3", "John Doe"),
        ]

        for book in books:
            mongodb_book_storage.add_book(book)

        results = mongodb_book_storage.search_books(author="John")
        assert len(results) == 2
        assert all("John" in b.author for b in results)

    def test_search_books_by_status(self, mongodb_book_storage):
        """Test searching books by status."""
        book1 = Book.create(1, "Available Book", "Author")
        book2 = Book.create(2, "Borrowed Book", "Author")
        book2.status = BookStatus.BORROWED

        mongodb_book_storage.add_book(book1)
        mongodb_book_storage.add_book(book2)

        results = mongodb_book_storage.search_books(status=BookStatus.BORROWED.value)
        assert len(results) == 1
        assert results[0].status == BookStatus.BORROWED

    def test_get_nonexistent_book(self, mongodb_book_storage):
        """Test getting a book that doesn't exist."""
        result = mongodb_book_storage.get_book_by_id(999)
        assert result is None

    def test_remove_nonexistent_book(self, mongodb_book_storage):
        """Test removing a book that doesn't exist."""
        result = mongodb_book_storage.remove_book(999)
        assert result is False

    def test_update_nonexistent_book(self, mongodb_book_storage):
        """Test updating a book that doesn't exist."""
        book = Book.create(999, "Nonexistent", "Author")
        result = mongodb_book_storage.update_book(book)
        assert result is False
