#!/usr/bin/env python3
"""Test if integer in subprocess list causes issues"""

import subprocess
import sys

# Test with integer in list
print("Test 1: Integer in subprocess list")
cmd_with_int = [sys.executable, "-c", "import sys; print(sys.argv)", "--id", 5001]
print(f"  cmd: {cmd_with_int}")
print(f"  types: {[type(x).__name__ for x in cmd_with_int]}")

try:
    result = subprocess.run(cmd_with_int, capture_output=True, text=True)
    print(f"  Error/Output: {result.stderr if result.stderr else result.stdout}")
except Exception as e:
    print(f"  Exception: {type(e).__name__}: {e}")

print("\nTest 2: String in subprocess list")
cmd_with_str = [sys.executable, "-c", "import sys; print(sys.argv)", "--id", "5001"]
print(f"  cmd: {cmd_with_str}")
print(f"  types: {[type(x).__name__ for x in cmd_with_str]}")

try:
    result = subprocess.run(cmd_with_str, capture_output=True, text=True)
    print("  Success!")
    print(f"  Output: {result.stdout.strip()}")
except Exception as e:
    print(f"  Exception: {e}")

print("\nTest 3: Check what happens if we have mixed types")
args = ["--id", 5001, "--librarian"]
print(f"  Before str conversion: {args}")

# Try to convert all to strings
args_str = [str(arg) for arg in args]
print(f"  After str conversion: {args_str}")

cmd = [sys.executable, "main.py", "delete-book"] + args_str
print(f"  Final cmd: {cmd}")
