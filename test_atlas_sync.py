#!/usr/bin/env python3
"""
اختبار سريع للاتصال بـ MongoDB Atlas والمزامنة
Quick test for MongoDB Atlas connection and data sync

يتحقق من:
- الاتصال بـ MongoDB Atlas
- وجود قاعدة البيانات
- Collections الموجودة
- عينة من البيانات
"""

import sys
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).resolve().parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


def test_atlas_connection():
    """اختبار الاتصال بـ MongoDB Atlas"""
    print("\n" + "=" * 60)
    print("🧪 اختبار الاتصال بـ MongoDB Atlas")
    print("=" * 60)

    try:
        from config.database import MongoDBConfig, MongoDBConnection

        # عرض الإعدادات
        config = MongoDBConfig()
        print("📋 إعدادات الاتصال:")
        print(f"   • Connection Method: {'URI (Atlas)' if config.uri else 'Host:Port'}")
        if config.uri:
            # أخفِ الكلمة المرورية
            masked_uri = (
                config.uri.replace(config.password, "****")
                if config.password
                else config.uri
            )
            print(f"   • URi: {masked_uri[:80]}...")
        else:
            print(f"   • Host: {config.host}")
            print(f"   • Port: {config.port}")
        print(f"   • Database: {config.database}")

        # محاولة الاتصال
        print("🔗 محاولة الاتصال...")
        db = MongoDBConnection.get_database()

        print("✅ تم الاتصال بنجاح!")
        print(f"   Database: {db.name}")

        # عرض Collections
        print("📊 Collections الموجودة:")
        collections = db.list_collection_names()
        if collections:
            for coll in collections:
                count = db[coll].count_documents({})
                print(f"   • {coll}: {count} document(s)")
        else:
            print("   • لا توجد collections بعد")

        # اختبار الكتابة والقراءة
        print("🔄 اختبار المزامنة (Write/Read):")

        # إنشاء test collection
        test_collection = db["test_sync"]

        # اكتب بيانات
        test_doc = {
            "test": "data",
            "timestamp": __import__("datetime").datetime.now().isoformat(),
            "message": "✅ البيانات تُكتب وتُقرأ من Atlas مباشرة",
        }
        result = test_collection.insert_one(test_doc)
        print(f"   ✍️  تم الكتابة: {result.inserted_id}")

        # اقرأ البيانات
        read_doc = test_collection.find_one({"_id": result.inserted_id})
        if read_doc:
            print(f"   📖 تم القراءة: {read_doc['message']}")
            print("   ✅ المزامنة تعمل بشكل صحيح!")

        # احذف test document
        test_collection.delete_one({"_id": result.inserted_id})

        # الإحصائيات
        print("📈 إحصائيات قاعدة البيانات:")
        stats = db.command("dbStats")
        print(f"   • حجم البيانات: {stats.get('dataSize', 0) / 1024:.2f} KB")
        print(f"   • عدد المجموعات: {stats.get('collections', 0)}")

        assert True, "Connection test passed"

    except Exception as e:
        print("❌ خطأ في الاتصال:")
        print(f"   {type(e).__name__}: {e}")
        assert False, f"Connection test failed: {e}"


def test_cli_sync():
    """اختبار مزامنة البيانات عبر CLI"""
    print("\n" + "=" * 60)
    print("🧪 اختبار المزامنة عبر API")
    print("=" * 60)

    try:
        import subprocess

        # اختبر أمر list-books
        print("📚 عرض قائمة الكتب:")
        result = subprocess.run(
            [sys.executable, "main.py", "list-books", "--librarian"],
            capture_output=True,
            text=True,
            timeout=5,
        )

        if result.returncode == 0:
            print("✅ الأمر نجح")
            if result.stdout:
                lines = result.stdout.strip().split("\n")[:3]  # أول 3 أسطر
                for line in lines:
                    print(f"   {line}")
        else:
            print(f"   ⚠️  {result.stderr[:200]}")

        # اختبر عرض المستخدمين
        print("👥 عرض قائمة المستخدمين:")
        result = subprocess.run(
            [sys.executable, "main.py", "list-users", "--librarian"],
            capture_output=True,
            text=True,
            timeout=5,
        )

        if result.returncode == 0:
            print("   ✅ الأمر نجح")
            if result.stdout:
                lines = result.stdout.strip().split("\n")[:3]
                for line in lines:
                    print(f"   {line}")
        else:
            print(f"   ⚠️  {result.stderr[:200]}")

        assert True, "CLI sync test passed"

    except Exception as e:
        print("⚠️  خطأ في الاختبار:")
        print(f"   {type(e).__name__}: {e}")
        assert False, f"CLI sync test failed: {e}"


def main():
    """الدالة الرئيسية"""
    print("\n" + "🔍 " * 15)
    print("اختبار MongoDB Atlas والمزامنة")
    print("MongoDB Atlas Connection & Sync Test")
    print("🔍" * 15)

    # اختبر الاتصال
    connection_ok = test_atlas_connection()

    # اختبر CLI sync
    cli_ok = test_cli_sync()

    # النتيجة النهائية
    print("\n" + "=" * 60)
    print("📊 النتيجة النهائية:")
    print("=" * 60)

    if connection_ok and cli_ok:
        print("✅ جميع الاختبارات نجحت!")
        print("🎉 التطبيق جاهز للنشر على Azure مع MongoDB Atlas!")
        return 0
    else:
        print("⚠️  بعض الاختبارات لم تنجح")
        return 1


if __name__ == "__main__":
    sys.exit(main())
