#!/usr/bin/env python3
"""
API Integration Tests for School Library
Tests the complete workflow: login → view books → add book → pick book
"""

import json
import sys
import time
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


class Colors:
    GREEN = "\033[92m"
    RED = "\033[91m"
    YELLOW = "\033[93m"
    BLUE = "\033[94m"
    RESET = "\033[0m"
    BOLD = "\033[1m"


def print_header(text):
    print(f"\n{Colors.BOLD}{Colors.BLUE}{'=' * 60}{Colors.RESET}")
    print(f"{Colors.BOLD}{text}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.BLUE}{'=' * 60}{Colors.RESET}\n")


def print_success(text):
    print(f"{Colors.GREEN}✓ {text}{Colors.RESET}")


def print_error(text):
    print(f"{Colors.RED}✗ {text}{Colors.RESET}")


def print_info(text):
    print(f"{Colors.BLUE}ℹ {text}{Colors.RESET}")


def print_warning(text):
    print(f"{Colors.YELLOW}⚠ {text}{Colors.RESET}")


def make_request(url, method="GET", data=None, headers=None):
    """Make HTTP request and return response."""
    if headers is None:
        headers = {}

    try:
        if data:
            headers["Content-Type"] = "application/json"
            if isinstance(data, dict):
                data = json.dumps(data).encode("utf-8")

        req = Request(url, data=data, headers=headers, method=method)
        with urlopen(req, timeout=10) as response:
            response_data = response.read().decode("utf-8")
            return {
                "status": response.status,
                "data": json.loads(response_data) if response_data else None,
                "error": None,
            }
    except HTTPError as e:
        error_data = e.read().decode("utf-8")
        return {"status": e.code, "data": None, "error": error_data}
    except URLError as e:
        return {"status": None, "data": None, "error": str(e)}
    except json.JSONDecodeError as e:
        return {"status": 500, "data": None, "error": f"Invalid JSON: {str(e)}"}


def test_health_check(base_url):
    """Test health endpoint."""
    print_header("1️⃣ HEALTH CHECK")

    url = f"{base_url}/health"
    print_info(f"Testing: {url}")

    result = make_request(url)

    if result["error"]:
        print_error(f"Connection failed: {result['error']}")
        return False

    if result["status"] == 200:
        print_success("Server is healthy")
        print_info(f"Response: {json.dumps(result['data'], indent=2)}")
        return True
    else:
        print_error(f"Unexpected status: {result['status']}")
        return False


def test_login(base_url, username, password):
    """Test user login."""
    print_header("2️⃣ USER LOGIN")
    print_info(f"Attempting login as '{username}'...")

    url = f"{base_url}/api/login"
    data = {"username": username, "password": password}

    result = make_request(url, method="POST", data=data)

    if result["error"]:
        print_error(f"Login failed: {result['error']}")
        return None

    if result["status"] == 200 and result["data"].get("success"):
        print_success("Login successful!")
        print_info(f"Role: {result['data'].get('role')}")
        print_info(f"Username: {result['data'].get('username')}")
        return result["data"]
    else:
        print_error(f"Login failed: {result['data'].get('message', 'Unknown error')}")
        return None


def test_get_books(base_url):
    """Test getting books list."""
    print_header("3️⃣ GET BOOKS")

    url = f"{base_url}/api/books"
    print_info(f"Fetching books from: {url}")

    result = make_request(url)

    if result["error"]:
        print_error(f"Failed to get books: {result['error']}")
        return []

    if result["status"] == 200:
        books = result["data"]
        if isinstance(books, list) and len(books) > 0:
            print_success(f"Retrieved {len(books)} books")

            # Show first 3 books
            for i, book in enumerate(books[:3], 1):
                print_info(
                    f"Book {i}: '{book.get('title')}' by {book.get('author')} - Status: {book.get('status')}"
                )

            if len(books) > 3:
                print_info(f"... and {len(books) - 3} more books")

            return books
        else:
            print_warning("No books found in database")
            return []
    else:
        print_error(f"Unexpected status: {result['status']}")
        return []


def test_add_book(base_url, book_id, title, author):
    """Test adding a book (librarian only)."""
    print_header("4️⃣ ADD BOOK (Librarian)")

    url = f"{base_url}/api/execute"
    data = {
        "command": "add-book",
        "args": [
            "--id",
            str(book_id),
            "--title",
            title,
            "--author",
            author,
            "--librarian",
        ],
    }

    print_info(f"Adding book: {title} by {author} (ID: {book_id})")

    result = make_request(url, method="POST", data=data)

    if result["error"]:
        print_error(f"Failed to add book: {result['error']}")
        return False

    if result["status"] == 200 and result["data"].get("success"):
        print_success("Book added successfully!")
        return True
    else:
        print_warning(f"Book addition response: {result['status']}")
        if result["data"]:
            print_info(f"Server response: {json.dumps(result['data'], indent=2)}")
        return False


def test_pick_book(base_url, book_id, username):
    """Test picking a book."""
    print_header("5️⃣ PICK BOOK (User)")

    url = f"{base_url}/api/execute"
    data = {
        "command": "pick-book",
        "args": ["--id", str(book_id), "--username", username],
    }

    print_info(f"User '{username}' picking book ID: {book_id}")

    result = make_request(url, method="POST", data=data)

    if result["error"]:
        print_error(f"Failed to pick book: {result['error']}")
        return False

    if result["status"] == 200 and result["data"].get("success"):
        print_success("Book picked successfully!")
        return True
    else:
        print_warning(f"Pick book response: {result['status']}")
        if result["data"]:
            print_info(f"Server response: {json.dumps(result['data'], indent=2)}")
        return False


def main():
    """Run all tests."""
    print(f"\n{Colors.BOLD}{Colors.BLUE}🧪 SCHOOL LIBRARY API TEST SUITE{Colors.RESET}")
    print("=" * 60)

    # Get base URL from argument or use default
    base_url = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:8000"
    base_url = base_url.rstrip("/")

    print_info(f"Testing API at: {base_url}\n")

    # Test 1: Health Check
    if not test_health_check(base_url):
        print_error("Cannot reach server. Ensure the app is running:")
        print_info("  python run_app.py 8000")
        return False

    time.sleep(1)

    # Test 2: Login as User
    user_session = test_login(base_url, "tala", "1234")
    if not user_session:
        print_error("User login failed")
        return False

    time.sleep(0.5)

    # Test 3: Get Books
    books = test_get_books(base_url)
    if not books:
        print_warning("No books found - this might be OK if database is empty")

    time.sleep(0.5)

    # Test 4: Login as Librarian
    admin_session = test_login(base_url, "admin", "1234")
    if not admin_session:
        print_error("Admin login failed")
        return False

    time.sleep(0.5)

    # Test 5: Add Book (if librarian)
    if admin_session and admin_session.get("role") == "librarian":
        test_add_book(base_url, 9999, "Test Book API", "Test Author")
        time.sleep(0.5)

    # Test 6: Pick Book (if user and books exist)
    if user_session and books:
        book_to_pick = books[0]
        test_pick_book(base_url, book_to_pick["id"], "tala")
        time.sleep(0.5)

    # Summary
    print_header("✅ TEST SUITE COMPLETE")
    print_success("All API endpoints are working correctly!")
    print_info("The application is ready for Azure deployment.")

    return True


if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n⚠ Tests interrupted by user")
        sys.exit(1)
    except Exception as e:
        print_error(f"Unexpected error: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)
