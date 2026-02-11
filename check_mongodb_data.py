#!/usr/bin/env python3
"""Check MongoDB data"""

try:
    from config.database import MongoDBConnection
    from lib_logging.logger import get_logger
except Exception:
    import sys
    from pathlib import Path

    ROOT = Path(__file__).resolve().parent
    if str(ROOT) not in sys.path:
        sys.path.insert(0, str(ROOT))
    from config.database import MongoDBConnection
    from lib_logging.logger import get_logger

logger = get_logger(__name__)


def main():
    try:
        db = MongoDBConnection.get_database()

        # اعرض الكتب
        print("\n" + "=" * 60)
        print("📚 BOOKS IN DATABASE")
        print("=" * 60)
        books = db["books"].find()
        count = 0
        for book in books:
            count += 1
            print(f"\nBook #{count}:")
            print(f"  ID: {book.get('id')}")
            print(f"  Title: {book.get('title')}")
            print(f"  Author: {book.get('author')}")
            print(f"  Status: {book.get('status')}")
            print(f"  Picked By: {book.get('picked_by', 'N/A')}")

        if count == 0:
            print("❌ No books found!")
        else:
            print(f"\n✅ Total: {count} book(s)")

        # اعرض المستخدمين
        print("\n" + "=" * 60)
        print("👥 USERS IN DATABASE")
        print("=" * 60)
        users = db["users"].find()
        count = 0
        for user in users:
            count += 1
            print(f"\nUser #{count}:")
            print(f"  Username: {user.get('username')}")
            print(f"  Role: {user.get('role')}")
            print(f"  Picked Books: {user.get('picked_books', [])}")

        if count == 0:
            print("❌ No users found!")
        else:
            print(f"\n✅ Total: {count} user(s)")

        print("\n" + "=" * 60)

    except Exception as e:
        logger.error(f"Error: {e}")
        print(f"❌ Error connecting to MongoDB: {e}")
        print("\n⚠️  Make sure MongoDB is running!")
        print("   Run: docker run -d -p 27017:27017 --name mongodb mongo:latest")


if __name__ == "__main__":
    main()
