# تكوين نشر Azure / Azure Deployment Configuration

## إعداد Azure App Service

### 1. إنشاء Web App
- نوع التشغيل: Python 3.10
- نظام التشغيل: Linux

### 2. Startup Command (مطلوب)
في Azure Portal > App Service > Configuration > General settings:

```
python run_app.py
```

أو عبر Azure CLI:
```bash
az webapp config set --resource-group <RG> --name <APP_NAME> --startup-file "python run_app.py"
```

### 3. GitHub Secrets للنشر التلقائي
أضف في GitHub Repository > Settings > Secrets:
- `AZURE_WEBAPP_PUBLISH_PROFILE`: ملف Publish Profile من Azure Portal

### 4. نشر Docker (اختياري)
استخدم `Dockerfile.app`:
```bash
docker build -f Dockerfile.app -t school-library-app .
docker run -p 8000:8000 school-library-app
```

## الوصول للتطبيق
- الواجهة الجديدة: `https://<your-app>.azurewebsites.net/app`
- API: `https://<your-app>.azurewebsites.net/api/execute`
