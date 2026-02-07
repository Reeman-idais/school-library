#!/bin/bash
# Run pytest with coverage

set -e

echo "🧪 Running tests with pytest..."
python -m poetry run pytest -v --tb=short --cov=. --cov-report=term-missing

echo "✅ Tests complete!"
