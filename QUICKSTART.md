# ⚡ Quick Start - Test & Deploy

**Complete guide to test the School Library application locally and deploy to Azure.**

---

## 🚀 5-Minute Quick Test

### Step 1: Start the Application
```bash
python run_app.py
```

**Expected Output:**
```
Initializing database...
✓ Added user: admin (LIBRARIAN)
✓ User already exists: tala
✓ Added book: A Brief History of Time (ID: 1001)
...

Library Management System - Web Interface
Server running at http://localhost:8000/
  - New User App:    http://localhost:8000/app
  - Documentation:   http://localhost:8000/docs.html
  ...
```

### Step 2: Open in Browser
```
http://localhost:8000/app
```

### Step 3: Test Login

**Test User 1: Regular User**
- Username: `tala`
- Password: `1234`
- Expected: See all books, can pick books

**Test User 2: Librarian**
- Username: `admin`
- Password: `1234`
- Expected: See management panel, can add/edit books

### Step 4: Verify Books Display
- [ ] At least 4 books should be visible
- [ ] Books show title, author, and status
- [ ] Search works (type in search box)
- [ ] Can pick books (as user)
- [ ] Can add new book (as librarian)

---

## 🧪 Run Full API Tests

```bash
# Test all API endpoints
python scripts/test_api.py

# Expected: All tests pass (green ✓ marks)
```

---

## 🐳 Test with Docker (Optional)

```bash
# Build image
docker build -t school-library:latest .

# Run container
docker run -p 8000:8000 -e MONGODB_URI="YOUR_MONGODB_URI" school-library:latest

# Test health
curl http://localhost:8000/health
```

---

## 📦 Deploy to Azure

### Prerequisites
- Have `.env` file with MongoDB connection
- Azure CLI installed (`choco install azure-cli`)
- Azure subscription active

### Deploy Command

#### **Using PowerShell (Windows) - RECOMMENDED**
```powershell
# Login to Azure
az login

# Run deployment (handles everything)
.\scripts\deploy_to_azure.ps1
```

**Script will:**
1. ✅ Create Resource Group
2. ✅ Create App Service Plan  
3. ✅ Create Web App
4. ✅ Set environment variables
5. ✅ Get Publish Profile

#### **Or deploy manually**

```bash
# Step 1: Login
az login

# Step 2: Create Resource Group
az group create \
  --name school-library-rg \
  --location eastus

# Step 3: Create App Service Plan (B1 = cheapest tier with always-on)
az appservice plan create \
  --name school-library-plan \
  --resource-group school-library-rg \
  --sku B1 \
  --is-linux

# Step 4: Create Web App
az webapp create \
  --resource-group school-library-rg \
  --plan school-library-plan \
  --name school-library-app \
  --runtime "PYTHON|3.10"

# Step 5: Configure environment
az webapp config appsettings set \
  --resource-group school-library-rg \
  --name school-library-app \
  --settings \
    MONGODB_URI="mongodb+srv://reeman:Reeman@cluster0.nwwzgip.mongodb.net/school_library" \
    ENVIRONMENT="production" \
    DEBUG="False" \
    LOG_LEVEL="INFO" \
    WEBSITES_PORT="8000" \
    DATABASE_TYPE="mongodb"

# Step 6: Deploy (using GitHub or local Git)
# Option A: Deploy from local Git
az webapp deployment source config-local-git \
  --resource-group school-library-rg \
  --name school-library-app

# Option B: Deploy from ZIP
cd project-root
zip -r deploy.zip .
az webapp deployment source config-zip \
  --resource-group school-library-rg \
  --name school-library-app \
  --src-path ./deploy.zip
```

### Verify Deployment

```bash
# Open in browser
az webapp open --resource-group school-library-rg --name school-library-app

# Check health
curl https://school-library-app.azurewebsites.net/health

# View logs
az webapp log tail --resource-group school-library-rg --name school-library-app
```

---

## 🎯 Azure URLs

After deployment, the app will be available at:

| URL | Purpose |
|-----|---------|
| `https://school-library-app.azurewebsites.net/app` | 📱 Main Application |
| `https://school-library-app.azurewebsites.net/docs.html` | 📖 Documentation |
| `https://school-library-app.azurewebsites.net/logs.html` | 📊 Logs Dashboard |
| `https://school-library-app.azurewebsites.net/health` | ✅ Health Check |

---

## 🔍 Troubleshooting

### "Cannot connect to localhost:8000"
```bash
# Make sure nothing is using port 8000
lsof -i :8000  # Mac/Linux
netstat -ano | findstr :8000  # Windows

# Kill the process if needed
kill -9 <PID>  # Mac/Linux
taskkill /PID <PID> /F  # Windows
```

### "MongoDB connection error"
```bash
# Verify connection string in .env
# Test MongoDB connection
python -c "from pymongo import MongoClient; client = MongoClient('YOUR_URI'); print(client.admin.command('ping'))"
```

### "No books visible after login"
- Database initialization runs on first startup (wait 30 seconds)
- Refresh the browser page
- Check logs for errors

### "Users can't login"
```bash
# Verify test users exist in MongoDB
# Connect to MongoDB Atlas and check:
db.users.find()
```

---

## 📋 Checklist Before Deployment

- [ ] Application runs locally without errors
- [ ] Can login with admin/1234 (librarian)
- [ ] Can login with tala/1234 (user)
- [ ] Books are displayed correctly
- [ ] Can pick books (as user)
- [ ] Can add new book (as librarian)
- [ ] API tests pass: `python scripts/test_api.py`
- [ ] `.env` file has correct MONGODB_URI
- [ ] Docker builds successfully: `docker build -t school-library:latest .`
- [ ] Health endpoint responds: `http://localhost:8000/health`
- [ ] No errors in console/logs

---

## 📞 Support

### Need Help?

**Check these files:**
- 📖 [README.md](README.md) - Project overview
- 🚀 [QUICK_AZURE_SETUP.md](QUICK_AZURE_SETUP.md) - Azure setup steps
- 🧪 [AZURE_DEPLOYMENT_TESTING.md](AZURE_DEPLOYMENT_TESTING.md) - Complete testing guide
- 📝 [CODE_REVIEW_SUMMARY.md](CODE_REVIEW_SUMMARY.md) - All fixes made

### Common Questions

**Q: Can I use a different port?**
```bash
python run_app.py 3000  # Use port 3000
PORT=3000 python run_app.py  # Or set env var
```

**Q: How do I reset the database?**
```bash
# Run the init script to recreate test data
python scripts/init_db.py
```

**Q: Can I use fake data instead of MongoDB?**
```bash
# Set DATABASE_TYPE=fake in .env
# This uses in-memory fake storage (test only)
```

**Q: How do I view Azure logs?**
```bash
az webapp log tail --resource-group school-library-rg --name school-library-app
```

---

## ✅ Success Criteria

Your deployment is successful when:

1. ✅ Can visit `https://school-library-app.azurewebsites.net/app`
2. ✅ Can login with admin/1234
3. ✅ Books display from database
4. ✅ Can perform book operations
5. ✅ Health check passes
6. ✅ No errors in logs

---

**Status: READY FOR DEPLOYMENT** 🚀

All code has been reviewed and fixed. The application is production-ready for Azure deployment.
