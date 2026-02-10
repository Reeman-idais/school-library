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

# ======================== Docker Targets ========================

docker-build: ## Build Docker images
	docker-compose build

docker-build-prod: ## Build production Docker image
	docker build -t school-library:latest -f Dockerfile .

docker-build-test: ## Build test Docker image
	docker build -t school-library:test -f Dockerfile.test .

docker-build-no-cache: ## Build Docker images without cache
	docker-compose build --no-cache

docker-up: ## Start containers
	docker-compose up -d

docker-up-dev: ## Start containers in development mode
	docker-compose -f docker-compose.yml -f docker-compose.override.yml up -d

docker-down: ## Stop containers
	docker-compose down

docker-logs: ## View container logs
	docker-compose logs -f app

seed: ## Seed MongoDB (tries Docker Compose `app-seed` first, falls back to local script)
	@echo "Seeding MongoDB..."
	@docker compose build --quiet app || true
	@docker compose run --rm app-seed || python scripts/seed_mongodb.py
	@echo "Seeding finished."

docker-shell: ## Open shell in running container
	docker-compose exec app /bin/bash

docker-test: ## Run tests in Docker container
	docker build -t school-library:test -f Dockerfile.test .
	docker run --rm -v $$(pwd)/coverage:/app/coverage school-library:test

docker-push: ## Push images to registry
	docker tag school-library:latest ghcr.io/reeman-idais/school-library:latest
	docker push ghcr.io/reeman-idais/school-library:latest

docker-pull: ## Pull images from registry
	docker pull ghcr.io/reeman-idais/school-library:latest

docker-clean: ## Remove containers and images
	docker-compose down -v
	docker rmi school-library:latest school-library:test 2>/dev/null || true
	docker system prune -f

docker-status: ## Show Docker services status
	docker-compose ps

docker-metrics: ## Show Docker metrics (requires docker stats)
	docker stats --no-stream

# ======================== CI/CD Targets ========================

docker-ci: docker-build-test docker-test ## Run CI pipeline in Docker

docker-deploy: ## Deploy using Docker Compose
	docker-compose -f docker-compose.yml pull && docker-compose -f docker-compose.yml up -d

# ======================== Monitoring ========================

monitor-up: ## Start Prometheus monitoring
	docker-compose --profile monitoring up -d prometheus

monitor-down: ## Stop Prometheus monitoring
	docker-compose --profile monitoring down

monitor-logs: ## View Prometheus logs
	docker-compose logs -f prometheus

monitor-url: ## Print Prometheus URL
	@echo "Prometheus: http://localhost:9090"
	@echo "Metrics endpoint: http://localhost:8000/metrics"

.PHONY: help install install-dev format lint test test-cov clean run build check ci
.PHONY: docker-build docker-build-prod docker-build-test docker-build-no-cache
.PHONY: docker-up docker-up-dev docker-down docker-logs docker-shell docker-test
.PHONY: docker-push docker-pull docker-clean docker-status docker-metrics
.PHONY: docker-ci docker-deploy monitor-up monitor-down monitor-logs monitor-url
