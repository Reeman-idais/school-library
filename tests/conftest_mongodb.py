"""MongoDB fixtures and utilities for integration tests."""

from typing import Generator

import pytest

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
        MongoDBConnection.get_connection(config)
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
