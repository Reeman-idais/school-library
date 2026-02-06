"""Tests for CLI commands with mocked services."""

import pytest
from unittest.mock import Mock, patch
from models.book import Book, BookStatus
from models.role import Role
from cli.commands import (
    handle_add_book,
    handle_delete_book,
    handle_list_books,
    handle_pick_book,
    handle_update_status,
)


@pytest.mark.unit
class TestCLICommands:
    """Test CLI command handlers with mocked services."""

    @patch("cli.commands.BookService")
    def test_handle_add_book_success(self, mock_book_service_class):
        """Test successful book addition via CLI."""
        # Setup mock
        mock_service = Mock()
        mock_book = Book.create(1, "Test Book", "Test Author")
        mock_service.add_book.return_value = (mock_book, "")
        mock_book_service_class.return_value = mock_service

        # Execute command
        result = handle_add_book("Test Book", "Test Author", True, None)

        # Assertions
        assert result == 0
        mock_service.add_book.assert_called_once_with("Test Book", "Test Author")

    @patch("cli.commands.BookService")
    def test_handle_add_book_validation_error(self, mock_book_service_class):
        """Test book addition with validation error."""
        mock_service = Mock()
        mock_service.add_book.return_value = (None, "Title cannot be empty")
        mock_book_service_class.return_value = mock_service

        result = handle_add_book("", "Test Author", True, None)

        assert result == 1

    @patch("cli.commands.BookService")
    def test_handle_add_book_permission_denied(self, mock_book_service_class):
        """Test book addition without librarian permission."""
        # User tries to add book (not librarian)
        result = handle_add_book("Test Book", "Test Author", False, "testuser")

        assert result == 1  # Permission denied

    @patch("cli.commands.BookService")
    def test_handle_delete_book_success(self, mock_book_service_class):
        """Test successful book deletion."""
        mock_service = Mock()
        mock_service.delete_book.return_value = (True, "")
        mock_book_service_class.return_value = mock_service

        result = handle_delete_book("1", True, None)

        assert result == 0
        mock_service.delete_book.assert_called_once_with(1)

    @patch("cli.commands.BookService")
    def test_handle_delete_book_not_found(self, mock_book_service_class):
        """Test deleting non-existent book."""
        mock_service = Mock()
        mock_service.delete_book.return_value = (False, "Book not found")
        mock_book_service_class.return_value = mock_service

        result = handle_delete_book("999", True, None)

        assert result == 1

    @patch("cli.commands.BookService")
    def test_handle_list_books_success(self, mock_book_service_class):
        """Test listing books."""
        mock_service = Mock()
        books = [
            Book.create(1, "Book 1", "Author 1"),
            Book.create(2, "Book 2", "Author 2"),
        ]
        mock_service.list_all_books.return_value = books
        mock_book_service_class.return_value = mock_service

        result = handle_list_books(False, "testuser")

        assert result == 0
        mock_service.list_all_books.assert_called_once()

    @patch("cli.commands.BookService")
    def test_handle_pick_book_success(self, mock_book_service_class):
        """Test user picking a book."""
        mock_service = Mock()
        picked_book = Book.create(1, "Test Book", "Test Author")
        picked_book.status = BookStatus.PICKED
        mock_service.pick_book.return_value = (picked_book, "")
        mock_book_service_class.return_value = mock_service

        result = handle_pick_book("1", "testuser")

        assert result == 0
        mock_service.pick_book.assert_called_once_with(1, "testuser")

    @patch("cli.commands.BookService")
    def test_handle_pick_book_not_available(self, mock_book_service_class):
        """Test picking unavailable book."""
        mock_service = Mock()
        mock_service.pick_book.return_value = (None, "Book is not available")
        mock_book_service_class.return_value = mock_service

        result = handle_pick_book("1", "testuser")

        assert result == 1

    @patch("cli.commands.BookService")
    def test_handle_update_status_success(self, mock_book_service_class):
        """Test updating book status."""
        mock_service = Mock()
        updated_book = Book.create(1, "Test Book", "Test Author")
        updated_book.status = BookStatus.BORROWED
        mock_service.update_book_status.return_value = (updated_book, "")
        mock_book_service_class.return_value = mock_service

        result = handle_update_status("1", "Borrowed", True, None)

        assert result == 0
        mock_service.update_book_status.assert_called_once()

    def test_handle_pick_book_invalid_id(self):
        """Test picking book with invalid ID format."""
        result = handle_pick_book("invalid", "testuser")

        assert result == 1  # Should fail due to invalid ID
