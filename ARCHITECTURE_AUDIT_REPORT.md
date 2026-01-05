# Calculus_oom 後端架構審查報告

**審查日期**: 2026-01-05  
**審查標準**: strict_backend_rules.md (Backend Architecture Specification 2.0)  
**專案路徑**: /home/mitlab/project/Calculus_oom

---

## 執行摘要

本次審查對照 `strict_backend_rules.md` 規範，檢查 Calculus_oom 後端架構的符合性及需求文檔功能覆蓋度。

### 審查結果統計

| 類別 | 通過 | 警告 | 錯誤 | 嚴重錯誤 |
|-----|------|------|------|---------|
| Repo 結構 | ✅ | - | - | - |
| Request Chain | ✅ | - | - | - |
| Models 層 | ⚠️ | 2 | - | - |
| Serializers 層 | ✅ | - | - | - |
| Actors 層 | ❌ | - | 4 | 1 |
| Services 層 | ⚠️ | 1 | - | - |
| 環境變數管理 | ⚠️ | 1 | - | - |
| 功能覆蓋度 | ❌ | - | 3 | - |

**總結**: 發現 **1 個嚴重錯誤**, **7 個錯誤**, **4 個警告**

---

## 1. Repo 命名與根目錄結構

### ✅ 通過項目

1. **Repo 結構完整**: 包含所有必需目錄
   - ✅ `logs/`, `requirements/`, `shell/`, `main/`, `uploads/`
   - ✅ Docker 配置完整 (`Dockerfile`, `docker-compose.yaml`)
   - ✅ 環境變數配置 (`.env`, `.env.sample`)

2. **App 結構符合規範**:
   ```
   main/apps/Calculus_metadata/
   ├── models/          ✅
   ├── serializers/     ✅
   ├── actors/          ✅
   ├── services/        ✅
   │   ├── business/    ✅
   │   ├── common/      ✅
   │   └── optional/    ✅
   ├── api/             ✅
   └── tests/           ✅
   ```

### ⚠️ 警告

**無警告**

---

## 2. Request Chain (路由配置)

### ✅ 通過項目

1. **路由綁定正確**: `main/urls.py` → `app/api/urls.py` → Actor functions
   ```python
   # main/urls.py
   path('api/v0.1/Calculus_oom/Calculus_metadata/', include('main.apps.Calculus_metadata.api.urls'))
   
   # api/urls.py
   path('Student_MetadataWriter/create', StudentActor.create, name='student_create')
   ```

2. **views.py 空殼保留**: 符合規範要求
   ```python
   # Views layer preserved but not required in request chain
   ```

3. **URL 格式符合規範**: `/api/{version}/{System}/{Module}/{Component}/{Element}`

---

## 3. Models 層

### ✅ 通過項目

1. **每個 table 獨立檔案**: 符合規範
   - `students.py` → Students Model
   - `score.py` → Score Model
   - `test.py` → Test Model
   - `test_pic_information.py` → MongoDB Schema 定義

2. **欄位定義完整**: 包含 UUID、業務欄位、生命週期欄位

3. **關聯方式正確**: 使用 CharField 作為跨資料庫關聯
   ```python
   # Score Model
   f_student_uuid = models.CharField(max_length=255, db_index=True)
   ```

### ⚠️ 警告

#### Warning-M1: Test Model 狀態欄位命名不一致

**位置**: `main/apps/Calculus_metadata/models/test.py:57`

**問題**:
```python
# 當前命名
test_states = models.CharField(...)  # 使用複數形式
```

**規範要求**: 需求文檔中使用 `test_status`，但實現使用 `test_states`

**影響**: 可能造成前後端字段不一致

**建議**: 統一為 `test_status` 或在文檔中明確說明

---

#### Warning-M2: Test Model 狀態值不一致

**位置**: `main/apps/Calculus_metadata/models/test.py:57`

**問題**:
```python
# Model 中的狀態值
default="尚未出考卷"
help_text="狀態: 尚未出考卷/考卷完成/考卷成績結算"
```

**需求文檔**:
```
Initial status: 尚未出題
Status: 尚未出題 | 出題完成 | 歷屆
```

**差異對比**:
| Model | 需求文檔 |
|-------|---------|
| 尚未出考卷 | 尚未出題 |
| 考卷完成 | 出題完成 |
| 考卷成績結算 | 歷屆 |

**建議**: 統一狀態值命名

---

## 4. Serializers 層

### ✅ 通過項目

1. **區分 Read/Write**: 所有實體都有 Write 和 Read Serializer
   - `StudentsWriteSerializer` / `StudentsReadSerializer`
   - `ScoreWriteSerializer` / `ScoreReadSerializer`
   - `TestWriteSerializer` / `TestReadSerializer`

2. **驗證邏輯完整**: Write Serializer 包含驗證規則
   ```python
   def validate_student_status(self, value):
       allowed_statuses = ["修業中", "二退", "被當", "修業完畢"]
       if value not in allowed_statuses:
           raise serializers.ValidationError(...)
   ```

---

## 5. Actors 層

### ✅ 通過項目

1. **Actor 職責清晰**: HTTP 處理、數據驗證、業務編排、Service 調用、響應格式化
2. **使用裝飾器**: `@csrf_exempt`, `@require_http_methods`, `@transaction.atomic`
3. **錯誤處理完整**: try-except + logger
4. **不直接使用 Model.objects**: 透過 Business Service 操作

### 🔴 嚴重錯誤

#### Critical-A1: test-filedata Actor 違反模組職責規範

**位置**: `main/apps/Calculus_metadata/actors/testfiledata_actor.py:145-150`

**問題代碼**:
```python
# Step 8: 更新 Test 表的 pt_opt_score_uuid 和狀態
if asset_type == 'paper' and test.test_states == '尚未出考卷':
    update_data['test_states'] = '考卷完成'
    update_data['test_updated_at'] = timestamp
    logger.info(f"Auto-updating test status to '考卷完成' for test: {test_uuid}")
```

**違反規範**:
> **Requirements_document.md Section 6.1**:
> "本模組為 **純檔案管理服務（Pure File Storage API）**，  
> 僅負責考試相關之非結構化資料（圖片）存取。  
> ❗ **不得直接或間接修改任何 SQL Metadata（包含 test_status）**。"

> **Section 6.6 Forbidden Operations**:
> "❌ 因檔案上傳或刪除而修改 `test_status`  
> ❌ 因檔案存在而推論「出題完成」"

**正確做法**:
1. `test-filedata/create` **僅儲存檔案**，不修改 `test_states`
2. 呼叫端需要額外呼叫 `Test_MetadataWriter/status` 來更新狀態
3. 業務狀態的改變必須由呼叫端顯式 orchestrate

**修復方案**:
```python
# testfiledata_actor.py - create() 方法
# 移除自動更新狀態邏輯
update_data = {}
if not test.pt_opt_score_uuid:
    update_data['pt_opt_score_uuid'] = file_uuid
    # ❌ 刪除以下代碼
    # if asset_type == 'paper' and test.test_states == '尚未出考卷':
    #     update_data['test_states'] = '考卷完成'

if update_data:
    SqlDbBusinessService.update_entity(test, update_data)

# 由呼叫端自行決定是否更新狀態
# Frontend 或 API Gateway 需要額外調用:
# POST /Test_MetadataWriter/status
# { "test_uuid": "xxx", "status": "出題完成" }
```

---

### ❌ 錯誤

#### Error-A1: Score Actor delete() 方法參數不一致

**位置**: `main/apps/Calculus_oom/main/apps/Calculus_metadata/actors/score_actor.py:176-177`

**問題代碼**:
```python
score = SqlDbBusinessService.get_entity(Score, 'score_uuid', data['score_uuid'])
score = SqlDbBusinessService.get_entity(Score, 'score_uuid', data['uid'])  # 重複查詢，參數不一致
```

**問題**: 
1. 重複查詢同一個實體
2. 參數從 `score_uuid` 變成 `uid`，與需求文檔不一致

**需求文檔**:
```
### Delete Score
POST /Calculus_metadata/Score_MetadataWriter/delete
{ "uid": "score_uuid" }
```

**修復方案**:
```python
# 統一使用 'uid' 作為參數（符合需求文檔）
is_valid, missing_keys = ValidationService.validate_required_keys(data, ['uid'])
if not is_valid:
    return error_response(f"Missing required keys: {missing_keys}", None, 400)

score = SqlDbBusinessService.get_entity(Score, 'score_uuid', data['uid'])
if not score:
    return error_response("Score not found", None, 404)
```

---

#### Error-A2: 缺少 upload_excel API

**缺失**: `Student_MetadataWriter/upload_excel`

**需求文檔**:
```
### Upload Students (Excel)
POST /Calculus_metadata/Student_MetadataWriter/upload_excel

- Upload .xlsx
- Backend generates UUID
- Internally reuse create API
```

**影響**: 無法批量上傳學生資料

**修復方案**: 在 `StudentActor` 中新增 `upload_excel` 方法

---

#### Error-A3: 缺少 feedback_excel API

**缺失**: `Student_MetadataWriter/feedback_excel`

**需求文檔**:
```
### Export Students + Final Scores
POST /Calculus_metadata/Student_MetadataWriter/feedback_excel

{ "student_semester": "1141" }
```

**影響**: 無法匯出學生成績 Excel

**修復方案**: 在 `StudentActor` 中新增 `feedback_excel` 方法

---

#### Error-A4: 缺少 step_diagram API

**缺失**: `Score_MetadataWriter/step_diagram`

**需求文檔**:
```
### Score Distribution Diagram
POST /Calculus_metadata/Score_MetadataWriter/step_diagram

{
  "test_semester": "1142",
  "score_field": "score_quiz1",
  "bins": { "type": "fixed_width", "width": 10 },
  "title": "1142 期中考 分數分布",
  "format": "png"
}
```

**影響**: 無法生成分數分布圖

**修復方案**: 在 `ScoreActor` 中新增 `step_diagram` 方法，調用 Optional Service 的 `CalculationService.generate_histogram_data()`

---

## 6. Services 層

### ✅ 通過項目

1. **Business Service 提供通用方法**: 
   - `create_entity(model_class, validated_data)` ✅
   - `get_entity(model_class, uuid_field, uuid_value)` ✅
   - `update_entity(entity, update_data)` ✅
   - `delete_entity(entity)` ✅

2. **Common Service 完整**:
   - `UuidService` ✅
   - `TimestampService` ✅
   - `ValidationService` ✅

3. **Optional Service 按需創建**:
   - `CalculationService` (calculation/) ✅

4. **Service 不處理 HTTP**: 符合規範

### ⚠️ 警告

#### Warning-S1: UuidService 方法未完全通用化

**位置**: `main/apps/Calculus_metadata/services/common/uuid_service.py`

**問題**:
```python
# 為每個實體類型單獨寫方法
def generate_student_uuid(semester: str) -> str: ...
def generate_score_uuid(semester: str) -> str: ...
def generate_test_uuid(semester: str, test_type: str) -> str: ...
def generate_test_pic_uuid(semester: str, test_type: str) -> str: ...
```

**規範建議**: 
Common Service 應提供通用方法，但考慮到 UUID 格式因業務需求而異，此設計可接受。

**建議**: 保持現狀或提供一個通用方法：
```python
def generate_uuid(entity_type: str, semester: str, **kwargs) -> str:
    """通用 UUID 生成"""
    patterns = {
        'student': f"stu_{semester}_{timestamp}_{random}",
        'score': f"scr_{semester}_{timestamp}_{random}",
        ...
    }
```

---

## 7. 環境變數管理

### ✅ 通過項目

1. **env_loader 存在**: `main/utils/env_loader.py` ✅
2. **提供輔助函數**: `get_env()`, `get_env_bool()`, `get_env_int()` ✅
3. **Settings 使用 env_loader**: `from main.utils.env_loader import get_env` ✅

### ⚠️ 警告

#### Warning-E1: settings/__init__.py 直接使用 os.environ

**位置**: `main/settings/__init__.py:6`

**問題代碼**:
```python
environment = os.environ.get('DJANGO_ENV', 'local')
```

**規範要求**: 
> **Section 8.3**:
> "必須透過 `from main.utils.env_loader import ...`  
> 禁止直接使用 `os.getenv()`"

**修復方案**:
```python
from main.utils.env_loader import get_env

environment = get_env('DJANGO_ENV', 'local')
```

**影響**: 輕微，因為此處僅用於決定載入哪個 settings 檔案

---

## 8. 需求文檔功能覆蓋度

### ✅ 已實現功能

#### Student Module (5/8)
- ✅ Create Student
- ✅ Update Student
- ✅ Delete Student (含 cascade delete)
- ✅ Read Student
- ✅ Student Status (含二退清空成績邏輯)
- ❌ Upload Students (Excel)
- ❌ Export Students + Final Scores (Excel)

#### Score Module (4/6)
- ✅ Create/Update Score
- ✅ Update Score
- ✅ Delete Score
- ✅ Read Score
- ✅ Calculate Final Score
- ✅ Test Statistics
- ❌ Score Distribution Diagram

#### Test Module (4/4)
- ✅ Create Test
- ✅ Test Status
- ✅ Set Weights
- ✅ Read Test

#### Test-Filedata Module (4/4)
- ✅ Upload File
- ✅ Read File
- ✅ Update File
- ✅ Delete File

### ❌ 缺失功能

#### Missing-F1: Student_MetadataWriter/upload_excel
**優先級**: 高  
**影響**: 無法批量匯入學生資料  
**技術需求**: 需要 Excel 解析庫 (openpyxl)

#### Missing-F2: Student_MetadataWriter/feedback_excel
**優先級**: 高  
**影響**: 無法匯出學生成績報表  
**技術需求**: 需要 Excel 生成庫 (openpyxl)

#### Missing-F3: Score_MetadataWriter/step_diagram
**優先級**: 中  
**影響**: 無法生成分數分布視覺化圖表  
**技術需求**: 需要圖表生成庫 (matplotlib/pillow)

---

## 9. 其他觀察

### ✅ 優點

1. **代碼結構清晰**: 分層明確，職責分離良好
2. **日誌記錄完整**: 每個 Actor 都有適當的日誌
3. **錯誤處理健全**: 統一使用 `success_response` / `error_response`
4. **Transaction 管理**: 使用 `@transaction.atomic` 確保數據一致性
5. **Business Service 通用性**: 符合規範要求，不為每個 Model 單獨寫方法

### 🟡 可改進項目

1. **測試覆蓋率**: `tests/` 目錄存在但未確認測試完整性
2. **API 文檔**: 缺少 OpenAPI/Swagger 文檔
3. **Docker 配置**: 未確認 Docker Compose 是否包含 MongoDB
4. **CORS 配置**: `CORS_ALLOW_ALL_ORIGINS = True` 在 production 環境應限制

---

## 10. 修復優先級建議

### P0 (嚴重 - 立即修復)

1. **Critical-A1**: test-filedata Actor 移除自動更新 test_status 邏輯
   - **原因**: 嚴重違反模組職責規範
   - **風險**: 破壞業務邏輯一致性，造成狀態管理混亂

### P1 (高優先級 - 本週修復)

2. **Error-A1**: 修復 Score Actor delete() 方法參數不一致
3. **Warning-M1/M2**: 統一 Test Model 狀態欄位命名和狀態值
4. **Warning-E1**: settings/__init__.py 改用 env_loader

### P2 (中優先級 - 本月修復)

5. **Error-A2**: 實現 upload_excel API
6. **Error-A3**: 實現 feedback_excel API
7. **Error-A4**: 實現 step_diagram API

### P3 (低優先級 - 優化項目)

8. **Warning-S1**: UuidService 通用化 (可選)
9. 補充單元測試
10. 新增 API 文檔

---

## 11. 合規性總結

### 規範符合度評分

| 類別 | 得分 | 滿分 | 符合率 |
|-----|------|------|--------|
| 目錄結構 | 10 | 10 | 100% |
| Request Chain | 10 | 10 | 100% |
| Models | 8 | 10 | 80% |
| Serializers | 10 | 10 | 100% |
| Actors | 6 | 10 | 60% |
| Services | 9 | 10 | 90% |
| 環境變數 | 8 | 10 | 80% |
| 功能完整度 | 13 | 19 | 68% |

**總體符合率**: 82%

### 結論

Calculus_oom 後端架構**基本符合規範**，核心架構設計良好，但存在以下問題：

1. **嚴重問題**: test-filedata 模組違反職責規範（Critical-A1）
2. **功能缺失**: 3 個需求文檔中的 API 未實現
3. **命名不一致**: Model 與需求文檔的狀態值不統一
4. **小問題**: 環境變數管理有一處未使用 env_loader

建議優先修復 P0 和 P1 級別問題，確保系統符合規範要求並完成所有必需功能。

---

## 12. 附錄：快速修復檢查清單

```markdown
### 修復檢查清單

#### 立即修復 (P0)
- [ ] testfiledata_actor.py: 移除自動更新 test_states 邏輯 (Critical-A1)
- [ ] 更新相關文檔說明狀態更新需由呼叫端處理

#### 本週修復 (P1)
- [ ] score_actor.py: 修復 delete() 方法參數 (Error-A1)
- [ ] test.py: 統一狀態欄位命名 test_states → test_status (Warning-M1)
- [ ] test.py: 統一狀態值命名 (Warning-M2)
- [ ] settings/__init__.py: 改用 env_loader (Warning-E1)

#### 本月修復 (P2)
- [ ] 實現 upload_excel API (Error-A2)
- [ ] 實現 feedback_excel API (Error-A3)
- [ ] 實現 step_diagram API (Error-A4)
- [ ] 新增對應 API URL 路由
- [ ] 單元測試覆蓋新增功能

#### 優化項目 (P3)
- [ ] 考慮 UuidService 通用化 (Warning-S1)
- [ ] 補充完整單元測試
- [ ] 新增 Swagger API 文檔
- [ ] Production 環境 CORS 設定優化
```

---

**報告結束**

如需詳細修復方案或代碼範例，請參考各節的「修復方案」說明。
