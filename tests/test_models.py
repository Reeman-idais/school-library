"""Tests for model classes."""

from models.book import Book, BookStatus
from models.role import Role
from models.user import User


class TestBook:
    """Test Book model."""

    def test_create_book(self):
        """Test creating a book."""
        book = Book.create(1, "Test Book", "Test Author")
        assert book.id == 1
        assert book.title == "Test Book"
        assert book.author == "Test Author"
        assert book.status == BookStatus.AVAILABLE
        assert book.picked_by is None

    def test_book_to_dict(self):
        """Test book serialization."""
        book = Book.create(1, "Test Book", "Test Author")
        book_dict = book.to_dict()
        assert book_dict["id"] == 1
        assert book_dict["title"] == "Test Book"
        assert book_dict["status"] == "Available"

    def test_book_from_dict(self):
        """Test book deserialization."""
        data = {
            "id": 1,
            "title": "Test Book",
            "author": "Test Author",
            "status": "Available",
        }
        book = Book.from_dict(data)
        assert book.id == 1
        assert book.title == "Test Book"
        assert book.status == BookStatus.AVAILABLE

    def test_create_with_status_and_picked_by(self):
        """Book.create accepts optional status and picked_by and preserves them."""
        book = Book.create(
            2, "Picked Book", "Author", status=BookStatus.PICKED, picked_by="alice"
        )
        assert book.id == 2
        assert book.status == BookStatus.PICKED
        assert book.picked_by == "alice"

    def test_create_ignores_extra_kwargs(self):
        """Book.create should ignore unexpected kwargs (forward-compatible)."""
        # simulate callers that pass full document or extra fields
        book = Book.create(
            3,
            "Extra Book",
            "Some Author",
            status=BookStatus.AVAILABLE,
            picked_by=None,
            unexpected_field="x",
            _meta={"a": 1},
        )
        assert book.id == 3
        assert book.title == "Extra Book"
        assert book.status == BookStatus.AVAILABLE


class TestUser:
    """Test User model."""

    def test_create_user(self):
        """Test creating a user."""
        user = User.create("testuser", Role.USER)
        assert user.username == "testuser"
        assert user.role == Role.USER
        assert user.id is not None

    def test_user_to_dict(self):
        """Test user serialization."""
        user = User.create("testuser", Role.USER)
        user_dict = user.to_dict()
        assert user_dict["username"] == "testuser"
        assert user_dict["role"] == "user"
