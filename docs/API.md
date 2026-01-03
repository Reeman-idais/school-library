# API Endpoints Documentation - School Library System

## Base URL
```
http://localhost:5000/api
```

## Authentication
All endpoints (except login/register) require JWT token in header:
```
Authorization: Bearer <jwt_token>
```

---

## Phase 1: MVP Endpoints

### Authentication

#### Register User
```
POST /auth/register
Content-Type: application/json

{
  "email": "student@school.edu",
  "password": "SecurePass123!",
  "firstName": "Ahmed",
  "lastName": "Mohammed",
  "role": "Student"
}

Response: 200 OK
{
  "userId": 1,
  "email": "student@school.edu",
  "message": "User registered successfully"
}
```

#### Login
```
POST /auth/login
Content-Type: application/json

{
  "email": "student@school.edu",
  "password": "SecurePass123!"
}

Response: 200 OK
{
  "token": "eyJhbGciOiJIUzI1NiIs...",
  "userId": 1,
  "role": "Student",
  "expiresIn": 3600
}
```

---

### Users

#### Get Current User Profile
```
GET /users/profile
Authorization: Bearer <token>

Response: 200 OK
{
  "userId": 1,
  "email": "student@school.edu",
  "firstName": "Ahmed",
  "lastName": "Mohammed",
  "role": "Student",
  "libraryCard": {
    "cardNumber": "SL-2024-001",
    "expiryDate": "2025-12-31",
    "status": "Active"
  }
}
```

#### Get User Library Card
```
GET /users/{userId}/library-card
Authorization: Bearer <token>

Response: 200 OK
{
  "cardId": 1,
  "cardNumber": "SL-2024-001",
  "userId": 1,
  "issueDate": "2024-01-15",
  "expiryDate": "2025-12-31",
  "status": "Active"
}
```

---

### Books

#### Get All Books
```
GET /books?page=1&pageSize=20&status=available
Authorization: Bearer <token>

Query Parameters:
- page: int (default: 1)
- pageSize: int (default: 20, max: 100)
- status: string (available, all)
- genre: string (optional)

Response: 200 OK
{
  "totalCount": 150,
  "pageNumber": 1,
  "pageSize": 20,
  "data": [
    {
      "bookId": 1,
      "title": "The Great Book",
      "author": "John Author",
      "isbn": "978-0-123456-78-9",
      "genre": "Fiction",
      "publishYear": 2023,
      "location": "A-123",
      "totalCopies": 3,
      "availableCopies": 1,
      "condition": "Good",
      "description": "An amazing story..."
    }
  ]
}
```

#### Get Single Book
```
GET /books/{bookId}
Authorization: Bearer <token>

Response: 200 OK
{
  "bookId": 1,
  "title": "The Great Book",
  "author": "John Author",
  "isbn": "978-0-123456-78-9",
  "genre": "Fiction",
  "publishYear": 2023,
  "location": "A-123",
  "totalCopies": 3,
  "availableCopies": 1,
  "condition": "Good",
  "description": "An amazing story...",
  "currentBorrowings": 2,
  "reservations": 0
}
```

#### Search Books
```
GET /books/search?q=title+or+author
Authorization: Bearer <token>

Query Parameters:
- q: string (search query)

Response: 200 OK
{
  "totalCount": 5,
  "data": [
    {
      "bookId": 1,
      "title": "The Great Book",
      "author": "John Author",
      "isbn": "978-0-123456-78-9"
    }
  ]
}
```

---

### Borrowings

#### Checkout Book
```
POST /borrowings/checkout
Content-Type: application/json
Authorization: Bearer <token>

{
  "bookId": 1
}

Response: 201 Created
{
  "borrowingId": 10,
  "userId": 1,
  "bookId": 1,
  "bookTitle": "The Great Book",
  "checkoutDate": "2024-01-20T10:30:00Z",
  "dueDate": "2024-02-03T23:59:59Z",
  "status": "Borrowed",
  "loanPeriodDays": 14
}
```

#### Return Book
```
POST /borrowings/{borrowingId}/return
Content-Type: application/json
Authorization: Bearer <token>

{
  "condition": "Good"
}

Response: 200 OK
{
  "borrowingId": 10,
  "returnDate": "2024-01-25T14:20:00Z",
  "fine": 0,
  "status": "Returned",
  "message": "Book returned successfully"
}
```

#### Get User's Borrowed Items
```
GET /borrowings/my-items?status=borrowed
Authorization: Bearer <token>

Query Parameters:
- status: string (borrowed, returned, overdue, all)

Response: 200 OK
{
  "totalCount": 3,
  "data": [
    {
      "borrowingId": 10,
      "bookId": 1,
      "bookTitle": "The Great Book",
      "author": "John Author",
      "checkoutDate": "2024-01-20T10:30:00Z",
      "dueDate": "2024-02-03T23:59:59Z",
      "daysUntilDue": 14,
      "status": "Borrowed"
    }
  ]
}
```

#### Renew Borrowed Item
```
POST /borrowings/{borrowingId}/renew
Authorization: Bearer <token>

Response: 200 OK
{
  "borrowingId": 10,
  "newDueDate": "2024-02-17T23:59:59Z",
  "renewalCount": 1,
  "message": "Book renewed successfully"
}
```

---

### Librarian/Admin Endpoints (Phase 1)

#### Add New Book
```
POST /admin/books
Content-Type: application/json
Authorization: Bearer <token>

{
  "title": "New Book Title",
  "author": "Author Name",
  "isbn": "978-0-123456-78-9",
  "genre": "Fiction",
  "publishYear": 2024,
  "description": "Book description",
  "location": "A-123",
  "totalCopies": 2,
  "condition": "Excellent"
}

Response: 201 Created
{
  "bookId": 25,
  "message": "Book added successfully"
}
```

#### Update Book Information
```
PUT /admin/books/{bookId}
Content-Type: application/json
Authorization: Bearer <token>

{
  "title": "Updated Title",
  "condition": "Good",
  "totalCopies": 3
}

Response: 200 OK
{
  "bookId": 25,
  "message": "Book updated successfully"
}
```

#### Delete Book
```
DELETE /admin/books/{bookId}
Authorization: Bearer <token>

Response: 204 No Content
```

---

## Error Responses

### 400 Bad Request
```json
{
  "status": 400,
  "message": "Invalid input",
  "errors": [
    {
      "field": "email",
      "message": "Email is required"
    }
  ]
}
```

### 401 Unauthorized
```json
{
  "status": 401,
  "message": "Unauthorized access"
}
```

### 403 Forbidden
```json
{
  "status": 403,
  "message": "You don't have permission for this action"
}
```

### 404 Not Found
```json
{
  "status": 404,
  "message": "Resource not found"
}
```

### 500 Internal Server Error
```json
{
  "status": 500,
  "message": "Internal server error",
  "traceId": "0HN1GH5JRVDDE:00000001"
}
```

---

## Rate Limiting
- 100 requests per minute per user
- Response header: `X-RateLimit-Remaining`

## Versioning
Current API Version: `v1`
Future versions will use: `/api/v2/`
