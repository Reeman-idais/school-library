# School Library Management System

A comprehensive school library management system designed to streamline library operations and enhance user experience for students, teachers, and library staff.

## 🎯 Project Overview

This is a full-stack web application that enables:
- **Students & Teachers**: Browse, search, borrow, and manage books
- **Librarians**: Manage catalog, track borrowings, and generate reports
- **Administrators**: System configuration and advanced analytics

## 📋 Features (Phase 1 - MVP)

### User Management
- User registration (Students, Teachers, Librarians)
- Secure login with JWT authentication
- Role-based access control
- Automatic library card generation

### Book Management
- Comprehensive book catalog
- Search by title, author, or ISBN
- Track book availability and location
- Manage multiple copies

### Borrowing System
- Checkout and return books
- Automatic due date calculation
- Overdue tracking and fine calculation
- Book renewal with limits
- View borrowing history

### Admin Features
- Add/edit/delete books
- User management
- Circulation monitoring
- Basic reporting

## 🏗️ Project Structure

```
school-library/
├── backend/                    # .NET Core API
│   ├── SchoolLibrary.API/
│   ├── SchoolLibrary.Data/
│   ├── SchoolLibrary.Services/
│   └── Tests/
├── frontend/                   # Web UI (HTML/CSS/JS)
│   ├── public/
│   ├── src/
│   └── assets/
├── docs/                       # Documentation
│   ├── API.md                  # API endpoints
│   ├── DATABASE.md             # Database schema
│   ├── SETUP.md                # Installation guide
│   ├── FEATURES.md             # Feature details
│   └── PROJECT_STRUCTURE.md    # Project structure
├── .gitignore
├── .env.example                # Configuration template
├── README.md
└── CONTRIBUTING.md
```

## 🚀 Quick Start

### Prerequisites
- .NET 8.0 SDK or later
- Node.js 18+
- SQL Server Express or SQLite
- Git

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/Reeman-idais/school-library.git
   cd school-library
   ```

2. **Setup Backend**
   ```bash
   cd backend
   dotnet restore
   copy ..\.env.example .env
   # Edit .env with your configuration
   dotnet ef database update
   dotnet run
   ```

3. **Setup Frontend**
   ```bash
   cd frontend
   npm install
   npm start
   ```

4. **Access Application**
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:5000
   - API Docs: http://localhost:5000/swagger

For detailed setup instructions, see [SETUP.md](docs/SETUP.md)

## 📚 Documentation

- [Project Structure](docs/PROJECT_STRUCTURE.md) - Directory organization and tech stack
- [Database Schema](docs/DATABASE.md) - Complete database design
- [API Endpoints](docs/API.md) - All REST API endpoints
- [Setup Guide](docs/SETUP.md) - Installation and configuration
- [Features](docs/FEATURES.md) - Detailed feature specifications
- [Contributing](CONTRIBUTING.md) - Contribution guidelines

## 🔐 Technology Stack

### Backend
- **Framework**: ASP.NET Core 8.0
- **Language**: C#
- **Database**: SQL Server / SQLite
- **ORM**: Entity Framework Core
- **Authentication**: JWT

### Frontend
- **Markup**: HTML5
- **Styling**: CSS3 / Bootstrap 5
- **Scripting**: Vanilla JavaScript
- **API Client**: Fetch API

### Tools
- **Version Control**: Git
- **API Documentation**: Swagger/OpenAPI
- **Testing**: xUnit, Jest

## 📈 Development Phases

### Phase 1: MVP ✅ (Current)
- Core user management and authentication
- Basic book catalog and search
- Borrowing and return system
- Library card generation
- Simple reporting

**Status**: Planning & Documentation Complete

### Phase 2: Advanced Features 📋
- Reservation and hold system
- Advanced search with filters
- User dashboard
- Enhanced reporting and analytics

**Target**: Q2 2026

### Phase 3: Mobile & Admin 🔄
- Mobile application
- Admin dashboard
- Advanced analytics and statistics
- Staff scheduling

**Target**: Q3 2026

### Phase 4: Integration & AI 🎯
- AI-powered recommendations
- E-book and multimedia support
- System integration (SMS, Calendar, etc.)
- Automated notifications

**Target**: Q4 2026+

## 📖 Key Components

### Database
Fully designed relational database with:
- **Users Table**: User accounts with roles
- **Books Table**: Book catalog with availability tracking
- **LibraryCards Table**: Automatic card generation
- **Borrowings Table**: Circulation history
- **Reservations Table**: Book holds and reservations

See [DATABASE.md](docs/DATABASE.md) for complete schema.

### API Endpoints
Comprehensive REST API with:
- Authentication endpoints (register, login)
- Book management (search, add, update, delete)
- Borrowing operations (checkout, return, renew)
- User management (profile, library card)
- Admin operations (book management, user management)

See [API.md](docs/API.md) for complete endpoint documentation.

## 🛠️ Development Workflow

1. Create a feature branch: `git checkout -b feature/feature-name`
2. Make your changes and test thoroughly
3. Commit with clear messages: `git commit -m "Add feature description"`
4. Push to your branch: `git push origin feature/feature-name`
5. Create a Pull Request for review

## 📝 API Example

### Register User
```bash
curl -X POST http://localhost:5000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "student@school.edu",
    "password": "SecurePass123!",
    "firstName": "Ahmed",
    "lastName": "Mohammed",
    "role": "Student"
  }'
```

### Search Books
```bash
curl -X GET "http://localhost:5000/api/books?q=Programming" \
  -H "Authorization: Bearer <token>"
```

See [API.md](docs/API.md) for complete endpoint documentation.

## 🧪 Testing

### Backend Unit Tests
```bash
cd backend/Tests
dotnet test
```

### Frontend Tests
```bash
cd frontend
npm test
```

## 🐛 Issues & Debugging

For common issues and solutions, see [SETUP.md - Common Issues](docs/SETUP.md#common-issues)

## 👥 Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

See [CONTRIBUTING.md](CONTRIBUTING.md) for detailed guidelines.

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 👨‍💻 Authors

- **Reeman-idais** - Project Initiator and Maintainer

## 📞 Support & Contact

For support, please:
1. Check existing issues on [GitHub Issues](https://github.com/Reeman-idais/school-library/issues)
2. Create a new issue with detailed description
3. Include error messages and steps to reproduce

## 🙏 Acknowledgments

- School community for requirements and feedback
- Open-source libraries and frameworks
- Contributors and reviewers

## 📊 Project Status

**Current Phase**: MVP (Phase 1)
**Status**: 🟡 Planning & Documentation Complete
**Last Updated**: January 3, 2026

### Current Tasks
- ✅ Project structure and organization
- ✅ Database design and schema
- ✅ API endpoints documentation
- ✅ Setup and installation guide
- ✅ Features specification
- 🟡 Backend implementation (Next)
- 🟡 Frontend implementation (Next)
- ⚪ Testing and QA
- ⚪ Deployment preparation

### Roadmap
- Phase 1: Target Q1 2026 (Documentation ✅, Implementation 🔄)
- Phase 2: Target Q2 2026
- Phase 3: Target Q3 2026
- Phase 4: Target Q4 2026+

## 🔗 Useful Links

- [GitHub Repository](https://github.com/Reeman-idais/school-library)
- [.NET Documentation](https://docs.microsoft.com/dotnet/)
- [Bootstrap Documentation](https://getbootstrap.com/docs/)
- [JWT Introduction](https://jwt.io/introduction)
- [Entity Framework Core Docs](https://docs.microsoft.com/ef/core/)

---

**Made with ❤️ for School Libraries**
