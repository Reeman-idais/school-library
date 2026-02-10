"""Check which storage backend the app will use (loads .env)."""

import os
import sys

from dotenv import load_dotenv


def main():
    # Ensure project root is on sys.path when run as a script
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    load_dotenv()

    from core.factory import ServiceFactory

    s = ServiceFactory().create_book_service().storage
    print("Storage class:", s.__class__.__module__ + "." + s.__class__.__name__)


if __name__ == "__main__":
    main()
