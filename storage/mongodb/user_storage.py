"""MongoDB implementation of user storage."""

from typing import List, Optional

from pymongo import ASCENDING
from pymongo.collection import Collection
from pymongo.errors import PyMongoError

from config.database import MongoDBConnection
from lib_logging.logger import get_logger
from models.role import Role
from models.user import User

logger = get_logger(__name__)


class MongoDBUserStorage:
    """MongoDB implementation of user storage."""

    def __init__(self):
        """Initialize MongoDB user storage."""
        self.db = MongoDBConnection.get_database()
        self.collection: Collection = self.db["users"]
        self.id_counter: Collection = self.db["user_id_counter"]
        self._ensure_indexes()
        self._ensure_counter()

    def _ensure_indexes(self) -> None:
        """Create necessary indexes for efficient querying."""
        try:
            # Index on user ID for quick lookups
            self.collection.create_index([("id", ASCENDING)], unique=True)
            # Index on username for quick lookups
            self.collection.create_index([("username", ASCENDING)], unique=True)
            # Index on role for filtering
            self.collection.create_index([("role", ASCENDING)])
            logger.info("User collection indexes ensured")
        except PyMongoError as e:
            logger.warning(f"Error creating indexes: {e}")

    def _ensure_counter(self) -> None:
        """Ensure ID counter exists."""
        if self.id_counter.find_one({"_id": "user_id"}) is None:
            self.id_counter.insert_one({"_id": "user_id", "sequence_value": 0})
            logger.info("Initialized user ID counter")

    def _get_next_id(self) -> int:
        """Get the next user ID using atomic increment."""
        try:
            result = self.id_counter.find_one_and_update(
                {"_id": "user_id"},
                {"$inc": {"sequence_value": 1}},
                return_document=True,
            )
            return result["sequence_value"]
        except PyMongoError as e:
            logger.error(f"Error getting next ID: {e}")
            raise

    def load_users(self) -> List[User]:
        """Load all users from MongoDB."""
        try:
            users = []
            for doc in self.collection.find().sort("id", 1):
                users.append(self._doc_to_user(doc))
            logger.info(f"Loaded {len(users)} users from MongoDB")
            return users
        except PyMongoError as e:
            logger.error(f"Error loading users: {e}")
            raise

    def get_user_by_id(self, user_id: int) -> Optional[User]:
        """Get a specific user by ID."""
        try:
            doc = self.collection.find_one({"id": user_id})
            if doc:
                return self._doc_to_user(doc)
            return None
        except PyMongoError as e:
            logger.error(f"Error getting user {user_id}: {e}")
            raise

    def get_user_by_username(self, username: str) -> Optional[User]:
        """Get a specific user by username."""
        try:
            doc = self.collection.find_one({"username": username})
            if doc:
                return self._doc_to_user(doc)
            return None
        except PyMongoError as e:
            logger.error(f"Error getting user by username {username}: {e}")
            raise

    def get_next_user_id(self) -> int:
        """Get the next available user ID."""
        return self._get_next_id()

    def add_user(self, user: User) -> bool:
        """Add a new user to MongoDB."""
        try:
            doc = self._user_to_doc(user)
            result = self.collection.insert_one(doc)
            logger.info(f"Added user {user.id} with ObjectId {result.inserted_id}")
            return True
        except PyMongoError as e:
            logger.error(f"Error adding user: {e}")
            return False

    def update_user(self, user: User) -> bool:
        """Update an existing user in MongoDB."""
        try:
            doc = self._user_to_doc(user)
            result = self.collection.replace_one({"id": user.id}, doc)
            if result.matched_count == 0:
                logger.warning(f"User {user.id} not found for update")
                return False
            logger.info(f"Updated user {user.id}")
            return True
        except PyMongoError as e:
            logger.error(f"Error updating user {user.id}: {e}")
            return False

    def remove_user(self, user_id: int) -> bool:
        """Remove a user from MongoDB."""
        try:
            result = self.collection.delete_one({"id": user_id})
            if result.deleted_count == 0:
                logger.warning(f"User {user_id} not found for deletion")
                return False
            logger.info(f"Removed user {user_id}")
            return True
        except PyMongoError as e:
            logger.error(f"Error removing user {user_id}: {e}")
            return False

    def search_users(self, **kwargs) -> List[User]:
        """Search users by various criteria."""
        try:
            query = {}
            if "username" in kwargs:
                query["username"] = {"$regex": kwargs["username"], "$options": "i"}
            if "role" in kwargs:
                query["role"] = kwargs["role"]

            users = []
            for doc in self.collection.find(query):
                users.append(self._doc_to_user(doc))
            return users
        except PyMongoError as e:
            logger.error(f"Error searching users: {e}")
            return []

    @staticmethod
    def _user_to_doc(user: User) -> dict:
        """Convert User object to MongoDB document."""
        return {
            "id": user.id,
            "username": user.username,
            "role": user.role.value,
            "borrowed_book_ids": user.borrowed_book_ids,
        }

    @staticmethod
    def _doc_to_user(doc: dict) -> User:
        """Convert MongoDB document to User object."""
        return User(
            id=doc["id"],
            username=doc["username"],
            role=Role(doc["role"]),
            borrowed_book_ids=doc.get("borrowed_book_ids", []),
        )
