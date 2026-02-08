"""Pytest configuration and fixtures."""

import sys
from pathlib import Path
from unittest.mock import Mock

import pytest

from models.book import Book
from models.role import Role
from models.user import User

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Import mongodb fixtures (kept in a separate file) so pytest discovers them
try:
    from .conftest_mongodb import *  # noqa: F401,F403
except Exception:
    # If relative import fails (when tests executed differently), try absolute import
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
    return User.create("testuser", Role.USER)


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


# --- MongoDB integration fixtures (inlined from conftest_mongodb.py) ---
import os
from typing import Generator

from config.database import MongoDBConfig, MongoDBConnection
from lib_logging.logger import get_logger
from storage.mongodb.book_storage import MongoDBBookStorage
from storage.mongodb.user_storage import MongoDBUserStorage

logger = get_logger(__name__)


@pytest.fixture
def mongodb_config() -> MongoDBConfig:
    """Get MongoDB configuration for tests."""
    return MongoDBConfig()


@pytest.fixture
def mongodb_book_storage() -> Generator[MongoDBBookStorage, None, None]:
    """
    Provide MongoDB book storage for integration tests.

    Cleanup: Drops the books collection after each test.
    """
    storage = MongoDBBookStorage()

    # Clear before test
    storage.collection.delete_many({})
    storage.id_counter.update_one(
        {"_id": "book_id"}, {"$set": {"sequence_value": 0}}, upsert=True
    )

    yield storage

    # Clear after test
    storage.collection.delete_many({})
    storage.id_counter.update_one(
        {"_id": "book_id"}, {"$set": {"sequence_value": 0}}, upsert=True
    )


@pytest.fixture
def mongodb_user_storage() -> Generator[MongoDBUserStorage, None, None]:
    """
    Provide MongoDB user storage for integration tests.

    Cleanup: Drops the users collection after each test.
    """
    storage = MongoDBUserStorage()

    # Clear before test
    storage.collection.delete_many({})
    storage.id_counter.update_one(
        {"_id": "user_id"}, {"$set": {"sequence_value": 0}}, upsert=True
    )

    yield storage

    # Clear after test
    storage.collection.delete_many({})
    storage.id_counter.update_one(
        {"_id": "user_id"}, {"$set": {"sequence_value": 0}}, upsert=True
    )


@pytest.fixture(scope="session")
def mongodb_connection_check():
    """
    Check if MongoDB is available and skip tests if not.
    Runs once per test session.
    """
    config = MongoDBConfig()
    try:
        client = MongoDBConnection.get_connection(config)
        logger.info("MongoDB is available for testing")
        return True
    except Exception as e:
        logger.warning(f"MongoDB not available: {e}")
        pytest.skip("MongoDB not available")


@pytest.fixture(autouse=True)
def reset_mongodb_connection():
    """Reset MongoDB connection before each test."""
    MongoDBConnection.reset()
    yield
    MongoDBConnection.reset()
