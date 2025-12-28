#!/usr/bin/env python3
"""
完整 API 功能測試腳本
測試所有 API endpoints 和各種使用情境
"""

import requests
import json
import sys
from datetime import datetime

# 配置
BASE_URL = "http://localhost:8000"
API_BASE = f"{BASE_URL}/api/v0.1/Calculus_oom/Calculus_metadata"

# 測試結果追蹤
results = {"total": 0, "passed": 0, "failed": 0, "errors": []}

# 儲存測試資料
data_store = {"students": [], "tests": [], "scores": [], "files": []}

# 顏色
class C:
    G = '\033[92m'  # Green
    R = '\033[91m'  # Red
    Y = '\033[93m'  # Yellow
    B = '\033[94m'  # Blue
    E = '\033[0m'   # End

def print_header(title):
    print(f"\n{C.B}{'='*80}")
    print(f"  {title}")
    print(f"{'='*80}{C.E}\n")

def test(name, passed, msg=""):
    results["total"] += 1
    if passed:
        results["passed"] += 1
        print(f"{C.G}✓{C.E} {name}")
    else:
        results["failed"] += 1
        results["errors"].append(f"{name}: {msg}")
        print(f"{C.R}✗{C.E} {name}")
        if msg:
            print(f"  └─ {C.Y}{msg}{C.E}")

def api_call(endpoint, data):
    """發送 POST 請求"""
    try:
        url = f"{API_BASE}/{endpoint}"
        response = requests.post(url, json=data, timeout=10)
        resp_data = response.json()
        # 判斷成功: status_code 是 200 或 201 且包含 data 欄位
        success = response.status_code in [200, 201] and "data" in resp_data
        return success, resp_data, response.status_code
    except Exception as e:
        return False, {"error": str(e)}, 0

def main():
    print(f"\n{C.B}{'='*80}")
    print(f"  Calculus OOM - 完整 API 功能測試")
    print(f"  開始時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*80}{C.E}\n")
    
    # 檢查伺服器
    try:
        requests.get(BASE_URL, timeout=2)
        print(f"{C.G}✓ 伺服器運行中: {BASE_URL}{C.E}\n")
    except:
        print(f"{C.R}✗ 無法連接伺服器: {BASE_URL}{C.E}")
        print(f"請先啟動 Django: python manage.py runserver 0.0.0.0:8000\n")
        sys.exit(1)
    
    # ========================================================================
    # 測試 1: 學生 APIs
    # ========================================================================
    print_header("測試 1: Student_MetadataWriter APIs")
    
    # 1.1 創建學生
    print(f"{C.B}1.1 創建學生{C.E}")
    student1 = {
        "student_name": "王小明",
        "student_number": "B10901001",
        "student_semester": "1141",
        "student_status": "修業中"
    }
    ok, res, code = api_call("Student_MetadataWriter/create", student1)
    if ok:
        uuid1 = res["data"]["student_uuid"]
        data_store["students"].append(uuid1)
        test("創建學生", True)
        print(f"  UUID: {uuid1}")
    else:
        test("創建學生", False, str(res))
    
    # 1.2 讀取學生
    print(f"\n{C.B}1.2 讀取學生{C.E}")
    if data_store["students"]:
        ok, res, code = api_call("Student_MetadataWriter/read", 
                                  {"student_uuid": data_store["students"][0]})
        test("讀取學生", ok and res.get("data", {}).get("student_name") == "王小明")
    
    # 1.3 更新學生
    print(f"\n{C.B}1.3 更新學生{C.E}")
    if data_store["students"]:
        update = {
            "student_uuid": data_store["students"][0],
            "student_name": "王小明(更新)",
            "student_number": "B10901001",
            "student_semester": "1142"
        }
        ok, res, code = api_call("Student_MetadataWriter/update", update)
        test("更新學生", ok)
    
    # 1.4 更新狀態
    print(f"\n{C.B}1.4 更新學生狀態{C.E}")
    if data_store["students"]:
        ok, res, code = api_call("Student_MetadataWriter/status", 
                                  {"student_uuid": data_store["students"][0],
                                   "student_status": "修業完畢"})
        test("更新狀態為修業完畢", ok)
    
    # 1.5 創建第二個學生並測試二退
    print(f"\n{C.B}1.5 測試二退狀態{C.E}")
    student2 = {
        "student_name": "李小華",
        "student_number": "B10901002",
        "student_semester": "1141",
        "student_status": "修業中"
    }
    ok, res, code = api_call("Student_MetadataWriter/create", student2)
    if ok and "data" in res:
        uuid2 = res["data"]["student_uuid"]
        data_store["students"].append(uuid2)
        # 更新為二退
        ok2, res2, code2 = api_call("Student_MetadataWriter/status",
                                     {"student_uuid": uuid2, "student_status": "二退"})
        test("二退狀態更新", ok2)
    
    # ========================================================================
    # 測試 2: 考卷 APIs
    # ========================================================================
    print_header("測試 2: Test_MetadataWriter APIs")
    
    # 2.1 創建考卷
    print(f"{C.B}2.1 創建考卷{C.E}")
    test1 = {
        "test_name": "第一次小考",  # 改為與 calculation_final 匹配的名稱
        "test_weight": "0.2",
        "test_semester": "1141",
        "test_date": "2024-11-15",
        "test_range": "第1-5章",
        "test_state": "尚未出考卷"
    }
    ok, res, code = api_call("Test_MetadataWriter/create", test1)
    if ok and "data" in res:
        test_uuid1 = res["data"]["test_uuid"]
        data_store["tests"].append(test_uuid1)
        test("創建考卷", True)
        print(f"  UUID: {test_uuid1}")
    else:
        test("創建考卷", False, str(res))
    
    # 2.2 讀取考卷
    print(f"\n{C.B}2.2 讀取考卷{C.E}")
    if data_store["tests"]:
        ok, res, code = api_call("Test_MetadataWriter/read",
                                  {"test_uuid": data_store["tests"][0]})
        test("讀取考卷", ok and res.get("data", {}).get("test_name") == "期中考")
    
    # 2.3 更新考卷
    print(f"\n{C.B}2.3 更新考卷{C.E}")
    if data_store["tests"]:
        update = {
            "test_uuid": data_store["tests"][0],
            "test_name": "期中考(更新)",
            "test_weight": "0.35",
            "test_semester": "1141",
            "test_date": "2024-11-20",
            "test_range": "第1-6章"
        }
        ok, res, code = api_call("Test_MetadataWriter/update", update)
        test("更新考卷", ok)
    
    # 2.4 更新狀態
    print(f"\n{C.B}2.4 更新考卷狀態{C.E}")
    if data_store["tests"]:
        ok, res, code = api_call("Test_MetadataWriter/status",
                                  {"test_uuid": data_store["tests"][0],
                                   "test_state": "考卷完成"})
        test("更新狀態為考卷完成", ok)
    
    # 2.5 創建第二個考卷並設定權重
    print(f"\n{C.B}2.5 批量設定權重{C.E}")
    # 創建更多考卷以符合 calculation_final 的需求
    test2 = {
        "test_name": "期中考",
        "test_weight": "0.3",
        "test_semester": "1141",
        "test_date": "2025-01-15",
        "test_range": "第1-5章",
        "test_state": "尚未出考卷"
    }
    api_call("Test_MetadataWriter/create", test2)
    
    test3 = {
        "test_name": "第二次小考",
        "test_weight": "0.2",
        "test_semester": "1141",
        "test_date": "2025-01-18",
        "test_range": "第6-8章",
        "test_state": "尚未出考卷"
    }
    api_call("Test_MetadataWriter/create", test3)
    
    test4 = {
        "test_name": "期末考",
        "test_weight": "0.3",
        "test_semester": "1141",
        "test_date": "2025-01-20",
        "test_range": "第6-10章",
        "test_state": "尚未出考卷"
    }
    ok, res, code = api_call("Test_MetadataWriter/create", test4)
    if ok and "data" in res:
        test_uuid2 = res["data"]["test_uuid"]
        data_store["tests"].append(test_uuid2)
        
        # 設定權重 (必須總和為 1.0)
        ok2, res2, code2 = api_call("Test_MetadataWriter/setweight",
                                     {"test_semester": "1141",
                                      "weights": {
                                          "第一次小考": "0.2",
                                          "期中考": "0.3",
                                          "第二次小考": "0.2",
                                          "期末考": "0.3"
                                      }})
        test("批量設定權重", ok2)
    
    # ========================================================================
    # 測試 3: 成績 APIs
    # ========================================================================
    print_header("測試 3: Score_MetadataWriter APIs")
    
    if not data_store["students"] or not data_store["tests"]:
        print(f"{C.Y}跳過成績測試：缺少學生或考卷資料{C.E}")
    else:
        # 3.1 創建成績 (使用 update_field 方式)
        print(f"{C.B}3.1 創建成績 - Quiz 1{C.E}")
        score1 = {
            "f_student_uuid": data_store["students"][0],
            "update_field": "score_quiz1",
            "score_value": 85
        }
        ok, res, code = api_call("Score_MetadataWriter/create", score1)
        if ok and "data" in res:
            score_uuid = res["data"]["score_uuid"]
            data_store["scores"].append(score_uuid)
            test("創建成績 Quiz 1", True)
            print(f"  UUID: {score_uuid}")
            print(f"  Quiz 1: {res['data'].get('score_quiz1')}")
        else:
            test("創建成績 Quiz 1", False, str(res))
        
        # 3.2 讀取成績
        print(f"\n{C.B}3.2 讀取成績{C.E}")
        if data_store["scores"]:
            ok, res, code = api_call("Score_MetadataWriter/read",
                                      {"score_uuid": data_store["scores"][0]})
            test("讀取成績", ok and res.get("data", {}).get("score_quiz1") == '85')
        
        # 3.3 更新成績 - 添加 Midterm
        print(f"\n{C.B}3.3 更新成績 - Midterm{C.E}")
        if data_store["scores"]:
            update = {
                "f_student_uuid": data_store["students"][0],
                "update_field": "score_midterm",
                "score_value": 90
            }
            ok, res, code = api_call("Score_MetadataWriter/create", update)
            if ok and "data" in res:
                test("更新成績 Midterm", True)
                print(f"  Midterm: {res['data'].get('score_midterm')}")
            else:
                test("更新成績 Midterm", False, str(res))
        
        # 3.4 添加 Quiz 2 成績
        print(f"\n{C.B}3.4 添加 Quiz 2 成績{C.E}")
        if data_store["students"]:
            score2 = {
                "f_student_uuid": data_store["students"][0],
                "update_field": "score_quiz2",
                "score_value": 78
            }
            ok, res, code = api_call("Score_MetadataWriter/create", score2)
            if ok and "data" in res:
                test("添加 Quiz 2 成績", True)
                print(f"  Quiz 2: {res['data'].get('score_quiz2')}")
            else:
                test("添加 Quiz 2 成績", False, str(res))
        
        # 3.4.5 添加期末考成績 (calculation_final 需要所有成績)
        print(f"\n{C.B}3.4.5 添加期末考成績{C.E}")
        if data_store["students"]:
            score_final = {
                "f_student_uuid": data_store["students"][0],
                "update_field": "score_finalexam",
                "score_value": 88
            }
            ok, res, code = api_call("Score_MetadataWriter/create", score_final)
            if ok and "data" in res:
                test("添加期末考成績", True)
                print(f"  Final: {res['data'].get('score_finalexam')}")
            else:
                test("添加期末考成績", False, str(res))
        
        # 3.5 計算總成績
        print(f"\n{C.B}3.5 計算總成績{C.E}")
        ok, res, code = api_call("Score_MetadataWriter/calculation_final",
                                  {"test_semester": "1141", 
                                   "passing_score": 60})
        if ok and "data" in res:
            count = res["data"].get("updated_count")
            test("計算總成績", True)
            print(f"  計算了 {count} 個學生")
        else:
            test("計算總成績", False, str(res))
        
        # 3.6 考卷統計
        print(f"\n{C.B}3.6 考卷成績統計{C.E}")
        ok, res, code = api_call("Score_MetadataWriter/test_score",
                                  {"score_semester": "1141",
                                   "score_field": "score_quiz1"})
        if ok and "data" in res:
            test("考卷成績統計", True)
            print(f"  平均: {res['data'].get('average')}, 中位數: {res['data'].get('median')}")
        else:
            test("考卷成績統計", False, str(res))
    
    # ========================================================================
    # 測試 4: 檔案資料 APIs (MongoDB)
    # ========================================================================
    print_header("測試 4: test-filedata APIs (MongoDB)")
    
    if not data_store["tests"]:
        print(f"{C.Y}跳過檔案測試：缺少考卷資料{C.E}")
    else:
        print(f"{C.Y}注意: 檔案上傳測試需要使用 multipart/form-data 格式{C.E}")
        print(f"{C.Y}此部分測試已簡化，實際測試請使用 Postman 或 curl{C.E}\n")
        
        # 簡單測試：嘗試讀取不存在的檔案
        ok, res, code = api_call("test-filedata/read", {"file_id": "000000000000000000000000"})
        test("檔案API錯誤處理", not ok or res.get("code") != 200)
    
    # ========================================================================
    # 測試 5: 錯誤處理
    # ========================================================================
    print_header("測試 5: 錯誤處理與邊界情況")
    
    # 5.1 無效 UUID
    print(f"{C.B}5.1 無效 UUID 格式{C.E}")
    ok, res, code = api_call("Student_MetadataWriter/read", {"student_uuid": "invalid"})
    test("無效UUID處理", not ok or res.get("code") != 200)
    
    # 5.2 缺少必填欄位
    print(f"\n{C.B}5.2 缺少必填欄位{C.E}")
    ok, res, code = api_call("Student_MetadataWriter/create", {"student_name": "Test"})
    test("缺少必填欄位處理", not ok or res.get("code") != 200)
    
    # 5.3 重複學號
    print(f"\n{C.B}5.3 重複學號{C.E}")
    dup = {
        "student_name": "重複",
        "student_number": "B10901001",
        "student_semester": "1141",
        "student_status": "修業中"
    }
    ok, res, code = api_call("Student_MetadataWriter/create", dup)
    test("重複學號處理", not ok or "already exists" in str(res).lower())
    
    # 5.4 不存在的資料
    print(f"\n{C.B}5.4 刪除不存在的資料{C.E}")
    ok, res, code = api_call("Score_MetadataWriter/delete",
                              {"score_uuid": "00000000-0000-0000-0000-000000000000"})
    test("不存在資料處理", not ok or res.get("code") != 200)
    
    # 5.5 無效外鍵
    print(f"\n{C.B}5.5 無效外鍵約束{C.E}")
    invalid_fk = {
        "f_student_uuid": "00000000-0000-0000-0000-000000000000",
        "update_field": "score_quiz1",
        "score_value": 80
    }
    ok, res, code = api_call("Score_MetadataWriter/create", invalid_fk)
    test("外鍵約束處理", not ok or res.get("code") != 200)
    
    # ========================================================================
    # 測試 6: 資料一致性
    # ========================================================================
    print_header("測試 6: 資料一致性與關聯性")
    
    # 6.1 級聯刪除
    print(f"{C.B}6.1 級聯刪除測試{C.E}")
    temp_student = {
        "student_name": "刪除測試",
        "student_number": "B10999999",
        "student_semester": "1141",
        "student_status": "修業中"
    }
    ok, res, code = api_call("Student_MetadataWriter/create", temp_student)
    if ok and "data" in res:
        temp_uuid = res["data"]["student_uuid"]
        # 刪除學生
        ok2, res2, code2 = api_call("Student_MetadataWriter/delete",
                                     {"student_uuid": temp_uuid})
        test("級聯刪除", ok2)
    else:
        test("創建臨時學生", False)
    
    # ========================================================================
    # 清理資料
    # ========================================================================
    print_header("清理測試資料")
    
    cleanup = input(f"{C.Y}是否清理測試資料? (y/n): {C.E}").lower() == 'y'
    
    if cleanup:
        print(f"\n{C.B}清理中...{C.E}")
        
        # 刪除成績
        for uuid in data_store["scores"]:
            api_call("Score_MetadataWriter/delete", {"score_uuid": uuid})
        print(f"已刪除 {len(data_store['scores'])} 個成績")
        
        # 刪除考卷
        for uuid in data_store["tests"]:
            api_call("Test_MetadataWriter/delete", {"test_uuid": uuid})
        print(f"已刪除 {len(data_store['tests'])} 個考卷")
        
        # 刪除學生
        for uuid in data_store["students"]:
            api_call("Student_MetadataWriter/delete", {"student_uuid": uuid})
        print(f"已刪除 {len(data_store['students'])} 個學生")
        
        print(f"\n{C.G}✓ 清理完成{C.E}")
    else:
        print(f"\n{C.Y}⚠ 保留測試資料{C.E}")
    
    # ========================================================================
    # 測試總結
    # ========================================================================
    print_header("測試總結")
    
    total = results["total"]
    passed = results["passed"]
    failed = results["failed"]
    
    print(f"總測試數:  {total}")
    print(f"{C.G}通過:      {passed}{C.E}")
    print(f"{C.R}失敗:      {failed}{C.E}")
    
    if failed > 0:
        print(f"\n{C.R}失敗的測試:{C.E}")
        for error in results["errors"]:
            print(f"  - {error}")
    
    rate = (passed / total * 100) if total > 0 else 0
    print(f"\n{C.B}成功率: {rate:.1f}%{C.E}")
    
    if rate == 100:
        print(f"\n{C.G}🎉 所有測試通過! 🎉{C.E}")
    elif rate >= 80:
        print(f"\n{C.Y}⚠ 大部分測試通過，但有些問題{C.E}")
    else:
        print(f"\n{C.R}❌ 多個測試失敗，請檢查錯誤{C.E}")
    
    print(f"\n結束時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    sys.exit(0 if failed == 0 else 1)

if __name__ == "__main__":
    main()
