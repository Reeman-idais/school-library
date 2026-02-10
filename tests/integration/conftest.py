"""
Integration fixtures for MongoDB tests.

These fixtures are only loaded when running integration tests (e.g. -m integration
or running the tests in tests/integration/). They rely on environment variables
for MongoDB connection details (MONGODB_HOST, MONGODB_PORT, ...).
"""

from typing import Generator

import pytest

from config.database import MongoDBConfig, MongoDBConnection
from lib_logging.logger import get_logger
from storage.mongodb.book_storage import MongoDBBookStorage
from storage.mongodb.user_storage import MongoDBUserStorage

logger = get_logger(__name__)


@pytest.fixture(scope="session")
def mongodb_config() -> MongoDBConfig:
    """Get MongoDB configuration for tests."""
    return MongoDBConfig()


@pytest.fixture(scope="session")
def mongodb_connection_check(mongodb_config):
    """
    Check if MongoDB is available and skip MongoDB tests if not.
    Runs once per test session.
    """
    try:
        MongoDBConnection.get_connection(mongodb_config)
        logger.info("MongoDB is available for testing")
        yield
    except Exception as e:
        logger.warning(f"MongoDB not available: {e}")
        pytest.skip("MongoDB not available")


@pytest.fixture
def reset_mongodb_connection():
    """
    Reset MongoDB connection before and after each MongoDB test.
    MUST NOT be autouse.
    """
    MongoDBConnection.reset()
    yield
    MongoDBConnection.reset()


@pytest.fixture
def mongodb_book_storage(
    mongodb_connection_check,
    reset_mongodb_connection,
) -> Generator[MongoDBBookStorage, None, None]:
    """
    Provide MongoDB book storage for integration tests.

    Cleanup: Clears books collection and resets ID counter.
    """
    storage = MongoDBBookStorage()

    # Clear before test
    storage.collection.delete_many({})
    storage.id_counter.update_one(
        {"_id": "book_id"},
        {"$set": {"sequence_value": 0}},
        upsert=True,
    )

    yield storage

    # Clear after test
    storage.collection.delete_many({})
    storage.id_counter.update_one(
        {"_id": "book_id"},
        {"$set": {"sequence_value": 0}},
        upsert=True,
    )


@pytest.fixture
def mongodb_user_storage(
    mongodb_connection_check,
    reset_mongodb_connection,
) -> Generator[MongoDBUserStorage, None, None]:
    """
    Provide MongoDB user storage for integration tests.

    Cleanup: Clears users collection and resets ID counter.
    """
    storage = MongoDBUserStorage()

    # Clear before test
    storage.collection.delete_many({})
    storage.id_counter.update_one(
        {"_id": "user_id"},
        {"$set": {"sequence_value": 0}},
        upsert=True,
    )

    yield storage

    # Clear after test
    storage.collection.delete_many({})
    storage.id_counter.update_one(
        {"_id": "user_id"},
        {"$set": {"sequence_value": 0}},
        upsert=True,
    )
