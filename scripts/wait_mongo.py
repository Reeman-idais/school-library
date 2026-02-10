import os
import time

import pymongo
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError

# Read the connection URI from the environment (CI sets MONGODB_URI)
uri = os.environ.get(
    "MONGODB_URI",
    "mongodb://admin:password123@mongodb:27017/school_library_test?authSource=admin",
)

max_retries = 120
for attempt in range(max_retries):
    try:
        client = pymongo.MongoClient(uri, serverSelectionTimeoutMS=5000)
        client.admin.command("ping")
        print("MongoDB is ready")
        break
    except (ConnectionFailure, ServerSelectionTimeoutError) as e:
        print(f"Attempt {attempt + 1}/{max_retries}: {e}")
        time.sleep(1)
else:
    raise SystemExit("MongoDB did not start in time")
