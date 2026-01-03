# Database Schema - School Library Management System

## Overview
This document describes the database schema for the school library management system.

## Entity Relationship Diagram

```
┌─────────────────┐
│     Users       │
├─────────────────┤
│ UserID (PK)     │
│ Email           │
│ PasswordHash    │
│ FirstName       │
│ LastName        │
│ Role            │
│ Status          │
│ CreatedDate     │
└────────┬────────┘
         │
         ├──────────────────────────┐
         │                          │
         ▼                          ▼
┌─────────────────┐      ┌──────────────────┐
│  LibraryCards   │      │    Borrowings    │
├─────────────────┤      ├──────────────────┤
│ CardID (PK)     │      │ BorrowingID (PK) │
│ UserID (FK)     │      │ UserID (FK)      │
│ CardNumber      │      │ BookID (FK)      │
│ IssueDate       │      │ CheckoutDate     │
│ ExpiryDate      │      │ DueDate          │
│ Status          │      │ ReturnDate       │
└─────────────────┘      │ Fine             │
                         │ Status           │
                         └──────────────────┘
                                  │
         ┌────────────────────────┴─────────────┐
         │                                      │
         ▼                                      ▼
    ┌──────────┐                      ┌──────────────┐
    │  Books   │                      │ Reservations │
    ├──────────┤                      ├──────────────┤
    │ BookID   │◄─────────────────────│ ReservID(PK) │
    │ Title    │  (FK)                │ UserID (FK)  │
    │ Author   │                      │ BookID (FK)  │
    │ ISBN     │                      │ ReserveDate  │
    │ Genre    │                      │ ExpireDate   │
    │ Status   │                      │ Status       │
    │ Location │                      └──────────────┘
    │ Quantity │
    │ Condition│
    └──────────┘
```

## Tables Description

### Users Table
Stores user account information.

```sql
CREATE TABLE Users (
    UserID INT PRIMARY KEY IDENTITY(1,1),
    Email NVARCHAR(255) UNIQUE NOT NULL,
    PasswordHash NVARCHAR(MAX) NOT NULL,
    FirstName NVARCHAR(100) NOT NULL,
    LastName NVARCHAR(100) NOT NULL,
    Role NVARCHAR(50) NOT NULL, -- 'Student', 'Teacher', 'Librarian', 'Admin'
    Status NVARCHAR(50) NOT NULL DEFAULT 'Active', -- 'Active', 'Inactive', 'Suspended'
    CreatedDate DATETIME DEFAULT GETDATE(),
    UpdatedDate DATETIME DEFAULT GETDATE()
);
```

### Books Table
Stores book catalog information.

```sql
CREATE TABLE Books (
    BookID INT PRIMARY KEY IDENTITY(1,1),
    Title NVARCHAR(255) NOT NULL,
    Author NVARCHAR(255) NOT NULL,
    ISBN NVARCHAR(13) UNIQUE NOT NULL,
    Genre NVARCHAR(100),
    PublicationYear INT,
    Description NVARCHAR(MAX),
    Location NVARCHAR(100), -- Call number / Shelf location
    TotalCopies INT NOT NULL DEFAULT 1,
    AvailableCopies INT NOT NULL DEFAULT 1,
    Condition NVARCHAR(50), -- 'Excellent', 'Good', 'Worn', 'Damaged'
    CreatedDate DATETIME DEFAULT GETDATE(),
    UpdatedDate DATETIME DEFAULT GETDATE()
);
```

### LibraryCards Table
Stores library card information per user.

```sql
CREATE TABLE LibraryCards (
    CardID INT PRIMARY KEY IDENTITY(1,1),
    UserID INT NOT NULL FOREIGN KEY REFERENCES Users(UserID),
    CardNumber NVARCHAR(50) UNIQUE NOT NULL,
    IssueDate DATETIME DEFAULT GETDATE(),
    ExpiryDate DATETIME NOT NULL,
    Status NVARCHAR(50) NOT NULL DEFAULT 'Active',
    CreatedDate DATETIME DEFAULT GETDATE(),
    UpdatedDate DATETIME DEFAULT GETDATE()
);
```

### Borrowings Table
Tracks book checkout and return history.

```sql
CREATE TABLE Borrowings (
    BorrowingID INT PRIMARY KEY IDENTITY(1,1),
    UserID INT NOT NULL FOREIGN KEY REFERENCES Users(UserID),
    BookID INT NOT NULL FOREIGN KEY REFERENCES Books(BookID),
    CheckoutDate DATETIME DEFAULT GETDATE(),
    DueDate DATETIME NOT NULL,
    ReturnDate DATETIME,
    Fine DECIMAL(10, 2) DEFAULT 0,
    Status NVARCHAR(50) NOT NULL DEFAULT 'Borrowed', -- 'Borrowed', 'Returned', 'Overdue'
    CreatedDate DATETIME DEFAULT GETDATE(),
    UpdatedDate DATETIME DEFAULT GETDATE()
);
```

### Reservations Table
Tracks book reservations and holds.

```sql
CREATE TABLE Reservations (
    ReservationID INT PRIMARY KEY IDENTITY(1,1),
    UserID INT NOT NULL FOREIGN KEY REFERENCES Users(UserID),
    BookID INT NOT NULL FOREIGN KEY REFERENCES Books(BookID),
    ReservationDate DATETIME DEFAULT GETDATE(),
    ExpiryDate DATETIME,
    PickupDate DATETIME,
    Status NVARCHAR(50) NOT NULL DEFAULT 'Pending', -- 'Pending', 'Ready', 'Picked Up', 'Cancelled'
    QueuePosition INT,
    CreatedDate DATETIME DEFAULT GETDATE(),
    UpdatedDate DATETIME DEFAULT GETDATE()
);
```

## Key Relationships

1. **Users → LibraryCards** (1:1): Each user has one active library card
2. **Users → Borrowings** (1:N): One user can have multiple borrowings
3. **Users → Reservations** (1:N): One user can reserve multiple books
4. **Books → Borrowings** (1:N): One book can be borrowed multiple times
5. **Books → Reservations** (1:N): One book can be reserved multiple times

## Indexes

```sql
CREATE INDEX idx_users_email ON Users(Email);
CREATE INDEX idx_books_isbn ON Books(ISBN);
CREATE INDEX idx_books_title ON Books(Title);
CREATE INDEX idx_borrowings_userid ON Borrowings(UserID);
CREATE INDEX idx_borrowings_bookid ON Borrowings(BookID);
CREATE INDEX idx_borrowings_status ON Borrowings(Status);
CREATE INDEX idx_reservations_userid ON Reservations(UserID);
CREATE INDEX idx_reservations_bookid ON Reservations(BookID);
CREATE INDEX idx_reservations_status ON Reservations(Status);
```

## Data Types & Conventions

- **Primary Keys**: INT IDENTITY for auto-increment
- **Dates**: DATETIME for timestamps
- **Currency**: DECIMAL(10, 2) for fine amounts
- **Status Fields**: NVARCHAR(50) for enumeration values
- **Names/Text**: NVARCHAR for Unicode support (Arabic names)

## Future Enhancements

- Add audit logs table for tracking all changes
- Add notification preferences table
- Add book reviews/ratings table
- Add reading level/curriculum alignment fields