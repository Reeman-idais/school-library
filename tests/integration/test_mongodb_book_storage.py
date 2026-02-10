import pytest

from models.book import Book, BookStatus

pytestmark = pytest.mark.integration


class TestMongoDBBookStorage:
    """Integration tests for MongoDBBookStorage."""

    def test_initialization(self, mongodb_book_storage):
        assert mongodb_book_storage.collection is not None
        assert mongodb_book_storage.id_counter is not None

    def test_get_next_id_increments(self, mongodb_book_storage):
        id1 = mongodb_book_storage.get_next_book_id()
        id2 = mongodb_book_storage.get_next_book_id()
        id3 = mongodb_book_storage.get_next_book_id()

        assert id1 == 1
        assert id2 == 2
        assert id3 == 3

    def test_add_and_retrieve_book(self, mongodb_book_storage):
        book = Book.create(1, "Python Testing", "John Doe")
        result = mongodb_book_storage.add_book(book)
        assert result is True

        retrieved = mongodb_book_storage.get_book_by_id(1)
        assert retrieved is not None
        assert retrieved.title == "Python Testing"

    def test_load_all_books(self, mongodb_book_storage):
        for i in range(1, 4):
            book = Book.create(i, f"Book {i}", "Author")
            mongodb_book_storage.add_book(book)

        loaded = mongodb_book_storage.load_books()
        assert len(loaded) == 3

    def test_update_book(self, mongodb_book_storage):
        book = Book.create(1, "Old Title", "Author")
        mongodb_book_storage.add_book(book)

        book.title = "New Title"
        result = mongodb_book_storage.update_book(book)
        assert result is True

        updated = mongodb_book_storage.get_book_by_id(1)
        assert updated.title == "New Title"

    def test_remove_book(self, mongodb_book_storage):
        book = Book.create(1, "To Remove", "Author")
        mongodb_book_storage.add_book(book)

        result = mongodb_book_storage.remove_book(1)
        assert result is True

        retrieved = mongodb_book_storage.get_book_by_id(1)
        assert retrieved is None

    def test_search_books_by_title(self, mongodb_book_storage):
        book = Book.create(1, "Python Programming", "John")
        mongodb_book_storage.add_book(book)

        results = mongodb_book_storage.search_books(title="Python")
        assert any("Python" in b.title for b in results)

    def test_search_books_by_author(self, mongodb_book_storage):
        book = Book.create(1, "My Book", "John")
        mongodb_book_storage.add_book(book)

        results = mongodb_book_storage.search_books(author="John")
        assert any(b.author == "John" for b in results)

    def test_search_books_by_status(self, mongodb_book_storage):
        book1 = Book.create(1, "B1", "A", status=BookStatus.AVAILABLE)
        book2 = Book.create(2, "B2", "A", status=BookStatus.BORROWED)
        mongodb_book_storage.add_book(book1)
        mongodb_book_storage.add_book(book2)

        results = mongodb_book_storage.search_books(status=BookStatus.BORROWED.value)
        assert any(b.id == 2 for b in results)

    def test_get_nonexistent_book(self, mongodb_book_storage):
        result = mongodb_book_storage.get_book_by_id(999)
        assert result is None

    def test_remove_nonexistent_book(self, mongodb_book_storage):
        result = mongodb_book_storage.remove_book(999)
        assert result is False

    def test_update_nonexistent_book(self, mongodb_book_storage):
        book = Book.create(999, "Ghost", "Nobody")
        result = mongodb_book_storage.update_book(book)
        assert result is False
