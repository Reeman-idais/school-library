import importlib
import traceback

try:
    importlib.import_module("tests.conftest_mongodb")
    print("import ok")
except Exception as e:
    print("import failed:", type(e), e)
    traceback.print_exc()
