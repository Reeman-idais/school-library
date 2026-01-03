# Setup and Installation Guide

## Prerequisites

Before you begin, ensure you have the following installed on your system:

### Backend Requirements
- **.NET 8.0 SDK** or later - [Download](https://dotnet.microsoft.com/download/dotnet/8.0)
- **Visual Studio 2022** or **VS Code** with C# extension
- **SQL Server Express** or **SQLite** for development

### Frontend Requirements
- **Node.js 18+** - [Download](https://nodejs.org/)
- Modern web browser (Chrome, Firefox, Edge, Safari)

### Development Tools
- **Git** - [Download](https://git-scm.com/)
- **Postman** or **Thunder Client** (for API testing)

---

## Installation Steps

### 1. Clone the Repository

```bash
git clone https://github.com/Reeman-idais/school-library.git
cd school-library
```

### 2. Backend Setup

#### Step 2.1: Navigate to Backend Directory
```bash
cd backend
```

#### Step 2.2: Restore NuGet Packages
```bash
dotnet restore
```

#### Step 2.3: Create Configuration File
Copy `.env.example` to `.env` and update with your settings:

```bash
copy ../.env.example .env
```

Edit `.env` file:
```
DatabaseConnection=Server=localhost;Database=SchoolLibraryDB;Trusted_Connection=true;
JwtSecret=YourSuperSecretKeyWith32CharactersMinimumLength
JwtIssuer=SchoolLibraryApp
JwtAudience=SchoolLibraryUsers
AppUrl=http://localhost:5000
```

#### Step 2.4: Create Database
For SQL Server:
```bash
dotnet ef migrations add InitialCreate
dotnet ef database update
```

For SQLite (development):
The database will be created automatically on first run.

#### Step 2.5: Run Backend
```bash
dotnet run
```

Backend will be available at: `http://localhost:5000`

API documentation (Swagger): `http://localhost:5000/swagger`

---

### 3. Frontend Setup

#### Step 3.1: Navigate to Frontend Directory
```bash
cd frontend
```

#### Step 3.2: Install Dependencies
```bash
npm install
```

#### Step 3.3: Create Configuration File
Create `config.js`:
```javascript
const config = {
  apiBaseUrl: 'http://localhost:5000/api',
  appName: 'School Library Management System',
  version: '1.0.0'
};
```

#### Step 3.4: Run Frontend
```bash
npm start
```

Frontend will be available at: `http://localhost:3000`

---

## Common Issues

### Issue: Port Already in Use
**Solution:**
```bash
# Find process using port 5000
netstat -ano | findstr :5000

# Kill process
taskkill /PID <ProcessId> /F
```

### Issue: Database Connection Failed
**Solution:**
1. Verify SQL Server is running
2. Check connection string in `.env`
3. Ensure database user has proper permissions

### Issue: CORS Error
**Solution:**
Ensure `AllowedOrigins` in backend `.env` includes your frontend URL

---

## Next Steps

1. Review documentation in docs/ folder
2. Understand database design
3. Explore API endpoints
4. Start developing features