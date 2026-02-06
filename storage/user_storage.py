"""User storage operations using JSON persistence."""

import json
import shutil
from pathlib import Path
from typing import List, Optional

from lib_logging.logger import get_logger

from models.role import Role
from models.user import User

logger = get_logger(__name__)


class UserStorage:
    """Handles user data persistence in JSON format."""

    def __init__(self, data_dir: Optional[Path] = None):
        """
        Initialize user storage.

        Args:
            data_dir: Directory for data files (default: project_root/data)
        """
        if data_dir is None:
            data_dir = Path("data")
        self.data_dir = data_dir
        self.data_dir.mkdir(exist_ok=True)
        self.users_file = self.data_dir / "users.json"

    def load_users(self) -> List[User]:
        """
        Load all users from JSON file.

        Returns:
            List of User objects
        """
        if not self.users_file.exists():
            logger.info(
                f"Users file not found at {self.users_file}, creating empty file"
            )
            self._save_users_internal([])
            return []

        try:
            with open(self.users_file, "r", encoding="utf-8") as f:
                data = json.load(f)
                users = [User.from_dict(user_data) for user_data in data]
                logger.info(f"Loaded {len(users)} users from storage")
                return users
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse users JSON: {e}")
            # Create backup and return empty list
            backup_file = self.users_file.with_suffix(".json.bak")
            shutil.copy2(self.users_file, backup_file)
            logger.warning(f"Created backup at {backup_file}")
            return []
        except Exception as e:
            logger.error(f"Error loading users: {e}")
            return []

    def save_users(self, users: List[User]) -> bool:
        """
        Save users to JSON file with atomic write.

        Args:
            users: List of User objects to save

        Returns:
            True if successful, False otherwise
        """
        try:
            return self._save_users_internal(users)
        except Exception as e:
            logger.error(f"Error saving users: {e}")
            return False

    def _save_users_internal(self, users: List[User]) -> bool:
        """Internal method to save users with atomic write."""
        # Write to temporary file first
        temp_file = self.users_file.with_suffix(".json.tmp")

        try:
            with open(temp_file, "w", encoding="utf-8") as f:
                users_data = [user.to_dict() for user in users]
                json.dump(users_data, f, indent=2, ensure_ascii=False)

            # Atomic move
            temp_file.replace(self.users_file)
            logger.info(f"Saved {len(users)} users to storage")
            return True
        except Exception as e:
            logger.error(f"Error writing users file: {e}")
            # Clean up temp file if it exists
            if temp_file.exists():
                temp_file.unlink()
            return False

    def get_user_by_username(self, username: str) -> Optional[User]:
        """
        Get a user by username.

        Args:
            username: Username to search for

        Returns:
            User object if found, None otherwise
        """
        users = self.load_users()
        for user in users:
            if user.username == username:
                return user
        return None

    def create_user(self, username: str, role: Role) -> Optional[User]:
        """
        Create a new user and save to storage.

        Args:
            username: Username for the new user
            role: Role for the new user

        Returns:
            Created User object if successful, None otherwise
        """
        # Check if username already exists
        if self.get_user_by_username(username):
            logger.warning(f"Username '{username}' already exists")
            return None

        user = User.create(username, role)
        users = self.load_users()
        users.append(user)

        if self.save_users(users):
            logger.info(f"Created user '{username}' with role '{role.value}'")
            return user
        else:
            logger.error(f"Failed to save user '{username}'")
            return None

    def user_exists(self, username: str) -> bool:
        """
        Check if a user exists.

        Args:
            username: Username to check

        Returns:
            True if user exists, False otherwise
        """
        return self.get_user_by_username(username) is not None
