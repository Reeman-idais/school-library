"""Core abstractions and design patterns."""

from .factory import ServiceFactory, StorageFactory
from .repository import BookRepository, Repository, UserRepository
from .strategy import BookValidationStrategy, UserValidationStrategy, ValidationStrategy

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
