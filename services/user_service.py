"""User service with business logic for user operations."""

from typing import Optional, Tuple

from models.user import User
from models.role import Role
from storage.user_storage import UserStorage
from validation.user_validator import validate_username, validate_role
from lib_logging.logger import get_logger

logger = get_logger(__name__)


class UserService:
    """Service for user-related operations."""

    def __init__(self, storage: UserStorage = None):
        """
        Initialize user service.

        Args:
            storage: UserStorage instance (creates new if not provided)
        """
        self.storage = storage or UserStorage()

    def get_or_create_user(self, username: str, role: Role) -> Tuple[User, bool]:
        """
        Get existing user or create a new one.

        Args:
            username: Username
            role: User role

        Returns:
            Tuple of (user, is_new)
            is_new is True if user was created, False if already existed
        """
        # Validate username
        is_valid, error_msg = validate_username(username, self.storage)
        if not is_valid:
            logger.warning(f"Username validation failed: {error_msg}")
            raise ValueError(error_msg)

        # Check if user exists
        user = self.storage.get_user_by_username(username)
        if user:
            logger.info(f"Retrieved existing user: '{username}'")
            return user, False

        # Create new user
        user = self.storage.create_user(username, role)
        if user:
            logger.info(f"Created new user: '{username}' with role '{role.value}'")
            return user, True
        else:
            error_msg = f"Failed to create user '{username}'"
            logger.error(error_msg)
            raise RuntimeError(error_msg)

    def get_user_role(self, username: str) -> Optional[Role]:
        """
        Get user's role.

        Args:
            username: Username

        Returns:
            Role if user exists, None otherwise
        """
        user = self.storage.get_user_by_username(username)
        if user:
            return user.role
        return None

    def register_user(
        self, username: str, role_string: str
    ) -> Tuple[Optional[User], str]:
        """
        Register a new user.

        Args:
            username: Username
            role_string: Role as string (will be validated)

        Returns:
            Tuple of (user, error_message)
            If successful: (User object, "")
            If failed: (None, error_message)
        """
        # Validate role
        is_valid, error_msg, role = validate_role(role_string)
        if not is_valid:
            logger.warning(f"Role validation failed: {error_msg}")
            return None, error_msg

        # Validate username
        is_valid, error_msg = validate_username(username, self.storage)
        if not is_valid:
            logger.warning(f"Username validation failed: {error_msg}")
            return None, error_msg

        # Create user
        try:
            user, is_new = self.get_or_create_user(username, role)
            if is_new:
                return user, ""
            else:
                return None, f"User '{username}' already exists"
        except (ValueError, RuntimeError) as e:
            return None, str(e)
