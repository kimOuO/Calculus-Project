
# Calculus_oom Backend API Specification (LLM-Ready)

## 1. System Overview
- Platform: Calculus_oom
- System: Calculus_metadata
- API Prefix: /api/v0.1
- Architecture:
  - SQL DB: student, score, test metadata
  - Non-SQL Object Storage: exam papers, histograms

## 2. Actors
- Student_MetadataWriter
- Score_MetadataWriter
- Test_MetadataWriter
- test-filedata (Non-SQL)

---

## 3. Student Metadata Module

### Create Student
POST /Calculus_metadata/Student_MetadataWriter/create

```json
{
  "student_name": "test",
  "student_number": "B11002020",
  "student_semester": 1141
}
```

Behavior:
- Create student record
- Generate UUID
- Initialize status = 修業中

### Update Student
POST /Calculus_metadata/Student_MetadataWriter/update

```json
{
  "uid": "student_uuid",
  "student_name": "test",
  "student_number": "B11002020",
  "student_semester": 1141
}
```

### Delete Student
POST /Calculus_metadata/Student_MetadataWriter/delete

```json
{ "uid": "student_uuid" }
```

Cascade delete all related scores.

### Read Student
POST /Calculus_metadata/Student_MetadataWriter/read

- Single
```json
{ "student_uuid": "stu_xxx" }
```

- List
```json
{ "student_semester": "1142", "student_status": "修業中" }
```

- All
```json
{}
```

### Student Status
POST /Calculus_metadata/Student_MetadataWriter/status

```json
{ "status": "修業中 | 二退 | 被當 | 修業完畢" }
```

State Flow:
修業中 → 二退 / 被當 / 修業完畢

二退為使用者主動調整 調整完畢成二退狀態後 其成績將會空白 不列如任何成績計算當中
### Upload Students (Excel)
POST /Calculus_metadata/Student_MetadataWriter/upload_excel

- Upload .xlsx
- Backend generates UUID
- Internally reuse create API

### Export Students + Final Scores
POST /Calculus_metadata/Student_MetadataWriter/feedback_excel

```json
{ "student_semester": "1141" }
```

---

## 4. Score Metadata Module

### Create / Update Score
POST /Calculus_metadata/Score_MetadataWriter/create

```json
{
  "score_semester": "1141",
  "f_student_uuid": "student_uuid",
  "update_field": "score_quiz1 | score_midterm | score_quiz2 | score_finalexam",
  "score_value": 80
}
```

### Update Score
POST /Calculus_metadata/Score_MetadataWriter/update

```json
{
  "score_uuid": "score_uuid",
  "update_field": "score_quiz1",
  "score_value": 82
}
```

### Delete Score
POST /Calculus_metadata/Score_MetadataWriter/delete

```json
{ "uid": "score_uuid" }
```

### Read Score
POST /Calculus_metadata/Score_MetadataWriter/read

```json
{ "f_student_uuid": "student_uuid" }
```

### Calculate Final Score
POST /Calculus_metadata/Score_MetadataWriter/calculation_final

```json
{
  "test_semester": "1142",
  "passing_score": 60.0
}
```

### Test Statistics
POST /Calculus_metadata/Score_MetadataWriter/test_score

```json
{
  "score_semester": "1142",
  "score_field": "score_quiz1",
  "exclude_empty": true
}
```


### Score Distribution Diagram
POST /Calculus_metadata/Score_MetadataWriter/step_diagram

```json
{
  "test_semester": "1142",
  "score_field": "score_quiz1",
  "bins": { "type": "fixed_width", "width": 10 },
  "title": "1142 期中考 分數分布",
  "format": "png"
}
```
更新 test_status: 出題完成
---

## 5. Test Metadata Module

### Create Test
POST /Calculus_metadata/Test_MetadataWriter/create

```json
{
  "test_name": "期中考",
  "test_date": "114/12/28",
  "test_range": "1-1~2-6",
  "test_semester": "1141"
}
```

Initial status: 尚未出題

### Test Status
POST /Calculus_metadata/Test_MetadataWriter/status

```json
{ "status": "尚未出題 | 出題完成 | 歷屆" }
```

### Set Weights
POST /Calculus_metadata/Test_MetadataWriter/setweight

```json
{
  "test_semester": "1142",
  "weights": {
    "第一次小考": 0.2,
    "期中考": 0.3,
    "第二次小考": 0.2,
    "期末考": 0.3
  }
}
```
更新 status: 歷屆
---

## 6. test-filedata (Non-SQL)

> 本模組為 **純檔案管理服務（Pure File Storage API）**，  
> 僅負責考試相關之非結構化資料（圖片）存取。  
> ❗ **不得直接或間接修改任何 SQL Metadata（包含 test_status）**。

---

### 6.1 Asset Type 定義（固定，不可擴充）

| asset_type | 說明 | 關聯對象 | 是否影響業務狀態 |
|---|---|---|---|
| paper | 原始考卷圖片（可多張） | Test | ❌ 否 |
| test_pic | 單張考卷圖片（legacy） | Test | ❌ 否 |
| histogram | 成績級距分布圖 | Test | ❌ 否 |
| test_pic_histogram | legacy 級距圖 | Test | ❌ 否 |

> ⚠️ 不可根據檔案是否存在，自動推論考試狀態。

---

### 6.2 Upload Exam Paper / Histogram

**POST** `/Calculus_metadata/test-filedata/create`

```python
data = {
  "test_uuid": "test_uuid",
  "asset_type": "paper | histogram"
}

files = [
  ("file", ("p1.jpg", <binary>, "image/jpeg"))
]
```

#### 系統行為（僅限本模組）

- 將檔案存入 Non-SQL Object Storage
- 為每個檔案產生唯一 `file_uuid`
- 建立 `file_uuid ↔ test_uuid` 關聯
- **不得執行以下行為：**
  - ❌ 修改 `test_status`
  - ❌ 修改 Test Metadata
  - ❌ 呼叫其他 Module API

> 🔔 若需將考試標記為「出題完成」，  
> 必須由呼叫端額外呼叫 `Test_MetadataWriter.status`。

---

### 6.3 Update File（Replace Only）

**POST** `/Calculus_metadata/test-filedata/update`

```python
data = {
  "uid": "file_uuid",
  "asset_type": "test_pic"
}

files = {
  "file": ("new_exam.jpg", <binary>, "image/jpeg")
}
```

#### 規則

- 僅更新檔案內容
- `file_uuid` 不變
- 不允許變更 `asset_type`
- 不影響任何業務狀態或 SQL 資料

---

### 6.4 Read File

**POST** `/Calculus_metadata/test-filedata/read`

```json
{
  "test_pic_uuid": "file_uuid",
  "asset_type": "test_pic | histogram"
}
```

#### 系統行為

- 驗證：
  - `file_uuid` 是否存在
  - `asset_type` 是否與該檔案一致
- 成功時回傳 binary stream（image/jpeg 或 image/png）

---

### 6.5 Delete File

**POST** `/Calculus_metadata/test-filedata/delete`

```json
{
  "test_pic_uuid": "file_uuid",
  "asset_type": "test_pic | test_pic_histogram"
}
```

#### 系統行為

- 僅刪除指定檔案
- 不影響：
  - Test.status
  - Test Metadata
- 不檢查該 Test 是否仍有其他檔案存在

---

### 6.6 Forbidden Operations（嚴格禁止）

❌ 因檔案上傳或刪除而修改 `test_status`  
❌ 因檔案存在而推論「出題完成」  
❌ 使用未定義之 `asset_type`  
❌ 跨模組直接操作 SQL Metadata  

---

## 7. Error Format（統一）

```json
// 200
{ "detail": "Metadata created successfully", "data": {...} }

// 400
{ "detail": "ClientError: Missing required keys" }

// 400
{ "detail": "ClientError: asset_type not allowed" }

// 400
{ "detail": "ClientError: asset_type mismatch with file_uuid" }

// 404
{ "detail": "Source not found" }

// 500
{ "detail": "Unknown error: {error_message}" }
```

---

## 8. LLM Implementation Rules（強制）

- UUID 必須由後端產生
- SQL 與 Non-SQL 必須完全分離
- 不可在 test-filedata 中實作任何業務狀態邏輯
- 所有流程語意（如「出題完成」）必須由呼叫端顯式 orchestrate
- 檔案操作不得破壞資料一致性
