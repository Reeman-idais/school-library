import pytest

from models.role import Role
from models.user import User

pytestmark = pytest.mark.integration


class TestMongoDBUserStorage:
    """Integration tests for MongoDBUserStorage."""

    def test_initialization(self, mongodb_user_storage):
        assert mongodb_user_storage.collection is not None
        assert mongodb_user_storage.id_counter is not None

    def test_get_next_id_increments(self, mongodb_user_storage):
        id1 = mongodb_user_storage.get_next_user_id()
        id2 = mongodb_user_storage.get_next_user_id()
        id3 = mongodb_user_storage.get_next_user_id()

        assert id1 == 1
        assert id2 == 2
        assert id3 == 3

    def test_add_and_retrieve_user(self, mongodb_user_storage):
        user = User.create("bob", "1234", Role.USER)
        result = mongodb_user_storage.add_user(user)
        assert result is True

        retrieved = mongodb_user_storage.get_user_by_id(1)
        assert retrieved is not None
        assert retrieved.username == "bob"

    def test_get_user_by_username(self, mongodb_user_storage):
        user = User.create("bob", "1234", Role.USER)
        mongodb_user_storage.add_user(user)

        retrieved = mongodb_user_storage.get_user_by_username("bob")
        assert retrieved is not None
        assert retrieved.username == "bob"

    def test_load_all_users(self, mongodb_user_storage):
        for i, username in enumerate(["a", "b", "c"], start=1):
            user = User.create(username, "1234", Role.USER)
            mongodb_user_storage.add_user(user)

        loaded = mongodb_user_storage.load_users()
        assert len(loaded) == 3

    def test_update_user(self, mongodb_user_storage):
        user = User.create("bob", "1234", Role.USER)
        mongodb_user_storage.add_user(user)

        user.role = Role.LIBRARIAN
        result = mongodb_user_storage.update_user(user)
        assert result is True

        updated = mongodb_user_storage.get_user_by_id(1)
        assert updated.role == Role.LIBRARIAN

    def test_remove_user(self, mongodb_user_storage):
        user = User.create("alice", "pw", Role.USER)
        mongodb_user_storage.add_user(user)

        result = mongodb_user_storage.remove_user(1)
        assert result is True

        retrieved = mongodb_user_storage.get_user_by_id(1)
        assert retrieved is None

    def test_search_users_by_username(self, mongodb_user_storage):
        user = User.create("alice", "pw", Role.USER)
        mongodb_user_storage.add_user(user)

        results = mongodb_user_storage.search_users(username="alice")
        assert any(u.username == "alice" for u in results)

    def test_search_users_by_role(self, mongodb_user_storage):
        user = User.create("librarian", "pw", Role.LIBRARIAN)
        mongodb_user_storage.add_user(user)

        results = mongodb_user_storage.search_users(role=Role.LIBRARIAN)
        assert any(u.role == Role.LIBRARIAN for u in results)

    def test_get_nonexistent_user(self, mongodb_user_storage):
        result = mongodb_user_storage.get_user_by_id(999)
        assert result is None

    def test_get_user_by_nonexistent_username(self, mongodb_user_storage):
        result = mongodb_user_storage.get_user_by_username("nonexistent")
        assert result is None

    def test_remove_nonexistent_user(self, mongodb_user_storage):
        result = mongodb_user_storage.remove_user(999)
        assert result is False

    def test_update_nonexistent_user(self, mongodb_user_storage):
        user = User.create("ghost", "pw", Role.USER)
        user.id = 999
        result = mongodb_user_storage.update_user(user)
        assert result is False

    def test_unique_username_constraint(self, mongodb_user_storage):
        user1 = User.create("u1", "pw1", Role.USER)
        user2 = User.create("u1", "pw2", Role.USER)

        assert mongodb_user_storage.add_user(user1) is True
        assert mongodb_user_storage.add_user(user2) is False
