#!/usr/bin/env python
"""
完整功能測試 - 演示 calculation_final 和 test_score 的正確用法
"""
import requests
import json

BASE_URL = "http://localhost:8000/api/v0.1/Calculus_oom/Calculus_metadata"

def api_call(endpoint, data):
    r = requests.post(f"{BASE_URL}/{endpoint}", json=data)
    return r.status_code in [200, 201], r.json()

print("="*60)
print("完整功能測試")
print("="*60)

# 1. 創建 4 個考試
print("\n步驟 1: 創建 4 個考試")
tests = [
    {"test_name": "第一次小考", "test_weight": "0.2", "test_semester": "1141", "test_date": "2025-01-10", "test_range": "1-3章", "test_state": "尚未出考卷"},
    {"test_name": "期中考", "test_weight": "0.3", "test_semester": "1141", "test_date": "2025-01-15", "test_range": "1-5章", "test_state": "尚未出考卷"},
    {"test_name": "第二次小考", "test_weight": "0.2", "test_semester": "1141", "test_date": "2025-01-18", "test_range": "6-8章", "test_state": "尚未出考卷"},
    {"test_name": "期末考", "test_weight": "0.3", "test_semester": "1141", "test_date": "2025-01-20", "test_range": "6-10章", "test_state": "尚未出考卷"},
]

for t in tests:
    ok, res = api_call("Test_MetadataWriter/create", t)
    if ok:
        print(f"  ✓ 創建 {t['test_name']}")
    else:
        print(f"  ✗ 失敗: {res}")

# 2. 設定權重
print("\n步驟 2: 設定考試權重")
ok, res = api_call("Test_MetadataWriter/setweight", {
    "test_semester": "1141",
    "weights": {
        "第一次小考": "0.2",
        "期中考": "0.3",
        "第二次小考": "0.2",
        "期末考": "0.3"
    }
})
print(f"  權重設定: {'✓' if ok else '✗'} {res.get('detail', '')}")

# 3. 創建學生
print("\n步驟 3: 創建學生")
students = []
for i in range(3):
    ok, res = api_call("Student_MetadataWriter/create", {
        "student_name": f"學生{i+1}",
        "student_number": f"B1090100{i+1}",
        "student_semester": "1141",
        "student_status": "修業中"
    })
    if ok:
        uuid = res['data']['student_uuid']
        students.append(uuid)
        print(f"  ✓ 創建 學生{i+1}: {uuid}")

# 4. 為每個學生添加所有成績
print("\n步驟 4: 添加成績")
score_fields = [
    ("score_quiz1", [85, 78, 92]),
    ("score_midterm", [88, 82, 95]),
    ("score_quiz2", [90, 75, 88]),
    ("score_finalexam", [87, 80, 90])
]

for field, scores in score_fields:
    for i, uuid in enumerate(students):
        ok, res = api_call("Score_MetadataWriter/create", {
            "f_student_uuid": uuid,
            "update_field": field,
            "score_value": scores[i]
        })
    print(f"  ✓ 添加 {field}")

# 5. 計算總成績
print("\n步驟 5: 計算總成績")
ok, res = api_call("Score_MetadataWriter/calculation_final", {
    "test_semester": "1141",
    "passing_score": 60
})
if ok:
    count = res['data']['updated_count']
    print(f"  ✓ 成功計算 {count} 個學生的總成績")
else:
    print(f"  ✗ 失敗: {res}")

# 6. 統計成績
print("\n步驟 6: 統計 Quiz 1 成績")
ok, res = api_call("Score_MetadataWriter/test_score", {
    "score_semester": "1141",
    "score_field": "score_quiz1"
})
if ok:
    data = res['data']
    print(f"  ✓ 平均: {data['average']}, 中位數: {data['median']}, 人數: {data['total_count']}")
else:
    print(f"  ✗ 失敗: {res}")

# 7. 讀取學生成績
print("\n步驟 7: 檢查學生總成績")
for i, uuid in enumerate(students):
    ok, res = api_call("Student_MetadataWriter/read", {"student_uuid": uuid})
    if ok:
        name = res['data']['student_name']
        status = res['data']['student_status']
        print(f"  學生{i+1} ({name}): 狀態={status}")

print("\n" + "="*60)
print("測試完成！")
print("="*60)
