"""Integration tests for the library management system."""

import tempfile
from pathlib import Path

import pytest

from models.book import BookStatus
from services.book_service import BookService
from services.user_service import UserService
from storage.book_storage import BookStorage
from storage.user_storage import UserStorage


@pytest.mark.integration
class TestIntegration:
    """Integration tests with real storage (using temp files)."""

    @pytest.fixture
    def temp_data_dir(self):
        """Create temporary directory for test data."""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield Path(tmpdir)

    @pytest.fixture
    def book_storage(self, temp_data_dir):
        """Create BookStorage with temp directory."""
        return BookStorage(data_dir=temp_data_dir)

    @pytest.fixture
    def user_storage(self, temp_data_dir):
        """Create UserStorage with temp directory."""
        return UserStorage(data_dir=temp_data_dir)

    @pytest.fixture
    def book_service(self, book_storage):
        """Create BookService with test storage."""
        return BookService(storage=book_storage)

    @pytest.fixture
    def user_service(self, user_storage):
        """Create UserService with test storage."""
        return UserService(storage=user_storage)

    def test_add_and_list_books_integration(self, book_service):
        """Test adding books and listing them."""
        # Add first book
        book1, error1 = book_service.add_book(1001, "Book 1", "Author 1")
        assert book1 is not None
        assert error1 == ""
        assert book1.id == 1001

        # Add second book
        book2, error2 = book_service.add_book(1002, "Book 2", "Author 2")
        assert book2 is not None
        assert error2 == ""
        assert book2.id == 1002

        # List all books
        all_books = book_service.list_all_books()
        assert len(all_books) == 2
        assert all_books[0].title == "Book 1"
        assert all_books[1].title == "Book 2"

    def test_pick_and_approve_borrow_workflow(self, book_service):
        """Test complete workflow: add -> pick -> approve."""
        # Add book
        book, _ = book_service.add_book(1001, "Test Book", "Test Author")
        assert book.status == BookStatus.AVAILABLE

        # User picks book
        picked_book, _ = book_service.pick_book(book.id, "testuser")
        assert picked_book.status == BookStatus.PICKED
        assert picked_book.picked_by == "testuser"

        # Librarian approves
        approved_book, _ = book_service.approve_borrow(book.id)
        assert approved_book.status == BookStatus.BORROWED
        assert approved_book.picked_by == "testuser"

    def test_update_and_delete_workflow(self, book_service):
        """Test updating and deleting books."""
        # Add book
        book, _ = book_service.add_book(1001, "Original Title", "Original Author")
        book_id = book.id

        # Update title
        updated_book, _ = book_service.update_book_info(book_id, title="New Title")
        assert updated_book.title == "New Title"
        assert updated_book.author == "Original Author"

        # Delete book
        success, _ = book_service.delete_book(book_id)
        assert success is True

        # Verify deleted
        all_books = book_service.list_all_books()
        assert len(all_books) == 0

    def test_list_picked_books(self, book_service):
        """Test listing picked books."""
        # Add books
        book1, _ = book_service.add_book(1001, "Book 1", "Author 1")
        book2, _ = book_service.add_book(1002, "Book 2", "Author 2")

        # Pick books
        book_service.pick_book(book1.id, "user1")
        book_service.pick_book(book2.id, "user2")

        # List picked
        picked_books = book_service.list_picked_books()
        assert len(picked_books) == 2
        assert all(book.status == BookStatus.PICKED for book in picked_books)
        assert picked_books[0].picked_by == "user1"
        assert picked_books[1].picked_by == "user2"

    def test_return_book_workflow(self, book_service):
        """Test returning a borrowed book."""
        # Add and borrow book
        book, _ = book_service.add_book(1001, "Test Book", "Test Author")
        book_service.pick_book(book.id, "testuser")
        book_service.approve_borrow(book.id)

        # Return book
        returned_book, _ = book_service.return_book(book.id)
        assert returned_book.status == BookStatus.AVAILABLE
        assert returned_book.picked_by is None

    def test_persistence_across_instances(self, temp_data_dir):
        """Test that data persists across service instances."""
        # Create first service and add book
        storage1 = BookStorage(data_dir=temp_data_dir)
        service1 = BookService(storage=storage1)
        book, _ = service1.add_book(1001, "Persistent Book", "Author")

        # Create new service instance
        storage2 = BookStorage(data_dir=temp_data_dir)
        service2 = BookService(storage=storage2)

        # Verify book still exists
        all_books = service2.list_all_books()
        assert len(all_books) == 1
        assert all_books[0].title == "Persistent Book"
        assert all_books[0].id == book.id
