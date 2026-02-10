from models.book import Book
from storage.fake.book_storage import FakeBookStorage


def test_add_and_get_book():
    s = FakeBookStorage()

    book = Book.create(1, "T1", "A")
    assert s.add_book(book) is True

    got = s.get_book_by_id(1)
    assert got is not None
    assert got.title == "T1"


def test_get_next_book_id_increments():
    s = FakeBookStorage()
    assert s.get_next_book_id() == 1
    assert s.get_next_book_id() == 2


def test_update_and_remove():
    s = FakeBookStorage()
    book = Book.create(1, "X", "Y")
    s.add_book(book)

    book.title = "Z"
    assert s.update_book(book) is True
    assert s.get_book_by_id(1).title == "Z"

    assert s.remove_book(1) is True
    assert s.get_book_by_id(1) is None
