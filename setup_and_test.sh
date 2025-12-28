#!/bin/bash

# 資料庫連接測試與 Schema 驗證腳本

echo "========================================="
echo "Calculus OOM - 資料庫測試"
echo "========================================="

# 啟動 Docker 容器
echo "啟動資料庫容器..."
docker-compose up -d postgres mongodb

# 等待資料庫啟動
echo "等待資料庫啟動（30秒）..."
sleep 30

# 測試 PostgreSQL 連接
echo ""
echo "========================================="
echo "測試 PostgreSQL 連接..."
echo "========================================="
docker exec calculus_postgres pg_isready -U calculus_user -d calculus_db
if [ $? -eq 0 ]; then
    echo "✅ PostgreSQL 連接成功"
else
    echo "❌ PostgreSQL 連接失敗"
fi

# 測試 MongoDB 連接
echo ""
echo "========================================="
echo "測試 MongoDB 連接..."
echo "========================================="
docker exec calculus_mongodb mongosh --eval "db.adminCommand('ping')" > /dev/null 2>&1
if [ $? -eq 0 ]; then
    echo "✅ MongoDB 連接成功"
else
    echo "❌ MongoDB 連接失敗"
fi

# 執行 Django 資料庫測試
echo ""
echo "========================================="
echo "執行 Django 資料庫遷移與測試..."
echo "========================================="

# 確保 manage.py 有執行權限
chmod +x manage.py

# 生成並執行遷移
python manage.py makemigrations Calculus_metadata
python manage.py migrate

if [ $? -eq 0 ]; then
    echo "✅ Django 資料庫遷移成功"
else
    echo "❌ Django 資料庫遷移失敗"
    exit 1
fi

# 執行 Python 測試腳本
echo ""
echo "========================================="
echo "執行連接測試腳本..."
echo "========================================="
python <<EOF
import os
import sys
import django

# 設定 Django 環境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'main.settings')
django.setup()

from django.db import connection
from pymongo import MongoClient
from main.apps.Calculus_metadata.models import Students, Score, Test
from main.apps.Calculus_metadata.services.business import NoSqlDbBusinessService
from main.apps.Calculus_metadata.services.common import UuidService, TimestampService

print("\n" + "="*60)
print("SQL 資料庫測試")
print("="*60)

try:
    # 測試 SQL 連接
    with connection.cursor() as cursor:
        cursor.execute("SELECT 1")
        result = cursor.fetchone()
        print("✅ SQL 資料庫連接成功")
        
    # 測試 Model 查詢
    students_count = Students.objects.count()
    print(f"✅ Students 表查詢成功（筆數: {students_count}）")
    
    scores_count = Score.objects.count()
    print(f"✅ Score 表查詢成功（筆數: {scores_count}）")
    
    tests_count = Test.objects.count()
    print(f"✅ Test 表查詢成功（筆數: {tests_count}）")
    
    # 測試插入與刪除
    test_student_uuid = UuidService.generate_student_uuid("1142")
    test_student = Students.objects.create(
        student_uuid=test_student_uuid,
        student_name="測試學生",
        student_number="TEST001",
        student_semester="1142",
        student_status="修業中",
        student_created_at=TimestampService.get_current_timestamp(),
        student_updated_at=TimestampService.get_current_timestamp()
    )
    print(f"✅ 測試資料插入成功: {test_student_uuid}")
    
    # 刪除測試資料
    test_student.delete()
    print("✅ 測試資料刪除成功")
    
except Exception as e:
    print(f"❌ SQL 資料庫測試失敗: {str(e)}")
    sys.exit(1)

print("\n" + "="*60)
print("MongoDB 資料庫測試")
print("="*60)

try:
    # 測試 MongoDB 連接
    client = NoSqlDbBusinessService.get_connection()
    client.admin.command('ping')
    print("✅ MongoDB 連接成功")
    
    # 測試文檔插入
    test_doc = {
        'test_pic_uuid': UuidService.generate_test_pic_uuid("1142", "test"),
        'test_pic': '/test/path/pic.jpg',
        'test_pic_histogram': '/test/path/histogram.png',
        'pic_created_at': TimestampService.get_current_timestamp(),
        'pic_updated_at': TimestampService.get_current_timestamp()
    }
    
    inserted_id = NoSqlDbBusinessService.create_document('test_pic_information', test_doc)
    print(f"✅ MongoDB 文檔插入成功: {inserted_id}")
    
    # 測試文檔查詢
    retrieved_doc = NoSqlDbBusinessService.get_document('test_pic_information', {'test_pic_uuid': test_doc['test_pic_uuid']})
    if retrieved_doc:
        print(f"✅ MongoDB 文檔查詢成功")
        
        # 驗證欄位
        required_fields = ['test_pic_uuid', 'test_pic', 'test_pic_histogram', 'pic_created_at', 'pic_updated_at']
        missing_fields = [field for field in required_fields if field not in retrieved_doc]
        
        if missing_fields:
            print(f"❌ 缺少欄位: {', '.join(missing_fields)}")
        else:
            print(f"✅ 所有欄位完整")
    
    # 刪除測試文檔
    NoSqlDbBusinessService.delete_document('test_pic_information', {'test_pic_uuid': test_doc['test_pic_uuid']})
    print("✅ MongoDB 測試文檔刪除成功")
    
    client.close()
    
except Exception as e:
    print(f"❌ MongoDB 測試失敗: {str(e)}")
    sys.exit(1)

print("\n" + "="*60)
print("所有測試通過！ ✅")
print("="*60)
EOF

echo ""
echo "========================================="
echo "測試完成！"
echo "========================================="
echo "訪問管理界面："
echo "  - PostgreSQL: http://localhost:5051 (admin@calculus.com / admin123)"
echo "  - MongoDB: http://localhost:8081 (admin / admin123)"
echo ""
echo "啟動開發伺服器："
echo "  python manage.py runserver 0.0.0.0:8000"
echo "========================================="
