# 🚀 Azure Deployment & Testing Guide

**School Library Management System** - Complete guide for testing and deploying to Azure.

---

## ✅ PreDeployment Checklist

### Environment Setup

- [ ] MongoDB Atlas cluster is running and accessible
- [ ] Connection string: `mongodb+srv://reeman:Reeman@cluster0.nwwzgip.mongodb.net/school_library`
- [ ] `.env` file contains `MONGODB_URI` (see below)
- [ ] Flask/Python dependencies installed

### Required Environment Variables

Create or verify `.env` file in project root:

```env
# Application Settings
APP_PORT=8000
ENVIRONMENT=production
DEBUG=false
LOG_LEVEL=INFO

# Database (MongoDB Atlas)
DATABASE_TYPE=mongodb
MONGODB_URI=mongodb+srv://reeman:Reeman@cluster0.nwwzgip.mongodb.net/school_library?retryWrites=true&w=majority&appName=Cluster0

# Logging
LOG_DIR=./logs
LOG_FORMAT=json

# Security
SECRET_KEY=change-me-in-production
CORS_ORIGINS=*

# API Configuration
API_TITLE=School Library API
API_VERSION=1.0.0
```

---

## 🔧 Local Testing

### 1. Install Dependencies

```bash
# Install Poetry
pip install poetry

# Install project dependencies
poetry install

# Or if Poetry is already installed
poetry install --no-root --only main
```

### 2. Start the Application

```bash
# Using Poetry
poetry run python run_app.py

# Or directly
python run_app.py 8000
```

The application will:
- Start on `http://localhost:8000`
- Initialize database with test users and books (if not already present)
- Load the web interface

### 3. Test Users

**Default test credentials** (auto-created):

| Username | Password | Role | Purpose |
|----------|----------|------|---------|
| `admin` | `1234` | Librarian | Manage books & users |
| `tala` | `1234` | User | Browse & pick books |
| `reman` | `4321` | User | Browse & pick books |

### 4. Test All Features

#### A. **Login Testing**
```bash
# Test endpoint: POST /api/login
# Request:
{
  "username": "admin",
  "password": "1234"
}

# Expected response:
{
  "success": true,
  "role": "librarian",
  "username": "admin"
}
```

#### B. **Books Data Testing**
```bash
# Get all books: GET /api/books
# Expected: Array of book objects with id, title, author, status, picked_by

# Add new book (librarian only):
# POST /api/execute
{
  "command": "add-book",
  "args": ["--id", "2001", "--title", "New Book", "--author", "Author Name", "--librarian"]
}
```

#### C. **User Operations**
```bash
# Register new user:
# POST /api/execute
{
  "command": "register-user",
  "args": ["--username", "newuser", "--password", "5678", "--role", "user"]
}
```

#### D. **Web Interface Testing**

Visit `http://localhost:8000/app`:

1. **Login as User (tala/1234)**
   - [ ] Login succeeds
   - [ ] Books list displays all available books
   - [ ] Can pick (reserve) a book
   - [ ] Picked books appear in "My Picks" section

2. **Login as Librarian (admin/1234)**
   - [ ] Login succeeds
   - [ ] Can see all books with full details
   - [ ] Can add new books
   - [ ] Can edit book information
   - [ ] Can delete books
   - [ ] Can view and approve picked books
   - [ ] Can register new users

---

## 📊 Database Verification

### Check MongoDB Data

```bash
# Using MongoDB Shell (mongosh)
mongosh "mongodb+srv://reeman:Reeman@cluster0.nwwzgip.mongodb.net/school_library"

# Then run:
db.users.find()          # See all users
db.books.find()          # See all books
db.users.countDocuments() # Should be ≥ 3
db.books.countDocuments() # Should be ≥ 4
```

### Reset Database (if needed)

```python
# Run this Python script to clear and reinitialize:
python scripts/init_db.py
```

---

## 🐳 Docker Testing (Optional)

### Build Docker Image

```bash
docker build -t school-library:latest .
```

### Run with Docker Compose

```bash
docker-compose up
```

The app will be available at `http://localhost:8000/app`

---

## 🚀 Deploy to Azure

### Step 1: Prepare for Deployment

```bash
# Ensure all changes are committed
git status
git add .
git commit -m "Ready for Azure deployment"

# Verify Dockerfile and docker-compose files
```

### Step 2: Run Azure Deployment Script

#### Option A: Using PowerShell (Windows)
```powershell
# First install Azure CLI if not already installed
choco install azure-cli

# Login to Azure
az login

# Run deployment script
.\scripts\deploy_to_azure.ps1
```

#### Option B: Manual Azure CLI Commands
```bash
# Login
az login

# Create Resource Group
az group create \
  --name school-library-rg \
  --location eastus

# Create App Service Plan
az appservice plan create \
  --name school-library-plan \
  --resource-group school-library-rg \
  --sku B1 \
  --is-linux

# Create Web App with Python 3.10
az webapp create \
  --resource-group school-library-rg \
  --plan school-library-plan \
  --name school-library-app \
  --runtime "PYTHON|3.10"

# Set environment variables
az webapp config appsettings set \
  --resource-group school-library-rg \
  --name school-library-app \
  --settings \
    MONGODB_URI="mongodb+srv://reeman:Reeman@cluster0.nwwzgip.mongodb.net/school_library?retryWrites=true&w=majority&appName=Cluster0" \
    ENVIRONMENT="production" \
    DEBUG="False" \
    LOG_LEVEL="INFO" \
    WEBSITES_PORT="8000" \
    DATABASE_TYPE="mongodb"

# Deploy code (using local Git)
az webapp deployment source config-local-git \
  --resource-group school-library-rg \
  --name school-library-app

# Or deploy from a ZIP file
az webapp deployment source config-zip \
  --resource-group school-library-rg \
  --name school-library-app \
  --src-path ./deploy.zip
```

### Step 3: Verify Deployment

```bash
# Open the app in browser
az webapp open \
  --resource-group school-library-rg \
  --name school-library-app

# Check health
curl https://school-library-app.azurewebsites.net/health

# View logs
az webapp log tail \
  --resource-group school-library-rg \
  --name school-library-app
```

---

## 🔍 Troubleshooting

### Issue: "MongoDB Connection Failed"

**Solution:** Verify your connection string in `.env`:
```bash
# Test connection manually
python -c "from pymongo import MongoClient; client = MongoClient('YOUR_URI'); print(client.admin.command('ping'))"
```

### Issue: "Port 8000 already in use"

**Solution:**
```bash
# Unix/Linux/Mac
lsof -i :8000
kill -9 <PID>

# Windows PowerShell
Get-Process -Id (Get-NetTCPConnection -LocalPort 8000).OwningProcess
Stop-Process -Id <PID> -Force
```

### Issue: "Module not found" on Azure

**Solution:** Check Docker logs:
```bash
az webapp log tail --resource-group school-library-rg --name school-library-app
```

Ensure `pyproject.toml` has all dependencies listed.

### Issue: Books/Users not showing on first login

**Solution:** Database initialization might still be running. Wait 30 seconds and refresh the page. Check logs:
```bash
# Local
tail -f ./logs/library.log

# Azure
az webapp log tail --resource-group school-library-rg --name school-library-app
```

---

## 📋 Post Deployment Steps

### 1. Verify All Users Can Login
Test with each of the default credentials above.

### 2. Add More Test Data (Optional)
Use the librarian interface to add more books.

### 3. Monitor Application
- Check Azure Monitor dashboard in Azure Portal
- Review logs regularly for errors

### 4. Set up Custom Domain (Optional)
```bash
az webapp config hostname add \
  --resource-group school-library-rg \
  --webapp-name school-library-app \
  --hostname yourdomain.com
```

---

## 📞 Support URLs

After deployment:

- **Web App**: `https://school-library-app.azurewebsites.net/app`
- **API Docs**: `https://school-library-app.azurewebsites.net/docs.html`
- **Health Check**: `https://school-library-app.azurewebsites.net/health`
- **Logs**: `https://school-library-app.azurewebsites.net/logs.html`

---

## 🔒 Security Notes

- Change `SECRET_KEY` in production
- Use environment variables, NOT hard-coded credentials
- Ensure MongoDB Atlas IP whitelist includes Azure App Service IPs
- Enable HTTPS (Azure provides free SSL)
- Monitor logs for suspicious activity

---

## ✨ Success Criteria

Before considering deployment complete, verify:

- [ ] Can login as admin
- [ ] Can login as regular users
- [ ] All books display correctly
- [ ] Can add a new book (as admin)
- [ ] Can pick/reserve books (as user)
- [ ] Can manage borrowed books (as admin)
- [ ] Register new user works
- [ ] All API endpoints respond with proper JSON
- [ ] Docker health check passes
- [ ] Application responds to /health endpoint
- [ ] No errors in logs after 5 minutes of usage
