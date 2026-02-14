# دليل نشر التطبيق على Azure مع MongoDB Atlas

## المتطلبات:
1. حساب Azure
2. حساب MongoDB Atlas
3. حساب GitHub
4. Docker (للتطوير المحلي)

## الخطوة 1: إعداد MongoDB Atlas

### 1.1 إنشاء Cluster:
1. اذهب إلى https://www.mongodb.com/cloud/atlas
2. اضغط "Create" → اختر "Free Cluster" (M0)
3. اختر المنطقة والإعدادات
4. اضغط "Create Cluster"

### 1.2 إنشاء Database User:
1. اضغط "Database Access"
2. اضغط "Add New Database User"
3. أدخل Username و Password قوية
4. اضغط "Add User"

### 1.3 الحصول على Connection String:
1. اضغط "Clusters" → "Connect"
2. اختر "Drivers" → "Python"
3. انسخ Connection String:
```
mongodb+srv://USERNAME:PASSWORD@CLUSTER.mongodb.net/school_library?retryWrites=true&w=majority
```

### 1.4 إضافة IP Address:
1. اضغط "Network Access"
2. اضغط "Add IP Address"
3. اختر "Allow access from anywhere" أو أدخل IP الـ Azure App Service

---

## الخطوة 2: إعداد Azure

### 2.1 إنشاء Resource Group:
```bash
az group create \
  --name school-library-rg \
  --location eastus
```

### 2.2 إنشاء App Service Plan:
```bash
az appservice plan create \
  --name school-library-plan \
  --resource-group school-library-rg \
  --sku B1 \
  --is-linux
```

### 2.3 إنشاء Web App:
```bash
az webapp create \
  --resource-group school-library-rg \
  --plan school-library-plan \
  --name <YOUR_APP_NAME> \
  --deployment-container-image-name-user-name <username> \
  --deployment-container-image-name <image>
```

### 2.4 تعيين Environment Variables:
```bash
az webapp config appsettings set \
  --resource-group school-library-rg \
  --name <YOUR_APP_NAME> \
  --settings MONGODB_URI="mongodb+srv://USERNAME:PASSWORD@CLUSTER.mongodb.net/school_library?retryWrites=true&w=majority" \
  ENVIRONMENT=production \
  DEBUG=False \
  LOG_LEVEL=INFO
```

---

## الخطوة 3: GitHub Secrets (للـ CI/CD)

أضف هذه Secrets إلى GitHub:
1. اذهب إلى Repository Settings → Secrets → Actions
2. أضف:
   - `AZURE_APP_NAME`: اسم التطبيق على Azure
   - `AZURE_PUBLISH_PROFILE`: التنزيل من Azure Portal

### لتحميل Publish Profile:
1. اذهب إلى App Service على Azure
2. اضغط "Get publish profile" وحفظ الملف
3. انسخ محتوى الملف إلى GitHub Secret

---

## الخطوة 4: الاختبار المحلي

### مع MongoDB Atlas:
1. عدّل ملف `.env`:
```
MONGODB_URI=mongodb+srv://USERNAME:PASSWORD@CLUSTER.mongodb.net/school_library?retryWrites=true&w=majority
```

2. شغّل التطبيق:
```bash
python run_app.py
```

### مع Docker:
```bash
# بدون MongoDB محلي (فقط Atlas):
docker-compose -f docker-compose.production.yml up --build
```

---

## الخطوة 5: الـ Deployment التلقائي (GitHub Actions)

عند عمل `push` إلى `main` أو `ci.cd`:

1. يتم بناء Docker image
2. يتم رفع الـ image إلى GitHub Container Registry
3. يتم النشر على Azure App Service تلقائياً

---

## Troubleshooting

### المشكلة: "Failed to connect to MongoDB"
**الحل:**
- تحقق من Connection String
- تأكد من إضافة IP Address في MongoDB Atlas
- تحقق من متغيرات البيئة على Azure

### المشكلة: "Container failed to start"
**الحل:**
```bash
# عرض السجلات:
az webapp log tail --name <app-name> --resource-group <rg-name>
```

### المشكلة: "Database migrations failed"
**الحل:**
```bash
# إعادة تشغيل التطبيق:
az webapp restart --name <app-name> --resource-group <rg-name>
```

---

## الروابط المفيدة:

- MongoDB Atlas: https://www.mongodb.com/cloud/atlas
- Azure App Service: https://azure.microsoft.com/en-us/services/app-service/
- GitHub Actions: https://docs.github.com/en/actions
- Azure CLI: https://docs.microsoft.com/en-us/cli/azure/

---

## الخطوات التالية:

1. ✅ إعداد MongoDB Atlas
2. ✅ إعداد Azure
3. ✅ تعديل ملفات التطبيق (تم بالفعل)
4. ✅ إضافة GitHub Secrets
5. ✅ Deploy التطبيق
