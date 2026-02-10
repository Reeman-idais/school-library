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

from web.app_server import run_server  # noqa: E402

if __name__ == "__main__":
    port = int(os.environ.get("PORT", sys.argv[1] if len(sys.argv) > 1 else 8000))
    run_server(port)
