"""Database connection configuration and management."""

import os
from typing import Optional

from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError

from lib_logging.logger import get_logger

logger = get_logger(__name__)


class MongoDBConfig:
    """MongoDB connection configuration."""

    def __init__(self):
        """Initialize MongoDB configuration from environment variables."""
        # Read from environment variables with defaults
        self.host = os.getenv("MONGODB_HOST", "localhost")
        self.port = int(os.getenv("MONGODB_PORT", "27017"))
        self.database = os.getenv("MONGODB_DATABASE", "school_library")
        self.username = os.getenv("MONGODB_USERNAME", "")
        self.password = os.getenv("MONGODB_PASSWORD", "")
        self.uri = os.getenv("MONGODB_URI", "")

    @property
    def connection_string(self) -> str:
        """Generate connection string from config."""
        if self.uri:
            return str(self.uri)

        if self.username and self.password:
            return f"mongodb://{self.username}:{self.password}@{self.host}:{self.port}/{self.database}?authSource=admin"
        return f"mongodb://{self.host}:{self.port}"

    def __repr__(self) -> str:
        """String representation without exposing credentials."""
        return f"MongoDBConfig(host={self.host}, port={self.port}, database={self.database})"


class MongoDBConnection:
    """MongoDB connection manager with singleton pattern."""

    _instance: Optional[MongoClient] = None
    _config: Optional[MongoDBConfig] = None

    @classmethod
    def get_connection(cls, config: Optional[MongoDBConfig] = None) -> MongoClient:
        """
        Get or create MongoDB connection.

        Args:
            config: MongoDBConfig instance (created if not provided)

        Returns:
            MongoClient instance

        Raises:
            ConnectionFailure: If unable to connect to MongoDB
        """
        if cls._instance is None:
            if config is None:
                config = MongoDBConfig()
            cls._config = config
            cls._instance = cls._create_connection(config)

        return cls._instance

    @classmethod
    def _create_connection(cls, config: MongoDBConfig) -> MongoClient:
        """
        Create a new MongoDB connection.

        Args:
            config: MongoDBConfig instance

        Returns:
            MongoClient instance

        Raises:
            ConnectionFailure: If unable to connect to MongoDB
        """
        try:
            logger.info(f"Connecting to MongoDB: {config}")
            client = MongoClient(
                config.connection_string,
                serverSelectionTimeoutMS=5000,
                connectTimeoutMS=10000,
                retryWrites=True,
            )
            # Verify connection
            client.admin.command("ping")
            logger.info(f"Successfully connected to MongoDB: {config.database}")
            return client
        except (ConnectionFailure, ServerSelectionTimeoutError) as e:
            logger.error(f"Failed to connect to MongoDB: {e}")
            raise

    @classmethod
    def get_database(cls, config: Optional[MongoDBConfig] = None):
        """
        Get MongoDB database instance.

        Args:
            config: MongoDBConfig instance

        Returns:
            Database instance
        """
        client = cls.get_connection(config)
        if cls._config is None:
            if config is None:
                config = MongoDBConfig()
            cls._config = config
        return client[cls._config.database]

    @classmethod
    def close(cls) -> None:
        """Close MongoDB connection."""
        if cls._instance is not None:
            cls._instance.close()
            cls._instance = None
            logger.info("MongoDB connection closed")

    @classmethod
    def reset(cls) -> None:
        """Reset connection (useful for testing)."""
        cls.close()
        cls._config = None
