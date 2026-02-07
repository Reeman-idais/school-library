# Run pytest with coverage (Windows PowerShell)

$ErrorActionPreference = "Stop"

Write-Host "🧪 Running tests with pytest..." -ForegroundColor Cyan
python -m poetry run pytest -v --tb=short --cov=. --cov-report=term-missing

Write-Host "✅ Tests complete!" -ForegroundColor Green
