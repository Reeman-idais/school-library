"""Migrate books from JSON storage (data/books.json) into MongoDB.

Usage: python scripts/migrate_json_to_mongo.py
"""

import json
import os
import sys
from pathlib import Path

from dotenv import load_dotenv

DATA_FILE = Path(__file__).parent.parent / "data" / "books.json"


def main():
    # Add project root to path so imports work when run as a script
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    load_dotenv()

    from config.database import MongoDBConfig
    from lib_logging.logger import get_logger
    from models.book import Book
    from storage.mongodb.book_storage import MongoDBBookStorage

    logger = get_logger(__name__)

    cfg = MongoDBConfig()
    print("Using MongoDB config:", cfg)

    try:
        # Ensure connection and DB initial setup (indexes, counters)
        print("Initializing MongoDB (indexes/counters)...")
        from scripts.init_mongodb import (
            create_indexes,
            initialize_counters,
            wait_for_mongodb,
        )

        wait_for_mongodb(cfg)
        create_indexes()
        initialize_counters()

        storage = MongoDBBookStorage()

        # Always report current state
        current_count = storage.collection.count_documents({})
        print(f"Current books in MongoDB: {current_count}")

        if not DATA_FILE.exists():
            print(f"No JSON file found at {DATA_FILE}. Nothing to migrate.")
            samples = list(storage.collection.find().limit(5))
            print(f"Sample documents (up to 5): {samples}")
            return

        with open(DATA_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)

        if not isinstance(data, list):
            print("JSON file format invalid: expected a list of book objects")
            return

        added = 0
        skipped = 0
        for item in data:
            try:
                book = Book.from_dict(item)
            except Exception as e:
                logger.warning(f"Skipping invalid book entry: {e} | item={item}")
                skipped += 1
                continue

            # Avoid duplicates by id
            if storage.get_book_by_id(book.id) is not None:
                logger.info(f"Skipping existing book ID {book.id}")
                skipped += 1
                continue

            if storage.add_book(book):
                added += 1
            else:
                logger.warning(f"Failed to add book ID {book.id}")
                skipped += 1

        print(f"Migration complete. Added: {added}, Skipped: {skipped}")
        print(f"Total books in MongoDB now: {storage.collection.count_documents({})}")

    except Exception as e:
        print("Migration failed:", e)


if __name__ == "__main__":
    main()
