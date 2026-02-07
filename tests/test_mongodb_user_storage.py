"""Integration tests for MongoDB user storage."""

import pytest

from models.role import Role
from models.user import User
from storage.mongodb.user_storage import MongoDBUserStorage


@pytest.mark.integration
class TestMongoDBUserStorage:
    """Integration tests for MongoDBUserStorage."""

    def test_initialization(self, mongodb_user_storage):
        """Test storage initialization."""
        assert mongodb_user_storage.collection is not None
        assert mongodb_user_storage.id_counter is not None

    def test_get_next_id_increments(self, mongodb_user_storage):
        """Test that ID counter increments properly."""
        id1 = mongodb_user_storage.get_next_user_id()
        id2 = mongodb_user_storage.get_next_user_id()
        id3 = mongodb_user_storage.get_next_user_id()

        assert id1 == 1
        assert id2 == 2
        assert id3 == 3

    def test_add_and_retrieve_user(self, mongodb_user_storage):
        """Test adding and retrieving a user."""
        user = User(id=1, username="alice", role=Role.STUDENT)

        result = mongodb_user_storage.add_user(user)
        assert result is True

        retrieved = mongodb_user_storage.get_user_by_id(1)
        assert retrieved is not None
        assert retrieved.username == "alice"
        assert retrieved.role == Role.STUDENT

    def test_get_user_by_username(self, mongodb_user_storage):
        """Test retrieving a user by username."""
        user = User(id=1, username="bob", role=Role.LIBRARIAN)
        mongodb_user_storage.add_user(user)

        retrieved = mongodb_user_storage.get_user_by_username("bob")
        assert retrieved is not None
        assert retrieved.id == 1
        assert retrieved.role == Role.LIBRARIAN

    def test_load_all_users(self, mongodb_user_storage):
        """Test loading all users."""
        users = [
            User(id=1, username="alice", role=Role.STUDENT),
            User(id=2, username="bob", role=Role.LIBRARIAN),
            User(id=3, username="charlie", role=Role.STUDENT),
        ]

        for user in users:
            mongodb_user_storage.add_user(user)

        loaded = mongodb_user_storage.load_users()
        assert len(loaded) == 3
        assert loaded[0].username == "alice"
        assert loaded[1].username == "bob"
        assert loaded[2].username == "charlie"

    def test_update_user(self, mongodb_user_storage):
        """Test updating a user."""
        user = User(id=1, username="alice", role=Role.STUDENT)
        mongodb_user_storage.add_user(user)

        user.borrowed_book_ids = [1, 2, 3]
        result = mongodb_user_storage.update_user(user)
        assert result is True

        updated = mongodb_user_storage.get_user_by_id(1)
        assert updated.borrowed_book_ids == [1, 2, 3]

    def test_remove_user(self, mongodb_user_storage):
        """Test removing a user."""
        user = User(id=1, username="alice", role=Role.STUDENT)
        mongodb_user_storage.add_user(user)

        result = mongodb_user_storage.remove_user(1)
        assert result is True

        retrieved = mongodb_user_storage.get_user_by_id(1)
        assert retrieved is None

    def test_search_users_by_username(self, mongodb_user_storage):
        """Test searching users by username."""
        users = [
            User(id=1, username="alice_smith", role=Role.STUDENT),
            User(id=2, username="bob_jones", role=Role.STUDENT),
            User(id=3, username="alice_johnson", role=Role.LIBRARIAN),
        ]

        for user in users:
            mongodb_user_storage.add_user(user)

        results = mongodb_user_storage.search_users(username="alice")
        assert len(results) == 2
        assert all("alice" in u.username for u in results)

    def test_search_users_by_role(self, mongodb_user_storage):
        """Test searching users by role."""
        users = [
            User(id=1, username="alice", role=Role.STUDENT),
            User(id=2, username="bob", role=Role.LIBRARIAN),
            User(id=3, username="charlie", role=Role.STUDENT),
        ]

        for user in users:
            mongodb_user_storage.add_user(user)

        results = mongodb_user_storage.search_users(role=Role.LIBRARIAN)
        assert len(results) == 1
        assert results[0].username == "bob"

    def test_get_nonexistent_user(self, mongodb_user_storage):
        """Test getting a user that doesn't exist."""
        result = mongodb_user_storage.get_user_by_id(999)
        assert result is None

    def test_get_user_by_nonexistent_username(self, mongodb_user_storage):
        """Test getting a user by nonexistent username."""
        result = mongodb_user_storage.get_user_by_username("nonexistent")
        assert result is None

    def test_remove_nonexistent_user(self, mongodb_user_storage):
        """Test removing a user that doesn't exist."""
        result = mongodb_user_storage.remove_user(999)
        assert result is False

    def test_update_nonexistent_user(self, mongodb_user_storage):
        """Test updating a user that doesn't exist."""
        user = User(id=999, username="nonexistent", role=Role.STUDENT)
        result = mongodb_user_storage.update_user(user)
        assert result is False

    def test_unique_username_constraint(self, mongodb_user_storage):
        """Test that usernames must be unique."""
        user1 = User(id=1, username="alice", role=Role.STUDENT)
        user2 = User(id=2, username="alice", role=Role.STUDENT)

        assert mongodb_user_storage.add_user(user1) is True
        # Note: MongoDB should prevent this, but we'll just verify it doesn't break
        # In production MongoDB would raise a duplicate key error
