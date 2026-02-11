#!/usr/bin/env python3
"""
تشغيل واجهة المستخدم الجديدة
Run the new user interface

يستخدم الخادم الموسّع الذي يدعم /app
Usage: python run_app.py [port]
       PORT=8000 python run_app.py
"""

import os
import sys
from pathlib import Path

from dotenv import load_dotenv

# Load environment variables from .env file
ROOT = Path(__file__).resolve().parent
env_file = ROOT / ".env"
if env_file.exists():
    load_dotenv(env_file)

if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

# Attempt to import the web app entrypoint and provide an actionable
# diagnostic message if it fails — this helps users who run the wrong
# Python interpreter or have a conflicting/global `web` package.
try:
    from web.app_server import run_server  # noqa: E402
except ModuleNotFoundError:  # provide clear, actionable diagnostics
    import importlib.util
    import sys

    print(
        "ERROR: could not import 'web.app_server' (ModuleNotFoundError).",
        file=sys.stderr,
    )
    print("--- Diagnostic information ---", file=sys.stderr)
    print(f"Python executable: {sys.executable}", file=sys.stderr)
    print("First entries of sys.path:", file=sys.stderr)
    for p in sys.path[:8]:
        print(f"  {p}", file=sys.stderr)
    print("find_spec('web'):", importlib.util.find_spec("web"), file=sys.stderr)
    print(
        "find_spec('web.app_server'):",
        importlib.util.find_spec("web.app_server"),
        file=sys.stderr,
    )
    print("", file=sys.stderr)
    print("Quick fixes:", file=sys.stderr)
    print(
        "  - Activate the project venv and run: .venv\\Scripts\\Activate.ps1  then: python run_app.py",
        file=sys.stderr,
    )
    print(
        "  - Or run directly with the venv interpreter: .venv\\Scripts\\python.exe run_app.py",
        file=sys.stderr,
    )
    print(
        "  - Or ensure the project root is on PYTHONPATH before running.",
        file=sys.stderr,
    )
    raise

if __name__ == "__main__":
    port = int(os.environ.get("PORT", sys.argv[1] if len(sys.argv) > 1 else 8000))
    run_server(port)
