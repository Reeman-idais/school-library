# 🚀 دليل MongoDB Atlas - نشر التطبيق

## ✅ الوضع الحالي

✨ المشروع **مجهز بالفعل** للتعامل مع MongoDB Atlas!

### الملفات الرئيسية:
- ✅ [config/database.py](config/database.py) - يدعم `MONGODB_URI`
- ✅ [docker-compose.production.yml](docker-compose.production.yml) - معد للإنتاج
- ✅ [.env.production](.env.production) - يحتوي على بيانات الاتصال

---

## 📋 بيانات الاتصال الحالية

Connection String الذي تم إنشاؤه:
```
mongodb+srv://reeman:Reeman@cluster0.nwwzgip.mongodb.net/school_library?retryWrites=true&w=majority&appName=Cluster0
```

قاعدة البيانات: `school_library`

---

## 🔧 خطوات التشغيل

### 1. لتشغيل محليًا مع Atlas:

```bash
# تفعيل البيئة الافتراضية
.venv\Scripts\Activate.ps1

# تشغيل التطبيق (سيقرأ .env.production تلقائيًا)
python run_app.py
```

أو مباشرة:
```bash
# تحديد ملف env
$env:MONGODB_URI = 'mongodb+srv://reeman:Reeman@cluster0.nwwzgip.mongodb.net/school_library?retryWrites=true&w=majority&appName=Cluster0'
python run_app.py
```

### 2. لنشر على Azure:

#### الخطوة 1: تعيين متغيرات البيئة في Azure
```bash
az webapp config appsettings set \
  --resource-group school-library-rg \
  --name school-library-app \
  --settings \
    MONGODB_URI='mongodb+srv://reeman:Reeman@cluster0.nwwzgip.mongodb.net/school_library?retryWrites=true&w=majority&appName=Cluster0' \
    DATABASE_TYPE=mongodb \
    ENVIRONMENT=production
```

#### الخطوة 2: نشر الكود
```bash
# إذا كنت تستخدم GitHub Actions (موصى به)
git push origin main

# أو نشر مباشر
az webapp up --name school-library-app --resource-group school-library-rg
```

### 3. استخدام Docker:

```bash
# بناء وتشغيل مع docker-compose
docker-compose -f docker-compose.production.yml up --build

# أو مع متغيرات البيئة:
set MONGODB_URI=mongodb+srv://reeman:Reeman@cluster0.nwwzgip.mongodb.net/school_library?retryWrites=true&w=majority&appName=Cluster0
docker-compose -f docker-compose.production.yml up --build
```

---

## 🔄 المزامنة التلقائية للبيانات

عندما تضيف / تحرر / تحذف بيانات من الواجهة:

```
👤 المستخدم يعدل البيانات
        ↓
🌐 الواجهة تُرسل طلب إلى API
        ↓
🔌 API يتصل بـ MongoDB Atlas
        ↓
💾 البيانات تُحفظ في قاعدة البيانات السحابية
        ↓
📊 البيانات تظهر مباشرة في المتصفح والـ Atlas Console
```

### أمثلة:

#### ✏️ إضافة كتاب جديد
```bash
curl -X POST http://localhost:8000/api/execute \
  -H "Content-Type: application/json" \
  -d '{
    "command": "add-book",
    "args": [
      "--id", "2001",
      "--title", "Python for Beginners",
      "--author", "John Smith",
      "--librarian"
    ]
  }'
```

#### 👥 تسجيل مستخدم جديد
```bash
curl -X POST http://localhost:8000/api/execute \
  -H "Content-Type: application/json" \
  -d '{
    "command": "register-user",
    "args": ["fatima", "password123", "user"]
  }'
```

#### 📚 عرض جميع الكتب
```bash
curl http://localhost:8000/api/execute \
  -H "Content-Type: application/json" \
  -d '{"command": "list-books", "args": ["--librarian"]}'
```

---

## 🧪 اختبار الاتصال

### تحقق من اتصال MongoDB Atlas:

```python
# اختبار سريع
python -c "
from config.database import MongoDBConnection
db = MongoDBConnection.get_database()
print('✅ Connected to:', db.name)
print('📊 Collections:', db.list_collection_names())
"
```

أو من Terminal:
```bash
mongosh 'mongodb+srv://reeman:Reeman@cluster0.nwwzgip.mongodb.net/school_library' --eval 'db.stats()'
```

---

## ⚡ المميزات المفعلة

| الميزة | الحالة | ملاحظات |
|--------|--------|---------|
| 📦 اتصال Atlas | ✅ | اتصال مباشر وسريع |
| 📡 مزامنة فورية | ✅ | البيانات تظهر مباشرة |
| 🔐 مصادقة آمنة | ✅ | اسم مستخدم وكلمة مرور |
| 🌐 دعم Docker | ✅ | جاهز للنشر |
| ☁️ دعم Azure | ✅ | مع Health Check |
| 📊 Monitoring | ✅ | Prometheus metrics متاح |

---

## 🆘 استكشاف الأخطاء

### خطأ: "Unable to connect to MongoDB"

✅ **الحل:**
1. تحقق من Connection String (لا مسافات زيادة)
2. تأكد من تفعيل IP الخاص بك في MongoDB Atlas
3. تأكد من صحة الكلمة المرورية (خاصة الأحرف الخاصة)

### خطأ: "Authentication failed"

✅ **الحل:**
```bash
# اختبر بشكل مباشر:
mongosh 'mongodb+srv://reeman:Reeman@cluster0.nwwzgip.mongodb.net/'
```

### البيانات لا تظهر

✅ **الحقق من:**
1. التطبيق متصل بـ Atlas (تحقق من السجلات)
2. Database اسمها `school_library` (صحيح ✅)
3. Collections موجودة (`users`, `books`)

---

## 📚 مراجع إضافية

- [MongoDB Atlas Documentation](https://docs.mongodb.com/atlas/)
- [PyMongo Connection Strings](https://pymongo.readthedocs.io/en/stable/examples/connecting.html)
- [Azure App Service + MongoDB](https://learn.microsoft.com/en-us/azure/app-service/)

---

**تم التحديث: 12 فبراير 2026** ✨
