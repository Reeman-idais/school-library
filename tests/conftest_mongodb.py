import pytest

pytest.skip(
    "MongoDB fixtures moved to tests/integration/conftest.py. Run integration tests with -m integration or pytest tests/integration/",
    allow_module_level=True,
)
