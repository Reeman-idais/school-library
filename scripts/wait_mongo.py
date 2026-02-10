import time
import pymongo
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError

max_retries = 30
for attempt in range(max_retries):
    try:
        client = pymongo.MongoClient(
            'mongodb://admin:password123@localhost:27017/school_library_test',
            serverSelectionTimeoutMS=5000,
        )
        client.admin.command('ping')
        print('MongoDB is ready')
        break
    except (ConnectionFailure, ServerSelectionTimeoutError) as e:
        print('waiting...', attempt)
        time.sleep(1)
else:
    raise RuntimeError('MongoDB did not start in time')
