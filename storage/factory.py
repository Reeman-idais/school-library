"""Storage factory for creating appropriate storage implementation."""

import os

from lib_logging.logger import get_logger

logger = get_logger(__name__)


class StorageFactory:
    """Factory for creating storage implementations based on configuration."""

    _instances: dict[str, object] = {}  # Cache for singleton pattern

    @classmethod
    def create_book_storage(cls):
        """Create book storage instance based on configuration."""
        storage_type = os.getenv("DATABASE_TYPE", "json").lower()

        if storage_type == "mongodb":
            from storage.mongodb.book_storage import MongoDBBookStorage

            if "book_storage_mongodb" not in cls._instances:
                cls._instances["book_storage_mongodb"] = MongoDBBookStorage()
            return cls._instances["book_storage_mongodb"]

        elif storage_type == "json":
            from storage.book_storage import BookStorage

            if "book_storage_json" not in cls._instances:
                cls._instances["book_storage_json"] = BookStorage()
            return cls._instances["book_storage_json"]

        else:
            logger.error(f"Unknown database type: {storage_type}")
            raise ValueError(f"Unsupported DATABASE_TYPE: {storage_type}")

    @classmethod
    def create_user_storage(cls):
        """Create user storage instance based on configuration."""
        storage_type = os.getenv("DATABASE_TYPE", "json").lower()

        if storage_type == "mongodb":
            from storage.mongodb.user_storage import MongoDBUserStorage

            if "user_storage_mongodb" not in cls._instances:
                cls._instances["user_storage_mongodb"] = MongoDBUserStorage()
            return cls._instances["user_storage_mongodb"]

        elif storage_type == "json":
            from storage.user_storage import UserStorage

            if "user_storage_json" not in cls._instances:
                cls._instances["user_storage_json"] = UserStorage()
            return cls._instances["user_storage_json"]

        else:
            logger.error(f"Unknown database type: {storage_type}")
            raise ValueError(f"Unsupported DATABASE_TYPE: {storage_type}")

    @classmethod
    def reset(cls) -> None:
        """Reset all cached instances (useful for testing)."""
        cls._instances.clear()
        logger.info("Storage factory instances reset")
