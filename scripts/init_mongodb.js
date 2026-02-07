/**
 * MongoDB initialization script
 * This script runs when the MongoDB container starts
 */

// Create database admin user
db = db.getSiblingDB("school_library");

db.createCollection("books");
db.createCollection("users");
db.createCollection("book_id_counter");
db.createCollection("user_id_counter");

// Initialize ID counters
db.book_id_counter.insertOne({
    "_id": "book_id",
    "sequence_value": 0
});

db.user_id_counter.insertOne({
    "_id": "user_id",
    "sequence_value": 0
});

// Create indexes
db.books.createIndex({ "id": 1 }, { unique: true });
db.books.createIndex({ "title": 1 });
db.books.createIndex({ "author": 1 });
db.books.createIndex({ "status": 1 });

db.users.createIndex({ "id": 1 }, { unique: true });
db.users.createIndex({ "username": 1 }, { unique: true });
db.users.createIndex({ "role": 1 });

print("MongoDB initialization complete");
