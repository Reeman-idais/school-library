import os

from storage.factory import StorageFactory


def test_factory_returns_fake_when_env_set(monkeypatch):
    monkeypatch.setenv("DATABASE_TYPE", "fake")
    StorageFactory.reset()
    book = StorageFactory.create_book_storage()
    user = StorageFactory.create_user_storage()
    assert book is not None
    assert user is not None


def test_reset_clears_singletons():
    StorageFactory.reset()
    # create one instance and then reset
    os.environ["DATABASE_TYPE"] = "fake"
    b1 = StorageFactory.create_book_storage()
    StorageFactory.reset()
    b2 = StorageFactory.create_book_storage()
    assert b1 is not b2
