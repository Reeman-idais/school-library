"""Pytest configuration and fixtures."""

import os
import sys
from pathlib import Path
from unittest.mock import Mock

import pytest

from lib_logging.logger import get_logger
from models.book import Book
from models.role import Role
from models.user import User

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

logger = get_logger(__name__)

"""
Import mongodb fixtures (kept in a separate file) only when running
integration tests. Set environment variable `RUN_INTEGRATION=1` to enable.
This avoids module-level pytest.skip() during regular test runs.
"""
if os.environ.get("RUN_INTEGRATION") == "1":
    try:
        from .conftest_mongodb import *  # noqa: F401,F403
    except Exception:
        try:
            from tests.conftest_mongodb import *  # noqa: F401,F403
        except Exception:
            pass


@pytest.fixture
def sample_book_data():
    """Sample book data for testing."""
    return {
        "id": 1,
        "title": "Test Book",
        "author": "Test Author",
        "status": "Available",
    }


@pytest.fixture
def sample_user_data():
    """Sample user data for testing."""
    return {"username": "testuser", "role": "user"}


@pytest.fixture
def mock_book_storage():
    """Mock BookStorage for unit tests."""
    mock = Mock()
    mock.load_books.return_value = []
    mock.get_book_by_id.return_value = None
    mock.add_book.return_value = True
    mock.update_book.return_value = True
    mock.remove_book.return_value = True
    mock.get_next_book_id.return_value = 1
    return mock


@pytest.fixture
def mock_user_storage():
    """Mock UserStorage for unit tests."""
    mock = Mock()
    mock.get_user_by_username.return_value = None
    mock.create_user.return_value = None
    mock.user_exists.return_value = False
    return mock


@pytest.fixture
def sample_book():
    """Create a sample Book instance."""
    return Book.create(1, "Test Book", "Test Author")


@pytest.fixture
def sample_user():
    """Create a sample User instance."""
    return User.create("testuser", "1234", Role.USER)


@pytest.fixture
def sample_books_list():
    """Create a list of sample books."""
    return [
        Book.create(1, "Book 1", "Author 1"),
        Book.create(2, "Book 2", "Author 2"),
        Book.create(3, "Book 3", "Author 3"),
    ]


@pytest.fixture
def mocker(pytestconfig):
    """Provide mocker fixture for pytest-mock."""
    # This is provided by pytest-mock plugin
    # If pytest-mock is installed, this will work automatically
    pass


logger = get_logger(__name__)
