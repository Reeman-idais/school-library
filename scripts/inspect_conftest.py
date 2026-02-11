import importlib

m = importlib.import_module("tests.conftest")
print("module:", m.__name__)
print("has mongodb_book_storage:", "mongodb_book_storage" in dir(m))
print("has mongodb_user_storage:", "mongodb_user_storage" in dir(m))
print("mongodb-related:", [n for n in dir(m) if "mongodb" in n])
