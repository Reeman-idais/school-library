# 📚 Electronic Library Management System

A modern **CLI and web-based library management system** built with Python. Features role-based access control, data persistence, comprehensive testing, and CI/CD automation.

## ✨ Features

### Core Features
- 📖 **Book Management**: Add, update, delete, and list books with status tracking
- 👥 **User Management**: Register users with role-based access (Librarian/User)
- 🔐 **Role-Based Access Control**: Different permissions for librarians and regular users
- 📋 **Borrowing System**: Users can pick books, librarians can approve/return borrowings
- 💾 **Data Persistence**: JSON-based storage with automatic backup

### Technology Stack
- **Language**: Python 3.8+
- **Dependency Manager**: Poetry
- **Testing**: pytest with 44 comprehensive tests (unit + integration)
- **Code Quality**: black, flake8, pylint, mypy
- **Web Interface**: HTTP server with OpenAPI/Swagger documentation
- **CI/CD**: GitHub Actions (multi-platform, multi-Python version)
- **Monitoring**: Prometheus metrics, Logs dashboard, Grafana visualization

---

## 🚀 Quick Start

### Prerequisites
- Python 3.8 or higher
- Poetry (install from [poetry.python-poetry.org](https://python-poetry.org/docs/#installation))

### Installation

**Windows (PowerShell):**
```powershell
# Install dependencies
poetry install

# Run tests
poetry run pytest

# Run the CLI
poetry run python main.py --help
```

**Linux/macOS:**
```bash
# Make scripts executable
chmod +x scripts/*.sh

# Install dependencies
poetry install

# Run tests
poetry run pytest

# Run the CLI
poetry run python main.py --help
```

---

## 📖 Usage

### CLI Commands

#### Book Management (Librarian Only)
```bash
# List all books
poetry run python main.py list-books --librarian

# Add a new book
poetry run python main.py add-book --title "Python 101" --author "John Doe" --librarian

# Update book information
poetry run python main.py update-book --id 1 --title "New Title" --librarian

# Delete a book
poetry run python main.py delete-book --id 1 --librarian

# Update book status
poetry run python main.py update-status --id 1 --status Available --librarian

# List books picked for borrowing (librarian only)
poetry run python main.py list-picked --librarian

# Approve a book for borrowing
poetry run python main.py approve-borrow --id 1 --librarian

# Return a borrowed book
poetry run python main.py return-book --id 1 --librarian
```

#### User Commands
```bash
# Register a new user
poetry run python main.py register-user --username john --role user

# Pick a book for borrowing (user only)
poetry run python main.py pick-book --id 1 --username john
```

### Web Interface

Start the web server:
```bash
poetry run python web/server.py
```

Access the interface at `http://localhost:8000`:
- 📊 **Logs Dashboard**: View and filter system logs with charts
- 📚 **Interactive Documentation**: Learn and test CLI commands
- 🔄 **API Docs**: Swagger UI and OpenAPI specification
- 📈 **Metrics**: Prometheus metrics at `/metrics`

---

## 🧪 Testing

### Run All Tests
```bash
# Run all 44 tests
poetry run pytest

# Run with verbose output
poetry run pytest -v

# Run with coverage report
poetry run pytest --cov=.

# Run specific test file
poetry run pytest tests/test_models.py

# Run tests with pytest markers
poetry run pytest -m unit      # Only unit tests
poetry run pytest -m integration # Only integration tests
```

### Test Structure
```
tests/
├── test_models.py          # Unit tests for Book, User, Role models
├── test_validation.py      # Unit tests for validation logic
├── test_services.py        # Unit tests for service layer
├── test_cli_commands.py    # Unit tests for CLI handlers
├── test_integration.py     # Integration tests with real storage
└── conftest.py            # Pytest fixtures and configuration
```

---

## 🏗️ Project Structure

```
school-library/
├── README.md                    # This file
├── BUILD.md                     # Detailed build & development guide
├── DEMO.md                      # Demo script guide
├── Makefile                     # Build automation
├── pyproject.toml              # Project metadata and dependencies
├── poetry.lock                 # Locked dependencies
│
├── main.py                     # CLI entry point
│
├── cli/                        # Command handlers
│   ├── __init__.py
│   └── commands.py
│
├── core/                       # Core abstractions
│   ├── factory.py             # Service factory pattern
│   ├── repository.py          # Repository pattern (protocols)
│   ├── strategy.py            # Strategy pattern
│   └── __init__.py
│
├── models/                     # Data models
│   ├── book.py                # Book model with status
│   ├── user.py                # User model
│   ├── role.py                # Role enumeration
│   └── __init__.py
│
├── services/                   # Business logic
│   ├── book_service.py        # Book operations
│   ├── user_service.py        # User operations
│   ├── borrow_service.py      # Borrowing logic
│   └── __init__.py
│
├── storage/                    # Data persistence
│   ├── book_storage.py        # Books JSON storage
│   ├── user_storage.py        # Users JSON storage
│   └── __init__.py
│
├── validation/                 # Input validation
│   ├── book_validator.py      # Book data validation
│   ├── user_validator.py      # User data validation
│   ├── isbn_validator.py      # ISBN validation
│   ├── id_validator.py        # ID validation
│   └── __init__.py
│
├── lib_logging/               # Logging utilities
│   ├── logger.py
│   └── __init__.py
│
├── web/                       # Web interface
│   ├── server.py              # HTTP server
│   ├── docs.html              # API documentation
│   ├── logs.html              # Logs dashboard
│   ├── swagger.html           # Swagger UI
│   ├── openapi.yaml           # OpenAPI specification
│   └── static/                # Static assets
│
├── tests/                     # Test suite (44 tests)
│   ├── conftest.py
│   ├── test_*.py
│   └── __init__.py
│
├── scripts/                   # Utility scripts
│   ├── format.sh/.bat         # Code formatting
│   ├── lint.sh/.bat           # Linting
│   ├── test.sh/.bat           # Testing
│   ├── setup.sh/.bat          # Setup
│   ├── demo.sh/.ps1           # Demo scripts
│   └── check_commit_msg.py    # Git hook
│
├── data/                      # Data files (JSON)
│   ├── books.json
│   └── users.json
│
├── k8s/                       # Kubernetes manifests
│   ├── deployment.yaml
│   ├── service.yaml
│   ├── pvc.yaml
│   └── configmap.yaml
│
├── monitoring/                # Monitoring setup
│   ├── docker-compose.yml
│   ├── prometheus/
│   ├── grafana/
│   ├── filebeat/
│   └── alertmanager/
│
├── terraform/                 # Infrastructure as Code
│   └── main.tf
│
├── .github/
│   └── workflows/
│       └── ci.yml             # GitHub Actions CI/CD
│
└── logs/                      # Application logs
```

---

## 🔨 Development

### Build & Code Quality

Use **Make** for quick commands:
```bash
make help          # Show all commands
make install-dev   # Install with dev dependencies
make format        # Format code (black, isort)
make lint          # Lint code (flake8, pylint, mypy)
make test          # Run tests
make test-cov      # Run tests with coverage
make check         # Format + lint + test (pre-commit check)
```

Or use **Poetry** directly:
```bash
# Format code
poetry run black .
poetry run isort .

# Lint code
poetry run flake8 .
poetry run pylint cli models services storage validation lib_logging main.py

# Type checking
poetry run mypy .

# Run tests
poetry run pytest -v
```

### Development Workflow

1. **Before committing**, run quality checks:
   ```bash
   make check  # Runs format, lint, and test
   ```

2. **Format code** automatically:
   ```bash
   make format
   ```

3. **Run tests** with coverage:
   ```bash
   make test-cov
   ```

4. For detailed build guide, see [BUILD.md](BUILD.md)

---

## 👥 Team Collaboration

### For Multiple Team Members

#### Option 1: Feature Branches (Recommended)
```bash
# Create and work on feature branch
git checkout -b feature/your-feature

# Make changes, test, and commit
poetry run pytest
git add .
git commit -m "feat: your feature description"

# Push and create PR
git push origin feature/your-feature
```

#### Option 2: Area Separation
- **Backend/Core**: `models/`, `services/`, `storage/`, `validation/`, `core/`
- **CLI/Interface**: `cli/`, `main.py`
- **Web Interface**: `web/`
- **Testing**: `tests/`
- **DevOps**: `k8s/`, `terraform/`, `monitoring/`

### Code Review Process
1. Create a feature branch
2. Make changes and ensure `make check` passes
3. Push and create a Pull Request
4. Request code review from team member
5. Address feedback and merge

---

## 🔄 CI/CD Pipeline

GitHub Actions automatically:
- ✅ Runs on **Ubuntu, Windows, macOS**
- ✅ Tests on **Python 3.8, 3.9, 3.10, 3.11**
- ✅ Formats code (black, isort)
- ✅ Lints code (flake8, pylint)
- ✅ Type checks (mypy)
- ✅ Runs all tests (44 tests total)
- ✅ Uploads coverage reports

Trigger pipeline with:
```bash
git push origin main
git push origin develop
```

---

## 📝 Demo & Presentation

Run the project demo:

**Windows PowerShell:**
```powershell
.\scripts\demo.ps1
```

**Linux/macOS Bash:**
```bash
bash scripts/demo.sh
```

The demo:
- Backs up data files
- Creates sample books and users
- Demonstrates all key features
- Restores original state

See [DEMO.md](DEMO.md) for detailed instructions.

---

## 🤝 Contributing

### Before Submitting Code
1. Run all tests: `make test`
2. Format code: `make format`
3. Check quality: `make check`
4. Create descriptive commit messages
5. Push to feature branch and create PR

### Commit Message Format
```
<type>: <description>

<optional body>
<optional footer>
```

Types: `feat`, `fix`, `docs`, `style`, `refactor`, `test`, `chore`

---

## 📋 Requirements

### Runtime
- Python 3.8+

### Development
- Poetry (dependency management)
- pytest (testing)
- black, isort (formatting)
- flake8, pylint, mypy (linting)

### Optional
- Docker (for containerization)
- Kubernetes (for orchestration)
- Terraform (for infrastructure)
- Prometheus & Grafana (for monitoring)

---

## 📚 Documentation

- **[BUILD.md](BUILD.md)** - Detailed build and development guide
- **[DEMO.md](DEMO.md)** - Demo script walkthrough
- **API Docs** - Available at `http://localhost:8000` (when web server running)

---

## 📄 License

This project is part of the School Library Management System.

---

## 🆘 Troubleshooting

### Poetry Issues
```bash
# Install Poetry
curl -sSL https://install.python-poetry.org | python3 -

# Clear Poetry cache
poetry cache clear pypi --all

# Reinstall dependencies
poetry install --no-cache
```

### Test Failures
```bash
# Run tests with verbose output
poetry run pytest -v

# Run specific test
poetry run pytest tests/test_models.py::TestBook::test_create_book

# Run with debugging
poetry run pytest -v --tb=short
```

### Import Errors
```bash
# Ensure project root is in Python path
export PYTHONPATH="${PYTHONPATH}:$(pwd)"

# Reinstall project
poetry install
```

---

## 📞 Contact & Support

For issues or questions:
1. Check existing issues on GitHub
2. Create a new GitHub issue with details
3. Include logs from `logs/` directory if applicable

Happy coding! 🎉
