#!/usr/bin/env python3
"""Test JSON serialization"""

import json

# محاكاة ما يحدث في app.js
args_from_js = ["--id", 5001, "--librarian"]

print(f"Original (from JS): {args_from_js}")
print(f"Original types: {[type(x).__name__ for x in args_from_js]}")

# JSON serialization
body = json.dumps({"command": "delete-book", "args": args_from_js})
print(f"\nJSON Body: {body}")

# JSON deserialization (on server)
received = json.loads(body)
args_after = received["args"]
print(f"\nAfter loads: {args_after}")
types_list = [type(x).__name__ for x in args_after]
print(f"Types after loads: {types_list}")

# هذا هو ما يدخل إلى _convert_positional_args_to_flags
print("\n---> This is what enters _convert_positional_args_to_flags")
