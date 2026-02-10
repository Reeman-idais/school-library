# Docker helper script for the school-library application
# Usage: .\scripts\docker-build.ps1 [command]

param(
    [Parameter(Position = 0)]
    [string]$Command = "help",
    
    [string]$Environment = "dev",
    [switch]$NoPull = $false,
    [switch]$NoCache = $false
)

$ErrorActionPreference = "Stop"

function Write-Header {
    param([string]$Text)
    Write-Host "`n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Blue
    Write-Host "🐳 $Text" -ForegroundColor Cyan
    Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Blue
}

function Write-Success {
    param([string]$Text)
    Write-Host "✅ $Text" -ForegroundColor Green
}

function Write-Error-Custom {
    param([string]$Text)
    Write-Host "❌ $Text" -ForegroundColor Red
}

function Show-Help {
    Write-Host @"
📚 School Library Docker Helper

USAGE: .\scripts\docker-build.ps1 [command] [options]

COMMANDS:
  help              Show this help message
  build             Build Docker images
  up                Start containers
  down              Stop containers
  logs              View container logs
  test              Run tests in Docker
  shell             Open shell in running container
  clean             Remove containers and images
  push              Push images to registry
  pull              Pull images from registry

OPTIONS:
  -Environment dev|staging|prod    Set environment (default: dev)
  -NoPull                          Don't pull images first
  -NoCache                         Build without cache

EXAMPLES:
  # Build images
  .\scripts\docker-build.ps1 build

  # Start containers for development
  .\scripts\docker-build.ps1 up -Environment dev

  # Run tests
  .\scripts\docker-build.ps1 test

  # View logs
  .\scripts\docker-build.ps1 logs
"@
}

function Build-Images {
    Write-Header "Building Docker Images"
    
    $cacheArg = if ($NoCache) { "--no-cache" } else { "" }
    
    # Build main application image
    Write-Host "Building main application image..."
    docker build -t school-library:latest -f Dockerfile $cacheArg .
    if ($LASTEXITCODE -ne 0) { throw "Failed to build main image" }
    Write-Success "Main image built"
    
    # Build test image
    Write-Host "Building test image..."
    docker build -t school-library:test -f Dockerfile.test $cacheArg .
    if ($LASTEXITCODE -ne 0) { throw "Failed to build test image" }
    Write-Success "Test image built"
}

function Start-Containers {
    Write-Header "Starting Containers ($Environment)"
    
    if (-not $NoPull) {
        Write-Host "Pulling latest images..."
        docker-compose pull 2>$null || $true
    }
    
    $composeArgs = "-f docker-compose.yml"
    if ($Environment -eq "dev") {
        $composeArgs += " -f docker-compose.override.yml"
    }
    
    Write-Host "Starting services..."
    docker-compose $composeArgs.Split() up -d
    if ($LASTEXITCODE -ne 0) { throw "Failed to start containers" }
    
    Write-Success "Containers started"
    Write-Host "`n📊 Service Status:"
    docker-compose $composeArgs.Split() ps
}

function Stop-Containers {
    Write-Header "Stopping Containers"
    docker-compose down
    Write-Success "Containers stopped"
}

function View-Logs {
    Write-Header "Container Logs"
    docker-compose logs -f
}

function Run-Tests {
    Write-Header "Running Tests"
    
    Write-Host "Building test image..."
    docker build -t school-library:test -f Dockerfile.test .
    
    Write-Host "Running tests..."
    docker run --rm `
        -v "${pwd}/coverage:/app/coverage" `
        school-library:test
    
    Write-Success "Tests completed"
    Write-Host "`n📊 Coverage report generated in ./coverage"
}

function Open-Shell {
    Write-Header "Opening Container Shell"
    
    $containerName = "school-library-app"
    if (-not (docker ps | Select-String $containerName)) {
        Write-Error-Custom "Container '$containerName' is not running"
        exit 1
    }
    
    docker exec -it $containerName /bin/bash
}

function Clean-Resources {
    Write-Header "Cleaning Up Docker Resources"
    
    Write-Host "Stopping containers..."
    docker-compose down --volumes
    
    Write-Host "Removing images..."
    docker rmi school-library:latest school-library:test 2>$null || $true
    
    Write-Host "Pruning system..."
    docker system prune -f
    
    Write-Success "Cleanup complete"
}

function Push-Images {
    Write-Header "Pushing Images to Registry"
    
    Write-Host "Tagging images..."
    docker tag school-library:latest ghcr.io/reeman-idais/school-library:latest
    
    Write-Host "Pushing to registry..."
    docker push ghcr.io/reeman-idais/school-library:latest
    
    Write-Success "Images pushed"
}

function Pull-Images {
    Write-Header "Pulling Images from Registry"
    
    Write-Host "Pulling images..."
    docker pull ghcr.io/reeman-idais/school-library:latest
    docker tag ghcr.io/reeman-idais/school-library:latest school-library:latest
    
    Write-Success "Images pulled"
}

# Main script logic
try {
    switch ($Command.ToLower()) {
        "help" { Show-Help }
        "build" { Build-Images }
        "up" { Start-Containers }
        "down" { Stop-Containers }
        "logs" { View-Logs }
        "test" { Run-Tests }
        "shell" { Open-Shell }
        "clean" { Clean-Resources }
        "push" { Push-Images }
        "pull" { Pull-Images }
        default {
            Write-Error-Custom "Unknown command: $Command"
            Write-Host ""
            Show-Help
            exit 1
        }
    }
}
catch {
    Write-Error-Custom "Error: $_"
    exit 1
}
