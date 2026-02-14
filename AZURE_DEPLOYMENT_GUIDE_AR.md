# 📚 دليل النشر على Azure مع MongoDB Atlas

## ✅ ما تم إنجازه:

- ✅ MongoDB Atlas متصل وجاهز
- ✅ ملفات Docker و docker-compose معدة
- ✅ GitHub Actions Workflow جاهز
- ✅ متغيرات البيئة مُعدة

---

## 🚀 خطوات النشر على Azure

### المتطلبات:
- حساب Azure مع subscription نشط
- Azure CLI مثبت
- Git و GitHub مثبتان

### 📝 خطوة 1: تثبيت Azure CLI

**Windows (PowerShell):**
```powershell
# الطريقة 1: Chocolatey
choco install azure-cli

# الطريقة 2: من الموقع الرسمي
# https://aka.ms/installazurecliwindows
```

**التحقق من التثبيت:**
```bash
az --version
```

---

### 🔑 خطوة 2: تسجيل الدخول إلى Azure

```bash
az login
```

ستفتح نافذة المتصفح لتسجيل الدخول.

---

### ⚡ خطوة 3: استخدام Script النشر (الطريقة السريعة)

**للـ PowerShell (موصى به للـ Windows):**
```powershell
# من المجلد الرئيسي للمشروع:
.\scripts\deploy_to_azure.ps1
```

**للـ Python:**
```bash
python scripts/deploy_to_azure.py
```

---

### 🔧 خطوة 4: إعداد GitHub Secrets (للـ CI/CD التلقائي)

بعد تشغيل الـ script، ستحصل على ملف `publishProfile.xml`

1. اذهب إلى: **GitHub → Repository → Settings → Secrets and variables → Actions**
2. أضف الـ Secrets التالية:

```
AZURE_APP_NAME = school-library-app
AZURE_PUBLISH_PROFILE = (محتوى publishProfile.xml)
```

---

### 🚀 خطوة 5: النشر التلقائي عبر GitHub

الآن عند عمل `push` إلى الفروع `main` أو `ci.cd`:

```bash
# اختر الفرع:
git checkout ci.cd

# أضف التغييرات:
git add .

# اكتب رسالة commit:
git commit -m "feat: prepare for Azure deployment with MongoDB Atlas"

# اضغط إلى GitHub:
git push origin ci.cd
```

الـ GitHub Actions سيقوم تلقائياً بـ:
1. ✅ بناء Docker image
2. ✅ رفع الـ image إلى GitHub Container Registry
3. ✅ النشر على Azure App Service

---

## 📊 متغيرات البيئة المستخدمة

```env
MONGODB_URI=mongodb+srv://reeman:Reeman@cluster0.nwwzgip.mongodb.net/school_library?retryWrites=true&w=majority&appName=Cluster0
ENVIRONMENT=production
DEBUG=False
LOG_LEVEL=INFO
WEBSITES_PORT=8000
```

---

## 🧪 اختبار التطبيق على Azure

بعد النشر:

```bash
# فتح التطبيق في المتصفح:
az webapp open --resource-group school-library-rg --name school-library-app

# أو الرابط المباشر:
# https://school-library-app.azurewebsites.net
```

### الـ URLs المتاحة:
- 🌐 التطبيق الرئيسي: `https://school-library-app.azurewebsites.net/app`
- 📖 التوثيق: `https://school-library-app.azurewebsites.net/docs.html`
- 📊 لوحة السجلات: `https://school-library-app.azurewebsites.net/logs.html`
- ⚕️ Health Check: `https://school-library-app.azurewebsites.net/health`

---

## 🔍 عرض السجلات على Azure

```bash
# عرض السجلات الحية:
az webapp log tail --resource-group school-library-rg --name school-library-app

# عرض آخر 50 سطر:
az webapp log tail --resource-group school-library-rg --name school-library-app -n 50
```

---

## ⚙️ إدارة MongoDB Atlas

### إضافة IP Address جديد:
1. اذهب إلى: **MongoDB Atlas → Network Access**
2. اضغط **Add IP Address**
3. أدخل IP الـ Azure App Service أو اختر "Allow access from anywhere"

### عرض البيانات:
1. اذهب إلى: **MongoDB Atlas → Database**
2. اضغط **Browse Collections**
3. شاهد الكتب والمستخدمين

---

## 🐛 استكشاف الأخطاء

### المشكلة: "Failed to connect to MongoDB"
**الحل:**
- تحقق من IP Address Configuration في MongoDB Atlas
- تأكد من صحة Connection String
- تحقق من Log الخصاص على Azure

### المشكلة: "Website failed to load"
**الحل:**
```bash
# إعادة تشغيل التطبيق:
az webapp restart --resource-group school-library-rg --name school-library-app

# عرض السجلات:
az webapp log tail --resource-group school-library-rg --name school-library-app
```

### المشكلة: "GitHub Actions فشلت"
**الحل:**
1. تحقق من GitHub Secrets صحيحة
2. تحقق من AZURE_APP_NAME مطابقة تماماً
3. تحقق من publishProfile.xml صحيح

---

## 📱 البيانات المعروضة على التطبيق

بعد النشر، سترى على الواجهة:

- 📖 قائمة الكتب من MongoDB Atlas
- 👥 قائمة المستخدمين المسجلين
- 🔐 تسجيل الدخول والحسابات
- 📊 إحصائيات الكتب والمستخدمين

---

## 🔄 تحديث التطبيق

لتحديث التطبيق على Azure:

1. اعمل التغييرات محلياً
2. اختبر التطبيق على جهازك:
   ```bash
   python run_app.py
   ```
3. اضغط التغييرات:
   ```bash
   git push origin ci.cd
   ```
4. GitHub Actions سينشر التعديلات تلقائياً

---

## 💰 التكاليف المقدرة:

| الخدمة | المستوى | السعر |
|--------|--------|-------|
| Azure App Service (B1) | Basic | ~$12-15/شهر |
| MongoDB Atlas | Free (M0) | مجاني |
| **المجموع** | | **~$12-15/شهر** |

---

## 📞 الدعم والمساعدة

- Azure Documentation: https://docs.microsoft.com/azure/
- MongoDB Atlas: https://docs.atlas.mongodb.com/
- GitHub Actions: https://docs.github.com/en/actions

---

## ✨ ماذا بعد؟

بعد النشر بنجاح، يمكنك:

1. ✅ إضافة نطاق مخصص (Custom Domain)
2. ✅ تفعيل SSL/HTTPS
3. ✅ إنشاء نسخ احتياطية من البيانات
4. ✅ مراقبة الأداء والسجلات
5. ✅ توسيع قاعدة البيانات (Upgrade MongoDB)

---

**آخر تحديث:** فبراير 2026
**الحالة:** ✅ جاهز للنشر
