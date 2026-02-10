import json

from config.database import MongoDBConfig, MongoDBConnection

cfg = MongoDBConfig()
db = MongoDBConnection.get_database(cfg)
docs = list(db.books.find())
print("count =", len(docs))
for i, d in enumerate(docs, 1):
    print("--- doc", i)
    print(json.dumps(d, default=str, indent=2))
    # show keys and if 'status' present
    print("keys:", sorted(list(d.keys())))
    print("has_status:", "status" in d)
