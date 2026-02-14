#!/usr/bin/env python3
"""Test connection to MongoDB Atlas"""

import os
import sys
from pathlib import Path

from dotenv import load_dotenv

# Add project root to path
PROJECT_ROOT = Path(__file__).resolve().parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


if __name__ == "__main__":
    # Load .env file
    env_file = PROJECT_ROOT / ".env"
    if env_file.exists():
        load_dotenv(env_file)
        print(f"Loaded .env from: {env_file}")

    # Check if MONGODB_URI is set
    mongodb_uri = os.getenv("MONGODB_URI")
    if mongodb_uri:
        print("[OK] MONGODB_URI is set")
        print(f"     Cluster: {mongodb_uri[24:30]}...")
    else:
        print("[ERROR] MONGODB_URI not set in .env")
        print("        Set it like this:")
        print(
            "        MONGODB_URI=mongodb+srv://reeman:Reeman@cluster0.nwwzgip.mongodb.net/school_library?..."
        )
        sys.exit(1)

    # Test connection
    print("\n[INFO] Attempting to connect to MongoDB Atlas...")
    try:
        from config.database import MongoDBConnection

        db = MongoDBConnection.get_database()
        print(f"[OK] Connected to database: {db.name}")

        # Check collections
        collections = db.list_collection_names()
        print(f"[OK] Collections found: {collections}")

        # Write test data
        test_coll = db["test_connection"]
        result = test_coll.insert_one({"test": "data", "timestamp": "test"})
        print(f"[OK] Can write data: {result.inserted_id}")

        # Cleanup
        test_coll.delete_one({"_id": result.inserted_id})
        print("[OK] Can delete data")

        print("\n[SUCCESS] MongoDB Atlas is working correctly!")

    except Exception as e:
        print(f"[ERROR] {type(e).__name__}: {e}")
        sys.exit(1)

except Exception as e:
    print(f"[ERROR] {type(e).__name__}: {e}")
    sys.exit(1)
