"""MongoDB implementation of book storage."""

from typing import List, Optional

from pymongo import ASCENDING
from pymongo.collection import Collection
from pymongo.errors import PyMongoError

from config.database import MongoDBConnection
from lib_logging.logger import get_logger
from models.book import Book, BookStatus

logger = get_logger(__name__)


class MongoDBBookStorage:
    """MongoDB implementation of book storage with auto-incrementing ID support."""

    def __init__(self):
        """Initialize MongoDB book storage."""
        self.db = MongoDBConnection.get_database()
        self.collection: Collection = self.db["books"]
        self.id_counter: Collection = self.db["book_id_counter"]
        self._ensure_indexes()
        self._ensure_counter()

    def _ensure_indexes(self) -> None:
        """Create necessary indexes for efficient querying."""
        try:
            # Index on book ID for quick lookups
            self.collection.create_index([("id", ASCENDING)], unique=True)
            # Index on title for searching
            self.collection.create_index([("title", ASCENDING)])
            # Index on author for searching
            self.collection.create_index([("author", ASCENDING)])
            # Index on status for filtering
            self.collection.create_index([("status", ASCENDING)])
            logger.info("Book collection indexes ensured")
        except PyMongoError as e:
            logger.warning(f"Error creating indexes: {e}")

    def _ensure_counter(self) -> None:
        """Ensure ID counter exists."""
        if self.id_counter.find_one({"_id": "book_id"}) is None:
            self.id_counter.insert_one({"_id": "book_id", "sequence_value": 0})
            logger.info("Initialized book ID counter")

    def _get_next_id(self) -> int:
        """Get the next book ID using atomic increment."""
        try:
            result = self.id_counter.find_one_and_update(
                {"_id": "book_id"},
                {"$inc": {"sequence_value": 1}},
                return_document=True,
            )
            if result is None:
                raise RuntimeError("Book ID counter missing")
            return int(result["sequence_value"]) 
        except PyMongoError as e:
            logger.error(f"Error getting next ID: {e}")
            raise

    def load_books(self) -> List[Book]:
        """Load all books from MongoDB."""
        try:
            books = []
            for doc in self.collection.find().sort("id", 1):
                books.append(self._doc_to_book(doc))
            logger.info(f"Loaded {len(books)} books from MongoDB")
            return books
        except PyMongoError as e:
            logger.error(f"Error loading books: {e}")
            raise

    def get_book_by_id(self, book_id: int) -> Optional[Book]:
        """Get a specific book by ID."""
        try:
            doc = self.collection.find_one({"id": book_id})
            if doc:
                return self._doc_to_book(doc)
            return None
        except PyMongoError as e:
            logger.error(f"Error getting book {book_id}: {e}")
            raise

    def get_next_book_id(self) -> int:
        """Get the next available book ID."""
        return self._get_next_id()

    def add_book(self, book: Book) -> bool:
        """Add a new book to MongoDB."""
        try:
            doc = self._book_to_doc(book)
            result = self.collection.insert_one(doc)
            logger.info(f"Added book {book.id} with ObjectId {result.inserted_id}")
            return True
        except PyMongoError as e:
            logger.error(f"Error adding book: {e}")
            return False

    def update_book(self, book: Book) -> bool:
        """Update an existing book in MongoDB."""
        try:
            doc = self._book_to_doc(book)
            result = self.collection.replace_one({"id": book.id}, doc)
            if result.matched_count == 0:
                logger.warning(f"Book {book.id} not found for update")
                return False
            logger.info(f"Updated book {book.id}")
            return True
        except PyMongoError as e:
            logger.error(f"Error updating book {book.id}: {e}")
            return False

    def remove_book(self, book_id: int) -> bool:
        """Remove a book from MongoDB."""
        try:
            result = self.collection.delete_one({"id": book_id})
            if result.deleted_count == 0:
                logger.warning(f"Book {book_id} not found for deletion")
                return False
            logger.info(f"Removed book {book_id}")
            return True
        except PyMongoError as e:
            logger.error(f"Error removing book {book_id}: {e}")
            return False

    def search_books(self, **kwargs) -> List[Book]:
        """Search books by various criteria."""
        try:
            query = {}
            if "title" in kwargs:
                query["title"] = {"$regex": kwargs["title"], "$options": "i"}
            if "author" in kwargs:
                query["author"] = {"$regex": kwargs["author"], "$options": "i"}
            if "status" in kwargs:
                query["status"] = kwargs["status"]

            books = []
            for doc in self.collection.find(query):
                books.append(self._doc_to_book(doc))
            return books
        except PyMongoError as e:
            logger.error(f"Error searching books: {e}")
            return []

    @staticmethod
    def _book_to_doc(book: Book) -> dict:
        """Convert Book object to MongoDB document."""
        return {
            "id": book.id,
            "title": book.title,
            "author": book.author,
            "status": book.status.value,
            "picked_by": book.picked_by,
        }

    @staticmethod
    def _doc_to_book(doc: dict) -> Book:
        """Convert MongoDB document to Book object."""
        return Book(
            id=doc["id"],
            title=doc["title"],
            author=doc["author"],
            status=BookStatus(doc["status"]),
            picked_by=doc.get("picked_by"),
        )
