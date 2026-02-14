#!/usr/bin/env python3
"""Test the args conversion logic"""


def convert_args(command, args):
    """محاكاة دالة _convert_positional_args_to_flags"""
    command_arg_specs = {
        "register-user": ["--username", "--password", "--role"],
        "add-book": ["--id", "--title", "--author"],
        "update-book": ["--id", "--title", "--author"],
        "delete-book": ["--id"],
        "pick-book": ["--id", "--username"],
        "approve-borrow": ["--id"],
        "return-book": ["--id"],
        "update-status": ["--id", "--status"],
        "list-books": [],
        "list-picked": [],
    }

    if command not in command_arg_specs:
        return args

    # Filter empty strings first
    args = [arg for arg in args if arg and str(arg).strip()]

    print(f"  After filtering: {args}")

    # Check if args already start with a flag
    if args and args[0].startswith("--"):
        print("  ✅ Detected flag format")
        print(f"  Returning as-is: {args}")
        return args

    print("  Positional format")
    return args


# Test cases
test_cases = [
    ("delete-book", ["--id", "4001", "--librarian"]),
    ("delete-book", ["4001", "--librarian"]),
    ("approve-borrow", ["--id", "5001", "--librarian"]),
    ("update-book", ["--id", "6001", "New Title", "New Author", "--librarian"]),
]

for cmd, args in test_cases:
    print(f"\n{'=' * 60}")
    print(f"Command: {cmd}")
    print(f"Input:   {args}")
    result = convert_args(cmd, args)

    # محاكاة الأمر النهائي
    final_cmd = ["python", "main.py", cmd] + result
    print(f"Output:  {result}")
    print(f"Final:   {' '.join(final_cmd)}")
