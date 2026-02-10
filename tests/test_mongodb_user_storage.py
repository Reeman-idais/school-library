import pytest

pytest.skip(
    "Integration tests moved to tests/integration/ and marked with @pytest.mark.integration",
    allow_module_level=True,
)
