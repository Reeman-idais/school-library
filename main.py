"""CLI entry point for the Library Management System."""

import argparse
import sys

from core.factory import ServiceFactory
from cli.commands import (
    handle_add_book,
    handle_delete_book,
    handle_update_book,
    handle_update_status,
    handle_list_books,
    handle_pick_book,
    handle_list_picked,
    handle_approve_borrow,
    handle_return_book,
    handle_register_user,
)


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Electronic Library Management System v1.0",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # add-book command (librarian only)
    add_book_parser = subparsers.add_parser(
        "add-book", help="Add a new book (librarian only)"
    )
    add_book_parser.add_argument("--title", required=True, help="Book title")
    add_book_parser.add_argument("--author", required=True, help="Book author")
    add_book_parser.add_argument(
        "--librarian", action="store_true", help="Login as librarian"
    )

    # delete-book command (librarian only)
    delete_book_parser = subparsers.add_parser(
        "delete-book", help="Delete a book (librarian only)"
    )
    delete_book_parser.add_argument(
        "--id", required=True, dest="book_id", help="Book ID (integer)"
    )
    delete_book_parser.add_argument(
        "--librarian", action="store_true", help="Login as librarian"
    )

    # update-book command (librarian only)
    update_book_parser = subparsers.add_parser(
        "update-book", help="Update book information (librarian only)"
    )
    update_book_parser.add_argument(
        "--id", required=True, dest="book_id", help="Book ID (integer)"
    )
    update_book_parser.add_argument(
        "--librarian", action="store_true", help="Login as librarian"
    )
    update_book_parser.add_argument("--title", help="New title")
    update_book_parser.add_argument("--author", help="New author")

    # update-status command (librarian only)
    update_status_parser = subparsers.add_parser(
        "update-status", help="Update book status (librarian only)"
    )
    update_status_parser.add_argument(
        "--id", required=True, dest="book_id", help="Book ID (integer)"
    )
    update_status_parser.add_argument(
        "--status",
        required=True,
        choices=["Available", "Picked", "Borrowed"],
        help="New status",
    )
    update_status_parser.add_argument(
        "--librarian", action="store_true", help="Login as librarian"
    )

    # list-books command (librarian and user)
    list_books_parser = subparsers.add_parser(
        "list-books", help="List all books with IDs and status"
    )
    login_group = list_books_parser.add_mutually_exclusive_group(required=True)
    login_group.add_argument(
        "--librarian", action="store_true", help="Login as librarian"
    )
    login_group.add_argument("--username", help="Username for user login")

    # pick-book command (user only)
    pick_book_parser = subparsers.add_parser(
        "pick-book", help="Pick a book for borrowing (user only)"
    )
    pick_book_parser.add_argument(
        "--id", required=True, dest="book_id", help="Book ID (integer)"
    )
    pick_book_parser.add_argument(
        "--username", required=True, help="Username to identify the user"
    )

    # list-picked command (librarian only)
    list_picked_parser = subparsers.add_parser(
        "list-picked", help="List picked books with user names (librarian only)"
    )
    list_picked_parser.add_argument(
        "--librarian", action="store_true", help="Login as librarian"
    )

    # approve-borrow command (librarian only)
    approve_borrow_parser = subparsers.add_parser(
        "approve-borrow",
        help="Approve a picked book and change status to Borrowed (librarian only)",
    )
    approve_borrow_parser.add_argument(
        "--id", required=True, dest="book_id", help="Book ID (integer)"
    )
    approve_borrow_parser.add_argument(
        "--librarian", action="store_true", help="Login as librarian"
    )

    # return-book command (librarian only)
    return_book_parser = subparsers.add_parser(
        "return-book",
        help="Return a borrowed book to Available status (librarian only)",
    )
    return_book_parser.add_argument(
        "--id", required=True, dest="book_id", help="Book ID (integer)"
    )
    return_book_parser.add_argument(
        "--librarian", action="store_true", help="Login as librarian"
    )

    # register-user command (no role restriction)
    register_parser = subparsers.add_parser("register-user", help="Register a new user")
    register_parser.add_argument("--username", required=True, help="Username")
    register_parser.add_argument(
        "--role", required=True, choices=["librarian", "user"], help="User role"
    )

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return 1

    # Dependency injection: create services once via factory (testable, loose coupling)
    service_factory = ServiceFactory()
    book_service = service_factory.create_book_service()
    user_service = service_factory.create_user_service()

    # Route to appropriate handler
    try:
        if args.command == "add-book":
            return handle_add_book(
                args.title, args.author, args.librarian, None, book_service
            )
        elif args.command == "delete-book":
            return handle_delete_book(args.book_id, args.librarian, None, book_service)
        elif args.command == "update-book":
            return handle_update_book(
                args.book_id,
                args.librarian,
                None,
                args.title,
                args.author,
                book_service,
            )
        elif args.command == "update-status":
            return handle_update_status(
                args.book_id, args.status, args.librarian, None, book_service
            )
        elif args.command == "list-books":
            return handle_list_books(args.librarian, args.username, book_service)
        elif args.command == "pick-book":
            return handle_pick_book(args.book_id, args.username, book_service)
        elif args.command == "list-picked":
            return handle_list_picked(args.librarian, None, book_service)
        elif args.command == "approve-borrow":
            return handle_approve_borrow(
                args.book_id, args.librarian, None, book_service
            )
        elif args.command == "return-book":
            return handle_return_book(args.book_id, args.librarian, None, book_service)
        elif args.command == "register-user":
            return handle_register_user(args.username, args.role, user_service)
        else:
            parser.print_help()
            return 1
    except KeyboardInterrupt:
        print("\nOperation cancelled by user")
        return 1
    except Exception as e:
        print(f"ERROR: Unexpected error: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
