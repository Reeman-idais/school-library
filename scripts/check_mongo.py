import json
import os
import sys

from dotenv import load_dotenv


def main():
    # Ensure project root is on sys.path when run as a script
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    load_dotenv()

    from config.database import MongoDBConfig, MongoDBConnection

    cfg = MongoDBConfig()
    print("Using config:", cfg)
    try:
        db = MongoDBConnection.get_database(cfg)
        print("Collections:", db.list_collection_names())
        count = db.books.count_documents({})
        print("books count =", count)
        doc = db.books.find_one()
        print("sample doc:", json.dumps(doc, default=str, indent=2))
    except Exception as e:
        print("ERROR:", e)


if __name__ == "__main__":
    main()
