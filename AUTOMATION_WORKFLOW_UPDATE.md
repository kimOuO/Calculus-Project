# 自動化工作流程更新說明

**更新日期**: 2026-01-05  
**更新目的**: 簡化前端操作，實現後端自動化流程

---

## 更新摘要

本次更新實現了三個自動化流程，減少前端需要調用的 API 次數：

1. ✅ **上傳考卷後自動更新狀態**
2. ✅ **學生成績計算後自動更新狀態**  
3. ✅ **生成直方圖後自動上傳檔案**

---

## 1. 考試狀態自動更新

### 工作流程

#### 1.1 上傳考卷 → 自動更新為「考卷完成」

**觸發條件**: 
- 上傳 `asset_type = 'paper'` 或 `'test_pic'`
- 當前狀態為 `尚未出考卷`

**API**: `POST /api/v0.1/Calculus_oom/Calculus_metadata/test-filedata/create`

**自動執行**:
```
上傳考卷 → test_states: 尚未出考卷 → 考卷完成
```

**範例**:
```python
import requests

response = requests.post(
    'http://localhost:8000/api/v0.1/Calculus_oom/Calculus_metadata/test-filedata/create',
    data={
        'test_uuid': 'tst_1141_mid_abc123',
        'asset_type': 'paper'
    },
    files={'file': open('midterm_exam.jpg', 'rb')}
)

# 響應
{
    "detail": "Files uploaded successfully",
    "data": {
        "file_uuid": "tpic_xxx",
        "asset_type": "paper",
        "file_count": 1,
        "mongodb_id": "...",
        "test_states": "考卷完成"  # ✅ 自動更新
    }
}
```

---

#### 1.2 上傳直方圖 → 自動更新為「考卷成績結算」

**觸發條件**:
- 上傳 `asset_type = 'histogram'` 或 `'test_pic_histogram'`
- 當前狀態為 `考卷完成`

**API**: `POST /api/v0.1/Calculus_oom/Calculus_metadata/test-filedata/create`

**自動執行**:
```
上傳直方圖 → test_states: 考卷完成 → 考卷成績結算
```

**完整狀態流轉**:
```
創建考試
   ↓
尚未出考卷
   ↓ (上傳考卷時自動更新)
考卷完成
   ↓ (上傳直方圖時自動更新)
考卷成績結算
```

---

## 2. 學生狀態自動更新

### 工作流程

#### 2.1 創建學生 → 預設「修業中」

**API**: `POST /api/v0.1/Calculus_oom/Calculus_metadata/Student_MetadataWriter/create`

**自動設定**:
```python
{
    "student_status": "修業中"  # 預設值
}
```

---

#### 2.2 計算總成績 → 自動更新為「修業完畢」或「被當」

**API**: `POST /api/v0.1/Calculus_oom/Calculus_metadata/Score_MetadataWriter/calculation_final`

**觸發條件**:
- 所有成績（quiz1, midterm, quiz2, finalexam）都已填寫
- 執行 `calculation_final` API

**自動執行**:
```python
# 計算加權總分
total_score = CalculationService.calculate_weighted_total(scores, weights)

# 根據及格分數自動更新狀態
if total_score >= passing_score:
    student_status = '修業完畢'  # ✅ 自動更新
else:
    student_status = '被當'       # ✅ 自動更新
```

**範例**:
```python
response = requests.post(
    'http://localhost:8000/api/v0.1/Calculus_oom/Calculus_metadata/Score_MetadataWriter/calculation_final',
    json={
        'test_semester': '1141',
        'passing_score': 60.0
    }
)

# 響應
{
    "detail": "Final scores calculated successfully for 50 students",
    "data": {
        "updated_count": 50  # 包含狀態自動更新
    }
}
```

---

#### 2.3 手動設定二退 → 清空成績

**API**: `POST /api/v0.1/Calculus_oom/Calculus_metadata/Student_MetadataWriter/status`

**自動執行**:
```python
if student_status == '二退':
    # 自動清空所有成績
    score.score_quiz1 = ''
    score.score_midterm = ''
    score.score_quiz2 = ''
    score.score_finalexam = ''
    score.score_total = ''
```

**完整狀態流轉**:
```
創建學生
   ↓
修業中
   ↓ (計算總成績時自動更新)
修業完畢 / 被當
   ↑
   └─ 前端手動設定 → 二退 (自動清空成績)
```

---

## 3. 直方圖自動上傳

### 工作流程

**API**: `POST /api/v0.1/Calculus_oom/Calculus_metadata/Score_MetadataWriter/step_diagram`

**自動執行流程**:
```
1. 生成直方圖 (matplotlib)
   ↓
2. 儲存到本地檔案系統
   ↓
3. 上傳到 MongoDB (test_pic_information)
   ↓
4. 更新 Test 狀態為「考卷成績結算」
   ↓
5. 返回圖片給前端
```

**範例**:
```python
response = requests.post(
    'http://localhost:8000/api/v0.1/Calculus_oom/Calculus_metadata/Score_MetadataWriter/step_diagram',
    json={
        'test_semester': '1141',
        'score_field': 'score_midterm',
        'bins': {'type': 'fixed_width', 'width': 10},
        'title': '1141 期中考 分數分布',
        'format': 'png'
    }
)

# 響應：直接返回圖片檔案
# Content-Type: image/png
# 同時後端已自動上傳到檔案系統並更新狀態
```

**後端自動執行**:
```python
# 1. 生成直方圖
plt.savefig(img_buffer, format='png')

# 2. 儲存到本地
file_path = os.path.join(UPLOAD_DIR, f"{test_uuid}_histogram.png")

# 3. 上傳到 MongoDB
NoSqlDbBusinessService.update_document(
    'test_pic_information',
    {'test_pic_uuid': file_uuid},
    {'test_pic_histogram': file_path}
)

# 4. 自動更新狀態
if test.test_states == '考卷完成':
    test.test_states = '考卷成績結算'  # ✅ 自動更新
```

---

## 4. 完整使用範例

### 4.1 考試完整流程

```python
import requests

base_url = 'http://localhost:8000/api/v0.1/Calculus_oom/Calculus_metadata'

# Step 1: 創建考試
response = requests.post(
    f'{base_url}/Test_MetadataWriter/create',
    json={
        'test_name': '期中考',
        'test_date': '114/12/28',
        'test_range': '1-1~2-6',
        'test_semester': '1141'
    }
)
test_uuid = response.json()['data']['test_uuid']
print(f"Test created: {test_uuid}, status: 尚未出考卷")

# Step 2: 上傳考卷 (自動更新狀態為「考卷完成」)
with open('midterm_exam.jpg', 'rb') as f:
    response = requests.post(
        f'{base_url}/test-filedata/create',
        data={'test_uuid': test_uuid, 'asset_type': 'paper'},
        files={'file': f}
    )
print(f"Paper uploaded, status: {response.json()['data']['test_states']}")  # 考卷完成

# Step 3: 學生填寫成績 (略)
# ...

# Step 4: 生成並上傳直方圖 (自動上傳 + 自動更新狀態為「考卷成績結算」)
response = requests.post(
    f'{base_url}/Score_MetadataWriter/step_diagram',
    json={
        'test_semester': '1141',
        'score_field': 'score_midterm',
        'title': '1141 期中考 分數分布'
    }
)
with open('histogram.png', 'wb') as f:
    f.write(response.content)
print(f"Histogram generated and auto-uploaded, status: 考卷成績結算")

# ✅ 完成！無需手動調用狀態更新 API
```

---

### 4.2 學生成績完整流程

```python
# Step 1: 批量上傳學生
with open('students_1141.xlsx', 'rb') as f:
    response = requests.post(
        f'{base_url}/Student_MetadataWriter/upload_excel',
        files={'file': f}
    )
print(f"Created {response.json()['data']['created_count']} students (status: 修業中)")

# Step 2: 填寫成績 (使用 Score_MetadataWriter/update)
# ...

# Step 3: 計算總成績 (自動更新學生狀態)
response = requests.post(
    f'{base_url}/Score_MetadataWriter/calculation_final',
    json={
        'test_semester': '1141',
        'passing_score': 60.0
    }
)
print(f"Final scores calculated, students auto-updated to 修業完畢/被當")

# Step 4: 匯出報表
response = requests.post(
    f'{base_url}/Student_MetadataWriter/feedback_excel',
    json={'student_semester': '1141'}
)
with open('final_report.xlsx', 'wb') as f:
    f.write(response.content)

# ✅ 完成！學生狀態自動更新
```

---

## 5. 前端操作簡化對比

### 5.1 考試狀態更新

**之前**（需要 3 次 API 調用）:
```javascript
// 1. 上傳考卷
await uploadPaper(testId, file)

// 2. 手動更新狀態
await updateTestStatus(testId, '出題完成')

// 3. 生成直方圖
const histogram = await generateHistogram(testId)

// 4. 上傳直方圖
await uploadHistogram(testId, histogram)

// 5. 再次手動更新狀態
await updateTestStatus(testId, '歷屆')
```

**現在**（只需 2 次 API 調用）:
```javascript
// 1. 上傳考卷 (自動更新狀態)
await uploadPaper(testId, file)  // ✅ 狀態自動變為「考卷完成」

// 2. 生成直方圖 (自動上傳 + 自動更新狀態)
await generateHistogram(testId)  // ✅ 自動上傳 + 狀態自動變為「考卷成績結算」
```

**節省**: 3 次 API 調用 → 2 次 (減少 33%)

---

### 5.2 學生成績計算

**之前**（需要 2 次 API 調用）:
```javascript
// 1. 計算總成績
await calculateFinalScores(semester)

// 2. 手動更新每個學生狀態
for (const student of students) {
    if (student.total_score >= 60) {
        await updateStudentStatus(student.id, '修業完畢')
    } else {
        await updateStudentStatus(student.id, '被當')
    }
}
```

**現在**（只需 1 次 API 調用）:
```javascript
// 1. 計算總成績 (自動更新所有學生狀態)
await calculateFinalScores(semester)  // ✅ 自動更新所有學生狀態
```

**節省**: N+1 次 API 調用 → 1 次 (減少 >90%)

---

## 6. 注意事項

### 6.1 冪等性保證

所有自動更新操作都是冪等的：
- 重複上傳考卷不會導致狀態錯誤
- 重複計算成績不會產生副作用
- 狀態只在符合條件時才會更新

### 6.2 錯誤處理

如果自動操作失敗：
- 主要操作（上傳、計算）仍會成功
- 錯誤會記錄在日誌中
- 可以手動調用 `Test_MetadataWriter/status` 補救

### 6.3 狀態流轉規則

**考試狀態**:
```
尚未出考卷 → 考卷完成 → 考卷成績結算
```

**學生狀態**:
```
修業中 → 修業完畢/被當
修業中 → 二退 (手動)
```

---

## 7. 測試建議

### 7.1 測試上傳考卷自動更新

```python
# 創建考試
test = create_test('1141', '期中考')
assert test['test_states'] == '尚未出考卷'

# 上傳考卷
response = upload_paper(test['test_uuid'], 'exam.jpg')
assert response['test_states'] == '考卷完成'  # ✅ 自動更新

# 驗證資料庫
test_db = get_test(test['test_uuid'])
assert test_db.test_states == '考卷完成'
```

---

### 7.2 測試生成直方圖自動上傳

```python
# 生成直方圖
response = generate_histogram('1141', 'score_midterm')
assert response.status_code == 200

# 驗證檔案已自動上傳
test = get_test_by_semester('1141')
assert test.pt_opt_score_uuid is not None

# 驗證 MongoDB 中有直方圖
doc = get_nosql_document(test.pt_opt_score_uuid)
assert doc['test_pic_histogram'] != ''

# 驗證狀態已更新
assert test.test_states == '考卷成績結算'  # ✅ 自動更新
```

---

### 7.3 測試學生狀態自動更新

```python
# 創建學生
student = create_student('1141', 'B11001001', '張三')
assert student['student_status'] == '修業中'

# 填寫成績
update_scores(student['student_uuid'], {
    'score_quiz1': 85,
    'score_midterm': 90,
    'score_quiz2': 88,
    'score_finalexam': 92
})

# 計算總成績
calculate_final_scores('1141', passing_score=60)

# 驗證狀態已自動更新
student_db = get_student(student['student_uuid'])
assert student_db.student_status == '修業完畢'  # ✅ 自動更新
assert float(student_db.score_total) >= 60
```

---

## 8. 總結

### 優點

1. ✅ **簡化前端邏輯**：減少 API 調用次數
2. ✅ **提高一致性**：避免忘記更新狀態
3. ✅ **改善用戶體驗**：操作更流暢
4. ✅ **減少錯誤**：自動化降低人為失誤

### 影響範圍

- ✅ test-filedata Actor (考卷上傳)
- ✅ Score Actor (成績計算、直方圖生成)
- ✅ Student Actor (學生狀態，已存在)

### 後續維護

- 確保日誌記錄完整
- 監控自動更新成功率
- 必要時提供手動補救機制

---

**更新完成時間**: 2026-01-05  
**架構變更**: 從手動觸發改為自動化流程 ✨

🎉 前端操作更簡化，後端邏輯更智能！
