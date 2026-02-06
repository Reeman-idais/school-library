"""CLI package for the Library Management System."""

from .commands import (
    handle_add_book,
    handle_approve_borrow,
    handle_delete_book,
    handle_list_books,
    handle_list_picked,
    handle_pick_book,
    handle_register_user,
    handle_return_book,
    handle_update_book,
    handle_update_status,
)

__all__ = [
    "handle_add_book",
    "handle_delete_book",
    "handle_update_book",
    "handle_update_status",
    "handle_list_books",
    "handle_pick_book",
    "handle_list_picked",
    "handle_approve_borrow",
    "handle_return_book",
    "handle_register_user",
]
