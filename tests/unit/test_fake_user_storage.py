from models.role import Role
from storage.fake.user_storage import FakeUserStorage


def test_create_and_get_user():
    s = FakeUserStorage()

    u = s.create_user("bob", "p", Role.USER)
    assert u is not None
    assert u.username == "bob"

    assert s.user_exists("bob") is True


def test_duplicate_username_rejected():
    s = FakeUserStorage()
    s.create_user("bob", "p", Role.USER)
    assert s.create_user("bob", "x", Role.USER) is None


def test_load_users_and_save():
    s = FakeUserStorage()
    s.create_user("a", "p", Role.USER)
    s.create_user("b", "p", Role.USER)
    users = s.load_users()
    assert len(users) == 2
