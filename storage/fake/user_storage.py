"""In-memory (fake) user storage used for unit tests and CI.

Mirrors the public API used across the app.
"""

from typing import List, Optional

from lib_logging.logger import get_logger
from models.role import Role
from models.user import User

logger = get_logger(__name__)


class FakeUserStorage:
    """In-memory user storage used for tests."""

    def __init__(self):
        self._users: List[User] = []

    def _reset(self) -> None:
        self._users = []

    def load_users(self) -> List[User]:
        return list(self._users)

    def save_users(self, users: List[User]) -> bool:
        self._users = list(users)
        return True

    def get_user_by_username(self, username: str) -> Optional[User]:
        for u in self._users:
            if u.username == username:
                return u
        return None

    def create_user(self, username: str, password: str, role: Role) -> Optional[User]:
        if self.get_user_by_username(username):
            logger.warning("Username '%s' already exists", username)
            return None
        user = User.create(username, password, role)
        self._users.append(user)
        return user

    def user_exists(self, username: str) -> bool:
        return self.get_user_by_username(username) is not None
