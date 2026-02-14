#!/usr/bin/env python3
"""Fix remaining linting issues."""

# Fix test_args.py - add newline at end of file
with open("test_args.py", "r") as f:
    content = f.read()

if not content.endswith("\n"):
    with open("test_args.py", "w") as f:
        f.write(content + "\n")
    print("✅ Added newline to test_args.py")
else:
    print("✅ test_args.py already has newline")
