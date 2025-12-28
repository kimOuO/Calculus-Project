import requests
import json

BASE_URL = "http://localhost:8000/api/v0.1/Calculus_oom/Calculus_metadata"

# 檢查數據庫中的考試
print("檢查當前考試...")
tests = requests.post(f"{BASE_URL}/Test_MetadataWriter/read", json={})
if tests.status_code == 200:
    data = tests.json()['data']
    print(f"找到 {len(data)} 個考試:")
    for t in data:
        print(f"  - {t['test_name']}: 權重={t['test_weight']}, 學期={t['test_semester']}")
    
    # 計算總權重
    total_weight = sum(float(t['test_weight']) if t['test_weight'] else 0 for t in data)
    print(f"\n總權重: {total_weight}")

# 檢查學生
print("\n檢查當前學生...")
students = requests.post(f"{BASE_URL}/Student_MetadataWriter/read", json={})
if students.status_code == 200:
    data = students.json()['data']
    if isinstance(data, list):
        print(f"找到 {len(data)} 個學生")
        for s in data:
            print(f"  - {s['student_name']}: 學期={s['student_semester']}")
    else:
        print(f"找到 1 個學生: {data['student_name']}, 學期={data['student_semester']}")

# 檢查成績
print("\n檢查當前成績...")
scores = requests.post(f"{BASE_URL}/Score_MetadataWriter/read", json={})
if scores.status_code == 200:
    data = scores.json()['data']
    if isinstance(data, list):
        print(f"找到 {len(data)} 個成績記錄")
        for s in data:
            print(f"  Quiz1={s['score_quiz1']}, Mid={s['score_midterm']}, Quiz2={s['score_quiz2']}, Final={s['score_finalexam']}")
    else:
        print(f"找到 1 個成績記錄:")
        print(f"  Quiz1={data['score_quiz1']}, Mid={data['score_midterm']}, Quiz2={data['score_quiz2']}, Final={data['score_finalexam']}")
