# 🚀 النشر على Azure - خطوات سريعة (5 دقائق)

## ✅ الحالة الحالية:
- ✅ MongoDB Atlas متصل
- ✅ بيانات الاتصال معدة في `.env.production`
- ✅ GitHub Actions جاهز

---

## 📋 الخطوات (اختر واحدة):

### **الطريقة الأولى: PowerShell (الأسهل للـ Windows)**

```powershell
# 1. تثبيت Azure CLI:
choco install azure-cli

# 2. تسجيل الدخول:
az login

# 3. تشغيل الـ script التلقائي:
.\scripts\deploy_to_azure.ps1

# سيقوم الـ script بـ:
# - إنشاء Resource Group
# - إنشاء App Service Plan
# - إنشاء Web App
# - تعيين البيانات
# - تحميل Publish Profile
```

---

### **الطريقة الثانية: Azure CLI (الأوامر اليدوية)**

```bash
# 1. تسجيل الدخول:
az login

# 2. إنشاء المجموعة:
az group create --name school-library-rg --location eastus

# 3. إنشاء الخطة:
az appservice plan create --name school-library-plan --resource-group school-library-rg --sku B1 --is-linux

# 4. إنشاء التطبيق:
az webapp create --resource-group school-library-rg --plan school-library-plan --name school-library-app --runtime "PYTHON|3.10"

# 5. تعيين البيانات:
az webapp config appsettings set --resource-group school-library-rg --name school-library-app --settings MONGODB_URI="mongodb+srv://reeman:Reeman@cluster0.nwwzgip.mongodb.net/school_library?retryWrites=true&w=majority&appName=Cluster0" ENVIRONMENT="production" DEBUG="False" LOG_LEVEL="INFO" WEBSITES_PORT="8000"

# 6. الحصول على Publish Profile:
az webapp deployment list-publishing-profiles --resource-group school-library-rg --name school-library-app --xml > publishProfile.xml
```

---

### **الطريقة الثالثة: GitHub Actions (التلقائي)**

بعد إنشاء التطبيق على Azure:

```bash
# 1. أضف GitHub Secrets:
# GitHub → Settings → Secrets → Actions
# أضف:
# - AZURE_APP_NAME = school-library-app
# - AZURE_PUBLISH_PROFILE = (محتوى publishProfile.xml)

# 2. اضغط الكود:
git push origin ci.cd

# ✅ سينشر تلقائياً!
```

---

## ✨ ماذا بعد؟

```bash
# افتح التطبيق:
https://school-library-app.azurewebsites.net

# أو:
az webapp open --resource-group school-library-rg --name school-library-app
```

### الـ URLs:
- 🎯 التطبيق: https://school-library-app.azurewebsites.net/app
- 📖 التوثيق: https://school-library-app.azurewebsites.net/docs.html
- 📊 السجلات: https://school-library-app.azurewebsites.net/logs.html

---

## 🔐 بيانات الاتصال:

| البيانات | القيمة |
|--------|--------|
| **MongoDB Atlas** | ✅ متصل |
| **Username** | reeman |
| **Cluster** | cluster0.nwwzgip.mongodb.net |
| **Database** | school_library |
| **Status** | 🟢 نشط |

---

## 🆘 إذا حدثت مشكلة:

```bash
# عرض السجلات:
az webapp log tail --resource-group school-library-rg --name school-library-app

# إعادة تشغيل:
az webapp restart --resource-group school-library-rg --name school-library-app

# حذف التطبيق (إذا لزم الأمر):
az webapp delete --resource-group school-library-rg --name school-library-app
```

---

**✅ كل شيء جاهز للنشر!**

اختر طريقتك وابدأ الآن 🚀
