.PHONY: help install install-dev format lint test test-cov clean run build

help: ## Show this help message
	@echo "Available commands:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-20s\033[0m %s\n", $$1, $$2}'

install: ## Install production dependencies
	poetry install --no-dev

install-dev: ## Install all dependencies including dev dependencies
	poetry install

format: ## Format code with black and isort
	poetry run black .
	poetry run isort .

lint: ## Run all linters (flake8, pylint, mypy)
	@echo "Running flake8..."
	poetry run flake8 .
	@echo "Running pylint..."
	poetry run pylint cli models services storage validation lib_logging main.py web/server.py || true
	@echo "Running mypy..."
	poetry run mypy . || true

test: ## Run tests
	poetry run pytest

test-unit: ## Run unit tests only
	poetry run pytest -m unit

test-integration: ## Run integration tests only
	poetry run pytest -m integration

test-cov: ## Run tests with coverage report
	poetry run pytest --cov=. --cov-report=html --cov-report=term-missing

test-cov-unit: ## Run unit tests with coverage
	poetry run pytest -m unit --cov=. --cov-report=html --cov-report=term-missing

test-watch: ## Run tests in watch mode
	poetry run pytest-watch

clean: ## Clean build artifacts and cache
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info
	rm -rf .pytest_cache/
	rm -rf .mypy_cache/
	rm -rf .coverage
	rm -rf htmlcov/
	find . -type d -name __pycache__ -exec rm -r {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete

run: ## Run the main application
	poetry run python main.py

build: ## Build the package
	poetry build

check: format lint test ## Run format, lint, and test (CI check)

ci: install-dev check ## Full CI pipeline (install, format, lint, test)
