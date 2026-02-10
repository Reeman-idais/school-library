"""Tests for service layer with mocked dependencies."""

from unittest.mock import Mock, patch

import pytest

from models.book import Book, BookStatus
from models.user import Role, User
from services.book_service import BookService
from services.user_service import UserService


@pytest.mark.unit
class TestBookService:
    """Test BookService with mocked storage."""

    def test_add_book_success(self, mocker):
        """Test adding a book successfully with mocked storage."""
        # Create mock storage
        mock_storage = Mock()
        mock_storage.get_book_by_id.return_value = None
        mock_storage.add_book.return_value = True

        # Create service with mocked storage
        service = BookService(storage=mock_storage)

        # Add book
        book, error_msg = service.add_book(1001, "Test Book", "Test Author")

        # Assertions
        assert book is not None
        assert error_msg == ""
        assert book.title == "Test Book"
        assert book.author == "Test Author"
        assert book.id == 1001
        assert book.status == BookStatus.AVAILABLE

        # Verify storage methods were called
        mock_storage.get_book_by_id.assert_called_once()
        mock_storage.add_book.assert_called_once()

    def test_add_book_empty_title(self, mocker):
        """Test adding book with empty title."""
        mock_storage = Mock()
        mock_storage.get_book_by_id.return_value = None
        service = BookService(storage=mock_storage)

        book, error_msg = service.add_book(1001, "", "Test Author")
        """Test adding book when storage fails."""
        mock_storage = Mock()
        mock_storage.get_book_by_id.return_value = None
        mock_storage.add_book.return_value = False

        service = BookService(storage=mock_storage)

        book, error_msg = service.add_book(1001, "Test Book", "Test Author")

        assert book is None
        assert "storage" in error_msg.lower()

    def test_delete_book_success(self, mocker):
        """Test deleting a book successfully."""
        mock_storage = Mock()
        mock_book = Book.create(1, "Test Book", "Test Author")
        mock_storage.get_book_by_id.return_value = mock_book
        mock_storage.remove_book.return_value = True

        service = BookService(storage=mock_storage)

        success, error_msg = service.delete_book(1)

        assert success is True
        assert error_msg == ""
        mock_storage.get_book_by_id.assert_called_once_with(1)
        mock_storage.remove_book.assert_called_once_with(1)

    def test_delete_book_not_found(self, mocker):
        """Test deleting non-existent book."""
        mock_storage = Mock()
        mock_storage.get_book_by_id.return_value = None

        service = BookService(storage=mock_storage)

        success, error_msg = service.delete_book(999)

        assert success is False
        assert "not found" in error_msg.lower()
        mock_storage.remove_book.assert_not_called()

    def test_update_book_info_success(self, mocker):
        """Test updating book information."""
        mock_storage = Mock()
        existing_book = Book.create(1, "Old Title", "Old Author")
        mock_storage.get_book_by_id.return_value = existing_book
        mock_storage.update_book.return_value = True

        service = BookService(storage=mock_storage)

        book, error_msg = service.update_book_info(1, title="New Title")

        assert book is not None
        assert error_msg == ""
        assert book.title == "New Title"
        assert book.author == "Old Author"  # Unchanged
        mock_storage.update_book.assert_called_once()

    def test_pick_book_success(self, mocker):
        """Test user picking a book."""
        mock_storage = Mock()
        available_book = Book.create(1, "Test Book", "Test Author")
        available_book.status = BookStatus.AVAILABLE
        mock_storage.get_book_by_id.return_value = available_book
        mock_storage.update_book.return_value = True

        service = BookService(storage=mock_storage)

        book, error_msg = service.pick_book(1, "testuser")

        assert book is not None
        assert error_msg == ""
        assert book.status == BookStatus.PICKED
        assert book.picked_by == "testuser"

    def test_pick_book_not_available(self, mocker):
        """Test picking a book that's not available."""
        mock_storage = Mock()
        borrowed_book = Book.create(1, "Test Book", "Test Author")
        borrowed_book.status = BookStatus.BORROWED
        mock_storage.get_book_by_id.return_value = borrowed_book

        service = BookService(storage=mock_storage)

        book, error_msg = service.pick_book(1, "testuser")

        assert book is None
        assert "not available" in error_msg.lower() or "available" in error_msg.lower()

    def test_approve_borrow_success(self, mocker):
        """Test librarian approving a borrow."""
        mock_storage = Mock()
        picked_book = Book.create(1, "Test Book", "Test Author")
        picked_book.status = BookStatus.PICKED
        picked_book.picked_by = "testuser"
        mock_storage.get_book_by_id.return_value = picked_book
        mock_storage.update_book.return_value = True

        service = BookService(storage=mock_storage)

        book, error_msg = service.approve_borrow(1)

        assert book is not None
        assert error_msg == ""
        assert book.status == BookStatus.BORROWED
        assert book.picked_by == "testuser"  # Still tracked

    def test_list_all_books(self, mocker):
        """Test listing all books."""
        mock_storage = Mock()
        books = [
            Book.create(1, "Book 1", "Author 1"),
            Book.create(2, "Book 2", "Author 2"),
        ]
        mock_storage.load_books.return_value = books

        service = BookService(storage=mock_storage)

        result = service.list_all_books()

        assert len(result) == 2
        assert result[0].title == "Book 1"
        assert result[1].title == "Book 2"
        mock_storage.load_books.assert_called_once()


@pytest.mark.unit
class TestUserService:
    """Test UserService with mocked storage."""

    def test_get_user_role_existing_user(self, mocker):
        """Test getting role of existing user."""
        mock_storage = Mock()
        mock_user = User.create("testuser", "1234", Role.USER)
        mock_storage.get_user_by_username.return_value = mock_user

        service = UserService(storage=mock_storage)

        role = service.get_user_role("testuser")

        assert role == Role.USER
        mock_storage.get_user_by_username.assert_called_once_with("testuser")

    def test_get_user_role_not_found(self, mocker):
        """Test getting role of non-existent user."""
        mock_storage = Mock()
        mock_storage.get_user_by_username.return_value = None

        service = UserService(storage=mock_storage)

        role = service.get_user_role("nonexistent")

        assert role is None

    @patch("services.user_service.validate_username")
    def test_get_or_create_user_existing(self, mock_validate, mocker):
        """Test getting existing user."""
        mock_storage = Mock()
        mock_validate.return_value = (True, "")
        existing_user = User.create("testuser", "1234", Role.USER)
        mock_storage.get_user_by_username.return_value = existing_user

        service = UserService(storage=mock_storage)

        user, is_new = service.get_or_create_user("testuser", "1234", Role.USER)

        assert user.username == "testuser"
        assert is_new is False
        mock_storage.create_user.assert_not_called()

    @patch("services.user_service.validate_username")
    def test_get_or_create_user_new(self, mock_validate, mocker):
        """Test creating new user."""
        mock_storage = Mock()
        mock_validate.return_value = (True, "")
        mock_storage.get_user_by_username.return_value = None
        new_user = User.create("newuser", "1234", Role.USER)
        mock_storage.create_user.return_value = new_user

        service = UserService(storage=mock_storage)

        user, is_new = service.get_or_create_user("newuser", "1234", Role.USER)

        assert user.username == "newuser"
        assert is_new is True
        mock_storage.create_user.assert_called_once_with("newuser", "1234", Role.USER)
