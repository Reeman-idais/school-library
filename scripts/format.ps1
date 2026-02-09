# Format code with black and isort (Windows PowerShell)

$ErrorActionPreference = "Stop"

Write-Host "🔄 Formatting code with black..." -ForegroundColor Cyan
python -m poetry run black .

Write-Host "🔄 Sorting imports with isort..." -ForegroundColor Cyan
python -m poetry run isort .

Write-Host "✅ Code formatting complete!" -ForegroundColor Green
