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


class TestUser:
    """Test User model."""

    def test_create_user(self):
        """Test creating a user."""
        user = User.create("testuser", "1234", Role.USER)
        assert user.username == "testuser"
        assert user.password == "1234"
        assert user.role == Role.USER
        assert user.id is not None

    def test_user_to_dict(self):
        """Test user serialization."""
        user = User.create("testuser", "1234", Role.USER)
        user_dict = user.to_dict()
        assert user_dict["username"] == "testuser"
        assert user_dict["password"] == "1234"
        assert user_dict["role"] == "user"
