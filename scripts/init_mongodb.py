"""MongoDB initialization script for Python environment."""

import os
import sys
import time

from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError

# Configure Python path to include the project root
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.database import MongoDBConfig, MongoDBConnection
from lib_logging.logger import get_logger

logger = get_logger(__name__)


def wait_for_mongodb(config: MongoDBConfig, max_retries: int = 30) -> None:
    """
    Wait for MongoDB to be ready.

    Args:
        config: MongoDB configuration
        max_retries: Maximum number of connection attempts

    Raises:
        RuntimeError: If MongoDB doesn't start within the timeout
    """
    for attempt in range(max_retries):
        try:
            client = MongoClient(
                config.connection_string,
                serverSelectionTimeoutMS=5000,
                connectTimeoutMS=10000,
            )
            client.admin.command("ping")
            logger.info("MongoDB is ready")
            client.close()
            return
        except (ConnectionFailure, ServerSelectionTimeoutError) as e:
            if attempt < max_retries - 1:
                logger.warning(
                    f"MongoDB not ready (attempt {attempt + 1}/{max_retries}), "
                    f"retrying in 1s: {e}"
                )
                time.sleep(1)
            else:
                logger.error(f"MongoDB failed to start after {max_retries} attempts")
                raise RuntimeError("MongoDB did not start in time") from e


def create_indexes() -> None:
    """Create indexes on MongoDB collections."""
    try:
        db = MongoDBConnection.get_database()

        # Create collections if they don't exist
        if "books" not in db.list_collection_names():
            db.create_collection("books")
            logger.info("Created 'books' collection")

        if "users" not in db.list_collection_names():
            db.create_collection("users")
            logger.info("Created 'users' collection")

        # Create indexes
        db.books.create_index([("id", 1)], unique=True)
        db.books.create_index([("title", 1)])
        db.books.create_index([("author", 1)])
        db.books.create_index([("status", 1)])
        logger.info("Created indexes on 'books' collection")

        db.users.create_index([("id", 1)], unique=True)
        db.users.create_index([("username", 1)], unique=True)
        db.users.create_index([("role", 1)])
        logger.info("Created indexes on 'users' collection")

    except Exception as e:
        logger.error(f"Error creating indexes: {e}")
        raise


def initialize_counters() -> None:
    """Initialize ID counter collections."""
    try:
        db = MongoDBConnection.get_database()

        # Initialize book ID counter
        if db.book_id_counter.find_one({"_id": "book_id"}) is None:
            db.book_id_counter.insert_one({"_id": "book_id", "sequence_value": 0})
            logger.info("Initialized book ID counter")

        # Initialize user ID counter
        if db.user_id_counter.find_one({"_id": "user_id"}) is None:
            db.user_id_counter.insert_one({"_id": "user_id", "sequence_value": 0})
            logger.info("Initialized user ID counter")

    except Exception as e:
        logger.error(f"Error initializing counters: {e}")
        raise


def main() -> None:
    """Main initialization function."""
    try:
        logger.info("Starting MongoDB initialization...")

        config = MongoDBConfig()
        logger.info(f"MongoDB configuration: {config}")

        # Wait for MongoDB to be ready
        wait_for_mongodb(config)

        # Create database connection
        client = MongoDBConnection.get_connection(config)
        logger.info(f"Connected to MongoDB: {config.database}")

        # Create indexes
        create_indexes()

        # Initialize counters
        initialize_counters()

        logger.info("MongoDB initialization completed successfully")

    except Exception as e:
        logger.error(f"MongoDB initialization failed: {e}")
        sys.exit(1)
    finally:
        MongoDBConnection.close()


if __name__ == "__main__":
    main()
