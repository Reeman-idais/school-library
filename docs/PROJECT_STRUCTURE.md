# School Library Management System - Project Structure

## Directory Overview

```
school-library/
├── backend/                    # .NET Core API backend
│   ├── SchoolLibrary.API/      # Main API project
│   ├── SchoolLibrary.Data/     # Data access and models
│   ├── SchoolLibrary.Services/ # Business logic
│   └── Tests/                  # Unit and integration tests
├── frontend/                   # Web UI (HTML/CSS/JavaScript)
│   ├── public/                 # Static assets
│   ├── src/                    # JavaScript/CSS source
│   ├── index.html              # Main page
│   └── assets/                 # Images, fonts, etc.
├── docs/                       # Documentation
│   ├── API.md                  # API endpoints documentation
│   ├── DATABASE.md             # Database schema
│   ├── SETUP.md                # Installation and setup guide
│   └── FEATURES.md             # Features specification
├── .gitignore
├── .env.example                # Environment variables template
└── README.md                   # Project overview
```

## Technology Stack

### Backend
- **Framework**: ASP.NET Core 8.0
- **Language**: C#
- **Database**: SQL Server / SQLite (development)
- **ORM**: Entity Framework Core
- **Authentication**: JWT (JSON Web Tokens)

### Frontend
- **Markup**: HTML5
- **Styling**: CSS3 / Bootstrap 5
- **Scripting**: Vanilla JavaScript / Fetch API
- **Build**: None required (static files)

### Tools & Services
- **Version Control**: Git / GitHub
- **API Documentation**: Swagger/OpenAPI
- **Testing**: xUnit for backend, Jest for frontend

## Project Phases

### Phase 1: MVP (Current Focus)
- Basic catalog management
- User management (students, teachers, librarians)
- Simple borrowing/returning system
- Basic search functionality
- Library card system

### Phase 2: Advanced Features
- Reservation/Hold system
- Advanced search with filters
- User dashboard
- Basic reporting

### Phase 3: Mobile & Administration
- Mobile application
- Admin dashboard
- Advanced analytics
- Staff scheduling

### Phase 4: Integration & AI
- E-book support
- Recommendation engine
- External system integration
- Advanced automation

## Development Workflow

1. Create feature branch: `git checkout -b feature/feature-name`
2. Implement changes
3. Write tests
4. Create pull request
5. Code review and merge to main

## Getting Started

See [SETUP.md](SETUP.md) for detailed installation instructions.