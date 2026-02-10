"""Unit tests for FakeBookRepository (fast, deterministic, in-memory)."""

from models.book import Book
from storage.repositories.fake_repo import FakeBookRepository


def test_fake_repo_add_and_get():
    repo = FakeBookRepository()

    book = Book.create(1, "Test", "Author")
    assert repo.add_book(book) is True

    got = repo.get_book_by_id(1)
    assert got is not None
    assert got.title == "Test"


def test_fake_repo_get_next_id_and_remove():
    repo = FakeBookRepository()

    nid = repo.get_next_book_id()
    assert nid == 1

    b = Book.create(nid, "A", "B")
    assert repo.add_book(b)

    assert repo.remove_book(nid) is True
    assert repo.get_book_by_id(nid) is None


def test_fake_repo_update_and_search():
    repo = FakeBookRepository()

    b1 = Book.create(1, "Python Guide", "Alice")
    b2 = Book.create(2, "Advanced Python", "Bob")
    repo.add_book(b1)
    repo.add_book(b2)

    results = repo.search_books(title="Python")
    assert len(results) == 2

    b1.title = "Python 101"
    assert repo.update_book(b1) is True
    assert repo.get_book_by_id(1).title == "Python 101"
