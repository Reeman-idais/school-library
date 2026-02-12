"""HTTP server for serving HTML pages and API endpoints."""

import http.server
import json
import os
import re
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path
from urllib.parse import urlparse

from dotenv import load_dotenv

from lib_logging.logger import get_logger

# Load environment variables from .env file
_root = Path(__file__).resolve().parent.parent
_env_file = _root / ".env"
if _env_file.exists():
    load_dotenv(_env_file)

try:
    from prometheus_client import (
        CONTENT_TYPE_LATEST,
        REGISTRY,
        Counter,
        Histogram,
        generate_latest,
    )

    PROMETHEUS_AVAILABLE = True
except ImportError:
    PROMETHEUS_AVAILABLE = False

# Application metrics for Prometheus (errors, request count, latency)
if PROMETHEUS_AVAILABLE:
    HTTP_REQUESTS_TOTAL = Counter(
        "library_http_requests_total",
        "Total HTTP requests",
        ["method", "path", "status"],
    )
    HTTP_REQUEST_DURATION = Histogram(
        "library_http_request_duration_seconds",
        "HTTP request latency in seconds",
        ["method", "path"],
        buckets=(0.01, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0),
    )
    APPLICATION_ERRORS_TOTAL = Counter(
        "library_application_errors_total",
        "Total application errors",
    )

# Logger
logger = get_logger(__name__)


class LibraryWebHandler(http.server.BaseHTTPRequestHandler):
    """HTTP request handler for library web interface."""

    # Allowed commands for security
    ALLOWED_COMMANDS = {
        "add-book",
        "delete-book",
        "update-book",
        "update-status",
        "list-books",
        "pick-book",
        "list-picked",
        "approve-borrow",
        "return-book",
        "register-user",
    }

    # Project root directory
    PROJECT_ROOT = Path(__file__).parent.parent

    def handle(self):
        """Wrap request to record Prometheus metrics (latency, count, status)."""
        start = time.perf_counter()
        status = 500  # default if something breaks
        method = ""
        path = ""
        try:
            # Let the base class parse the request first (it sets `self.path` and `self.command`).
            super().handle()
            method = getattr(self, "command", "")
            path = urlparse(getattr(self, "path", "")).path
            status = getattr(self, "_status_code", 200)
        except Exception:
            if PROMETHEUS_AVAILABLE:
                APPLICATION_ERRORS_TOTAL.labels(component="web").inc()
            raise
        finally:
            if PROMETHEUS_AVAILABLE:
                HTTP_REQUESTS_TOTAL.labels(
                    method=method, path=path, status=str(status)
                ).inc()
                HTTP_REQUEST_DURATION.labels(method=method, path=path).observe(
                    time.perf_counter() - start
                )

    def send_response(self, code, message=None):
        self._status_code = code
        super().send_response(code, message)

    def _normalize_api_path(self, path):
        """Support API versioning: /v1/api/* and /api/* map to same handlers."""
        if path.startswith("/v1/api/"):
            return "/api/" + path[len("/v1/api/") :]
        return path

    def do_GET(self):
        """Handle GET requests."""
        parsed_path = urlparse(self.path)
        path = parsed_path.path
        api_path = self._normalize_api_path(path)

        # Route handling
        if path == "/" or path == "/index.html":
            self.serve_file("web/app/index.html")
        elif path == "/docs.html":
            self.serve_file("web/docs.html")
        elif path == "/logs.html":
            self.serve_file("web/logs.html")
        elif path == "/api-docs" or path == "/api-docs/":
            self.serve_file("web/swagger.html")
        elif path.startswith("/app/"):
            # Serve static files from web/app/ directory
            self.serve_file("web" + path)
        elif api_path == "/api/logs":
            self.serve_logs_api()
        elif api_path == "/api/books":
            self.serve_books_api()
        elif api_path == "/api/openapi.yaml":
            self.serve_openapi()
        elif path == "/metrics":
            self.serve_metrics()
        else:
            self.send_error(404, "File not found")

    def do_POST(self):
        """Handle POST requests."""
        parsed_path = urlparse(self.path)
        path = parsed_path.path
        api_path = self._normalize_api_path(path)

        if api_path == "/api/execute":
            self.handle_execute_api()
        else:
            self.send_error(404, "Endpoint not found")

    def serve_file(self, file_path):
        """Serve a static file."""
        try:
            file_full_path = self.PROJECT_ROOT / file_path
            if not file_full_path.exists():
                self.send_error(404, "File not found")
                return

            # Determine content type
            if file_path.endswith(".html"):
                content_type = "text/html"
            elif file_path.endswith(".css"):
                content_type = "text/css"
            elif file_path.endswith(".js"):
                content_type = "application/javascript"
            else:
                content_type = "text/plain"

            with open(file_full_path, "rb") as f:
                content = f.read()

            self.send_response(200)
            self.send_header("Content-type", content_type)
            self.send_header("Access-Control-Allow-Origin", "*")
            self.send_header("Content-length", str(len(content)))
            self.end_headers()
            self.wfile.write(content)
        except Exception as e:
            self.send_error(500, f"Error serving file: {str(e)}")

    def serve_metrics(self):
        """Serve Prometheus metrics."""
        if not PROMETHEUS_AVAILABLE:
            self.send_error(501, "Prometheus client not installed")
            return
        self.send_response(200)
        self.send_header("Content-Type", CONTENT_TYPE_LATEST)
        self.end_headers()
        self.wfile.write(generate_latest(REGISTRY))

    def serve_openapi(self):
        """Serve OpenAPI 3 spec (YAML) for Swagger UI."""
        try:
            spec_path = self.PROJECT_ROOT / "web" / "openapi.yaml"
            if not spec_path.exists():
                self.send_error(404, "OpenAPI spec not found")
                return
            with open(spec_path, "r", encoding="utf-8") as f:
                content = f.read()
            self.send_response(200)
            self.send_header("Content-Type", "application/x-yaml")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.send_header("Content-Length", str(len(content.encode("utf-8"))))
            self.end_headers()
            self.wfile.write(content.encode("utf-8"))
        except Exception as e:
            self.send_error(500, str(e))

    def serve_logs_api(self):
        """Serve log data as JSON."""
        try:
            log_dir = Path(__file__).parent.parent
            log_file = Path(os.environ.get("LOG_DIR", "logs")) / "library.log"
            if not log_file.is_absolute():
                log_file = log_dir / log_file

            if not log_file.exists():
                self.send_json_response([])
                return

            logs = self.parse_log_file(log_file)
            self.send_json_response(logs)
        except Exception as e:
            self.send_error(500, f"Error reading logs: {str(e)}")

    def parse_log_file(self, log_file_path):
        """
        Parse log file and return structured data.
        Supports: (1) NDJSON from structured logger (2) legacy text format.
        """
        logs = []
        legacy_pattern = re.compile(
            r"^(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}) - ([^-]+) - (INFO|WARNING|ERROR) - (.+)$"
        )

        try:
            with open(log_file_path, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue

                    # Try NDJSON (structured logging) first
                    try:
                        obj = json.loads(line)
                        ts = obj.get("timestamp", "")
                        logs.append(
                            {
                                "timestamp": ts,
                                "datetime": ts,
                                "logger": obj.get("logger", "unknown"),
                                "level": obj.get("level", "INFO"),
                                "message": obj.get("message", line),
                            }
                        )
                        continue
                    except json.JSONDecodeError:
                        pass

                    # Legacy format: YYYY-MM-DD HH:MM:SS - logger_name - LEVEL - message
                    match = legacy_pattern.match(line)
                    if match:
                        timestamp_str, logger_name, level, message = match.groups()
                        try:
                            ts_dt = datetime.strptime(
                                timestamp_str, "%Y-%m-%d %H:%M:%S"
                            )
                            datetime_iso = ts_dt.isoformat()
                        except ValueError:
                            datetime_iso = None
                        logs.append(
                            {
                                "timestamp": timestamp_str,
                                "datetime": datetime_iso,
                                "logger": logger_name.strip(),
                                "level": level,
                                "message": message,
                            }
                        )
                    else:
                        logs.append(
                            {
                                "timestamp": "",
                                "datetime": None,
                                "logger": "unknown",
                                "level": "INFO",
                                "message": line,
                            }
                        )
        except Exception as e:
            logs.append(
                {
                    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "datetime": datetime.now().isoformat(),
                    "logger": "server",
                    "level": "ERROR",
                    "message": f"Error parsing log file: {str(e)}",
                }
            )

        return logs

    def serve_books_api(self):
        """Serve list of all books from database as JSON."""
        try:
            from core.factory import ServiceFactory

            # Create service factory and get book service
            factory = ServiceFactory()
            book_service = factory.create_book_service()

            # Log storage backend
            storage_name = getattr(book_service, "storage", None)
            logger.info(
                f"Using storage backend: {storage_name.__class__.__name__ if storage_name else 'unknown'}"
            )

            # Get all books
            books = book_service.list_all_books()

            # Use the model's `to_dict()` (robust and forward-compatible)
            books_data = [book.to_dict() for book in books]

            self.send_json_response(books_data)
        except Exception as e:
            logger.error(f"Error serving books API: {e}")
            self.send_error(500, f"Error retrieving books: {str(e)}")

    def _convert_positional_args_to_flags(self, command, args):
        """
        Convert positional arguments to flag-based arguments for CLI commands.

        Maps commands that use --flag format to their expected arguments.
        Supports both positional args and inline flags (e.g., "--librarian").

        Args:
            command: Command name (e.g., 'register-user')
            args: List of positional arguments or mixed args/flags

        Returns:
            Converted list of flag-based arguments
        """
        # Define command argument mappings (position -> flag name)
        # Only include required positional args; flags like --librarian are passed through
        command_arg_specs = {
            "register-user": ["--username", "--password", "--role"],
            "add-book": ["--id", "--title", "--author"],
            "update-book": ["--id", "--title", "--author"],
            "delete-book": ["--id"],
            "pick-book": ["--book-id"],
            "approve-borrow": ["--book-id"],
            "return-book": ["--book-id"],
            "update-status": ["--id", "--status"],
            "list-books": [],
            "list-picked": [],
        }

        if command not in command_arg_specs:
            # If command not in mapping, pass args as-is
            return args

        # Separate positional args from flag args
        positional_args = []
        flag_args = []

        for arg in args:
            if arg.startswith("--"):
                flag_args.append(arg)
            else:
                positional_args.append(arg)

        # Convert positional args to flags
        required_flags = command_arg_specs[command]
        converted = []

        for i, arg in enumerate(positional_args):
            if i < len(required_flags):
                converted.append(required_flags[i])
                converted.append(arg)

        # Append any flag arguments (e.g., --librarian, --username=value)
        converted.extend(flag_args)

        return converted

    def handle_execute_api(self):
        """Handle command execution API (public endpoint)."""
        try:
            # Read request body
            content_length = int(self.headers.get("Content-Length", 0))
            if content_length == 0:
                self.send_error(400, "Empty request body")
                return

            body = self.rfile.read(content_length)
            data = json.loads(body.decode("utf-8"))

            command = data.get("command")
            args = data.get("args", [])

            # Validate command
            if command not in self.ALLOWED_COMMANDS:
                self.send_json_response(
                    {
                        "success": False,
                        "error": f'Command "{command}" is not allowed',
                        "stdout": "",
                        "stderr": "",
                        "exit_code": 1,
                    },
                    status=400,
                )
                return

            # Validate args (basic security check)
            if not isinstance(args, list):
                self.send_json_response(
                    {
                        "success": False,
                        "error": "Args must be a list",
                        "stdout": "",
                        "stderr": "",
                        "exit_code": 1,
                    },
                    status=400,
                )
                return

            # Execute command
            result = self.execute_command(command, args)
            self.send_json_response(result)

        except json.JSONDecodeError:
            self.send_error(400, "Invalid JSON in request body")
        except Exception as e:
            self.send_json_response(
                {
                    "success": False,
                    "error": str(e),
                    "stdout": "",
                    "stderr": "",
                    "exit_code": 1,
                },
                status=500,
            )

    def execute_command(self, command, args):
        """
        Execute a CLI command safely.

        Args:
            command: Command name (e.g., 'add-book')
            args: List of arguments (positional or will be converted to flags)

        Returns:
            Dictionary with execution results
        """
        try:
            # Convert positional args to flag-based args for commands that require it
            converted_args = self._convert_positional_args_to_flags(command, args)

            # Build command: python main.py <command> <converted_args>
            main_py = self.PROJECT_ROOT / "main.py"
            cmd = [sys.executable, str(main_py), command] + converted_args

            # Copy current environment (already has .env loaded at startup)
            env = os.environ.copy()

            # Execute with timeout
            process = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=5,
                cwd=str(self.PROJECT_ROOT),
                env=env,
            )

            # Sanitize output for HTML
            stdout = self.sanitize_output(process.stdout)
            stderr = self.sanitize_output(process.stderr)

            return {
                "success": process.returncode == 0,
                "stdout": stdout,
                "stderr": stderr,
                "exit_code": process.returncode,
            }
        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "stdout": "",
                "stderr": "Command execution timed out (5 seconds)",
                "exit_code": 1,
            }
        except Exception as e:
            return {
                "success": False,
                "stdout": "",
                "stderr": f"Error executing command: {str(e)}",
                "exit_code": 1,
            }

    def sanitize_output(self, text):
        """Sanitize output for safe HTML display."""
        if not text:
            return ""

        # Escape HTML special characters
        text = text.replace("&", "&amp;")
        text = text.replace("<", "&lt;")
        text = text.replace(">", "&gt;")
        text = text.replace('"', "&quot;")
        text = text.replace("'", "&#x27;")

        return text

    def send_json_response(self, data, status=200):
        """Send JSON response."""
        json_data = json.dumps(data, indent=2)

        self.send_response(status)
        self.send_header("Content-type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Content-length", str(len(json_data.encode("utf-8"))))
        self.end_headers()
        self.wfile.write(json_data.encode("utf-8"))

    def log_message(self, format, *args):
        """Override to reduce server logging noise."""
        # Only log errors
        if "error" in format.lower() or args[1].startswith("5"):
            super().log_message(format, *args)


def run_server(port=8000):
    """Run the HTTP server."""
    server_address = ("", port)
    httpd = http.server.HTTPServer(server_address, LibraryWebHandler)

    print("Library Management System Web Interface")
    print(f"Server running at http://localhost:{port}/")
    print(f"  - Documentation: http://localhost:{port}/docs.html")
    print(f"  - Logs Dashboard: http://localhost:{port}/logs.html")
    print(f"  - API Docs (Swagger): http://localhost:{port}/api-docs")
    print(f"  - OpenAPI spec: http://localhost:{port}/api/openapi.yaml")
    print("\nPress Ctrl+C to stop the server")

    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down server...")
        httpd.server_close()


if __name__ == "__main__":
    port = int(os.environ.get("PORT", sys.argv[1] if len(sys.argv) > 1 else 8000))
    run_server(port)
