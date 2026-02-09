"""Tests for validation functions."""

from validation.isbn_validator import normalize_isbn, validate_isbn10
from validation.user_validator import validate_role, validate_username


class TestUserValidator:
    """Test user validation functions."""

    def test_validate_username_valid(self):
        """Test valid username."""
        is_valid, error_msg = validate_username("testuser123")
        assert is_valid is True
        assert error_msg == ""

    def test_validate_username_empty(self):
        """Test empty username."""
        is_valid, error_msg = validate_username("")
        assert is_valid is False
        assert "empty" in error_msg.lower()

    def test_validate_username_too_short(self):
        """Test username too short."""
        is_valid, error_msg = validate_username("ab")
        assert is_valid is False
        assert "3 characters" in error_msg

    def test_validate_role_valid(self):
        """Test valid role."""
        is_valid, error_msg, role = validate_role("user")
        assert is_valid is True
        assert role.value == "user"

    def test_validate_role_invalid(self):
        """Test invalid role."""
        is_valid, error_msg, role = validate_role("invalid")
        assert is_valid is False
        assert role is None


class TestISBNValidator:
    """Test ISBN validation functions."""

    def test_validate_isbn10_valid(self):
        """Test valid ISBN."""
        is_valid, error_msg = validate_isbn10("1234567890")
        assert is_valid is True

    def test_validate_isbn10_too_short(self):
        """Test ISBN too short."""
        is_valid, error_msg = validate_isbn10("123")
        assert is_valid is False

    def test_validate_isbn10_non_numeric(self):
        """Test non-numeric ISBN."""
        is_valid, error_msg = validate_isbn10("abc123")
        assert is_valid is False

    def test_normalize_isbn(self):
        """Test ISBN normalization."""
        normalized = normalize_isbn("123-456-7890")
        assert normalized == "1234567890"
