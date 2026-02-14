#!/usr/bin/env python3
"""Seed MongoDB with sample books and users for local development."""

import sys
import time
from pathlib import Path
from dotenv import load_dotenv
from config.database import MongoDBConfig, MongoDBConnection
from models.role import Role
from storage.mongodb.book_storage import MongoDBBookStorage
from storage.mongodb.user_storage import MongoDBUserStorage

# Make sure project root is importable
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

# Load environment variables from .env file
env_file = ROOT / ".env"
if env_file.exists():
    load_dotenv(env_file)
    print(f"Loaded .env from: {env_file}")


def main():
    print("Seeding MongoDB with sample data...")
    cfg = MongoDBConfig()
    # Wait briefly for DB to be ready
    for _ in range(10):
        try:
            MongoDBConnection.get_connection(cfg).admin.command("ping")
            break
        except Exception:
            print("Waiting for MongoDB...")
            time.sleep(1)

    book_storage = MongoDBBookStorage()
    user_storage = MongoDBUserStorage()

    # Add sample users
    sample_users = [
        ("admin", "1234", Role.LIBRARIAN),
        ("tala", "1234", Role.USER),
        ("reman", "4321", Role.USER),
    ]
    for username, password, role in sample_users:
        if not user_storage.user_exists(username):
            user_storage.create_user(username, password, role)
            print(f"Added user: {username}")

    # Add sample books
    sample_books = [
        (1001, "A Brief History of Time", "Stephen Hawking"),
        (1002, "The Pragmatic Programmer", "Andrew Hunt, David Thomas"),
        (1003, "Clean Code", "Robert C. Martin"),
        (1004, "The Hobbit", "J.R.R. Tolkien"),
    ]
    for bid, title, author in sample_books:
        # Avoid duplicates by ID
        if book_storage.get_book_by_id(bid) is None:
            from models.book import Book

            b = Book.create(bid, title, author)
            book_storage.add_book(b)
            print(f"Added book: {title} ({bid})")

    print("Seeding completed.")


if __name__ == "__main__":
    main()
