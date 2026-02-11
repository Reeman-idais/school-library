# MongoDB Integration Guide

This guide explains the MongoDB integration for the School Library application, including setup, configuration, and best practices.

## Overview

The application now supports MongoDB as the primary database backend, with environment-based configuration for flexibility between local development, Docker, and CI/CD environments.

## Quick Start

### Local Development with Docker

1. **Copy environment file:**
   ```bash
   cp .env.example .env
   ```

2. **Start MongoDB and the app:**
   ```bash
   docker-compose up -d
   ```

3. **Verify MongoDB is running:**
   ```bash
   docker-compose logs mongodb
   docker-compose exec mongodb mongosh -u admin -p password123 --authenticationDatabase admin
   ```

### Without Docker

1. **Install MongoDB locally** (macOS: `brew install mongodb-community`)

2. **Configure environment:**
   ```bash
   cp .env.example .env
   # Edit .env to point to your local MongoDB instance
   ```

3. **Install Python dependencies:**
   ```bash
   poetry install
   ```

4. **Initialize MongoDB:**
   ```bash
   python scripts/init_mongodb.py
   ```

5. **Run the application:**
   ```bash
   python main.py
   ```

## Configuration

### Environment Variables

The application uses the following environment variables for MongoDB configuration:

| Variable | Default | Description |
|----------|---------|-------------|
| `DATABASE_TYPE` | `mongodb` | Database backend ('mongodb' or 'json') |
| `MONGODB_HOST` | `localhost` | MongoDB server hostname |
| `MONGODB_PORT` | `27017` | MongoDB server port |
| `MONGODB_DATABASE` | `school_library` | Database name |
| `MONGODB_USERNAME` | `admin` | MongoDB username |
| `MONGODB_PASSWORD` | `password123` | MongoDB password |
| `MONGODB_URI` | - | Full connection string (overrides host/port) |
| `LOG_LEVEL` | `INFO` | Logging level |
| `ENVIRONMENT` | `development` | Environment type |

### Local Development

Create `.env.local` for local overrides (not committed to git):

```bash
# .env.local - Local development overrides
DATABASE_TYPE=mongodb
MONGODB_HOST=localhost
MONGODB_PORT=27017
MONGODB_DATABASE=school_library_dev
MONGODB_USERNAME=admin
MONGODB_PASSWORD=password123
LOG_LEVEL=DEBUG
ENVIRONMENT=development
```

### CI/CD (GitHub Actions)

Environment variables are set in the CI workflow:

```yaml
env:
  DATABASE_TYPE: mongodb
  MONGODB_HOST: localhost
  MONGODB_PORT: 27017
  MONGODB_DATABASE: school_library_test
  MONGODB_USERNAME: admin
  MONGODB_PASSWORD: password123
```

**CI behavior note:** If `secrets.MONGODB_URI` is provided in the repository secrets, the integration job will use that external URI. If not provided, the workflow will start a **local MongoDB service** inside the runner (image: `mongo:7`) with credentials `admin` / `password123` and database `school_library_test`, wait for it to be ready, run `scripts/init_mongodb.py` to create indexes and counters, then run the integration tests against it. This makes CI resilient and allows testing without Atlas.

### Connecting with MongoDB Compass (local Docker)

When running MongoDB via `docker-compose` locally, you can connect MongoDB Compass to:

- Host: `localhost`
- Port: `27017`
- Authentication: **Username:** `admin`, **Password:** `password123`, **Auth DB:** `admin`

Or use a full URI:
```
mongodb://admin:password123@localhost:27017/school_library?authSource=admin
```

### Production Deployment

For production, use MongoDB Atlas:

```bash
# Use MONGODB_URI instead of host/port
MONGODB_URI=mongodb+srv://user:password@cluster.mongodb.net/school_library?retryWrites=true&w=majority
```

## Architecture

### Storage Layer

The application uses a storage abstraction layer that allows multiple backend implementations:

- **JSON Storage** (legacy): `storage/book_storage.py`, `storage/user_storage.py`
- **MongoDB Storage**: `storage/mongodb/book_storage.py`, `storage/mongodb/user_storage.py`

### Configuration

The MongoDB connection is managed by:

- **`config/database.py`**: Connection configuration and singleton manager
- **`MongoDBConfig`**: Reads environment variables
- **`MongoDBConnection`**: Manages connection lifecycle

### Auto-Incrementing IDs

MongoDB doesn't have built-in auto-increment like SQL databases. The implementation uses:

- Counter collections: `book_id_counter`, `user_id_counter`
- Atomic increment operations for thread-safe ID generation
- Pattern: `find_one_and_update` with `$inc` operator

Example:
```python
# Generated next book ID atomically
book_id = storage.get_next_book_id()  # Returns 1, 2, 3...
```

## Docker Compose Services

### Services

1. **MongoDB** (`mongodb`): Database service with health check
2. **App** (`app`): Main application (depends on MongoDB)
3. **App-Init** (`app-init`): Initialization service (creates indexes, counters)
4. **App-Dev** (`app-dev`): Development mode with hot reload
5. **App-Test** (`app-test`): Test runner with coverage

### Running Different Configurations

**Production:**
```bash
docker-compose --profile prod up
```

**Development (with hot-reload):**
```bash
docker-compose --profile dev up
```

**Testing:**
```bash
docker-compose --profile test up
```

**With monitoring (Prometheus):**
```bash
docker-compose --profile monitoring up
```

## Database Operations

### Book Storage

```python
from storage.mongodb.book_storage import MongoDBBookStorage
from models.book import Book

storage = MongoDBBookStorage()

# Get next ID
book_id = storage.get_next_book_id()  # Returns 1

# Add book
book = Book.create(book_id, "Python Guide", "John Doe")
storage.add_book(book)

# Retrieve books
all_books = storage.load_books()
book = storage.get_book_by_id(1)

# Search
results = storage.search_books(author="John", status="Available")

# Update
book.status = BookStatus.BORROWED
storage.update_book(book)

# Delete
storage.remove_book(1)
```

### User Storage

```python
from storage.mongodb.user_storage import MongoDBUserStorage
from models.user import User
from models.role import Role

storage = MongoDBUserStorage()

# Get next ID
user_id = storage.get_next_user_id()  # Returns 1

# Add user
user = User(id=user_id, username="alice", role=Role.STUDENT)
storage.add_user(user)

# Retrieve users
all_users = storage.load_users()
user = storage.get_user_by_id(1)
user = storage.get_user_by_username("alice")

# Search
results = storage.search_users(role=Role.STUDENT)

# Update
user.borrowed_book_ids.append(5)
storage.update_user(user)

# Delete
storage.remove_user(1)
```

## Indexes

The MongoDB implementation creates indexes for optimal query performance:

### Books Collection
- `id` (unique): Fast lookups by book ID
- `title`: Search by book title
- `author`: Search by author
- `status`: Filter by availability status

### Users Collection
- `id` (unique): Fast lookups by user ID
- `username` (unique): Ensure username uniqueness and fast lookups
- `role`: Filter users by role

## Testing

### Unit Tests with MongoDB

Tests use the same `MONGODB_DATABASE` as configured, using a separate `school_library_test` database:

```bash
# Run tests with MongoDB
DATABASE_TYPE=mongodb MONGODB_DATABASE=school_library_test pytest -v

# With Docker
docker-compose --profile test up
```

### GitHub Actions CI/CD

The CI pipeline includes a MongoDB service that:

1. Automatically starts before tests
2. Waits for MongoDB to be healthy
3. Tests run against the MongoDB instance
4. Service stops after tests complete

### Testing with JSON Storage (Legacy)

To test with JSON storage instead:

```bash
DATABASE_TYPE=json pytest -v
```

## Migration from JSON to MongoDB

### Data Migration Script

To migrate existing JSON data to MongoDB:

```python
from storage.book_storage import BookStorage as JSONBookStorage
from storage.mongodb.book_storage import MongoDBBookStorage

# Load from JSON
json_storage = JSONBookStorage()
books = json_storage.load_books()

# Write to MongoDB
mongo_storage = MongoDBBookStorage()
for book in books:
    mongo_storage.add_book(book)

print(f"Migrated {len(books)} books to MongoDB")
```

## Troubleshooting

### MongoDB Connection Error

**Error:** `ServerSelectionTimeoutError`

**Solution:**
- Check MongoDB is running: `docker-compose logs mongodb`
- Verify credentials in `.env`
- Check MONGODB_HOST points to correct server
- For Docker, ensure containers are on same network

### Unique Constraint Violation

**Error:** `DuplicateKeyError: E11000 duplicate key error`

**Solution:**
- Check for duplicate IDs or usernames
- Reset counters if needed: `db.book_id_counter.deleteOne({_id: "book_id"})`
- Reinitialize: `python scripts/init_mongodb.py`

### Slow Queries

**Solution:**
- Check indexes are created: `db.books.getIndexes()`
- Reinitialize: `python scripts/init_mongodb.py`
- Use MongoDB Compass to analyze query performance

## Security Best Practices

### Development (.env file)
- Use default credentials from `.env.example`
- Keep `.env` in `.gitignore` (never commit)
- Use `.env.local` for local overrides

### Production (Environment Variables)
- Use strong passwords (minimum 16 characters)
- Store credentials in CI/CD secrets
- Use MongoDB Atlas with IP whitelist
- Enable TLS/SSL for connections
- Use connection strings with authentication database specified

Example GitHub Secrets:
```
MONGODB_URI: mongodb+srv://[user]:[password]@cluster.mongodb.net/school_library?retryWrites=true&w=majority
```

### Code-Level Security
- Never hardcode credentials in source code
- Use environment variables exclusively
- Log connections without revealing passwords
- Validate and sanitize all user input before database queries

## Performance Considerations

1. **Indexes**: Ensure all frequently queried fields have indexes
2. **Batch Operations**: Use batch inserts for bulk data
3. **Connection Pooling**: Handled by PyMongo client automatically
4. **Query Optimization**: Use `.find()` projections to limit fields
5. **Database Load**: Monitor MongoDB metrics in production

## References

- [MongoDB Official Documentation](https://docs.mongodb.com/)
- [PyMongo Documentation](https://pymongo.readthedocs.io/)
- [MongoDB Atlas](https://www.mongodb.com/cloud/atlas)
- [MongoDB Docker Hub](https://hub.docker.com/_/mongo)

## Support

For issues or questions:
1. Check the troubleshooting section above
2. Review application logs: `docker-compose logs app`
3. Review MongoDB logs: `docker-compose logs mongodb`
4. Open an issue on GitHub with detailed logs
