"""CLI command handlers with role-based access control."""

from typing import Optional, Tuple

from lib_logging.logger import get_logger
from models.book import BookStatus
from models.role import Role
from services.book_service import BookService
from services.user_service import UserService
from core.factory import ServiceFactory

logger = get_logger(__name__)


def _resolve_book_service(book_service: Optional[BookService]) -> BookService:
    """Resolve BookService (injected or default). Enables DI and backward-compat tests."""
    if book_service is not None:
        return book_service
    # Use ServiceFactory so the service is constructed with a proper storage
    return ServiceFactory().create_book_service()


def _resolve_user_service(user_service: Optional[UserService]) -> UserService:
    """Resolve UserService (injected or default)."""
    if user_service is not None:
        return user_service
    return ServiceFactory().create_user_service()


def _check_role_permission(required_role: Role, provided_role: Optional[Role]) -> bool:
    """
    Check if provided role has permission for an operation.

    Args:
        required_role: Required role for the operation
        provided_role: Role provided by user

    Returns:
        True if permission granted, False otherwise
    """
    return provided_role == required_role


def _get_role_from_login(
    is_librarian: bool, username: Optional[str] = None
) -> Tuple[Optional[Role], Optional[str]]:
    """
    Detect role from login method.
    - If is_librarian=True → librarian (no username needed)
    - If username provided → user (username identifies the user)

    Args:
        is_librarian: True if logging in as librarian
        username: Username for user login (required if not librarian)

    Returns:
        Tuple of (role, error_message)
    """
    if is_librarian:
        return Role.LIBRARIAN, None

    # For users, username is required to identify them
    if not username:
        return None, "Username is required for user login. Use --username <username>"

    username = username.strip()
    if not username:
        return None, "Username cannot be empty"

    return Role.USER, None


def _parse_book_id(book_id_str: str) -> Tuple[Optional[int], Optional[str]]:
    """
    Parse book ID string to integer.

    Args:
        book_id_str: Book ID as string

    Returns:
        Tuple of (book_id, error_message)
    """
    try:
        book_id = int(book_id_str)
        if book_id <= 0:
            return None, f"Book ID must be a positive integer, got: {book_id_str}"
        return book_id, None
    except ValueError:
        return None, f"Invalid book ID format: {book_id_str}. Must be an integer."


def handle_add_book(
    book_id_str: str,
    title: str,
    author: str,
    is_librarian: bool = False,
    username: Optional[str] = None,
    book_service: Optional[BookService] = None,
) -> int:
    """
    Handle add-book command (librarian only).

    Args:
        book_id_str: Book ID (integer as string)
        title: Book title
        author: Book author
        is_librarian: True if logging in as librarian
        username: Username (not used for librarian, required for users but users can't add books)

    Returns:
        Exit code (0 for success, 1 for failure)
    """
    # Parse book ID
    book_id, error_msg = _parse_book_id(book_id_str)
    if error_msg:
        print(f"ERROR: {error_msg}")
        return 1

    assert book_id is not None, "book_id should not be None after validation"
    # Check role
    user_role, error_msg = _get_role_from_login(is_librarian, username)
    if error_msg:
        print(f"ERROR: {error_msg}")
        return 1

    assert user_role is not None, "user_role should not be None after validation"
    if not _check_role_permission(Role.LIBRARIAN, user_role):
        print(f"ERROR: Only librarians can add books. Your role: {user_role.value}")
        return 1

    # Add book
    svc = _resolve_book_service(book_service)
    book, error_msg = svc.add_book(book_id, title, author)

    if error_msg:
        print(f"ERROR: {error_msg}")
        return 1

    assert book is not None, "book should not be None after successful add"
    print(f"SUCCESS: Added book '{book.title}' by {book.author} (ID: {book.id})")
    return 0
    isbn_display = f" (ISBN: {book.isbn})" if book.isbn else ""
    print(
        f"SUCCESS: Added book '{book.title}' by {book.author} (ID: {book.id}){isbn_display}"
    )
    return 0


def handle_delete_book(
    book_id: str,
    is_librarian: bool = False,
    username: Optional[str] = None,
    book_service: Optional[BookService] = None,
) -> int:
    """
    Handle delete-book command (librarian only).

    Args:
        book_id: Book ID (integer)
        is_librarian: True if logging in as librarian
        username: Username (not used for librarian)

    Returns:
        Exit code (0 for success, 1 for failure)
    """
    # Check role
    user_role, error_msg = _get_role_from_login(is_librarian, username)
    if error_msg:
        print(f"ERROR: {error_msg}")
        return 1

    assert user_role is not None, "user_role should not be None after validation"
    if not _check_role_permission(Role.LIBRARIAN, user_role):
        print(f"ERROR: Only librarians can delete books. Your role: {user_role.value}")
        return 1

    book_id_int, error_msg = _parse_book_id(book_id)
    if error_msg:
        print(f"ERROR: {error_msg}")
        return 1

    assert book_id_int is not None, "book_id_int should not be None after validation"
    svc = _resolve_book_service(book_service)
    success, error_msg = svc.delete_book(book_id_int)

    if not success:
        print(f"ERROR: {error_msg}")
        return 1

    print(f"SUCCESS: Deleted book (ID: {book_id})")
    return 0


def handle_update_book(
    book_id: str,
    is_librarian: bool = False,
    username: Optional[str] = None,
    title: Optional[str] = None,
    author: Optional[str] = None,
    book_service: Optional[BookService] = None,
) -> int:
    """
    Handle update-book command (librarian only).

    Args:
        book_id: Book ID (integer)
        is_librarian: True if logging in as librarian
        username: Username (not used for librarian)
        title: New title (optional)
        author: New author (optional)

    Returns:
        Exit code (0 for success, 1 for failure)
    """
    # Check role
    user_role, error_msg = _get_role_from_login(is_librarian, username)
    if error_msg:
        print(f"ERROR: {error_msg}")
        return 1

    assert user_role is not None, "user_role should not be None after validation"
    if not _check_role_permission(Role.LIBRARIAN, user_role):
        print(f"ERROR: Only librarians can update books. Your role: {user_role.value}")
        return 1

    # Check if at least one field is provided
    if not any([title, author]):
        print("ERROR: At least one field (--title or --author) must be provided")
        return 1

    book_id_int, error_msg = _parse_book_id(book_id)
    if error_msg:
        print(f"ERROR: {error_msg}")
        return 1

    assert book_id_int is not None, "book_id_int should not be None after validation"
    svc = _resolve_book_service(book_service)
    book, error_msg = svc.update_book_info(book_id_int, title=title, author=author)

    if error_msg:
        print(f"ERROR: {error_msg}")
        return 1

    assert book is not None, "book should not be None after successful update"
    print(f"SUCCESS: Updated book '{book.title}' (ID: {book_id})")
    return 0


def handle_update_status(
    book_id: str,
    status: str,
    is_librarian: bool = False,
    username: Optional[str] = None,
    book_service: Optional[BookService] = None,
) -> int:
    """
    Handle update-status command (librarian only).

    Args:
        book_id: Book ID (integer)
        status: New status (Available, Picked, or Borrowed)
        is_librarian: True if logging in as librarian
        username: Username (not used for librarian)

    Returns:
        Exit code (0 for success, 1 for failure)
    """
    # Check role
    user_role, error_msg = _get_role_from_login(is_librarian, username)
    if error_msg:
        print(f"ERROR: {error_msg}")
        return 1

    assert user_role is not None, "user_role should not be None after validation"
    if not _check_role_permission(Role.LIBRARIAN, user_role):
        print(
            f"ERROR: Only librarians can update book status. Your role: {user_role.value}"
        )
        return 1

    # Parse book ID
    book_id_int, error_msg = _parse_book_id(book_id)
    if error_msg:
        print(f"ERROR: {error_msg}")
        return 1

    assert book_id_int is not None, "book_id_int should not be None after validation"
    # Parse status
    try:
        book_status = BookStatus(status)
    except ValueError:
        valid_statuses = [s.value for s in BookStatus]
        print(
            f"ERROR: Invalid status '{status}'. Valid statuses: {', '.join(valid_statuses)}"
        )
        return 1

    # Update status
    svc = _resolve_book_service(book_service)
    book, error_msg = svc.update_book_status(book_id_int, book_status)

    if error_msg:
        print(f"ERROR: {error_msg}")
        return 1

    assert book is not None, "book should not be None after successful update"
    print(f"SUCCESS: Updated book '{book.title}' (ID: {book_id}) status to {status}")
    return 0


def handle_list_books(
    is_librarian: bool = False,
    username: Optional[str] = None,
    book_service: Optional[BookService] = None,
) -> int:
    """
    Handle list-books command (user and librarian can view).

    Args:
        is_librarian: True if logging in as librarian
        username: Username for user login (required if not librarian)

    Returns:
        Exit code (0 for success, 1 for failure)
    """
    # Check role (both librarian and user can list)
    _, error_msg = _get_role_from_login(is_librarian, username)
    if error_msg:
        print(f"ERROR: {error_msg}")
        return 1

    # List all books
    svc = _resolve_book_service(book_service)
    books = svc.list_all_books()

    if not books:
        print("No books found")
        return 0

    print(f"All books ({len(books)}):")
    print(f"{'ID':<6} {'Title':<30} {'Author':<25} {'Status':<12} {'Picked By':<15}")
    print("-" * 90)
    for book in books:
        picked_by = book.picked_by if book.picked_by else "-"
        print(
            f"{book.id:<6} {book.title[:28]:<30} {book.author[:23]:<25} {book.status.value:<12} {picked_by:<15}"
        )

    return 0


def handle_pick_book(
    book_id: str,
    username: str,
    book_service: Optional[BookService] = None,
) -> int:
    """
    Handle pick-book command (user only).

    Args:
        book_id: Book ID (integer)
        username: Username (required to identify the user)

    Returns:
        Exit code (0 for success, 1 for failure)
    """
    # Check role (username is required for this command)
    user_role, error_msg = _get_role_from_login(False, username)
    if error_msg:
        print(f"ERROR: {error_msg}")
        return 1

    assert user_role is not None, "user_role should not be None after validation"
    if not _check_role_permission(Role.USER, user_role):
        print(f"ERROR: Only users can pick books. Your role: {user_role.value}")
        return 1

    # Parse book ID
    book_id_int, error_msg = _parse_book_id(book_id)
    if error_msg:
        print(f"ERROR: {error_msg}")
        return 1

    assert book_id_int is not None, "book_id_int should not be None after validation"
    # Pick book
    svc = _resolve_book_service(book_service)
    book, error_msg = svc.pick_book(book_id_int, username)

    if error_msg:
        print(f"ERROR: {error_msg}")
        return 1

    assert book is not None, "book should not be None after successful pick"
    print(
        f"SUCCESS: User '{username}' picked book '{book.title}' (ID: {book_id}). Waiting for librarian approval."
    )
    return 0


def handle_list_picked(
    is_librarian: bool = False,
    username: Optional[str] = None,
    book_service: Optional[BookService] = None,
) -> int:
    """
    Handle list-picked command (librarian only).

    Args:
        is_librarian: True if logging in as librarian
        username: Username (not used for librarian)

    Returns:
        Exit code (0 for success, 1 for failure)
    """
    # Check role
    user_role, error_msg = _get_role_from_login(is_librarian, username)
    if error_msg:
        print(f"ERROR: {error_msg}")
        return 1

    assert user_role is not None, "user_role should not be None after validation"
    if not _check_role_permission(Role.LIBRARIAN, user_role):
        print(
            f"ERROR: Only librarians can view picked books. Your role: {user_role.value}"
        )
        return 1

    # List picked books
    svc = _resolve_book_service(book_service)
    picked_books = svc.list_picked_books()

    if not picked_books:
        print("No picked books found")
        return 0

    print(f"Picked books ({len(picked_books)}):")
    print(f"{'ID':<6} {'Title':<30} {'Author':<25} {'Picked By':<15}")
    print("-" * 80)
    for book in picked_books:
        picked_by = book.picked_by if book.picked_by else "-"
        print(
            f"{book.id:<6} {book.title[:28]:<30} {book.author[:23]:<25} {picked_by:<15}"
        )

    return 0


def handle_approve_borrow(
    book_id: str,
    is_librarian: bool = False,
    username: Optional[str] = None,
    book_service: Optional[BookService] = None,
) -> int:
    """
    Handle approve-borrow command (librarian only).

    Args:
        book_id: Book ID (integer)
        is_librarian: True if logging in as librarian
        username: Username (not used for librarian)

    Returns:
        Exit code (0 for success, 1 for failure)
    """
    # Check role
    user_role, error_msg = _get_role_from_login(is_librarian, username)
    if error_msg:
        print(f"ERROR: {error_msg}")
        return 1

    assert user_role is not None, "user_role should not be None after validation"
    if not _check_role_permission(Role.LIBRARIAN, user_role):
        print(
            f"ERROR: Only librarians can approve borrows. Your role: {user_role.value}"
        )
        return 1

    book_id_int, error_msg = _parse_book_id(book_id)
    if error_msg:
        print(f"ERROR: {error_msg}")
        return 1

    assert book_id_int is not None, "book_id_int should not be None after validation"
    svc = _resolve_book_service(book_service)
    book, error_msg = svc.approve_borrow(book_id_int)

    if error_msg:
        print(f"ERROR: {error_msg}")
        return 1

    assert book is not None, "book should not be None after successful approve"
    print(
        f"SUCCESS: Approved borrow for book '{book.title}' (ID: {book_id}) by '{book.picked_by}'"
    )
    return 0


def handle_return_book(
    book_id: str,
    is_librarian: bool = False,
    username: Optional[str] = None,
    book_service: Optional[BookService] = None,
) -> int:
    """
    Handle return-book command (librarian only).

    Args:
        book_id: Book ID (integer)
        is_librarian: True if logging in as librarian
        username: Username (not used for librarian)

    Returns:
        Exit code (0 for success, 1 for failure)
    """
    # Check role
    user_role, error_msg = _get_role_from_login(is_librarian, username)
    if error_msg:
        print(f"ERROR: {error_msg}")
        return 1

    assert user_role is not None, "user_role should not be None after validation"
    if not _check_role_permission(Role.LIBRARIAN, user_role):
        print(f"ERROR: Only librarians can return books. Your role: {user_role.value}")
        return 1

    book_id_int, error_msg = _parse_book_id(book_id)
    if error_msg:
        print(f"ERROR: {error_msg}")
        return 1

    assert book_id_int is not None, "book_id_int should not be None after validation"
    svc = _resolve_book_service(book_service)
    book, error_msg = svc.return_book(book_id_int)

    if error_msg:
        print(f"ERROR: {error_msg}")
        return 1

    assert book is not None, "book should not be None after successful return"
    print(f"SUCCESS: Returned book '{book.title}' (ID: {book_id}) to Available status")
    return 0


def handle_register_user(
    username: str,
    password: str,
    role_string: str,
    user_service: Optional[UserService] = None,
) -> int:
    """
    Handle register-user command.

    Args:
        username: Username
        password: User password
        role_string: Role (librarian/user)

    Returns:
        Exit code (0 for success, 1 for failure)
    """
    svc = _resolve_user_service(user_service)
    user, error_msg = svc.register_user(username, password, role_string)

    if error_msg:
        print(f"ERROR: {error_msg}")
        return 1

    assert user is not None, "user should not be None after successful registration"
    print(
        f"SUCCESS: Registered user '{user.username}' with role '{user.role.value}' (ID: {user.id})"
    )
    return 0
