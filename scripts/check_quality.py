#!/usr/bin/env python3
"""
Project Quality Check Script
يقوم بفحص جودة المشروع والتحقق من مبادئ الهندسة
"""

import subprocess
import sys
from pathlib import Path


def run_command(cmd: list, description: str) -> bool:
    """تشغيل أمر والتحقق من النجاح"""
    print(f"🔍 فحص: {description}...", end=" ")
    try:
        result = subprocess.run(
            cmd, capture_output=True, text=True, timeout=30
        )
        if result.returncode == 0:
            print("✅")
            return True
        else:
            print("❌")
            if result.stderr:
                print(f"   خطأ: {result.stderr[:100]}")
            return False
    except subprocess.TimeoutExpired:
        print("⏱️ انتهت المهلة الزمنية")
        return False
    except Exception as e:
        print(f"❌ خطأ: {str(e)[:50]}")
        return False


def main():
    """فحص شامل لجودة المشروع"""
    print("=" * 60)
    print("📊 فحص جودة المشروع - Quality Check")
    print("=" * 60)

    checks = [
        (
            ["poetry", "check"],
            "صحة ملف pyproject.toml",
        ),
        (
            ["poetry", "run", "black", "--check", "."],
            "تنسيق الكود (black)",
        ),
        (
            ["poetry", "run", "flake8", "--max-line-length=100"],
            "معايير Linting (flake8)",
        ),
        (
            ["poetry", "run", "mypy", "cli", "core", "services"],
            "فحص النوع (mypy)",
        ),
        (
            ["poetry", "run", "pytest", "--co", "-q"],
            "جمع الاختبارات (pytest)",
        ),
    ]

    results = []
    for cmd, desc in checks:
        results.append(run_command(cmd, desc))

    print("\n" + "=" * 60)
    passed = sum(results)
    total = len(results)
    print(f"النتيجة: {passed}/{total} فحوصات نجحت")
    print("=" * 60)

    if passed == total:
        print("✅ جميع الفحوصات نجحت! المشروع بحالة جيدة.")
        return 0
    else:
        print(f"⚠️  {total - passed} فحص(صات) فشل(ت).")
        return 1


if __name__ == "__main__":
    sys.exit(main())
