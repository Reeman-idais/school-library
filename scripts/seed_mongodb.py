"""Seed MongoDB with sample data from data/*.json.

Usage:
  # From host (uses .env if present):
  python scripts/seed_mongodb.py

  # Inside container (uses container env):
  docker exec -it school-library-app /app/.venv/bin/python scripts/seed_mongodb.py
"""

import json
import logging
import os
from pathlib import Path
from typing import Any, Dict, List

# Ensure project root is on sys.path when executed inside container
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.database import MongoDBConnection, MongoDBConfig
from pymongo import UpdateOne

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("seed")

ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"


def load_json(file: Path) -> List[Dict[str, Any]]:
    if not file.exists():
        logger.warning("Data file %s not found", file)
        return []
    with file.open("r", encoding="utf-8") as fh:
        return json.load(fh)


def seed_books(db, books: List[Dict[str, Any]]):
    if not books:
        logger.info("No books to seed")
        return

    ops = []
    max_id = 0
    for b in books:
        ops.append(UpdateOne({"id": b.get("id")}, {"$set": b}, upsert=True))
        try:
            if isinstance(b.get("id"), int):
                max_id = max(max_id, b.get("id", 0))
        except Exception:
            pass

    result = db["books"].bulk_write(ops)
    logger.info("Books seeded: matched=%s, upserted=%s", result.matched_count, len(result.upserted_ids))

    # Ensure counter at least max_id
    if max_id > 0:
        db["book_id_counter"].update_one(
            {"_id": "book_id"}, {"$max": {"sequence_value": max_id}}, upsert=True
        )
        logger.info("Book ID counter set to at least %d", max_id)


def seed_users(db, users: List[Dict[str, Any]]):
    if not users:
        logger.info("No users to seed")
        return

    ops = []
    max_user_id = 0
    numeric_ids_seen = False

    for u in users:
        # prefer username uniqueness
        ops.append(UpdateOne({"username": u.get("username")}, {"$set": u}, upsert=True))
        uid = u.get("id")
        if isinstance(uid, int):
            numeric_ids_seen = True
            max_user_id = max(max_user_id, uid)

    result = db["users"].bulk_write(ops)
    logger.info("Users seeded: matched=%s, upserted=%s", result.matched_count, len(result.upserted_ids))

    # Update numeric user counter when numeric IDs present
    if numeric_ids_seen and max_user_id > 0:
        db["user_id_counter"].update_one(
            {"_id": "user_id"}, {"$max": {"sequence_value": max_user_id}}, upsert=True
        )
        logger.info("User ID counter set to at least %d", max_user_id)


def main():
    config = MongoDBConfig()
    logger.info("MongoDB config: %s", config)
    client = MongoDBConnection.get_connection(config)
    db = client[config.database]

    books = load_json(DATA_DIR / "books.json")
    users = load_json(DATA_DIR / "users.json")

    seed_books(db, books)
    seed_users(db, users)

    logger.info("Seeding completed")


if __name__ == "__main__":
    main()
