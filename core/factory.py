"""Factory pattern: centralize creation of services and storage for DI and consistency."""

from pathlib import Path
from typing import Optional

from services.book_service import BookService
from services.user_service import UserService
from storage.book_storage import BookStorage
from storage.user_storage import UserStorage


class StorageFactory:
    """
    Factory for creating storage instances (Abstract Factory / Factory pattern).
    Single place to configure persistence (e.g. JSON path, future DB).
    """

    def __init__(self, data_dir: Optional[Path] = None):
        self.data_dir = data_dir

    def create_book_storage(self) -> BookStorage:
        """Create BookStorage with configured data directory."""
        return BookStorage(data_dir=self.data_dir) if self.data_dir else BookStorage()

    def create_user_storage(self) -> UserStorage:
        """Create UserStorage with configured data directory."""
        return UserStorage(data_dir=self.data_dir) if self.data_dir else UserStorage()


class ServiceFactory:
    """
    Factory for creating application services (Factory + DI).
    Injects storage so services are testable with mocks.
    """

    def __init__(
        self,
        book_storage: Optional[BookStorage] = None,
        user_storage: Optional[UserStorage] = None,
        data_dir: Optional[Path] = None,
    ):
        self._book_storage = book_storage
        self._user_storage = user_storage
        self._storage_factory = (
            StorageFactory(data_dir=data_dir) if data_dir else StorageFactory()
        )

    def create_book_service(self) -> BookService:
        """Create BookService, reusing injected storage if set."""
        storage = self._book_storage or self._storage_factory.create_book_storage()
        return BookService(storage=storage)

    def create_user_service(self) -> UserService:
        """Create UserService, reusing injected storage if set."""
        storage = self._user_storage or self._storage_factory.create_user_storage()
        return UserService(storage=storage)
