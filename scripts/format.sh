#!/bin/bash
# Format code with black and isort

set -e

echo "🔄 Formatting code with black..."
python -m poetry run black .

echo "🔄 Sorting imports with isort..."
python -m poetry run isort .

echo "✅ Code formatting complete!"
