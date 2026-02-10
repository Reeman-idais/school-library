"""
Tests for CLI commands with mocked services.
"""

from unittest.mock import Mock

import pytest

from cli.commands import (
    handle_add_book,
    handle_delete_book,
    handle_list_books,
    handle_pick_book,
    handle_update_status,
)
from models.book import Book, BookStatus


@pytest.mark.unit
class TestCLICommands:
    """Test CLI command handlers with mocked services."""

    def test_handle_add_book_success(self):
        """Test successful book addition via CLI."""
        mock_service = Mock()
        mock_book = Book.create(1001, "Test Book", "Test Author")
        mock_service.add_book.return_value = (mock_book, "")

        result = handle_add_book(
            "1001",
            "Test Book",
            "Test Author",
            True,
            None,
            mock_service,
        )

        assert result == 0
        mock_service.add_book.assert_called_once_with(
            1001,
            "Test Book",
            "Test Author",
        )

    def test_handle_add_book_validation_error(self):
        """Test book addition with validation error."""
        mock_service = Mock()
        mock_service.add_book.return_value = (None, "Title cannot be empty")

        result = handle_add_book(
            "",
            "Test Book",
            "Test Author",
            True,
            None,
            mock_service,
        )

        assert result == 1

    def test_handle_add_book_permission_denied(self):
        """Test book addition without librarian permission."""
        mock_service = Mock()

        result = handle_add_book(
            "1001",
            "Test Book",
            "Test Author",
            False,
            "testuser",
            mock_service,
        )

        assert result == 1
        mock_service.add_book.assert_not_called()

    def test_handle_delete_book_success(self):
        """Test successful book deletion."""
        mock_service = Mock()
        mock_service.delete_book.return_value = (True, "")

        result = handle_delete_book(
            "1",
            True,
            None,
            mock_service,
        )

        assert result == 0
        mock_service.delete_book.assert_called_once_with(1)

    def test_handle_delete_book_not_found(self):
        """Test deleting non-existent book."""
        mock_service = Mock()
        mock_service.delete_book.return_value = (False, "Book not found")

        result = handle_delete_book(
            "999",
            True,
            None,
            mock_service,
        )

        assert result == 1

    def test_handle_list_books_success(self):
        """Test listing books."""
        mock_service = Mock()
        books = [
            Book.create(1, "Book 1", "Author 1"),
            Book.create(2, "Book 2", "Author 2"),
        ]
        mock_service.list_all_books.return_value = books

        result = handle_list_books(
            False,
            "testuser",
            mock_service,
        )

        assert result == 0
        mock_service.list_all_books.assert_called_once()

    def test_handle_pick_book_success(self):
        """Test user picking a book."""
        mock_service = Mock()
        picked_book = Book.create(1, "Test Book", "Test Author")
        picked_book.status = BookStatus.PICKED
        mock_service.pick_book.return_value = (picked_book, "")

        result = handle_pick_book(
            "1",
            "testuser",
            mock_service,
        )

        assert result == 0
        mock_service.pick_book.assert_called_once_with(1, "testuser")

    def test_handle_pick_book_not_available(self):
        """Test picking unavailable book."""
        mock_service = Mock()
        mock_service.pick_book.return_value = (None, "Book is not available")

        result = handle_pick_book(
            "1",
            "testuser",
            mock_service,
        )

        assert result == 1

    def test_handle_pick_book_invalid_id(self):
        """Test picking book with invalid ID format."""
        mock_service = Mock()

        result = handle_pick_book(
            "invalid",
            "testuser",
            mock_service,
        )

        assert result == 1
        mock_service.pick_book.assert_not_called()

    def test_handle_update_status_success(self):
        """Test updating book status."""
        mock_service = Mock()
        updated_book = Book.create(1, "Test Book", "Test Author")
        updated_book.status = BookStatus.BORROWED
        mock_service.update_book_status.return_value = (updated_book, "")

        result = handle_update_status(
            "1",
            "Borrowed",
            True,
            None,
            mock_service,
        )

        assert result == 0
        mock_service.update_book_status.assert_called_once()
