"""
واجهة المستخدم الجديدة - خادم الويب
New User Interface - Web Server

يوسّع الخادم الأصلي ليدعم مسار /app بدون تعديل server.py
Extends the original server to support /app route without modifying server.py
"""

import os
import sys
from pathlib import Path

from dotenv import load_dotenv

# إضافة المجلد الأب للمسار
PROJECT_ROOT = Path(__file__).parent.parent

# Load environment variables from .env file
env_file = PROJECT_ROOT / ".env"
if env_file.exists():
    load_dotenv(env_file)

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from web.server import LibraryWebHandler  # noqa: E402


class AppWebHandler(LibraryWebHandler):
    """معالج موسّع يدعم واجهة المستخدم الجديدة في /app"""

    def do_GET(self):
        from urllib.parse import urlparse

        parsed = urlparse(self.path)
        path = parsed.path.rstrip("/") or "/"

        # مسارات تطبيق الواجهة الجديدة
        app_routes = {
            "/app": "web/app/index.html",
            "/app/index.html": "web/app/index.html",
            "/app/app.css": "web/app/app.css",
            "/app/app.js": "web/app/app.js",
        }

        if path in app_routes:
            self.serve_file(app_routes[path])
            return

        # نقطة فحص الصحة (لـ Docker و Azure)
        if path == "/health":
            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self.end_headers()
            self.wfile.write(b'{"status":"ok"}')
            return

        super().do_GET()


def run_server(port=8000):
    """تشغيل الخادم مع دعم واجهة المستخدم الجديدة"""
    import http.server
    from pathlib import Path
    import subprocess

    # Initialize database with test data
    init_script = Path(__file__).parent.parent / "scripts" / "init_db.py"
    if init_script.exists():
        try:
            print("\nInitializing database...")
            result = subprocess.run(
                [sys.executable, str(init_script)],
                capture_output=True,
                text=True,
                timeout=30,
            )
            if result.stdout:
                print(result.stdout)
            if result.returncode != 0 and result.stderr:
                print(f"Warning: {result.stderr}")
        except Exception as e:
            print(f"Warning: Could not initialize database: {e}")

    server_address = ("", port)
    httpd = http.server.HTTPServer(server_address, AppWebHandler)

    print("\nLibrary Management System - Web Interface")
    print(f"Server running at http://localhost:{port}/")
    print(f"  - New User App:    http://localhost:{port}/app")
    print(f"  - Documentation:   http://localhost:{port}/docs.html")
    print(f"  - Logs Dashboard:  http://localhost:{port}/logs.html")
    print(f"  - API Docs:        http://localhost:{port}/api-docs")
    print("\nPress Ctrl+C to stop")

    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down...")
        httpd.server_close()


if __name__ == "__main__":
    port = int(os.environ.get("PORT", sys.argv[1] if len(sys.argv) > 1 else 8000))
    run_server(port)
