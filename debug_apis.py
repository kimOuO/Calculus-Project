import requests
import json

BASE_URL = "http://localhost:8000/api/v0.1/Calculus_oom/Calculus_metadata"

def test_api(endpoint, data):
    try:
        response = requests.post(f"{BASE_URL}/{endpoint}", 
                                json=data, 
                                headers={'Content-Type': 'application/json'})
        print(f"\n{'='*60}")
        print(f"測試: {endpoint}")
        print(f"發送數據: {json.dumps(data, ensure_ascii=False, indent=2)}")
        print(f"狀態碼: {response.status_code}")
        print(f"回應: {json.dumps(response.json(), ensure_ascii=False, indent=2)}")
    except Exception as e:
        print(f"錯誤: {e}")

# 測試 1: calculation_final (測試發送錯誤參數)
print("問題 1: calculation_final API 參數不匹配")
test_api("Score_MetadataWriter/calculation_final", 
         {"f_student_uuid": "stu_1141_1228_test123"})

# 測試 2: test_score (測試發送錯誤參數)
print("\n問題 2: test_score API 參數不匹配")
test_api("Score_MetadataWriter/test_score",
         {"f_test_uuid": "tst_1141_q1_test123"})

# 測試 3: 級聯刪除
print("\n問題 3: 級聯刪除測試")
# 創建學生
create_res = requests.post(f"{BASE_URL}/Student_MetadataWriter/create",
                          json={"student_name": "測試刪除", 
                                "student_number": "B10888888",
                                "student_semester": "1141",
                                "student_status": "修業中"})
if create_res.status_code in [200, 201]:
    student_uuid = create_res.json()['data']['student_uuid']
    print(f"創建學生成功: {student_uuid}")
    
    # 刪除學生
    delete_res = requests.post(f"{BASE_URL}/Student_MetadataWriter/delete",
                              json={"student_uuid": student_uuid})
    print(f"刪除狀態碼: {delete_res.status_code}")
    print(f"刪除回應: {json.dumps(delete_res.json(), ensure_ascii=False, indent=2)}")
else:
    print(f"創建失敗: {create_res.json()}")
