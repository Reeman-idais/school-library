# 🐳 Docker & CI/CD Setup Guide

Complete guide for containerizing and deploying the Electronic Library Management System.

## Table of Contents

- [Quick Start](#quick-start)
- [Docker Setup](#docker-setup)
- [Docker Compose](#docker-compose)
- [CI/CD Pipelines](#cicd-pipelines)
- [Deployment](#deployment)
- [Troubleshooting](#troubleshooting)

---

## Quick Start

### Prerequisites

- **Docker** 20.10+
- **Docker Compose** 1.29+
- **Git**

### Installation

**Windows (PowerShell):**
```powershell
# Install Docker Desktop
# https://www.docker.com/products/docker-desktop

# Verify installation
docker --version
docker-compose --version

# Make scripts executable
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

**Linux/macOS:**
```bash
# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh | sh

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Make scripts executable
chmod +x scripts/docker-build.sh

# Verify installation
docker --version
docker-compose --version
```

---

## Docker Setup

### Building Images

**Main Application Image:**
```bash
# Build the application image
docker build -t school-library:latest -f Dockerfile .

# Build with no cache
docker build -t school-library:latest -f Dockerfile --no-cache .
```

**Test Image:**
```bash
# Build the test image
docker build -t school-library:test -f Dockerfile.test .

# Run tests in container
docker run --rm -v $(pwd)/coverage:/app/coverage school-library:test
```

### Using Helper Scripts

**Windows:**
```powershell
# Build images
.\scripts\docker-build.ps1 build

# Start containers
.\scripts\docker-build.ps1 up -Environment dev

# View logs
.\scripts\docker-build.ps1 logs

# Run tests
.\scripts\docker-build.ps1 test

# Open shell in container
.\scripts\docker-build.ps1 shell

# Clean up
.\scripts\docker-build.ps1 clean
```

**Linux/macOS:**
```bash
# Build images
./scripts/docker-build.sh build

# Start containers
./scripts/docker-build.sh up

# View logs
./scripts/docker-build.sh logs

# Run tests
NO_CACHE=true ./scripts/docker-build.sh build

# Open shell in container
./scripts/docker-build.sh shell

# Clean up
./scripts/docker-build.sh clean
```

---

## Docker Compose

### Configuration Files

- **docker-compose.yml**: Main configuration for all services
- **docker-compose.override.yml**: Development overrides (auto-loaded)
- **Dockerfile**: Multi-stage production build
- **Dockerfile.test**: Testing environment

### Services

#### Main Application
```yaml
app:
  - HTTP server on port 8000
  - Data persistence with volumes
  - Health checks enabled
  - Non-root user for security
```

#### Development Service
```yaml
app-dev:
  - Live code mounting
  - Useful for development
  - Runs with mounted volumes
```

#### Testing Service
```yaml
app-test:
  - Complete test environment
  - Generates coverage reports
  - Includes pytest and all dev dependencies
```

#### Optional Services
```yaml
prometheus:   # Monitoring and metrics
redis:        # Caching (if needed)
```

### Running Services

**Start all services:**
```bash
docker-compose up -d
```

**Start specific service:**
```bash
docker-compose up -d app
```

**View logs:**
```bash
docker-compose logs -f app
```

**Stop services:**
```bash
docker-compose down
```

**Stop and remove volumes:**
```bash
docker-compose down -v
```

**Run commands in container:**
```bash
# Interactive shell
docker-compose exec app /bin/bash

# Run Python command
docker-compose exec app python -c "print('Hello')"

# Run tests
docker-compose exec app pytest -v
```

### Using Profiles

Profiles allow running specific service configurations:

```bash
# Development (default)
docker-compose --profile dev up -d

# Testing
docker-compose --profile test up -d

# Production
docker-compose --profile prod up -d

# Monitoring
docker-compose --profile monitoring up -d

# Multiple profiles
docker-compose --profile dev --profile monitoring up -d
```

---

## CI/CD Pipelines

### GitHub Actions Workflows

Three main workflows are configured:

#### 1. **CI - Build & Test** (`ci.yml`)

Runs on every push and pull request.

**Jobs:**
- **quality**: Code quality checks (black, isort, flake8, mypy, pylint)
- **test**: Unit and integration tests (Python 3.10, 3.11, 3.12)
- **build**: Docker image building and pushing

**Triggered by:**
```yaml
on:
  push:
    branches: [main, develop, feature/**]
  pull_request:
    branches: [main, develop]
```

**View results:**
- GitHub Actions tab → CI workflow → Latest run
- See test results, coverage, and build status

#### 2. **CD - Deploy** (`cd.yml`)

Handles deployment after successful CI.

**Jobs:**
- **determine-env**: Decides staging or production
- **deploy**: Deploys to target environment
- **cleanup**: Removes old images

**Triggered by:**
```yaml
on:
  workflow_run:
    workflows: [CI - Build & Test]
    types: [completed]
  workflow_dispatch:  # Manual trigger
```

**Manual deployment:**
1. Go to GitHub Actions → CD workflow
2. Click "Run workflow"
3. Select environment (staging/production)
4. Click "Run workflow"

#### 3. **Release** (`release.yml`)

Creates releases when tags are pushed.

**Jobs:**
- **release**: Creates GitHub release
- **build-and-push**: Builds and pushes to registry
- **security-scan**: Scans for vulnerabilities
- **notify**: Sends notifications

**Triggered by:**
```yaml
on:
  push:
    tags:
      - 'v*.*.*'
      - 'release-*'
```

**Create a release:**
```bash
# Tag version
git tag v1.0.0
git push origin v1.0.0

# Or with release notes
git tag -a v1.0.0 -m "Release version 1.0.0"
git push origin v1.0.0
```

### Workflow Status

Check status at: `https://github.com/Reeman-idais/school-library/actions`

---

## Registry Configuration

### GitHub Container Registry (GHCR)

Images are automatically pushed to GHCR on main branch.

**Image URL:** `ghcr.io/reeman-idais/school-library:sha-abc123`

**Authenticate with GHCR:**
```bash
# Create personal access token at https://github.com/settings/tokens
# Scopes: read:packages, write:packages, delete:packages

docker login ghcr.io -u USERNAME -p TOKEN

# Pull image
docker pull ghcr.io/reeman-idais/school-library:latest

# Push image
docker tag school-library:latest ghcr.io/reeman-idais/school-library:v1.0.0
docker push ghcr.io/reeman-idais/school-library:v1.0.0
```

---

## Deployment

### Local Deployment

**Using Docker Compose:**
```bash
# Development setup
docker-compose up -d

# Access application
curl http://localhost:8000

# View health
curl http://localhost:8000/health

# Logs
docker-compose logs -f app
```

### Staging Deployment

**Manual trigger via GitHub Actions:**
1. Go to Actions → CD workflow
2. Run workflow → Select "staging"
3. Monitor deployment progress

### Production Deployment

**Create release (auto-deploys):**
```bash
git tag v1.0.0-prod
git push origin v1.0.0-prod
```

Or manually trigger:
1. Actions → CD workflow → Run workflow
2. Select "production" environment

### Custom Deployment

Add your deployment script to `scripts/deploy.sh`:
```bash
#!/bin/bash
ENVIRONMENT=$1
IMAGE=$2

# Your deployment logic here
# Examples: SSH, kubectl, AWS CLI, etc.
```

---

## Security

### Best Practices

1. **Non-root User**: App runs as unprivileged user (uid 1000)
2. **Health Checks**: Container health monitored
3. **Image Scanning**: Trivy scans for vulnerabilities on release
4. **Secrets Management**: Use GitHub Secrets for credentials

    ```bash
    # Set secrets in GitHub Actions secrets
    # https://github.com/Reeman-idais/school-library/settings/secrets/actions
    
    DEPLOY_TOKEN
    DEPLOY_HOST
    DEPLOY_USER
    SLACK_WEBHOOK_URL
    ```

### Docker Image Security

```bash
# Scan image for vulnerabilities
docker run --rm -v /var/run/docker.sock:/var/run/docker.sock \
  aquasec/trivy image school-library:latest

# View image layers
docker history school-library:latest

# Inspect image
docker inspect school-library:latest
```

---

## Monitoring & Logging

### Container Logs

**View logs:**
```bash
# All services
docker-compose logs

# Specific service
docker-compose logs app

# Follow logs
docker-compose logs -f app

# Last 100 lines
docker-compose logs --tail=100 app

# With timestamps
docker-compose logs -t app
```

### Prometheus Metrics

**Start Prometheus:**
```bash
docker-compose --profile monitoring up -d prometheus

# Access dashboard at http://localhost:9090
```

**Scrape metrics:**
```bash
curl http://localhost:8000/metrics
```

---

## Troubleshooting

### Container Won't Start

```bash
# Check logs
docker-compose logs app

# Inspect image
docker inspect school-library:latest

# Run interactive shell
docker run -it school-library:latest /bin/bash
```

### Port Already in Use

```bash
# Change port in docker-compose.yml
# Or kill process using port
lsof -i :8000  # macOS/Linux
netstat -ano | findstr :8000  # Windows
```

### Build Fails

```bash
# Clear cache
docker builder prune

# Rebuild without cache
docker-compose build --no-cache

# Check Docker daemon
docker ps

# View build logs
docker-compose build --verbose
```

### Permission Denied

```bash
# Add user to docker group (Linux)
sudo usermod -aG docker $USER
newgrp docker

# Logout and login again
```

### Image Not Found

```bash
# Pull image from registry
docker pull ghcr.io/reeman-idais/school-library:main

# List local images
docker images

# Build locally
docker build -t school-library:latest .
```

### Health Check Failing

```bash
# Test endpoint manually
curl http://localhost:8000/health

# Adjust health check in Dockerfile
# HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3
```

---

## Additional Resources

- [Docker Documentation](https://docs.docker.com/)
- [Docker Compose Documentation](https://docs.docker.com/compose/)
- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [Container Registry Documentation](https://docs.github.com/en/packages/working-with-a-github-packages-registry/working-with-the-container-registry)

---

## Support

For issues or questions:
1. Check logs: `docker-compose logs app`
2. Search existing issues: https://github.com/Reeman-idais/school-library/issues
3. Create new issue with logs and steps to reproduce
