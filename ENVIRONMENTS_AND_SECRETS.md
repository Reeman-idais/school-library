# Environment Variable Secrets Best Practices

This document outlines how to safely handle environment variables and secrets in the School Library application.

## Overview

The application uses environment variables for configuration, including sensitive data like database credentials. This guide explains the best practices for different environments.

## Local Development

### .env File

**Location:** `.env` (in project root)  
**Status:** Git-ignored (never committed)  
**Purpose:** Local configuration overrides

**Example ``.env``:**
```bash
# Database
DATABASE_TYPE=mongodb
MONGODB_HOST=localhost
MONGODB_PORT=27017
MONGODB_DATABASE=school_library_dev
MONGODB_USERNAME=admin
MONGODB_PASSWORD=password123

# Application
APP_PORT=8000
LOG_LEVEL=DEBUG
ENVIRONMENT=development
```

### .env.local File (Optional)

**Location:** `.env.local` (in project root)  
**Status:** Git-ignored (never committed)  
**Purpose:** Machine-specific overrides (takes precedence over `.env`)

**Example ``.env.local``:**
```bash
# Override for this machine only
MONGODB_PASSWORD=my_local_password
LOG_LEVEL=DEBUG
```

### .env.example File

**Location:** `.env.example` (tracked in Git)  
**Status:** Committed to repository  
**Purpose:** Template for developers

**Example content:**
```bash
# Database Configuration
MONGODB_HOST=localhost
MONGODB_PORT=27017
MONGODB_DATABASE=school_library
MONGODB_USERNAME=admin
MONGODB_PASSWORD=password123
```

### Setup Instructions

1. **First time setup:**
   ```bash
   cp .env.example .env
   # Edit .env with your local settings
   ```

2. **Never commit** `.env` file:
   ```bash
   # Verify .env is in .gitignore
   grep "\.env" .gitignore
   ```

## Docker Development

### docker-compose.yml

Environment variables are defined in the service configuration:

```yaml
services:
  mongodb:
    environment:
      MONGO_INITDB_ROOT_USERNAME: ${MONGODB_USERNAME}
      MONGO_INITDB_ROOT_PASSWORD: ${MONGODB_PASSWORD}
  
  app:
    environment:
      MONGODB_HOST: ${MONGODB_HOST:-mongodb}
      MONGODB_PORT: ${MONGODB_PORT:-27017}
      MONGODB_DATABASE: ${MONGODB_DATABASE}
      MONGODB_USERNAME: ${MONGODB_USERNAME}
      MONGODB_PASSWORD: ${MONGODB_PASSWORD}
```

**Key Points:**
- Variables come from `.env` file in project root
- Defaults use `${VAR:-default}` syntax
- Docker Compose automatically loads `.env`

### Running with Docker

```bash
# Uses .env file automatically
docker-compose up

# Or override specific variables
docker-compose -e MONGODB_PASSWORD=custom_password up

# Run with specific profile
docker-compose --profile dev up
docker-compose --profile test up
```

## GitHub Actions CI/CD

### Secrets Configuration

**Location:** Repository Settings → Secrets and Variables → Actions

**Never store in** `.github/workflows/*.yml` (visible in git history)

**Setup in GitHub:**

1. Go to repository Settings
2. Navigate to Secrets and Variables → Actions
3. Create organization or repository secrets

**Required Secrets for CI/CD:**

```
MONGODB_PASSWORD     # MongoDB admin password
DOCKER_USERNAME      # Docker Hub username (for registry)
DOCKER_PASSWORD      # Docker Hub or PAT
```

### CI Workflow Configuration

**\.github/workflows/ci.yml:**

```yaml
jobs:
  test:
    runs-on: ubuntu-latest
    
    services:
      mongodb:
        image: mongo:7-alpine
        env:
          MONGO_INITDB_ROOT_USERNAME: admin
          MONGO_INITDB_ROOT_PASSWORD: password123
    
    env:
      DATABASE_TYPE: mongodb
      MONGODB_HOST: localhost
      MONGODB_PORT: 27017
      MONGODB_DATABASE: school_library_test
      MONGODB_USERNAME: admin
      MONGODB_PASSWORD: password123
    
    steps:
      - uses: actions/checkout@v4
      
      - name: Run tests
        run: poetry run pytest -v
```

**Note:** Test database credentials can be hardcoded since they're test-only.

## Production Deployment

### Environment Variable Sources

1. **Kubernetes Secrets** (recommended)
   ```yaml
   apiVersion: v1
   kind: Secret
   metadata:
     name: app-secrets
   type: Opaque
   data:
     mongodb-uri: <base64-encoded-connection-string>
   ```

2. **Environment Variables in Container Runtime**
   ```bash
   docker run -e MONGODB_URI="mongodb+srv://..." app:latest
   ```

3. **Cloud Provider Secrets Management**
   - AWS Secrets Manager
   - Azure Key Vault
   - Google Cloud Secret Manager

### Production Configuration Example

```bash
# Use full connection string for MongoDB Atlas
MONGODB_URI=mongodb+srv://user:password@cluster.mongodb.net/school_library?retryWrites=true&w=majority

# Or individual components (avoid if possible)
MONGODB_HOST=cluster.mongodb.net
MONGODB_PORT=27017
MONGODB_DATABASE=school_library
MONGODB_USERNAME=production_user
MONGODB_PASSWORD=<strong-random-password>

# Application settings
APP_PORT=8000
LOG_LEVEL=INFO
ENVIRONMENT=production
PYTHONUNBUFFERED=1
```

### Security Checklist

- [ ] Use strong passwords (minimum 16 characters)
- [ ] Store passwords in secrets manager, never in code
- [ ] Rotate passwords regularly
- [ ] Use database user with minimal required permissions
- [ ] Enable TLS/SSL for MongoDB connections
- [ ] Use IP whitelisting on MongoDB (Atlas)
- [ ] Never log sensitive values
- [ ] Use `.gitignore` to exclude `.env` files

## Environment Variables in Code

### Reading Environment Variables

**Safe Pattern:**
```python
import os
from typing import Optional

# With defaults for optional values
MONGODB_HOST = os.getenv("MONGODB_HOST", "localhost")
MONGODB_PORT = int(os.getenv("MONGODB_PORT", "27017"))

# Without defaults for required values
def get_required_env(name: str) -> str:
    """Get required environment variable."""
    value = os.getenv(name)
    if not value:
        raise ValueError(f"Required environment variable {name} not set")
    return value

MONGODB_DATABASE = get_required_env("MONGODB_DATABASE")
```

**Using python-dotenv (local development only):**
```python
from dotenv import load_dotenv
import os

# Load from .env file (local development only)
load_dotenv()

# Now use os.getenv() normally
database = os.getenv("MONGODB_DATABASE")
```

### Never Log Secrets

**Bad:**
```python
logger.info(f"Connecting to {MONGODB_URI}")  # Logs password!
```

**Good:**
```python
logger.info(f"Connecting to MongoDB at {MONGODB_HOST}:{MONGODB_PORT}")  # Safe
```

**Redact in Exception Messages:**
```python
try:
    client = MongoClient(MONGODB_URI)
except Exception as e:
    logger.error("Failed to connect to database")  # Don't include URI
    raise
```

## CI/CD Variable Management

### GitHub Actions Best Practices

1. **Use Secrets for sensitive values:**
   ```yaml
   - name: Deploy
     env:
      MONGODB_PASSWORD: ${{ secrets.MONGODB_PASSWORD }}
     run: ./deploy.sh
   ```

2. **Never print secrets:**
   ```yaml
   # Bad - logs the secret
   - run: echo ${{ secrets.MONGODB_PASSWORD }}
   
   # Good - doesn't log it
   - run: docker login -u user -p ${{ secrets.DOCKER_PASSWORD }}
   ```

3. **Use environment files for multiple secrets:**
   ```yaml
   - name: Create env file
     run: |
       echo "MONGODB_URI=${{ secrets.MONGODB_URI }}" >> .env
       echo "API_KEY=${{ secrets.API_KEY }}" >> .env
     continue-on-error: true
   ```

## Checking Your Configuration

### Verify Environment Variables

```bash
# Check if required variables are set
python -c "
import os
required = ['MONGODB_HOST', 'MONGODB_DATABASE', 'MONGODB_USERNAME']
for var in required:
    if not os.getenv(var):
        print(f'ERROR: {var} not set')
    else:
        print(f'✓ {var} is set')
"
```

### Test Database Connection

```bash
# Verify MongoDB connection with configured URI
python -c "
import os
from pymongo import MongoClient
from config.database import MongoDBConfig

config = MongoDBConfig()
try:
    client = MongoClient(config.connection_string, serverSelectionTimeoutMS=5000)
    client.admin.command('ping')
    print('✓ MongoDB connection successful')
except Exception as e:
    print(f'✗ MongoDB connection failed: {e}')
"
```

## Troubleshooting

### "Environment variable not found" Error

**Cause:** Variable not set in current environment

**Solution:**
1. Check `.env` file exists
2. Verify variable name (case-sensitive)
3. Reload environment: `source .env` (Linux/Mac) or restart editor/terminal
4. For Docker: Check `docker-compose.yml` and `.env`

### "Connection refused" Error

**Cause:** Wrong credentials or wrong host

**Solution:**
1. Verify `MONGODB_HOST` is correct
2. Check `MONGODB_USERNAME` and `MONGODB_PASSWORD`
3. Test connection: `mongosh -u admin -p password123 localhost:27017`

### Variables not updating in Running Container

**Solution:**
1. Stop container: `docker-compose down`
2. Update `.env` file
3. Restart: `docker-compose up`

## .gitignore Configuration

Ensure these files are in `.gitignore`:

```gitignore
# Environment files with credentials
.env
.env.local
.env.*.local

# IDE files
.vscode/
.idea/
*.swp
*.swo

# Python
__pycache__/
*.pyc
.pytest_cache/
.coverage

# Docker
docker-compose.override.yml

# Logs
logs/
*.log

# Data
data/
*.db
```

## References

- [Python-dotenv Documentation](https://python-dotenv.readthedocs.io/)
- [12 Factor App - Configuration](https://12factor.net/config)
- [GitHub Actions Secrets](https://docs.github.com/en/actions/security-guides/encrypted-secrets)
- [MongoDB Authentication](https://docs.mongodb.com/manual/core/authentication/)
- [OWASP - Secrets Management](https://cheatsheetseries.owasp.org/cheatsheets/Secrets_Management_Cheat_Sheet.html)
