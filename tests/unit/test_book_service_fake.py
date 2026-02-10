"""Unit tests for BookService using FakeBookRepository (no network, deterministic)."""

from models.book import BookStatus
from services.book_service import BookService
from storage.repositories.fake_repo import FakeBookRepository


def test_add_and_get_book_with_fake_repo():
    repo = FakeBookRepository()
    service = BookService(storage=repo)

    # Use a valid user-provided ID (validation requires >= 4 digits)
    book_id = 1001
    book, err = service.add_book(book_id, "Hello Python", "Guido")
    assert err == ""
    assert book is not None

    fetched = service.get_book(book.id)
    assert fetched is not None
    assert fetched.title == "Hello Python"


def test_pick_and_approve_with_fake_repo():
    repo = FakeBookRepository()
    service = BookService(storage=repo)

    # Use a valid user-provided ID
    bid = 1002
    book, _ = service.add_book(bid, "Pickable", "Author")

    got, err = service.pick_book(book.id, "alice")
    assert err == ""
    assert got.status == BookStatus.PICKED
    assert got.picked_by == "alice"

    got2, err2 = service.approve_borrow(book.id)
    assert err2 == ""
    assert got2.status == BookStatus.BORROWED
