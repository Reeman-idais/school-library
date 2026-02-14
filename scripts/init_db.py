#!/usr/bin/env python3
"""Initialize database with test users and books if empty."""

import sys
from pathlib import Path

from dotenv import load_dotenv

from models.book import Book
from models.role import Role
from storage.factory import StorageFactory

# Add project root to path
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

# Load environment variables
env_file = ROOT / ".env"
if env_file.exists():
    load_dotenv(env_file)


def init_db():
    """Initialize database with test data if needed."""
    try:
        # Create storage instances
        factory = StorageFactory()
        user_storage = factory.create_user_storage()
        book_storage = factory.create_book_storage()

        # Test users with passwords matching what's in .env comments
        test_users = [
            ("admin", "1234", Role.LIBRARIAN),  # librarian default
            ("tala", "1234", Role.USER),  # user default
            ("reman", "4321", Role.USER),  # another user
        ]

        # Add test users if they don't exist
        users_added = 0
        for username, password, role in test_users:
            existing_user = user_storage.get_user_by_username(username)
            if not existing_user:
                user_storage.create_user(username, password, role)
                print(f"✓ Added user: {username} ({role.value})")
                users_added += 1
            else:
                print(f"✓ User already exists: {username}")

        # Add test books if they don't exist
        test_books = [
            (1001, "A Brief History of Time", "Stephen Hawking"),
            (1002, "The Pragmatic Programmer", "Andrew Hunt, David Thomas"),
            (1003, "Clean Code", "Robert C. Martin"),
            (1004, "The Hobbit", "J.R.R. Tolkien"),
            (1005, "Design Patterns", "Gang of Four"),
            (1006, "The Lord of the Rings", "J.R.R. Tolkien"),
        ]

        books_added = 0
        for book_id, title, author in test_books:
            existing_book = book_storage.get_book_by_id(book_id)
            if not existing_book:
                book = Book.create(book_id, title, author)
                book_storage.add_book(book)
                print(f"✓ Added book: {title} (ID: {book_id})")
                books_added += 1
            else:
                print(f"✓ Book already exists: {title} (ID: {book_id})")

        if users_added > 0 or books_added > 0:
            print(
                f"\n✓ Database initialized: {users_added} users, {books_added} books added"
            )
        else:
            print("\n✓ Database already initialized")

        return True

    except Exception as e:
        print(f"✗ Error initializing database: {e}")
        import traceback

        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = init_db()
    sys.exit(0 if success else 1)
