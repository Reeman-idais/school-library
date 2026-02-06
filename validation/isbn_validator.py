"""Compatibility shim for ISBN validation kept for tests.

This module re-exports functions from `id_validator` to preserve the
original public API (`validate_isbn10`, `normalize_isbn`) used in tests.
"""

from .id_validator import normalize_id as normalize_isbn
from .id_validator import validate_id as validate_isbn10

__all__ = ["validate_isbn10", "normalize_isbn"]
