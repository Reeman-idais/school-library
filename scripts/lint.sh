#!/bin/bash
# Lint code with flake8, pylint, and mypy

set -e

echo "🔍 Linting with flake8..."
python -m poetry run flake8 . || true

echo "🔍 Linting with pylint..."
python -m poetry run pylint cli models services storage validation lib_logging main.py web/server.py || true

echo "🔍 Type checking with mypy..."
python -m poetry run mypy . || true

echo "✅ Linting complete!"
