"""Factory pattern: centralize creation of services and storage for DI and consistency."""

from pathlib import Path
from typing import Optional

from services.book_service import BookService
from services.user_service import UserService
from storage.factory import StorageFactory as ConfigurableStorageFactory
from storage.repositories.base import BookRepository
from storage.user_storage import UserStorage  # user_storage left as-is for now


class StorageFactory:
    """
    Factory for creating storage instances (Abstract Factory / Factory pattern).
    Single place to configure persistence (supports JSON and MongoDB via env vars).
    """

    def __init__(self, data_dir: Optional[Path] = None):
        self.data_dir = data_dir
        self._configurable_factory = ConfigurableStorageFactory()

    def create_book_storage(self):
        """Create BookStorage based on DATABASE_TYPE environment variable."""
        # Use the configurable factory that respects env vars (JSON or MongoDB)
        return self._configurable_factory.create_book_storage()

    def create_user_storage(self):
        """Create UserStorage based on DATABASE_TYPE environment variable."""
        # Use the configurable factory that respects env vars (JSON or MongoDB)
        return self._configurable_factory.create_user_storage()


class ServiceFactory:
    """
    Factory for creating application services (Factory + DI).
    Injects storage so services are testable with mocks.
    """

    def __init__(
        self,
        book_repo: Optional[BookRepository] = None,
        user_storage: Optional[UserStorage] = None,
        data_dir: Optional[Path] = None,
    ):
        self._book_repo = book_repo
        self._user_storage = user_storage
        self._storage_factory = (
            StorageFactory(data_dir=data_dir) if data_dir else StorageFactory()
        )

    def create_book_service(self) -> BookService:
        """Create BookService, reusing injected repository if set."""
        repo = self._book_repo or self._storage_factory.create_book_storage()
        return BookService(storage=repo)

    def create_user_service(self) -> UserService:
        """Create UserService, reusing injected storage if set."""
        storage = self._user_storage or self._storage_factory.create_user_storage()
        return UserService(storage=storage)
