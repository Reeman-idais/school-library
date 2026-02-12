# Feature/Database Branch - MongoDB Integration

## Summary

This branch adds MongoDB database support to the School Library application with full CI/CD integration, environment-based configuration, and best practices for secrets management.

## Changes Included

### Configuration Files
- **pyproject.toml**: Added `pymongo` and `python-dotenv` dependencies
- **.env.example**: Updated with MongoDB configuration variables
- **docker-compose.yml**: Added MongoDB service, updated all services with MongoDB variables, added health checks

### New Files Created

#### Configuration Module
- **config/__init__.py**: Configuration package
- **config/database.py**: MongoDB connection configuration, singleton manager, and connection pooling

#### Storage Layer (MongoDB)
- **storage/mongodb/__init__.py**: MongoDB storage package
- **storage/mongodb/book_storage.py**: MongoDB implementation for book storage with auto-incrementing IDs
- **storage/mongodb/user_storage.py**: MongoDB implementation for user storage
- **storage/factory.py**: Storage factory for pluggable database backends

#### Initialization Scripts
- **scripts/init_mongodb.js**: MongoDB initialization script (runs in container on startup)
- **scripts/init_mongodb.py**: Python initialization script for creating indexes and counters

#### Documentation
- **MONGODB_SETUP.md**: Comprehensive MongoDB setup and usage guide
- **ENVIRONMENTS_AND_SECRETS.md**: Environment variables and secrets management best practices

### Updated Files

#### CI/CD
- **.github/workflows/ci.yml**: 
  - Added MongoDB service to test job
  - Added MongoDB health check and wait logic
  - Set environment variables for test database
  - Uses separate `school_library_test` database for tests

#### Application Configuration
- **docker-compose.yml**:
  - Added MongoDB service with Alpine image (minimal footprint)
  - MongoDB data volume for persistence
  - Health checks on all services
  - Environment variables for MongoDB credentials
  - Updated app, app-dev, app-test services to use MongoDB
  - Added dependencies on MongoDB service

## Key Features

### 1. Database Flexibility
- **Factory Pattern**: Switch between JSON and MongoDB via `DATABASE_TYPE` environment variable
- **Backwards Compatible**: Existing JSON storage still available
- **Easy Migration**: Factory allows gradual migration from JSON to MongoDB

### 2. Connection Management
- **Singleton Pattern**: Single MongoDB connection per application
- **Connection Pooling**: PyMongo handles pooling automatically
- **Health Checks**: Container health checks verify database readiness
- **Error Handling**: Graceful error handling with detailed logging

### 3. Auto-Incrementing IDs
- **Counter Collections**: Separate counters for books and users
- **Atomic Operations**: Thread-safe ID generation using MongoDB atomic operations
- **Unique Constraints**: Indexes ensure ID uniqueness

### 4. Environment-Based Configuration
- **Development**: Local `.env` file with defaults
- **Docker**: Environment variables in docker-compose.yml
- **CI/CD**: GitHub Actions secrets and service configuration
- **Production**: MongoDB Atlas or self-hosted with connection strings

### 5. Security Best Practices
- **Credentials Management**: Sensitive values in environment variables, never hardcoded
- **Secrets in GitHub**: Use GitHub Actions secrets for passwords and connection strings
- **No Credential Logging**: Credentials never logged in error messages
- **Git Ignored**: `.env` and `.env.local` excluded from repository

### 6. CI/CD Integration
- **MongoDB Service**: GitHub Actions CI includes MongoDB service
- **Test Database**: Separate `school_library_test` database for tests
- **Wait Logic**: Built-in wait for MongoDB to be healthy before running tests
- **Test Isolation**: Each test run uses clean database

## Usage

### Local Development

```bash
# Setup
cp .env.example .env

# Start MongoDB and app with Docker
docker-compose up

# Or without Docker (requires local MongoDB)
poetry install
python scripts/init_mongodb.py
python main.py
```

### Switch Database Type

```bash
# Use MongoDB (default)
DATABASE_TYPE=mongodb python main.py

# Use JSON storage (legacy)
DATABASE_TYPE=json python main.py
```

### Docker Profiles

```bash
# Production
docker-compose --profile prod up

# Development with hot-reload
docker-compose --profile dev up

# Testing
docker-compose --profile test up

# Monitoring
docker-compose --profile monitoring up
```

## Testing

### Local Testing
```bash
# Run tests with MongoDB
DATABASE_TYPE=mongodb pytest -v

# Run tests with Docker
docker-compose --profile test up
```

### CI/CD Testing
- GitHub Actions automatically runs MongoDB service
- Tests run against `school_library_test` database
- Coverage reports uploaded to Codecov

## Migration Path

### From JSON to MongoDB

1. Configure MongoDB via `.env` or environment variables
2. Run application with `DATABASE_TYPE=mongodb`
3. New operations use MongoDB
4. Optional: Migrate historical data using scripts

Example migration:
```python
from storage.book_storage import BookStorage as JSONStorage
from storage.mongodb.book_storage import MongoDBBookStorage

# Load from JSON
json_books = JSONStorage().load_books()

# Write to MongoDB  
mongo_storage = MongoDBBookStorage()
for book in json_books:
    mongo_storage.add_book(book)
```

## Deployment

### Docker Deployment
```bash
# Build
docker-compose build

# Deploy with MongoDB
docker-compose -f docker-compose.yml up -d
```

### Kubernetes (Future)
- Update MongoDB host in environment to Kubernetes service name
- Use ConfigMaps for non-sensitive configuration
- Use Secrets for credentials and connection strings

### MongoDB Atlas (Cloud)
```bash
MONGODB_URI=mongodb+srv://user:password@cluster.mongodb.net/school_library?retryWrites=true&w=majority
```

## Next Steps

1. **Review** the changes in this branch
2. **Test locally** with `docker-compose up`
3. **Run tests** with `pytest` or `docker-compose --profile test up`
4. **Merge** into main after approval
5. **Deploy** to production with appropriate secrets

## References

- [MONGODB_SETUP.md](./MONGODB_SETUP.md) - Complete MongoDB guide
- [ENVIRONMENTS_AND_SECRETS.md](./ENVIRONMENTS_AND_SECRETS.md) - Secrets management guide
- [MongoDB Documentation](https://docs.mongodb.com/)
- [PyMongo Documentation](https://pymongo.readthedocs.io/)
- [Docker Compose Profiles](https://docs.docker.com/compose/compose-file/compose-file-v3/#profiles)

## Questions or Issues?

See:
1. Troubleshooting section in MONGODB_SETUP.md
2. Container logs: `docker-compose logs mongodb` or `docker-compose logs app`
3. GitHub Issues with detailed logs
