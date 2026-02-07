# Lint code with flake8, pylint, and mypy (Windows PowerShell)

$ErrorActionPreference = "Continue"

Write-Host "🔍 Linting with flake8..." -ForegroundColor Cyan
python -m poetry run flake8 .

Write-Host "🔍 Linting with pylint..." -ForegroundColor Cyan
python -m poetry run pylint cli models services storage validation lib_logging main.py web/server.py

Write-Host "🔍 Type checking with mypy..." -ForegroundColor Cyan
python -m poetry run mypy .

Write-Host "✅ Linting complete!" -ForegroundColor Green
