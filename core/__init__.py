"""Core abstractions and design patterns."""

from .repository import Repository, BookRepository, UserRepository
from .factory import ServiceFactory, StorageFactory
from .strategy import ValidationStrategy, BookValidationStrategy, UserValidationStrategy

__all__ = [
    "Repository",
    "BookRepository",
    "UserRepository",
    "ServiceFactory",
    "StorageFactory",
    "ValidationStrategy",
    "BookValidationStrategy",
    "UserValidationStrategy",
]
