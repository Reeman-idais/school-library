#!/usr/bin/env python
"""Verification script for MongoDB integration without requiring a running MongoDB."""

import os
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

print("=" * 60)
print("MongoDB Integration Verification")
print("=" * 60)


def test_imports():
    """Test that all modules can be imported."""
    print("\n✓ Testing imports...")
    try:
        from config.database import MongoDBConfig, MongoDBConnection  # noqa: F401

        print("  ✓ config.database imported successfully")

        from storage.factory import StorageFactory  # noqa: F401

        print("  ✓ storage.factory imported successfully")

        from storage.mongodb.book_storage import MongoDBBookStorage  # noqa: F401

        print("  ✓ storage.mongodb.book_storage imported successfully")

        from storage.mongodb.user_storage import MongoDBUserStorage  # noqa: F401

        print("  ✓ storage.mongodb.user_storage imported successfully")

        from models.book import Book, BookStatus  # noqa: F401

        print("  ✓ models.book imported successfully")

        from models.user import User  # noqa: F401

        print("  ✓ models.user imported successfully")

        return True
    except Exception as e:
        print(f"  ✗ Import failed: {e}")
        return False


def test_factory_pattern():
    """Test the storage factory pattern."""
    print("\n✓ Testing factory pattern...")
    try:
        from storage.factory import StorageFactory

        # Test with JSON storage
        os.environ["DATABASE_TYPE"] = "json"
        StorageFactory.reset()
        StorageFactory.create_book_storage()
        print("  ✓ Factory creates JSON storage successfully")

        # Test with MongoDB type (without connecting)
        os.environ["DATABASE_TYPE"] = "mongodb"
        StorageFactory.reset()
        print("  ✓ Factory reset successful")

        return True
    except Exception as e:
        print(f"  ✗ Factory pattern test failed: {e}")
        return False


def test_configuration():
    """Test MongoDB configuration."""
    print("\n✓ Testing MongoDB configuration...")
    try:
        from config.database import MongoDBConfig

        # Set test environment variables
        os.environ["MONGODB_HOST"] = "localhost"
        os.environ["MONGODB_PORT"] = "27017"
        os.environ["MONGODB_DATABASE"] = "test_db"
        os.environ["MONGODB_USERNAME"] = "test_user"
        os.environ["MONGODB_PASSWORD"] = "test_password"

        config = MongoDBConfig()

        assert config.host == "localhost", "Host not set correctly"
        assert config.port == 27017, "Port not set correctly"
        assert config.database == "test_db", "Database not set correctly"

        print("  ✓ MongoDBConfig reads environment variables correctly")

        # Test connection string generation
        connection_string = config.connection_string
        assert "localhost" in connection_string, "Connection string missing host"
        assert "27017" in connection_string, "Connection string missing port"
        print("  ✓ Connection string generated correctly")

        return True
    except Exception as e:
        print(f"  ✗ Configuration test failed: {e}")
        return False


def test_model_creation():
    """Test that models can be created."""
    print("\n✓ Testing model creation...")
    try:
        from models.book import Book, BookStatus
        from models.role import Role
        from models.user import User

        # Create a book
        book = Book.create(1, "Test Book", "Test Author")
        assert book.id == 1
        assert book.title == "Test Book"
        assert book.status == BookStatus.AVAILABLE
        print("  ✓ Book model created successfully")

        # Create a user
        user = User(id=1, username="testuser", role=Role.USER)
        assert user.id == 1
        assert user.username == "testuser"
        print("  ✓ User model created successfully")

        # Test book conversion
        book_dict = book.to_dict()
        assert book_dict["id"] == 1
        assert book_dict["title"] == "Test Book"
        print("  ✓ Book to_dict() works correctly")

        return True
    except Exception as e:
        print(f"  ✗ Model creation test failed: {e}")
        return False


def test_code_syntax():
    """Test that all Python files have valid syntax."""
    print("\n✓ Testing Python syntax...")
    import py_compile

    files_to_check = [
        "config/database.py",
        "storage/factory.py",
        "storage/mongodb/book_storage.py",
        "storage/mongodb/user_storage.py",
        "scripts/init_mongodb.py",
        "tests/conftest_mongodb.py",
        "tests/test_mongodb_book_storage.py",
        "tests/test_mongodb_user_storage.py",
    ]

    try:
        for file_path in files_to_check:
            full_path = project_root / file_path
            py_compile.compile(str(full_path), doraise=True)
        print(f"  ✓ All {len(files_to_check)} files have valid Python syntax")
        return True
    except py_compile.PyCompileError as e:
        print(f"  ✗ Syntax error in {file_path}: {e}")
        return False


def test_dependencies():
    """Test that required dependencies are installed."""
    print("\n✓ Testing dependencies...")
    try:
        import pymongo

        print(f"  ✓ pymongo {pymongo.__version__} is installed")

        import dotenv

        print(f"  ✓ python-dotenv ({dotenv.__name__}) is installed")

        import pytest

        print(f"  ✓ pytest {pytest.__version__} is installed")

        return True
    except ImportError as e:
        print(f"  ✗ Missing dependency: {e}")
        return False


def main():
    """Run all verification tests."""
    results = {
        "Imports": test_imports(),
        "Dependencies": test_dependencies(),
        "Configuration": test_configuration(),
        "Model Creation": test_model_creation(),
        "Python Syntax": test_code_syntax(),
        "Factory Pattern": test_factory_pattern(),
    }

    print("\n" + "=" * 60)
    print("VERIFICATION SUMMARY")
    print("=" * 60)

    for test_name, result in results.items():
        status = "✓ PASSED" if result else "✗ FAILED"
        print(f"{test_name:.<40} {status}")

    all_passed = all(results.values())

    print("=" * 60)
    if all_passed:
        print("✓ All verifications PASSED!")
        print("\nMongoDB integration is ready for use.")
        print("To run MongoDB tests:")
        print("  1. Ensure MongoDB is running")
        print("  2. Run: poetry run pytest tests/test_mongodb_*.py -v")
        return 0
    else:
        print("✗ Some verifications FAILED!")
        return 1


if __name__ == "__main__":
    sys.exit(main())
